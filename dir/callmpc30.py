import dir.mpc30
import os
from datetime import datetime
import random
def gps_to_region(gps):
    fopen = open('./datadir/chargerindex','r')
    chargergps=[]
    for k in fopen:
        k=k.split(',')
        chargergps.append([float(k[0]),float(k[1])])
    near =1000
    loc =0
    for i in range(len(chargergps)):
        cgps=chargergps[i]
        if abs(cgps[0]-gps[0])+abs(cgps[1]-gps[1])<near:
            loc =i
            near = abs(cgps[0]-gps[0])+abs(cgps[1]-gps[1])
    return loc


def get_middle_region(current,future,costtime):
    fopen = open('./datadir/chargerindex','r')
    chargergps=[]
    for k in fopen:
        k=k.split(',')
        chargergps.append([float(k[0]),float(k[1])])
    startx = chargergps[current][0]
    starty = chargergps[current][1]
    endx = chargergps[future][0]
    endy = chargergps[future][1]
    middlex = startx+(endx-startx)/costtime
    middley = starty+(endy-endx)/costtime
    return gps_to_region([middlex,middley])

def call_mpc(future):
    fopen = open('./datadir/chargerindex','r')
    n=0
    for k in fopen:
        n=n+1
    energystatus=[]
    location=[]
    occupancystatus=[]
    L1=1
    L2=3
    L=10
    timehorizon = future
    K=L/L2
    path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/evcharging/20161215/'
    # energylist=[]
    # for i in range(75):
    #     energylist.append(0)
    #     energylist.append(12)
    # for i in range(85):
    #     energylist.append(1)
    #     energylist.append(11)
    # for i in range(95):
    #     energylist.append(2)
    #     energylist.append(10)
    # for i in range(105):
    #     energylist.append(3)
    #     energylist.append(9)
    # for i in range(115):
    #     energylist.append(4)
    #     energylist.append(8)
    # for i in range(125):
    #     energylist.append(5)
    #     energylist.append(7)
    # for i in range(80):
    #     energylist.append(6)
    for root,dirs,files in os.walk(path):
        cvalue=0
        for file in files:
            chargingtime=[]
            fopen = open(path+file,'r')
            for k in fopen:
                k=k.strip('\n')
                k=k.split(',')
                start = float(k[0])
                start = int(start)
                end = float(k[1])
                end = int(end)
                if end-start>30:
                    chargingtime.append([start,end])
            fopen.close()
            if len(chargingtime)==0:
                energystatus.append(int((0.8)/(1/15.0)))
            else:
                firstcharge = chargingtime[0]
                if firstcharge[0]>=360 and firstcharge[0]<=480:
                    energy= int((0.6)/(1.0/15.0))
                    energy = cvalue%4 + 5
                    #energy = random.randint(0,12)
                    #energy = random.choice(energylist)

                    energystatus.append(energy)
                else:
                    energy=int((0.8)/(1/15.0))
                    energy= cvalue%4 + 5
                    #energy = random.randint(0,12)
                    #energy = random.choice(energylist)
                    energystatus.append(energy)
            cvalue+=1
            gpspath= '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gps/evgpsvehiclesorted/20161215/'+file
            if os.path.isfile(gpspath):
                fopen =open(gpspath,'r')
                gpsrecord=[]
                for k in fopen:
                    k=k.strip('\n')
                    gpsrecord.append(k)
                fopen.close()
                gps=[]
                for line in gpsrecord:
                    line =line.split(',')
                    ctime = datetime.strptime(line[4], '%Y-%m-%dT%H:%M:%S.000Z')
                    if (ctime.hour>=6):
                        gps.append(float(line[2]))
                        gps.append(float(line[3]))
                        break
                if len(gps)==0:
                    print file
                else:
                    location.append(gps_to_region(gps))
            dealpath = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/evdeal/20161215/'+file
            if os.path.isfile(dealpath):
                fopen = open(dealpath,'r')
                dealrecord=[]
                for k in fopen:
                    k=k.split(',')
                    ctime1 = datetime.strptime(k[1], '%Y-%m-%dT%H:%M:%S.000Z')
                    ctime2 = datetime.strptime(k[2], '%Y-%m-%dT%H:%M:%S.000Z')
                    dealrecord.append([ctime1.hour*60+ctime1.minute,ctime2.hour*60+ctime2.minute])
                occu =0
                for ck in dealrecord:
                    if ck[0]<=360 and ck[1]>360:
                        occu=1
                occupancystatus.append(occu)
            else:
                occupancystatus.append(0)

    chargingstatus=[]
    remainingchargingtime=[]
    remainingtriptime=[]
    destination=[]
    for i in range(len(energystatus)):
        chargingstatus.append(0)
        remainingchargingtime.append(0)
        remainingtriptime.append(0)
        destination.append(0)

    Vacant={}
    Occupied={}
    for i in range(n):
        for j in range(L):
            Occupied[i,j]=0
            Vacant[i,j]=0
    for i in range(len(energystatus)):
        if occupancystatus[i]==1:
            Occupied[location[i],energystatus[i]] +=1
        elif occupancystatus[i]==0:
            Vacant[location[i],energystatus[i]] +=1
    inputH={}
    for i in range(n):
        for t in range(L/L2):
            for l in range(L):
                inputH[i,t,l]= 0
    charginglength={}
    for i in range(n):
        for l in range(L):
            for k in range(timehorizon):
                if l>=L-1*L2-1 and l<L:
                    charginglength[i,l,k]=0
                # elif l<=L-2*L2-1 and l> L-4*L2-1:
                #     charginglength[i,l,k]=1
                else:
                    charginglength[i,l,k] = 1
    supplydemand=[]
    averagedistance=[]
    numofcharge=[]
    for i in range(len(energystatus)):
        numofcharge.append(0)

    occutime=[]
    for i in range(n):
        occutime.append(0)


    socbefore=[]
    socafter=[]
    for time in range(12,48):
        ctimehorizon = min(timehorizon,48-time)
        beta= 0.1
        fwrite1=open('./status','w')
        for i in range(len(energystatus)):
            fwrite1.write(str(energystatus[i])+','+str(chargingstatus[i])+','+str(occupancystatus[i])+','+str(location[i])+','+str(remainingchargingtime[i])+','+str(remainingtriptime[i])+'\n')
        fwrite1.close()
        print 'Current Time slot:', str(time),'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'
        X=dir.mpc30.mpc_iteration(time,ctimehorizon,Vacant,Occupied,inputH,charginglength,beta)


        distance =[]
        fopen = open('./datadir/distance','r')
        for k in fopen:
            k=k.strip('\n')
            k=k.split(',')
            one =[]
            for value in k:
                one.append(float(value))
            distance.append(one)

        chargingnum=0
        totaldistance=0
        # for i in range(n):
        #     for j in range(n):
        #         for l in range(L):
        #             chargingnum += X[i,j,l]
        #             if j!=i:
        #                 # print distance[i][j]
        #                 totaldistance+= X[i,j,l] *distance[i][j]
        #             else:
        #                 totaldistance+= X[i,j,l] *distance[i][j]
        # averagedistance.append([totaldistance,chargingnum])
        updatestatus=[]
        for i in range(len(energystatus)):
            updatestatus.append(0)
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    dispatchnum = int(X[i,j,l])
                    for index in range(len(energystatus)):
                        if dispatchnum>0:
                            if energystatus[index]==l and location[index]==i and occupancystatus[index]==0 and chargingstatus[index]==0 and updatestatus[index]==0:
                                before = (energystatus[index]+1)*1.0/L+random.uniform(-1.0/30,1.0/30)
                                socbefore.append(before)
                                after = (energystatus[index]+1+charginglength[j,l,0]*L2)*1.0/L+random.uniform(-1.0/30,1.0/30)
                                socafter.append(after)
                                chargingnum+=1
                                numofcharge[index]+=1
                                occutime[j] += 30*charginglength[i,l,0]
                                if distance[i][j]>3:
                                    totaldistance+= distance[i][j]
                                else:
                                    totaldistance +=distance[i][j]
                                if charginglength[j,l,0]>1:
                                    energystatus[index] += L2
                                    location[index] = j
                                    occupancystatus[index]=0
                                    chargingstatus[index]= 1
                                    remainingchargingtime[index] = charginglength[j,l,0]-1
                                    updatestatus[index]=1
                                    dispatchnum -=1
                                elif charginglength[j,l,0]==1:
                                    energystatus[index] += L2
                                    # after=(energystatus[index]+1)*1.0/L+random.uniform(-1.0/30,1.0/30)
                                    # socafter.append(after)
                                    location[index] = j
                                    occupancystatus[index]=0
                                    chargingstatus[index]= 0
                                    remainingchargingtime[index] = 0
                                    updatestatus[index]=1
                                    dispatchnum -=1

        p={}
        pp={}
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
            if float(k)>=30:
                p[i] = (int(float(k)/8))
            else:
                p[i] = (int(float(k)/5))
            pp[i] =p[i]

        for index in range(len(energystatus)):
            if energystatus[index]<L1 and updatestatus[index]==0:
                inputH={}
                for i in range(n):
                    for t in range(L/L2):
                        for l in range(L):
                            inputH[i,t,l]= 0

                for i in range(len(energystatus)):
                    if occupancystatus[i]==0 and chargingstatus[i]==1:
                        x1 = location[i]
                        x2 = remainingchargingtime[i]
                        x3 = energystatus[i]
                        inputH[x1,x2,x3] +=1
                print index
                chargingtime1 = 1
                cloc =location[index]

                find = False
                before=(energystatus[index]+1)*1.0/L+random.uniform(-1.0/30,1.0/30)
                socbefore.append(before)
                for j in range(n):
                    if p[j]>0:
                        p[j] -=1
                        find = True
                        chargingnum +=1
                        totaldistance+= distance[location[index]][j]
                        location[index] =j
                        break

                if find==False:
                    energystatus[index] +=L2
                else:
                    numofcharge[index]+=1
                    occutime[location[index]] +=30
                    if chargingtime1>1:
                        energystatus[index] += L2
                        #location[index] = location[index]
                        occupancystatus[index]=0
                        chargingstatus[index]= 1
                        remainingchargingtime[index] = chargingtime1-1
                        updatestatus[index]=1

                    elif chargingtime1==1:
                        energystatus[index] += L2
                        #location[index] = location[index]
                        occupancystatus[index]=0
                        chargingstatus[index]= 0
                        remainingchargingtime[index] = 0
                        updatestatus[index]=1
                after=(energystatus[index]+1)*1.0/L+random.uniform(-1.0/30,1.0/30)
                socafter.append(after)

        averagedistance.append([totaldistance,chargingnum,(totaldistance+1)/(1+chargingnum)])
        supply=[]
        for i in range(n):
            supply.append(0)
        for i in range(len(energystatus)):
            if occupancystatus[i]==0 and chargingstatus[i]==0 and updatestatus[i]==0:
                supply[location[i]] +=1
        demand =[]
        cdemand=[]
        fopen =open('./historydemand/slot30/groundtruth/'+str(time),'r')
        for line in fopen:
            line =line.strip('\n')
            line =line.split(',')
            csum=0
            one=[]
            for k in line:
                one.append(int(float(k))+1)
                csum += float(k)
            demand.append(csum)
            cdemand.append(one)
        fopen.close()
        # fwrite =open('./result/mpc/slot'+str(20)+'-'+str(time)+'-'+str(timehorizon),'w')
        # for i in range(len(demand)):
        #     fwrite.write((str((supply[i]+1)/(1+demand[i]))+'\n'))
        sdratio=0
        for i in range(n):
            c=float(supply[i]+1)/(demand[i]+1)
            sdratio += max(0,1-c)
        sdratio /=n
        supplydemand.append([sum(supply),sum(demand),sdratio])
        distance =[]
        fopen = open('./datadir/distance','r')
        for k in fopen:
            one=[]
            k=k.strip('\n')
            k=k.split(',')
            for cc in k:
                one.append(float(cc))
            distance.append(one)
        fopen.close()

        for i in range(n):
            pair=[]
            for j in range(n):
                pair.append([j,cdemand[i][j]])
            pair = sorted(pair,key= lambda  x:x[1],reverse=True)
            for j in range(n):
                cnum = pair[j][1]
                cdistance = distance[i][pair[j][0]]
                costtime = int((60.0*cdistance/40.0)/30)+1
                for index in range(len(energystatus)):
                    if cnum>0:
                        if energystatus[index]+1>costtime and location[index]==i and occupancystatus[index]==0 and chargingstatus[index]==0 and updatestatus[index]==0:
                            energystatus[index] -=L1
                            if energystatus[index]<0:
                                print 'Error---!!'
                                return
                            chargingstatus[index]=0

                            if costtime>1:
                                occupancystatus[index] =1
                                remainingtriptime[index] = costtime-1
                                destination[index] = pair[j][0]
                                location[index] = get_middle_region(location[index],destination[index],remainingtriptime[index]+1)
                            else:
                                occupancystatus[index] =0
                                remainingtriptime[index] =0
                                location[index] = pair[j][0]
                            updatestatus[index] =1
                            cnum -=1



        for i in range(len(energystatus)):
            if updatestatus[i]==0:
                updatestatus[i] = 1
                if occupancystatus[i]==1 and chargingstatus[i]==0:
                    if remainingtriptime[i]>1:
                        energystatus[i] -=L1
                        if energystatus[i]<0:
                            print 'Error!'
                            return
                        occupancystatus[i] =1
                        remainingtriptime[i] -=1
                        chargingstatus[i]=0
                        location[i] = get_middle_region(location[i],destination[i],remainingtriptime[i]+1)
                    else:
                        energystatus[i] -=L1
                        if energystatus[i]<0:
                            print 'Error!!'
                            return
                        occupancystatus[i] =0
                        remainingtriptime[i] =0
                        location[i] = destination[i]
                        chargingstatus[i] = 0

                elif occupancystatus[i]==0 and chargingstatus[i]==1:
                    if remainingchargingtime[i]>1:
                        energystatus[i] += L2
                        occupancystatus[i] =0
                        chargingstatus[i] = 1
                        remainingchargingtime[i] -=1
                    else:
                        energystatus[i] += L2
                        occupancystatus[i] =0
                        chargingstatus[i] =0
                        remainingchargingtime[i] =0
                        # after=(energystatus[i]+1)*1.0/L+random.uniform(-1.0/30,1.0/30)
                        # socafter.append(after)
                else:

                    energystatus[i] -= L1
                    fopen1 =open('./transition/slot30/'+str(time)+'pv','r')
                    transition = []
                    for k in fopen1:
                        k=k.strip('\n')
                        k=k.split(',')
                        one=[]
                        for line in k:
                            one.append(float(line))
                        transition.append(one)
                    fopen1 =open('./transition/slot30/'+str(time)+'qv','r')
                    transition1 = []
                    for k in fopen1:
                        k=k.strip('\n')
                        k=k.split(',')
                        one=[]
                        for line in k:
                            one.append(float(line))
                        transition1.append(one)
                    fopen1 =open('./transition/slot30/'+str(time)+'po','r')
                    transition2 = []
                    for k in fopen1:
                        k=k.strip('\n')
                        k=k.split(',')
                        one=[]
                        for line in k:
                            one.append(float(line))
                        transition2.append(one)
                    fopen1 =open('./transition/slot30/'+str(time)+'qo','r')
                    transition3 = []
                    for k in fopen1:
                        k=k.strip('\n')
                        k=k.split(',')
                        one=[]
                        for line in k:
                            one.append(float(line))
                        transition3.append(one)
                    loc = location[i]
                    transitionrow = transition[loc]
                    max1= max(transitionrow)
                    for cc in range(len(transitionrow)):
                        if transitionrow[cc]==max1:
                            location[i]=cc
                            break
                    possible=[]
                    for j in range(n):
                        possible.append(int(transition[loc][j]*1000))
                        #possible.append(int(transition[loc][j]*1000+transition1[loc][j]*1000+transition2[loc][j]*1000+transition3[loc][j]*1000))
                    mylist=[]
                    for j in range(n):
                        for c in range(possible[j]):
                            mylist.append(j)
                    if len(mylist)==0:
                        location[i] = location[i]
                    else:
                        cc = random.choice(mylist)
                        # while cc ==location[i]:
                        #     cc = random.choice(mylist)
                        location[i] =cc
                    # if energystatus[i]<=0:
                    #     print 'Alarm',i
                    #     return
        p={}
        pp={}
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
            if float(k)>=30:
                p[i] = (int(float(k)/8))
            else:
                p[i] = (int(float(k)/5))
            pp[i] =p[i]


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
        for i in range(n):
            for t in range(L/L2):
                for l in range(L):
                    inputH[i,t,l]= 0

        for i in range(len(energystatus)):
            if occupancystatus[i]==0 and chargingstatus[i]==1:
                x1 = location[i]
                x2 = remainingchargingtime[i]
                x3 = energystatus[i]
                inputH[x1,x2,x3] +=1
        for i in range(n):
            csum=0
            for t in range(L/L2):
                for l in range(L):
                    csum+= inputH[i,t,l]

            if csum>p[i]:

                print 'Error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'

        for index in range(len(energystatus)):
            if energystatus[index]<L1:
                for i in range(n):
                    for t in range(L/L2):
                        for l in range(L):
                            inputH[i,t,l]= 0

                for i in range(len(energystatus)):
                    if occupancystatus[i]==0 and chargingstatus[i]==1:
                        x1 = location[i]
                        x2 = remainingchargingtime[i]
                        x3 = energystatus[i]
                        inputH[x1,x2,x3] +=1
                print index
                chargingtime1 = 1
                cloc =location[index]

                find = False
                for j in range(n):
                    # if p[j]>0 and c[cloc,j,0]==1:
                    if p[j]>0:
                        location[index] =j
                        p[j] -=1
                        find = True
                        break
                # if find==False:
                #     for j in range(n):
                #         if p[j]>0:
                #             location[index]=j
                #             p[j] -=1
                #             find = True
                #             break
                if find==False:
                    energystatus[index] +=L2
                else:
                    if chargingtime1>1:
                        energystatus[index] += L2
                        #location[index] = location[index]
                        occupancystatus[index]=0
                        chargingstatus[index]= 1
                        remainingchargingtime[index] = chargingtime1-1
                        updatestatus[index]=1

                    elif chargingtime1==1:
                        energystatus[index] += L2
                        #location[index] = location[index]
                        occupancystatus[index]=0
                        chargingstatus[index]= 0
                        remainingchargingtime[index] = 0
                        updatestatus[index]=1


        for i in range(n):
            for j in range(L):
                Occupied[i,j]=0
                Vacant[i,j]=0
        for i in range(len(energystatus)):
            if occupancystatus[i]==1 and chargingstatus[i]==0:
                Occupied[location[i],energystatus[i]] +=1
            elif occupancystatus[i]==0 and chargingstatus[i]==0:
                if energystatus[i]==0:
                    print i
                Vacant[location[i],energystatus[i]] +=1


        for i in range(n):
            for t in range(L/L2):
                for l in range(L):
                    inputH[i,t,l]= 0

        for i in range(len(energystatus)):
            if occupancystatus[i]==0 and chargingstatus[i]==1:
                #print 'KKKKKKKKKKKKKKKERROR'
                x1 = location[i]
                x2 = remainingchargingtime[i]
                x3 = energystatus[i]
                inputH[x1,x2,x3] +=1

        for i in range(n):
            csum=0
            for t in range(L/L2):
                for l in range(L):
                    csum+=inputH[i,t,l]
            if csum>pp[i]:
                print 'ERROR________!!!!'

    fwrite2 =open('./resultdata/timehorizon/newslot30beta01_3horizon'+str(future),'w')
    for k in supplydemand:
        fwrite2.write(str(k[0])+','+str(k[1])+','+str(k[2])+'\n')
    fwrite2.close()

    fwrite2 =open('./resultdata/timehorizon/newdistanceslot30beta01_3horizon'+str(future),'w')
    for k in averagedistance:
        fwrite2.write(str(k[0])+','+str(k[1])+','+str(k[2])+'\n')
    fwrite2.close()

    # fwrite3= open('./resultdata/chargenum/p2charging','w')
    # for k in numofcharge:
    #     fwrite3.write(str(k)+'\n')
    # fwrite3.close()
    #
    # fwrite3= open('./resultdata/chargeroccupiedtime/p2charging','w')
    # for i in range(n):
    #     k=occutime[i]
    #     fwrite3.write(str(k)+','+str(p[i])+'\n')
    # fwrite3.close()
    #
    # fwrite3= open('./resultdata/soc/before','w')
    # for k in socbefore:
    #     fwrite3.write(str(k)+'\n')
    # fwrite3.close()
    #
    # fwrite3= open('./resultdata/soc/after','w')
    # for k in socafter:
    #     fwrite3.write(str(k)+'\n')
    # fwrite3.close()
