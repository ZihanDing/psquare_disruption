#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：newevaluation_dis 
@File    ：mpc_dis.py
@IDE     ：PyCharm 
@Author  ：Zihan Ding
@Date    ：3/26/23 4:18 PM
@Description: This file is for our CDC paper Fairness-aware charging problem. \
The file contains the optimization part of the mpc_iteration.
'''
import data_process as dp
from gurobipy import *


def mpc_iteration(starttimeslot,beta1,beta2, disruption,reachable,vacant,occupied):
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


    # {0,1} represent if an e-taxi can reach region j from i within the time interval k.
    w = {}
    for i in range(n):
        for j in range(n):
            for k in range(K):
                w[i, j, k] = 1 - reachable[i][j]
    try:

        # Create a new model
        m = Model("CPS")

        C = {}
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    for k in range(K):
                        for q in range(1, 1 + ((L - l - 1) / L2)):
                            if l < 0:
                                C[i, j, l, k, q] = m.addVar(lb=0.0, vtype=GRB.INTEGER,
                                                            name="C[%s,%s,%s,%s,%s]" % (i, j, l, k, q))
                            else:
                                C[i, j, l, k, q] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS,
                                                            name="C[%s,%s,%s,%s,%s]" % (i, j, l, k, q))
        S = {} #
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    for k in range(K):

                        if l < 0:
                            S[i, j, l, k] = m.addVar(lb=0.0, vtype=GRB.INTEGER,
                                                        name="S[%s,%s,%s,%s]" % (i, j, l, k))
                        else:
                            S[i, j, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS,
                                                        name="S[%s,%s,%s,%s]" % (i, j, l, k))
        DE = {} # number of passengers requesting taxi service in region i during time interval k.
        for i in range(n):
            for j in range(n):
                for k in range(K):
                    DE[i,j,k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS,
                                         name = "DE[%s,%s,%s,%s]" % (i,j,k))

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

        St = {} # total number of available e-taxis at the l-th energy level with region i during time slok k
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    St[i, l, k] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="St[%s,%s,%s]" % (i, l, k))
                    m.addConstr(St[i, l, k] <= 800)
        D = {}
        for i in range(n): # The number of l-th energy level e-taxis dispatched to region i during time slot k with q time slots charging duration.
            for l in range(L):
                for k in range(K):
                    for q in range(1, 1 + ((L - l - 1) / L2)):
                        D[i, l, k, q] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="D[%s,%s,%s,%s]" % (i, l, k, q))
                        m.addConstr(D[i, l, k, q] <= 800)

        Du = {}  # For l-th level e-taxis dispatched to region i at time slot k for charging q time slots, the number of unfininsh charging vehicles by the end of optimization time horizon.
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    for q in range(1, 1 + ((L - l - 1) / L2)):
                        Du[i, l, k, q] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="Du[%s,%s,%s,%s]" % (i, l, k, q))
                        m.addConstr(Du[i, l, k, q] <= 800)
        #
        Db = {}  # The number of e-taxis with higher charging priority
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
        alpha = {}
        u = {}

        Jservice = sum(sum(min(
            sum(S[i, j, l, k] for j in range(n) for l in range(L)),
            sum(DE[i,j,k] for j in range(n))) for i in range(n)) for k in range(K))

        Jfairness = sum(sum(abs(sum(
            sum(S[i,j,l,k] for j in range(n)) for l in range(L)
        ) / sum(DE[i,j,k] for j in range(n) - alpha[i,k])
        ) for i in range(n)) for k in range(K))

        Jcost = sum(u[i,j] * sum((S[i,j,l,k] + sum(C[i,j,l,k,q] for q in range(L))) for l in range(L)) for i in range(n) for j in range(n))

        if disruption[1] < starttimeslot <= disruption[2]: # now with disruption, consider fairness
            obj = Jfairness + beta1*Jcost
            m.setObjective(obj, GRB.MINIMIZE)
        else:
            obj = Jservice + beta2*Jcost
            m.setObjective(obj, GRB.MAXIMIZE)

        m.setParam(GRB.Param.TimeLimit, 150)
        # m.Params.BarHomogeneous = 1

        m.optimize()

        print str(m.objVal) + "----------------"


        S_out = {}
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
                x4 = int(float(line[3]))
                x5 = int(float(line[4]))
                if x4 == 0:
                    S_out[x1, x2, x3, x5] = v.x

        C_out = {}
        for v in m.getVars():
            if 'C' in v.VarName:
                C_out = {}
                # TODO: How to get correct C value
                # line = v.VarName
                # line = line.split('[')
                # line = line[1]
                # line = line.split(']')
                # line = line[0]
                # line = line.split(',')
                # x1 = int(float(line[0]))
                # x2 = int(float(line[1]))
                # x3 = int(float(line[2]))
                # x4 = int(float(line[3]))
                # x5 = int(float(line[4]))
                # if x4 == 0:
                #     C_out[x1, x2, x3, x5] = v.x
        return S_out,C_out
    except GurobiError as e:
        print 'Error code' + str(e.message) + ": " + str(e)

    except AttributeError:
        print 'Encountered an attribute error'