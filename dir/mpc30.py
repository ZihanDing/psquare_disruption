from gurobipy import *
import numpy as np
import os
from os import  path

def mpc_iteration(starttimeslot,timehorizon,vacant,occupied,inputH,charginglength,beta):
    n=0 # number of regions
    fopen =  open('./datadir/chargerindex','r')
    for k in fopen:
        n=n+1
#--------------------------------------------------------------
    L=10 # number of energy levels
    K=timehorizon # number of time horizon
    L1=1
    L2=3


    pv={}

    for k in range(K):
        fopen = open('./transition/slot30/'+str(k+starttimeslot)+'pv','r')
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
        fopen = open('./transition/slot30/'+str(k+starttimeslot)+'po','r')
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
        fopen = open('./transition/slot30/'+str(k+starttimeslot)+'qv','r')
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
        fopen = open('./transition/slot30/'+str(k+starttimeslot)+'qo','r')
        data=[]
        for line in fopen:
            line = line.strip('\n')
            line =line.split(',')
            data.append(line)
        for i in range(n):
            for j in range(n):
                qo[i,j,k]= float(data[i][j])
    T={}
    for i in range(n):
        for l in range(L):
            for k in range(K):
                T[i,l,k] = charginglength[i,l,k]


    H_initial={}
    for i in range(n):
        for t in range(L/L2):
            for l in range(L):
                H_initial[i,t,l]= inputH[i,t,l]




# get estimated demand from files
    inputdemand =[]
    for i in range(n):
        one=[]
        for j in range(K):
            one.append(0)
        inputdemand.append(one)

    for k in range(K):

        fopen = open('./historydemand/slot30/prediction/'+str(k+starttimeslot),'r')
        loc =0
        for line in fopen:
            line =line.strip('\n')
            line = line.split(',')
            valuesum =0
            for value in line:
                valuesum = valuesum + float(value)
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

# get the number of chargers in each charging station
    p={}
    fopen =  open('./datadir/chargerindex','r')
    chargderindex=[]
    for k in fopen:
        chargderindex.append(k)
    for i in range(len(chargderindex)):
        k=chargderindex[i]
        k=k.split(',')
        k=k[2]
        k=k.strip('\n')
        #p[i] = 20
        if float(k)>30:
            p[i]= int(float(k)/8)
            # p[i] = 40
        else:
            p[i] = int(float(k)/5)+1
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

        U={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    U[i,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="U[%s,%s,%s]"%(i,l,k))
        H={}
        for i in range(n):
            for t in range(L/L2):
                for l in range(L):
                    for k in range(K+1):
                        H[i,t,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="H[%s,%s,%s,%s]"%(i,t,l,k))

        for i in range(n):
            for l in range(L):
                for k in range(K):
                    m.addConstr(S[i,l,k]==(V[i,l,k]-sum(X[i,j,l,k] for j in range(n))))

        for i in range(n):
            for l in range(L-L1):
                for k in range(K-1):
                    m.addConstr(V[i,l,k+1]==(sum((pv[j,i,k]*S[j,l+L1,k]) for j in range(n)) + sum((qv[j,i,k]*O[j,l+L1,k]) for j in range(n)) + U[i,l,k+1]))


        for i in range(n):
            for l in range(L-L1):
                for k in range(K-1):
                    m.addConstr( O[i,l,k+1]== (sum((po[j,i,k]*S[j,l+L1,k]) for j in range(n)) + sum( (qo[j,i,k]*O[j,l+L1,k]) for j in range(n))) )

        for i in range(n):
            for l in range(L):
                for k in range(K):
                    if l <L2:
                        m.addConstr(U[i,l,k]==0)
                    else:
                        m.addConstr(U[i,l,k] == H[i,1,l-L2,k])

        for i in range(n):
            for t in range(L/L2):
                for l in range(L):
                    for k in range(K+1):
                        if k==0:
                            m.addConstr(H[i,t,l,k]==H_initial[i,t,l])
                        else:
                            if t==(L/L2-1):
                                m.addConstr(H[i,t,l,k]==0)
                            else:
                                if l<L2:
                                    if t == T[i,l,k-1] :
                                        m.addConstr(H[i,t,l,k]==(sum(X[j,i,l,k-1] for j in range(n))))
                                        #m.addConstr(H[i,t,l,k]==(sum(X[j,i,l,k-1]) for j in range(n)))
                                    else:
                                        m.addConstr(H[i,t,l,k]==0)
                                else:
                                    if t == T[i,l,k-1] :
                                        m.addConstr(H[i,t,l,k]==(H[i,t+1,l-L2,k-1]+(sum(X[j,i,l,k-1] for j in range(n)))))
                                    else:
                                        m.addConstr(H[i,t,l,k]==H[i,t+1,l-L2,k-1])

        # for i in range(n):
        #     for l in range(L):
        #         for k in range(K):
        #             if T[i,l,k]==0:
        #                 for j in range(n):
        #                     m.addConstr(X[j,i,l,k]==0)
        gap={}
        for i in range(n):
            for k in range(K):
                gap[i,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="gap[%s,%s]"%(i,k))
        for i in range(n):
            for k in range(K):
                m.addConstr(sum(S[i,l,k] for l in range(L))-gap[i,k]<= 1.0*demand[i,k])


        for i in range(n):
            for k in range(K+1):
                m.addConstr( sum(sum(H[i,t,l,k] for l in range(L)) for t in range(L/L2))<=p[i])

        # for i in range(n):
        #     for j in range(n):
        #         for l in range(L):
        #             for k in range(K):
        #                 m.addConstr((X[i,j,l,k]*c[i,j,k])==0)
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    m.addConstr(0<=S[i,l,k])
        # for i in range(n):
        #     for l in range(2):
        #         for k in range(K):
        #             m.addConstr(S[i,l,k]==0)
        for i in range(n):
            for k in range(K):
                # if starttimeslot+k==24  or starttimeslot+k ==50 or starttimeslot+k ==56:
                #     for l in range(3):
                #         m.addConstr(S[i,l,k]==0)
                # elif  starttimeslot+k ==25 or starttimeslot+k ==26 :
                #     for l in range(4):
                #         m.addConstr(S[i,l,k]==0)
                # else:
                for l in range(2):
                    m.addConstr(S[i,l,k]==0)
        obj1 = sum(sum(((demand[i,k]-sum(S[i,l,k] for l in range(L)))*(1+0.000*k)) for i in range(n)) for k in range(K))
        obj2 = sum(sum(sum((sum(X[i,j,l,k] for l in range(L))*W[i,j,k]) for i in range(n)) for j in range(n)) for k in range(K))
        obj3 = sum(sum(gap[i,k] for i in range(n)) for k in range(K))
        obj = obj1 + obj2*beta + obj3
        m.setObjective(obj,GRB.MINIMIZE)

        m.setParam(GRB.Param.TimeLimit, 150)
        m.Params.BarHomogeneous = 1


        m.optimize()
        out={}
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
                if x4==0:
                    out[x1,x2,x3] =v.x
                #print ('%s, %g' %(v.VarName,v.x))

        return out


    except GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error')
