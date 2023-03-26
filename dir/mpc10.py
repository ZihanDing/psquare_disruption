from gurobipy import *
import numpy as np
import os
from os import  path
import math
def mpc_iteration(starttimeslot,timehorizon,vacant,occupied,beta,chargingresource,futuresupply):
    n=0 # number of regions
    fopen =  open('./datadir/chargerindex','r')
    for k in fopen:
        n=n+1
#--------------------------------------------------------------
    L=30 # number of energy levels
    K=timehorizon # number of time horizon
    L1=1
    L2=3


    pv={}

    for k in range(K):
        fopen = open('./transition/slot10/'+str((k+starttimeslot)%144)+'pv','r')
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
        fopen = open('./transition/slot10/'+str((k+starttimeslot)%144)+'po','r')
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
        fopen = open('./transition/slot10/'+str((k+starttimeslot)%144)+'qv','r')
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
        fopen = open('./transition/slot10/'+str((k+starttimeslot)%144)+'qo','r')
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

        fopen = open('./historydemand/slot10/prediction/'+str((k+starttimeslot)%144),'r')
        loc =0
        for line in fopen:
            line =line.strip('\n')
            line = line.split(',')
            valuesum =0
            for value in line:
                valuesum = valuesum + (float(value))
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
        if float(k)>40:
            p[i]= int(float(k)/5)
            # p[i] = 40
        else:
            p[i] = int(float(k)/5)
    pp={}
    for i in range(n):
        for j in range(K):
            pp[i,j] = p[i]-chargingresource[i][j]
            if pp[i,j]<0:
                print 'EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE'
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
                        for q in range(1,1+((L-l-1)/L2)):
                            if l<0:
                                X[i,j,l,k,q] = m.addVar(lb=0.0,vtype=GRB.INTEGER,name="X[%s,%s,%s,%s,%s]"%(i,j,l,k,q))
                            else:
                                X[i,j,l,k,q] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="X[%s,%s,%s,%s,%s]"%(i,j,l,k,q))

                            if  q>6:
                                m.addConstr(X[i,j,l,k,q]==0)
                            else:
                                m.addConstr(X[i,j,l,k,q]<=800)


        V={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    V[i,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="V[%s,%s,%s]"%(i,l,k))
                    m.addConstr(V[i,l,k]<=800)



        O={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    O[i,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="O[%s,%s,%s]"%(i,l,k))
                    m.addConstr(O[i,l,k]<=800)

        for i in range(n):
            for l in range(L):
                m.addConstr(V[i,l,0]==vacant[i,l])
                m.addConstr(O[i,l,0]==occupied[i,l])



        S={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    S[i,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="S[%s,%s,%s]"%(i,l,k))
                    m.addConstr(S[i,l,k]<=800)

        D={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    for q in range(1,1+((L-l-1)/L2)):
                        D[i,l,k,q] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="D[%s,%s,%s,%s]"%(i,l,k,q))
                        m.addConstr(D[i,l,k,q]<=800)


        Du={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    for q in range(1,1+((L-l-1)/L2)):
                        Du[i,l,k,q] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="Du[%s,%s,%s,%s]"%(i,l,k,q))
                        m.addConstr(Du[i,l,k,q]<=800)
        #
        Db={}
        for i in range(n):
            for k in range(K):
                for q in range(1,1+((L-1)/L2)):
                    Db[i,k,q] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name ="Db[%s,%s,%s]"%(i,k,q))


        Df={}
        for i in range(n):
            for k in range(K):
                for q in range(1,1+((L-1)/L2)):
                    for kp in range(k+q,K+1):
                        Df[i,k,q,kp]= m.addVar(lb=0.0,vtype=GRB.CONTINUOUS, name="Df[%s,%s,%s,%s]"%(i,k,q,kp))

        Y={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    for q in range(1,1+((L-l-1)/L2)):
                        for kp in range(k+q,K+1):
                            Y[i,l,k,q,kp]= m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name= "Y[%s,%s,%s,%s,%s]"%(i,l,k,q,kp))


        U={}
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    U[i,l,k] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="U[%s,%s,%s]"%(i,l,k))


        for i in range(n):
            for l in range(L):
                for k in range(K):
                    m.addConstr(S[i,l,k]==(V[i,l,k]-sum(sum(X[i,j,l,k,q] for j in range(n)) for q in range(1,1+((L-l-1)/L2)))))

        for i in range(n):
            for l in range(L):
                for k in range(K):
                    m.addConstr(sum(X[i,j,l,k,q] for j in range(n) for q in range(1,1+((L-l-1)/L2))) <= V[i,l,k] )

        for i in range(n):
            for l in range(L):
                for k in range(K-1):
                    if l<=L-L1-1:
                        m.addConstr( V[i,l,k+1]==  (    sum((pv[j,i,k]*S[j,l+L1,k]) for j in range(n)) + sum((qv[j,i,k]*O[j,l+L1,k]) for j in range(n)) +U[i,l,k+1]
                                                        + futuresupply[i,l,k+1] )  )
                    else:
                        m.addConstr(V[i,l,k+1]==U[i,l,k+1])
                    # m.addConstr(V[i,l,k+1]==(sum((pv[j,i,k]*S[j,l+L1,k]) for j in range(n)) + sum((qv[j,i,k]*O[j,l+L1,k]) for j in range(n)) + U[i,l,k+1]))


        for i in range(n):
            for l in range(L-L1):
                for k in range(K-1):
                    m.addConstr( O[i,l,k+1]== (sum((po[j,i,k]*S[j,l+L1,k]) for j in range(n)) + sum( (qo[j,i,k]*O[j,l+L1,k]) for j in range(n))) )

        # for i in range(n):
        #     for j in range(n):
        #         for l in range(L):
        #             for k in range(K):
        #                 for q in range(1,(L-l-1)/L2):
        #                     m.addConstr(X[i,j,l,k,q]*reachable[i][j]== 0)

        for i in range(n):
            for l in range(L):
                for k in range(K):
                    for q in range(1,(L-l-1)/L2):
                        m.addConstr(D[i,l,k,q]== sum(X[j,i,l,k,q] for j in range(n)))

        for i in range(n):
            for l in range(L):
                for k in range(K):
                    for q in range(1,(L-l-1)/L2):
                        m.addConstr(    Du[i,l,k,q]==(D[i,l,k,q]-sum(Y[i,l,k,q,kp] for kp in range(k+q,K+1)) ) )
                        m.addConstr(0<= Du[i,l,k,q])
        #
        for i in range(n):
            for k in range(K):
                for q in range(1,(L-1)/L2):
                    m.addConstr(Db[i,k,q]==(  sum( sum(  sum(D[i,l1,k1,q1] for q1 in range(1,1+(L-1-l1)/L2)) for l1 in range(K)) for k1 in range(k) ) +
                                              sum( sum(D[i,l1,k,q1] for q1 in range(1,1+min(q-1,(L-1-l1)/L2))  )for l1 in range(L) )   ))

        for i in range(n):
            for k in range(K):
                for q in range(1,(L-1)/L2):
                    for kp in range(k+q,K+1):
                        m.addConstr(Df[i,k,q,kp]== ( sum( sum( sum( sum(Y[i,l1,k1,q1,kp1] for kp1 in range(k1+q1,kp-q+1) )
                                                                    for q1 in range(1,min((L-l1-1)/L2,kp-q-k1)+1 ) ) for k1 in range(k) )
                                                          for l1 in range(L)) +
                                                     sum( sum( sum( Y[i,l1,k,q1,kp1] for kp1 in range(k+q1,kp-q+1))
                                                               for q1 in range(1,min(q-1,kp-q-k,(L-l1-1)/L2)+1 ) ) for l1 in range(L) )    ) )


        for i in range(n):
            for k in range(K):
                for q in range(1,((L-1)/L2)+1):
                    for kp in range(k+q,K+1):
                        m.addConstr(Db[i,k,q]-Df[i,k,q,kp]+sum(Y[i,l,k,q,kp] for l in range((L-q*L2))) <= pp[i,k])


        for i in range(n):
            for lp in range(L):
                for kp in range(K):
                    m.addConstr( U[i,lp,kp]== sum(sum( Y[i,lp-q*L2,k1,q,kp] for k1 in range(kp-q+1)) for q in range(1, 1+(lp-1)/L2)))








        for i in range(n):
            for l in range(L):
                for k in range(K):
                    if k==0:
                        m.addConstr(S[i,l,k]<=V[i,l,k])
                    else:
                        if L-L1-1<=l:
                            m.addConstr(S[i,l,k]<=V[i,l,k])
                        else:
                            m.addConstr(S[i,l,k]<=V[i,l,k])
                    # m.addConstr(S[i,l,k]<=100)



        for i in range(n):
            for k in range(K):
                for l in range(L1+1):
                    m.addConstr(S[i,l,k]<=0.999)

        kk={}
        for i in range(n):
            for k in range(K):
                kk[i,k]=m.addVar(lb=0.0,vtype=GRB.CONTINUOUS,name="kk[%s,%s]"%(i,k))
                m.addConstr(0<=kk[i,k])
                m.addConstr(  (demand[i,k]-sum((S[i,l,k]) for l in range(L)))<=kk[i,k]  )
                m.addConstr((-demand[i,k]+sum((S[i,l,k]) for l in range(L)))<=kk[i,k])
        obj1 = sum(kk[i,k] for i in range(n) for k in range(K))
        # obj1 = sum(  sum(    ((demand[i,k]-sum((S[i,l,k]) for l in range(L))))  for i in range(n)) for k in range(K))
        obj2 = sum(sum(sum((sum(sum(X[i,j,l,k,q] for q in range(1,1+(L-1-l)/L2)) for l in range(L))*W[i,j,k]) for i in range(n)) for j in range(n)) for k in range(K))

        obj3 = sum(Y[i,l,k,q,kp]*(kp-k) for i in range(n)  for l in range(L) for k in range(K) for q in range(1,1+((L-1-l)/L2)) for kp in range(k+q,K+1))

        obj4 = sum(Du[i,l,k,q] * (K+2) for i in range(n) for l in range(L) for k in range(K) for q in range(1,1+((L-l-1)/L2)))

        obj5 = obj3 + obj4
        obj = obj1 + (60*obj2/40.0+1.5*obj5)*beta
        # obj= obj1 + beta*(60*obj2/40.0)
        # obj=obj1
        m.setObjective(obj,GRB.MINIMIZE)

        m.setParam(GRB.Param.TimeLimit, 300)
        # m.Params.BarHomogeneous = 1


        m.optimize()
        out={}
        for v in m.getVars():
            if 'X' in v.VarName:
                # print v.VarName
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
                x5=  int(float(line[4]))
                if x4==0:
                    out[x1,x2,x3,x5] =v.x
                #print ('%s, %g' %(v.VarName,v.x))
        out1={}
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
                if x2==0:
                    out1[x1] =v.x
        supply1={}
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
                if x3==0:
                    supply1[x1,x2] =v.x
                # if x3==0 and x2<L1:
                #     print v.VarName,v.x
        csupp=0
        for i in range(n):
            csupp +=  (sum(supply1[i,l] for l in range(L))- out1[i])
        print csupp, (sum(demand[i,0] for i in range(n)))

        out1={}
        for i in range(n):
            out1[i]=0
        return out,out1


    except GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error')
