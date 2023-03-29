#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：newevaluation_dis 
@File    ：mpc_alpha.py
@IDE     ：PyCharm 
@Author  ：Zihan Ding
@Date    ：3/27/23 11:20 PM 
@Description: This file is used for iteration for calculating alpha
'''
from gurobipy import *
import dir.data_process as dp

predictionerror = 1.0

def mpc_iteration_optimize_utility(starttimeslot,vacant,occupied,beta,disruption,dis):
    n=0 # number of regions
    fopen =  open('./datadir/chargerindex','r')
    for k in fopen:
        n=n+1

#--------------------------------------------------------------
    L, L1, L2, K = dp.exp_config()

    pv={}

    for k in range(K):
        fopen = open('./transition/slot20/'+str(k+starttimeslot)+'pv','r')
        data=[]
        for line in fopen:
            line = line.strip('\n')
            line =line.split(',')
            data.append(line)
        for i in range(n):
            for j in range(n):
                pv[i,j,k]= float(data[i][j])

    po={}

    for k in range(K):
        fopen = open('./transition/slot20/'+str(k+starttimeslot)+'po','r')
        data=[]
        for line in fopen:
            line = line.strip('\n')
            line =line.split(',')
            data.append(line)
        for i in range(n):
            for j in range(n):
                po[i,j,k]= float(data[i][j])

    qv={}

    for k in range(K):
        fopen = open('./transition/slot20/'+str(k+starttimeslot)+'qv','r')
        data=[]
        for line in fopen:
            line = line.strip('\n')
            line =line.split(',')
            data.append(line)
        for i in range(n):
            for j in range(n):
                qv[i,j,k]= float(data[i][j])

    qo={}


    for k in range(K):
        fopen = open('./transition/slot20/'+str(k+starttimeslot)+'qo','r')
        data=[]
        for line in fopen:
            line = line.strip('\n')
            line =line.split(',')
            data.append(line)
        for i in range(n):
            for j in range(n):
                qo[i,j,k]= float(data[i][j])


# get estimated demand from files
    inputdemand =[]
    for i in range(n):
        one=[]
        for j in range(K):
            one.append(0)
        inputdemand.append(one)

    for k in range(K):

        fopen = open('./historydemand/slot20/prediction/'+str(k+starttimeslot),'r')
        loc =0
        for line in fopen:
            line =line.strip('\n')
            line = line.split(',')
            valuesum =0
            for value in line:
                valuesum = valuesum + float(value)*1.15
            inputdemand[loc][k]= valuesum
            loc = loc+1
    demand={}
    for i in range(n):
        for k in range(K):
            demand[i,k] = inputdemand[i][k]
#---------------------------------------------------------------------------------------------------------
    #get the distance matric
    distance =[]
    fopen = open('./datadir/distance','r')
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        one =[]
        for value in k:
            one.append(float(value))
        distance.append(one)
    W={}
    for i in range(n):
        for j in range(n):
            for k in range(K):
                W[i,j,k] = distance[i][j]
# ------------------------------------------------------------------
    # get the number of chargers in each charging station
    # obtain region and charging stations infomation
    # input:
    # output:
    #         n: number of regions
    #         p: number of charging poles in each region: List<>[]
    fopen = open('./datadir/chargerindex', 'r')
    p = {}  # number of charging poles in each region
    n = 0  # number of regions
    for k in fopen:
        k = k.strip().split(',')
        p[n] = int(float(k[-1]) / 5)
        n += 1

    if dis:
        for i in range(n):
            if i in disruption[0] and disruption[1]<starttimeslot<=disruption[2]:
                p[i] = 0


#------------------------------------------------------------------
    reachable =[]
    fopen = open('./datadir/reachable','r')
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        one =[]
        for value in k:
            one.append(float(value))
        reachable.append(one)
    c={}
    for i in range(n):
        for j in range(n):
            for k in range(K):
                c[i,j,k] = 1-reachable[i][j]
#------------------------------------------------------------------
#   the predicted solar power in each charging station

    # solarradiation = []
    # for i in range(37):
    #     one =[]
    #     for j in range(timehorizon):
    #         one.append(0.0)
    #     solarradiation.append(one)
    #
    # for slot in range(timehorizon):
    #
    #     # fopen = open('realsolardata/2019-07-31/' + str(starttimeslot + slot), 'r')
    #     # fopen = open('/home/yuan/Dropbox/CPS/transportation solar uncertainty/motivationfigure/newdata/prediction_solar/'
    #     #              +str(day)+'/' + str(starttimeslot + slot), 'r')
    #     fopen = open('realsolardata/' + str(day) + '/' + str(starttimeslot + slot), 'r')
    #     one =[]
    #     for k in fopen:
    #         k = k.strip('\n')
    #         one.append(float(k))
    #     for region in range(37):
    #         solarradiation[region][slot] = one[region]
    #
    #
    #
    #
    # solar_generation = []
    # for slot in range(timehorizon):
    #
    #     one = []
    #     for region in range(len(solarsize)):
    #         size = solarsize[region]
    #         unitvalue = solarradiation[region][slot]
    #         energy = (unitvalue*predictionerror/7.5) * size*0.9
    #         one.append(energy)
    #     solar_generation.append(one)
    #
    # utilitymax = 0
#-------------------------------------------------------------------
    try:

        # Create a new model
        m = Model("CPS")

        # Create variables
        X={}
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    for k in range(K):
                        X[i,j,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="X[%s,%s,%s,%s]"%(i,j,l,k))

        V={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    V[i,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="V[%s,%s,%s]"%(i,l,k))



        O={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    O[i,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="O[%s,%s,%s]"%(i,l,k))

        for i in range(n):
            for l in range(L):

                m.addConstr(V[i,l,0]==vacant[i,l])
                m.addConstr(O[i,l,0]==occupied[i,l])

        S={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    S[i,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="S[%s,%s,%s]"%(i,l,k))

        Y={}
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    for k in range(K):
                        Y[i,j,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="Y[%s,%s,%s,%s]"%(i,j,l,k))


        # reverseflow = {}
        # for i in range(n):
        #     for k in range(K):
        #         reverseflow[i,k] = m.addVar(vtype=GRB.CONTINUOUS,name="reverseflow[%s,%s]"%(i,k))
        #
        # chargingflow = {}
        # for i in range(n):
        #     for k in range(K):
        #         chargingflow[i,k] = m.addVar(lb=-1000.0,vtype=GRB.CONTINUOUS,name="chargingflow[%s,%s]"%(i,k))
        #
        # dischargingflow = {}
        # for i in range(n):
        #     for k in range(K):
        #         dischargingflow[i,k] = m.addVar(lb=-1000.0,vtype=GRB.CONTINUOUS,name="dischargingflow[%s,%s]"%(i,k))
        #
        #
        # stored = {}
        # for i in range(n):
        #     for k in range(K):
        #         stored[i,k] = m.addVar(vtype=GRB.CONTINUOUS,name="stored[%s,%s]"%(i,k))
        #
        # for i in range(n):
        #     m.addConstr(stored[i,0] == storedenergy[i] )


        U={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    U[i,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="U[%s,%s,%s]"%(i,l,k))


        for i in range(n): #region i total served
            for l in range(L):
                for k in range(K):
                    m.addConstr(S[i,l,k] == sum(Y[j,i,l,k] for j in range(n)))
                    # m.addConstr(S[i, l, k] +0.5 >= sum(Y[j, i, l, k] for j in range(n)))

        for i in range(n): # equation 4
            for l in range(L-L1):
                for k in range(K-1):
                    m.addConstr(V[i,l,k+1]==(sum((pv[j,i,k]*S[j,l+L1,k]) for j in range(n)) + sum((qv[j,i,k]*O[j,l+L1,k]) for j in range(n)) + U[i,l,k]))


        for i in range(n): #
            for l in range(L-L1):
                for k in range(K-1):
                    m.addConstr(O[i,l,k+1] == (sum((po[j,i,k]*S[j,l+L1,k]) for j in range(n)) + sum((qo[j,i,k]*O[j,l+L1,k]) for j in range(n))))


#---------------describe the charging process in the charging station-------------------------------
        H={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    H[i,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="H[%s,%s,%s]"%(i,l,k))
                    m.addConstr(H[i,l,k]<= sum(X[j,i,l,k] for j in range(n)))

        for i in range(n):
            for k in range(K):
                # m.addConstr(sum(H[i,l,k] for l in range(L)) <= p[i])
                m.addConstr(sum(sum(X[j,i,l,k] for j in range(n)) for l in range(L))   <= p[i])

        for i in range(n):
            for l in range(L2,L):
                for k in range(K):
                    m.addConstr(U[i,l,k]== (H[i,l-L2,k] + sum(X[j,i,l,k] for j in range(n)) - H[i,l,k] ))
#---------------------------------------------------------------------------------------------------

        for i in range(n): # X和Y从vacant里面出
            for l in range(L):
                for k in range(K):
                    m.addConstr(V[i,l,k]== sum((X[i,j,l,k]+Y[i,j,l,k]) for j in range(n)))


        for i in range(n): #低于L1 的车全部去充电 不允许serve
            for k in range(K):
                for l in range(L1):
                    m.addConstr(sum(X[i,j,l,k] for j in range(n))==V[i,l,k])
                    m.addConstr(sum(Y[i,j,l,k] for j in range(n)) == 0)

        for i in range(n): # ij之间的距离不能不reachable
            for j in range(n):
                for l in range(L):
                    for k in range(K):
                        m.addConstr((X[i,j,l,k]+Y[i,j,l,k])*c[i,j,k]==0)

        kk={}
        for i in range(n): #卡着upper bound serve，
            for k in range(K):
                kk[i,k]=m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="kk[%s,%s]"%(i,k))
                m.addConstr(kk[i,k]<= demand[i,k])
                m.addConstr(kk[i,k]<= sum((S[i,l,k]) for l in range(L)))

        # sdratio_diff = {}
        # for i in range(n):
        #     for k in range(K):
        #         sdratio_diff[i,k]=m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="sdratio_diff[%s,%s]"%(i,k))
        #         m.addConstr(kk[i,k]>= sum((S[i,l,k]) for l in range(L))/demand[i,k] - alpha[i][k])
        #         m.addConstr(kk[i,k]>= - sum((S[i,l,k]) for l in range(L))/demand[i,k] + alpha[i][k])
        #
        # usedsolarpower = {}
        # for region in range(n):
        #     for slot in range(timehorizon):
        #         usedsolarpower[region, slot] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS,
        #                                                 name="usedsolarpower[%s,%s]" % (region, slot))
        #
        # for region in range(n):
        #     for slot in range(timehorizon):
        #         m.addConstr(usedsolarpower[region, slot] <= solar_generation[slot][region])
        #         m.addConstr(usedsolarpower[region, slot] <= 30.0 * sum(
        #             sum(X[j, region, l, slot] for j in range(n)) for l in range(L)))

        obj1 = sum( sum( (kk[i,k]) for i in range(n)) for k in range(K))
        obj2 = sum(sum(sum((sum((X[i,j,l,k]+Y[i,j,l,k]) for l in range(L))*W[i,j,k]) for i in range(n)) for j in range(n)) for k in range(K))

        m.setObjective(obj1 - beta*obj2 ,GRB.MAXIMIZE) # -0.001 is the negative weight between the two objectives. You can set up it as different values.
        # In our evaluation, we evaluate the performances under the different weights.
        m.setParam(GRB.Param.TimeLimit, 300)
        m.Params.BarHomogeneous = 1

        m.optimize()

        out_charging = {}
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
                if dis:
                    if x4 == 0:
                        out_charging[x1,x2,x3] = v.x
                # if x4 == 0:
                else:
                    out_charging[x1, x2, x3, x4] = v.x
                # print ('%s, %g' %(v.VarName,v.x))
        out1_serve = {}
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
                x3 = int(float(line[2]))
                x4 = int(float(line[3]))
                if dis:
                    if x4 == 0:
                        out1_serve[x1, x2, x3] = v.x
                else:
                    out1_serve[x1, x2, x3, x4] = v.x

        return out_charging, out1_serve

    except GurobiError as e:
        print('Error code ' + str(e.message) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error')

    # try:
    #
    #     # Create a new model
    #     m = Model("CPS")
    #
    #     # Create variables
    #     X = {}
    #     for i in range(n):
    #         for j in range(n):
    #             for l in range(L):
    #                 for k in range(K):
    #                     X[i, j, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="X[%s,%s,%s,%s]" % (i, j, l, k))
    #
    #     V = {}
    #     for i in range(n):
    #         for l in range(L):
    #             for k in range(K):
    #                 V[i, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="V[%s,%s,%s]" % (i, l, k))
    #
    #     O = {}
    #     for i in range(n):
    #         for l in range(L):
    #             for k in range(K):
    #                 O[i, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="O[%s,%s,%s]" % (i, l, k))
    #
    #     for i in range(n):
    #         for l in range(L):
    #             m.addConstr(V[i, l, 0] == vacant[i, l])
    #             m.addConstr(O[i, l, 0] == occupied[i, l])
    #
    #     S = {}
    #     for i in range(n):
    #         for l in range(L):
    #             for k in range(K):
    #                 S[i, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="S[%s,%s,%s]" % (i, l, k))
    #
    #     Y = {}
    #     for i in range(n):
    #         for j in range(n):
    #             for l in range(L):
    #                 for k in range(K):
    #                     Y[i, j, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="Y[%s,%s,%s,%s]" % (i, j, l, k))
    #
    #     reverseflow = {}
    #     for i in range(n):
    #         for k in range(K):
    #             reverseflow[i, k] = m.addVar(vtype=GRB.CONTINUOUS, name="reverseflow[%s,%s]" % (i, k))
    #
    #     chargingflow = {}
    #     for i in range(n):
    #         for k in range(K):
    #             chargingflow[i, k] = m.addVar(lb=-1000.0, vtype=GRB.CONTINUOUS, name="chargingflow[%s,%s]" % (i, k))
    #
    #     dischargingflow = {}
    #     for i in range(n):
    #         for k in range(K):
    #             dischargingflow[i, k] = m.addVar(lb=-1000.0, vtype=GRB.CONTINUOUS,
    #                                              name="dischargingflow[%s,%s]" % (i, k))
    #
    #     stored = {}
    #     for i in range(n):
    #         for k in range(K):
    #             stored[i, k] = m.addVar(vtype=GRB.CONTINUOUS, name="stored[%s,%s]" % (i, k))
    #
    #     for i in range(n):
    #         m.addConstr(stored[i, 0] == storedenergy[i])
    #
    #     U = {}
    #     for i in range(n):
    #         for l in range(L):
    #             for k in range(K):
    #                 U[i, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="U[%s,%s,%s]" % (i, l, k))
    #
    #     for i in range(n):
    #         for l in range(L):
    #             for k in range(K):
    #                 m.addConstr(S[i, l, k] == sum(Y[j, i, l, k] for j in range(n)))
    #                 # m.addConstr(S[i, l, k] +0.5 >= sum(Y[j, i, l, k] for j in range(n)))
    #
    #     for i in range(n):
    #         for l in range(L - L1):
    #             for k in range(K - 1):
    #                 m.addConstr(V[i, l, k + 1] == (sum((pv[j, i, k] * S[j, l + L1, k]) for j in range(n)) + sum(
    #                     (qv[j, i, k] * O[j, l + L1, k]) for j in range(n)) + U[i, l, k]))
    #
    #     for i in range(n):
    #         for l in range(L - L1):
    #             for k in range(K - 1):
    #                 m.addConstr(O[i, l, k + 1] == (sum((po[j, i, k] * S[j, l + L1, k]) for j in range(n)) + sum(
    #                     (qo[j, i, k] * O[j, l + L1, k]) for j in range(n))))
    #
    #     # ---------------describe the charging process in the charging station-------------------------------
    #     H = {}
    #     for i in range(n):
    #         for l in range(L):
    #             for k in range(K):
    #                 H[i, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="H[%s,%s,%s]" % (i, l, k))
    #                 m.addConstr(H[i, l, k] <= sum(X[j, i, l, k] for j in range(n)))
    #
    #     for i in range(n):
    #         for k in range(K):
    #             # m.addConstr(sum(H[i,l,k] for l in range(L)) <= p[i])
    #             m.addConstr(sum(sum(X[j, i, l, k] for j in range(n)) for l in range(L)) <= p[i])
    #
    #     for i in range(n):
    #         for l in range(L2, L):
    #             for k in range(K):
    #                 m.addConstr(U[i, l, k] == (H[i, l - L2, k] + sum(X[j, i, l, k] for j in range(n)) - H[i, l, k]))
    #     # ---------------------------------------------------------------------------------------------------
    #
    #     for i in range(n):
    #         for l in range(L):
    #             for k in range(K):
    #                 m.addConstr(V[i, l, k] == sum((X[i, j, l, k] + Y[i, j, l, k]) for j in range(n)))
    #
    #     for i in range(n):
    #         for k in range(K):
    #             for l in range(L1):
    #                 m.addConstr(sum(X[i, j, l, k] for j in range(n)) == V[i, l, k])
    #                 m.addConstr(sum(Y[i, j, l, k] for j in range(n)) == 0)
    #
    #     # for i in range(n):
    #     #     for j in range(n):
    #     #         for l in range(L):
    #     #             for k in range(K):
    #     #                 m.addConstr((X[i,j,l,k]+Y[i,j,l,k])*c[i,j,k]==0)
    #
    #     kk = {}
    #
    #     for i in range(n):
    #         for k in range(K):
    #             kk[i, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="kk[%s,%s]" % (i, k))
    #             m.addConstr(kk[i, k] <= demand[i, k])
    #             m.addConstr(kk[i, k] <= sum((S[i, l, k]) for l in range(L)))
    #
    #     usedsolarpower = {}
    #     for region in range(n):
    #         for slot in range(timehorizon):
    #             usedsolarpower[region, slot] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS,
    #                                                     name="usedsolarpower[%s,%s]" % (region, slot))
    #
    #     for region in range(n):
    #         for slot in range(timehorizon):
    #             m.addConstr(usedsolarpower[region, slot] <= solar_generation[slot][region])
    #             m.addConstr(usedsolarpower[region, slot] <= 30.0 * sum(
    #                 sum(X[j, region, l, slot] for j in range(n)) for l in range(L)))
    #
    #     obj1 = sum(sum((kk[i, k]) for i in range(n)) for k in range(K))
    #
    #     m.addConstr(obj1>= utilitymax*0.9)
    #
    #     obj2 = sum(sum(
    #         sum((sum((X[i, j, l, k] + Y[i, j, l, k]) for l in range(L)) * W[i, j, k]) for i in range(n)) for j in
    #         range(n)) for k in range(K))
    #     obj3 = sum(sum(usedsolarpower[region, slot] for region in range(n)) for slot in range(timehorizon))
    #     # m.addConstr(obj3<=0.9*sum(sum(solar_generation[slot][region] for slot in range(timehorizon)) for region in range(n)))
    #
    #     m.setObjective(obj3, GRB.MAXIMIZE)
    #
    #     m.setParam(GRB.Param.TimeLimit, 300)
    #     m.Params.BarHomogeneous = 1
    #
    #     m.optimize()
    #     utilitymax = m.objValue
    #
    #     out = {}
    #     for v in m.getVars():
    #         if 'X' in v.VarName:
    #             line = v.VarName
    #             line = line.split('[')
    #             line = line[1]
    #             line = line.split(']')
    #             line = line[0]
    #             line = line.split(',')
    #             x1 = int(float(line[0]))
    #             x2 = int(float(line[1]))
    #             x3 = int(float(line[2]))
    #             x4 = int(float(line[3]))
    #             if x4 == 0:
    #                 out[x1, x2, x3] = v.x
    #             # print ('%s, %g' %(v.VarName,v.x))
    #     out1 = {}
    #     for v in m.getVars():
    #         if 'Y' in v.VarName:
    #             line = v.VarName
    #             line = line.split('[')
    #             line = line[1]
    #             line = line.split(']')
    #             line = line[0]
    #             line = line.split(',')
    #             x1 = int(float(line[0]))
    #             x2 = int(float(line[1]))
    #             x3 = int(float(line[2]))
    #             x4 = int(float(line[3]))
    #             if x4 == 0:
    #                 out1[x1, x2, x3] = v.x
    #     supply1 = {}
    #     for v in m.getVars():
    #         if 'S' in v.VarName:
    #             line = v.VarName
    #             line = line.split('[')
    #             line = line[1]
    #             line = line.split(']')
    #             line = line[0]
    #             line = line.split(',')
    #             x1 = int(float(line[0]))
    #             x2 = int(float(line[1]))
    #             x3 = int(float(line[2]))
    #             # x4 = int(float(line[3]))
    #             if x3 == 0:
    #                 supply1[x1, x2] = v.x
    #
    #     serveddemand = {}
    #     for v in m.getVars():
    #         if 'kk' in v.VarName:
    #             line = v.VarName
    #             line = line.split('[')
    #             line = line[1]
    #             line = line.split(']')
    #             line = line[0]
    #             line = line.split(',')
    #             x1 = int(float(line[0]))
    #             x2 = int(float(line[1]))
    #             serveddemand[x1, x2] = v.x
    #
    #     return out, out1, serveddemand
    #
    #
    # except GurobiError as e:
    #     print('Error code ' + str(e.errno) + ": " + str(e))
    #
    # except AttributeError:
    #     print('Encountered an attribute error')

    return


