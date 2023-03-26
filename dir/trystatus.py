import dir.mpc
def whyinfeasible():
    fopen =open('./status','r')
    data=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        one=[]
        for cline in k:
            one.append(int(float(cline)))
        data.append(one)

    fopen = open('./datadir/chargerindex','r')
    n=0
    for k in fopen:
        n=n+1

    L=15
    L2=3
    timehorizon =6
    Vacant={}
    Occupied={}
    for i in range(n):
        for j in range(L):
            Occupied[i,j]=0
            Vacant[i,j]=0
    for i in range(len(data)):

        if data[i][2]==1 and data[i][1]==0:
            Occupied[data[i][3],data[i][0]] +=1
        elif data[i][2]==0 and data[i][1]==0:
            Vacant[data[i][3],data[i][0]] +=1
    inputH={}
    for i in range(n):
        for t in range(L/L2):
            for l in range(L):
                inputH[i,t,l]= 0

    # for i in range(len(data)):

    charginglength={}
    for i in range(n):
        for l in range(L):
            for k in range(timehorizon):
                if l>L-L2-1 and l<L:
                    charginglength[i,l,k]=0
                else:
                    charginglength[i,l,k]=1
    dir.mpc.mpc_iteration(29,timehorizon,Vacant,Occupied,inputH,charginglength,1)
