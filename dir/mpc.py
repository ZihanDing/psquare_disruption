# coding=utf-8
from gurobipy import *
import dir.data_process as dp


def mpc_iteration(starttimeslot, timehorizon, distance,vacant, occupied, beta, chargingresource, futuresupply,disruption):
    n,p = dp.obtain_regions()
    L, L1, L2, K = dp.exp_config()

    po,pv,qo,qv = dp.obtain_transition(n,K,starttimeslot)

    # get estimated demand from files
    inputdemand = []
    for i in range(n):
        one = []
        for j in range(K):
            one.append(0)
        inputdemand.append(one)

    for k in range(K):
        fopen = open('./historydemand/slot20/prediction/' + str((k + starttimeslot) % 72), 'r')
        loc = 0
        for line in fopen:
            line = line.strip().split(',')
            valuesum = 0
            for value in line:
                valuesum += (float(value))
            inputdemand[loc][k] = valuesum
            loc = loc + 1

    demand = {}
    for i in range(n):
        for k in range(K):
            demand[i, k] = inputdemand[i][k]

    W = {}
    for i in range(n):
        for j in range(n):
            for k in range(K):
                W[i, j, k] = distance[i][j] # TODO W(i,j,k) describe the driving time from region i to region j during time slot k.

    if disruption[1] < starttimeslot <= disruption[2]: # 在disruption scale中
        for i in range(len(disruption[0])):
            p[disruption[0][i]] = 0 # 单个region直接shut down  注意这里是disruption发生time slot的下一个time slot

    pp = {} #PP represent p[i,kp-q]
    for i in range(n):
        for j in range(K):
            pp[i, j] = p[i] - chargingresource[i][j]
            if pp[i, j] < 0:
                pp[i,j] = 0
                print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
    # ------------------------------------------------------------------
    # ??
    reachable = []
    fopen = open('./datadir/reachable', 'r')
    for k in fopen:
        k = k.strip('\n')
        k = k.split(',')
        one = []
        for value in k:
            one.append(float(value))
        reachable.append(one)
    # ??
    c = {}
    for i in range(n):
        for j in range(n):
            for k in range(K):
                c[i, j, k] = 1 - reachable[i][j]
    # ------------------------------------------------------------------
    try:

        # Create a new model
        m = Model("CPS")

        # Create variables
        X = {}
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    for k in range(K):
                        for q in range(1, 1 + ((L - l - 1) / L2)):
                            if l < 0:
                                X[i, j, l, k, q] = m.addVar(lb=0.0, vtype=GRB.INTEGER,
                                                            name="X[%s,%s,%s,%s,%s]" % (i, j, l, k, q))
                            else:
                                X[i, j, l, k, q] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS,
                                                            name="X[%s,%s,%s,%s,%s]" % (i, j, l, k, q))

                            if q > 2:
                                m.addConstr(X[i, j, l, k, q] == 0)
                            else:
                                m.addConstr(X[i, j, l, k, q] <= 800)# TODO 其实这里应该是700多辆车 但是限制在800以内

        V = {} # The number of Vaccant l-th level e-taxis at region i at the begining of time slot k before being dispatched for charging respectively,
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    V[i, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="V[%s,%s,%s]" % (i, l, k))
                    m.addConstr(V[i, l, k] <= 800)

        O = {} # The number of Occupied l-th level e-taxis at region i at the begining of time slot k before being dispatched for charging respectively,
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    O[i, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="O[%s,%s,%s]" % (i, l, k))
                    m.addConstr(O[i, l, k] <= 800)

        for i in range(n): # 初始化V和O 给定timeslot0的时候现有的vacant和occupied
            for l in range(L):
                m.addConstr(V[i, l, 0] == vacant[i, l])
                m.addConstr(O[i, l, 0] == occupied[i, l])

        S = {} # total number of available e-taxis at the l-th energy level with region i during time slok k
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    S[i, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="S[%s,%s,%s]" % (i, l, k))
                    m.addConstr(S[i, l, k] <= 800)

        D = {}
        for i in range(n): # The number of l-th energy level e-taxis dispatched to region i during time slot k with q time slots charging duration.
            for l in range(L):
                for k in range(K):
                    for q in range(1, 1 + ((L - l - 1) / L2)):
                        D[i, l, k, q] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="D[%s,%s,%s,%s]" % (i, l, k, q))
                        m.addConstr(D[i, l, k, q] <= 800)

        Du = {} # For l-th level e-taxis dispatched to region i at time slot k for charging q time slots, the number of unfininsh charging vehicles by the end of optimization time horizon.
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    for q in range(1, 1 + ((L - l - 1) / L2)):
                        Du[i, l, k, q] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="Du[%s,%s,%s,%s]" % (i, l, k, q))
                        m.addConstr(Du[i, l, k, q] <= 800)
        #
        Db = {} # The number of e-taxis with higher charging priority
        for i in range(n):
            for k in range(K):
                for q in range(1, 1 + ((L - 1) / L2)):
                    Db[i, k, q] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="Db[%s,%s,%s]" % (i, k, q))

        Df = {}
        for i in range(n):
            for k in range(K):
                for q in range(1, 1 + ((L - 1) / L2)):
                    for kp in range(k + q, K + 1):
                        Df[i, k, q, kp] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="Df[%s,%s,%s,%s]" % (i, k, q, kp))

        Y = {}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    for q in range(1, 1 + ((L - l - 1) / L2)):
                        for kp in range(k + q, K + 1):
                            Y[i, l, k, q, kp] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS,
                                                         name="Y[%s,%s,%s,%s,%s]" % (i, l, k, q, kp))

        U = {}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    U[i, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="U[%s,%s,%s]" % (i, l, k))

        for i in range(n): # 给定constraint
            for l in range(L):
                for k in range(K):
                    m.addConstr(S[i, l, k] == (V[i, l, k] - sum(
                        sum(X[i, j, l, k, q] for j in range(n)) for q in range(1, 1 + ((L - l - 1) / L2)))))

        for i in range(n):
            for l in range(L):
                for k in range(K):
                    m.addConstr(
                        sum(X[i, j, l, k, q] for j in range(n) for q in range(1, 1 + ((L - l - 1) / L2))) <= V[i, l, k])

        for i in range(n):
            for l in range(L):
                for k in range(K - 1):
                    '''为什么这里这么判断 和文章写的不大一样噻'''
                    if l <= L - L1 - 1:
                        m.addConstr(V[i, l, k + 1] == (sum((pv[j, i, k] * S[j, l + L1, k]) for j in range(n)) + sum(
                            (qv[j, i, k] * O[j, l + L1, k]) for j in range(n)) + U[i, l, k + 1]
                                                       + futuresupply[i, l, k + 1]))
                    else:
                        m.addConstr(V[i, l, k + 1] == U[i, l, k + 1])
                    # m.addConstr(V[i,l,k+1]==(sum((pv[j,i,k]*S[j,l+L1,k]) for j in range(n)) + sum((qv[j,i,k]*O[j,l+L1,k]) for j in range(n)) + U[i,l,k+1]))

        for i in range(n):
            for l in range(L - L1):
                for k in range(K - 1):
                    m.addConstr(O[i, l, k + 1] == (sum((po[j, i, k] * S[j, l + L1, k]) for j in range(n)) + sum(
                        (qo[j, i, k] * O[j, l + L1, k]) for j in range(n))))

        # for i in range(n):
        #     for j in range(n):
        #         for l in range(L):
        #             for k in range(K):
        #                 for q in range(1,(L-l-1)/L2):
        #                     m.addConstr(X[i,j,l,k,q]*reachable[i][j]== 0)

        for i in range(n):
            for l in range(L):
                for k in range(K):
                    for q in range(1, (L - l - 1) / L2):
                        m.addConstr(D[i, l, k, q] == sum(X[j, i, l, k, q] for j in range(n)))

        for i in range(n):
            for l in range(L):
                for k in range(K):
                    for q in range(1, (L - l - 1) / L2):
                        m.addConstr(
                            Du[i, l, k, q] == (D[i, l, k, q] - sum(Y[i, l, k, q, kp] for kp in range(k + q, K + 1))))
                        m.addConstr(0 <= Du[i, l, k, q])
        #
        for i in range(n):
            for k in range(K):
                for q in range(1, (L - 1) / L2):
                    m.addConstr(Db[i, k, q] == (sum(
                        sum(sum(D[i, l1, k1, q1] for q1 in range(1, 1 + (L - 1 - l1) / L2)) for l1 in range(K)) for k1
                        in range(k)) + sum(sum(D[i, l1, k, q1] for q1 in range(1, 1 + min(q - 1, (L - 1 - l1) / L2)))
                                           for l1 in range(L))))

        for i in range(n):
            for k in range(K):
                for q in range(1, (L - 1) / L2):
                    for kp in range(k + q, K + 1):
                        m.addConstr(Df[i, k, q, kp] == (
                                sum(sum(sum(sum(Y[i, l1, k1, q1, kp1] for kp1 in range(k1 + q1, kp - q + 1))
                                            for q1 in range(1, min((L - l1 - 1) / L2, kp - q - k1) + 1)) for k1 in
                                        range(k))
                                    for l1 in range(L)) +
                                sum(sum(sum(Y[i, l1, k, q1, kp1] for kp1 in range(k + q1, kp - q + 1))
                                        for q1 in range(1, min(q - 1, kp - q - k, (L - l1 - 1) / L2) + 1)) for l1 in
                                    range(L))))

        for i in range(n):
            for k in range(K):
                for q in range(1, ((L - 1) / L2) + 1):
                    for kp in range(k + q, K + 1):
                        # TODO why heres pp[i-k] but not p[kp-q]
                        m.addConstr(Db[i, k, q] - Df[i, k, q, kp] + sum(Y[i, l, k, q, kp] for l in range((L - q * L2))) <= pp[i, k])
                        # m.addConstr(Db[i, k, q] - Df[i, k, q, kp] + sum(Y[i, l, k, q, kp] for l in range((L - q * L2))) <= p[kp-q])

        for i in range(n):
            for lp in range(L):
                for kp in range(K):
                    m.addConstr(U[i, lp, kp] == sum(
                        sum(Y[i, lp - q * L2, k1, q, kp] for k1 in range(kp - q + 1)) for q in
                        range(1, 1 + (lp - 1) / L2)))

        for i in range(n):
            for l in range(L):
                for k in range(K):
                    if k == 0:
                        m.addConstr(S[i, l, k] <= V[i, l, k])
                    else:
                        if L - L1 - 1 <= l:
                            m.addConstr(S[i, l, k] <= V[i, l, k])
                        else:
                            m.addConstr(S[i, l, k] <= V[i, l, k])
                    # m.addConstr(S[i,l,k]<=100)

        for i in range(n):
            for k in range(K):
                for l in range(L1 + 1):
                    m.addConstr(S[i, l, k] <= 0.999)

        kk = {}
        for i in range(n):
            for k in range(K):
                kk[i, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="kk[%s,%s]" % (i, k))
                m.addConstr(0 <= kk[i, k])
                m.addConstr((demand[i, k] - sum((S[i, l, k]) for l in range(L))) <= kk[i, k])
                m.addConstr((-demand[i, k] + sum((S[i, l, k]) for l in range(L))) <= kk[i, k])

        obj1 = sum(kk[i, k]for i in range(n) for k in range(K)) #Js
        # obj1 = sum(  sum(    ((demand[i,k]-sum((S[i,l,k]) for l in range(L))))  for i in range(n)) for k in range(K))
        obj2 = sum(sum(sum(
            (sum(sum(X[i, j, l, k, q] for q in range(1, 1 + (L - 1 - l) / L2)) for l in range(L)) * W[i, j, k]) for i in range(n)) for j in range(n)) for k in range(K)) # Jidle

        obj3 = sum(Y[i, l, k, q, kp] * (kp - k) for i in range(n) for l in range(L) for k in range(K) for q in range(1, 1 + ((L - 1 - l) / L2)) for kp in range(k + q, K + 1))

        obj4 = sum(Du[i, l, k, q] * (K + 2) for i in range(n) for l in range(L) for k in range(K) for q in range(1, 1 + ((L - l - 1) / L2)))

        obj5 = obj3 + obj4 #J wait
        obj = obj1 + (0.3 * 60 * obj2 / 40.0 + 0.05 * 20 * obj5) * beta
        # obj= obj1 + beta*(60*obj2/40.0)
        # obj=obj1



        m.setObjective(obj, GRB.MINIMIZE)

        m.setParam(GRB.Param.TimeLimit, 150)
        # m.Params.BarHomogeneous = 1

        m.optimize()

        print str(m.objVal) + "----------------"

        out = {}
        for v in m.getVars():
            if 'X' in v.VarName:
                line = v.VarName
                line = line.split('[')
                line = line[1]
                line = line.split(']')
                line = line[0]
                line = line.split(',')
                x1 = int(float(line[0]))
                x2 = int(float(line[1]))
                x3 = int(float(line[2]))
                x4 = int(float(line[3]))
                x5 = int(float(line[4]))
                if x4 == 0:
                    out[x1, x2, x3, x5] = v.x
        out1 = {}
        for v in m.getVars():
            if 'Y' in v.VarName:
                line = v.VarName
                line = line.split('[')
                line = line[1]
                line = line.split(']')
                line = line[0]
                line = line.split(',')
                x1 = int(float(line[0]))
                x2 = int(float(line[1]))
                # x3 = int(float(line[2]))
                # x4 = int(float(line[3]))
                if x2 == 0:
                    out1[x1] = v.x
        supply1 = {}
        for v in m.getVars():
            if 'S' in v.VarName:
                line = v.VarName
                line = line.split('[')
                line = line[1]
                line = line.split(']')
                line = line[0]
                line = line.split(',')
                x1 = int(float(line[0]))
                x2 = int(float(line[1]))
                x3 = int(float(line[2]))
                # x4 = int(float(line[3]))
                if x3 == 0:
                    supply1[x1, x2] = v.x
                # if x3==0 and x2<L1:
                #     print v.VarName,v.x
        csupp = 0
        for i in range(n):
            csupp += (sum(supply1[i, l] for l in range(L)) - out1[i])
        print csupp, (sum(demand[i, 0] for i in range(n)))

        out1 = {}
        for i in range(n):
            out1[i] = 0
        return out, out1

    except GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error')
