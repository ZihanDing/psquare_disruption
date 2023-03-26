import dir.mpc10
import os
from datetime import datetime
import random
import math


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

def call_mpc(future,beta1):
    fopen = open('./datadir/chargerindex','r')
    n=0
    for k in fopen:
        n=n+1
    energystatus=[]
    location=[]
    occupancystatus=[]
    L1=1
    L2=3
    L=30
    timehorizon = future
    K=L/L2
    path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/evcharging/20161213/'
    energylist=[]
    for i in range(75):
        energylist.append(0)
        energylist.append(12)
    for i in range(85):
        energylist.append(1)
        energylist.append(11)
    for i in range(95):
        energylist.append(2)
        energylist.append(10)
    for i in range(105):
        energylist.append(3)
        energylist.append(9)
    for i in range(115):
        energylist.append(4)
        energylist.append(8)
    for i in range(125):
        energylist.append(5)
        energylist.append(7)
    for i in range(80):
        energylist.append(6)
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
            if os.path.exists('./newprediction/startenergy/'+file):
                fopen=open('./newprediction/startenergy/'+file,'r')
                cc =0
                for k in fopen:
                    cc=float(k)*2
                energystatus.append(int(cc)-1)
            else:
                energystatus.append(20)
            # if len(chargingtime)==0:
            #     energystatus.append(int((0.8)/(1/15.0)))
            # else:
            #     firstcharge = chargingtime[0]
            #     if firstcharge[0]>=360 and firstcharge[0]<=480:
            #         energy= int((0.6)/(1.0/15.0))
            #         energy = cvalue%6+8
            #         #energy = random.randint(0,12)
            #         #energy = random.choice(energylist)
            #
            #         energystatus.append(energy)
            #     else:
            #         energy=int((0.8)/(1/15.0))
            #         energy= cvalue%6+8
            #         #energy = random.randint(0,12)
            #         #energy = random.choice(energylist)
            #         energystatus.append(energy)
            cvalue+=1
            gpspath= '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gps/evgpsvehiclesorted/20161213/'+file
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
            dealpath = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/evdeal/20161213/'+file
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


    supplydemand=[]
    averagedistance=[]


    chargestation=[]
    vehiclestatus=[]

    numofcharge=[]
    waitingtime=[]
    idledrivingtime=[]
    idletime=[]
    withoutwaiting=[]
    futurecharginglength=[]
    dispatchedtime=[]
    for i in range(len(energystatus)):
        one =[]
        two=[]
        for j in range(144):
            one.append(0)
            two.append(-1)
        vehiclestatus.append(one)
    for i in range(len(energystatus)):
        numofcharge.append(0)
        withoutwaiting.append(0)
        chargestation.append(-1)
        waitingtime.append(0)
        idledrivingtime.append(0)
        idletime.append(0)
        futurecharginglength.append(0)
        dispatchedtime.append(-1)

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
        if float(k)>40:
            p[i]= int(float(k)/5)
        else:
            p[i] = int(float(k)/5)

    regionratio=[]


    beta= beta1

    chargingresource=[]
    futuresupply={}
    for i in range(n):
        for l in range(L):
            for k in range(timehorizon):
                futuresupply[i,l,k]=0
    for i in range(n):
        one=[]

        for k in range(timehorizon):
            one.append(0)
            chargingresource.append(one)

    for time in range(36,144):

        #ctimehorizon = min(timehorizon,72-time)
        ctimehorizon = timehorizon
        fwrite1=open('./status','w')
        for i in range(len(energystatus)):
            fwrite1.write(str(energystatus[i])+','+str(chargingstatus[i])+','+str(occupancystatus[i])+','+str(location[i])+','+str(remainingchargingtime[i])+','+str(remainingtriptime[i])+'\n')
        fwrite1.close()
        print 'Current Time slot:', str(time),'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'
        # for i in range(n):
        #     print Vacant[i,0],Vacant[i,1],Vacant[i,2],Vacant[i,3],Vacant[i,4],Vacant[i,5],Vacant[i,6],Vacant[i,7],Vacant[i,8],Vacant[i,9],Vacant[i,10],Vacant[i,11],Vacant[i,12],Vacant[i,13],Vacant[i,14]
        # print '-------------------------------------'
        # for i in range(n):
        #     print Occupied[i,0],Occupied[i,1],Occupied[i,2],Occupied[i,3],Occupied[i,4],Occupied[i,5],Occupied[i,6],Occupied[i,7],Occupied[i,8],Occupied[i,9],Occupied[i,10],Occupied[i,11],Occupied[i,12],Occupied[i,13],Occupied[i,14]
        print sum(Vacant[i,j] for i in range(n) for j in range(L)),sum(Occupied[i,j] for i in range(n) for j in range(L))
        X,Y=dir.mpc10.mpc_iteration(time,ctimehorizon,Vacant,Occupied,beta,chargingresource,futuresupply)


        distance =[]
        fopen = open('./datadir/distance','r')
        for k in fopen:
            k=k.strip('\n')
            k=k.split(',')
            one =[]
            for value in k:
                one.append(float(value))
            distance.append(one)


        updatestatus=[]
        for i in range(len(energystatus)):
            updatestatus.append(0)
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    for q in range(1,1+((L-l-1)/L2)):
                        if l<L1:
                            dispatchnum = math.ceil(X[i,j,l,q])
                        else:
                            dispatchnum = int(X[i,j,l,q])
                        for index in range(len(energystatus)):
                            if dispatchnum>0:
                                if energystatus[index]==l and location[index]==i and occupancystatus[index]==0 and chargingstatus[index]==0 and updatestatus[index]==0:
                                    # before = (energystatus[index]+1)*1.0/L+random.uniform(-1.0/30,1.0/30)
                                    # socbefore.append(before)
                                    # after = (energystatus[index]+1+q*L2)*1.0/L+random.uniform(-1.0/30,1.0/30)
                                    # socafter.append(after)
                                    idledrivingtime[index] += 60.0*distance[i][j]/40.0
                                    withoutwaiting[index] += 60.0*distance[i][j]/40.0
                                    idletime[index] += 60.0*distance[i][j]/40.0
                                    chargestation[index] = j
                                    chargingstatus[index] = 3
                                    futurecharginglength[index] = q
                                    location[index] = j
                                    dispatchnum -=1
                                    # updatestatus[index] = 1
                                    occupancystatus[index] = 0
                                    dispatchedtime[index] = time
                                    remainingchargingtime[index] = q

        for i in range(len(p)):
            stationid =i
            connectingvehicle=0
            for j in range(len(energystatus)):
                if chargingstatus[j]==2 and chargestation[j]==stationid:
                    connectingvehicle+=1
            freepoints = p[i] - connectingvehicle
            waitinginfo =[]
            for j in range(len(energystatus)):
                if chargestation[j] == stationid and (chargingstatus[j]==1 or chargingstatus[j]==3):
                    info =[j, dispatchedtime[j],remainingchargingtime[j]]
                    waitinginfo.append(info)
            waitinginfo=sorted(waitinginfo,key=lambda x:(x[1],x[2]))
            for record in waitinginfo:
                if freepoints>0:
                    id1 =record[0]
                    chargingstatus[id1]= 2
                    # remainingchargingtime[id1] = futurecharginglength[id1]
                    # updatestatus[id1]=1
                    freepoints-=1
                else:
                    idledrivingtime[record[0]]+=10.0
                    idletime[record[0]] +=10.0
                    id1 =record[0]
                    chargingstatus[id1]= 1
                    updatestatus[id1]=1



        for i in range(n):
            num=0
            for j in range(len(energystatus)):
                if chargingstatus[j]==2 and chargestation[j]==i:
                    num+=1
            if num>p[i]:
                print 'LLLLLLLLLLLLLLLLLLLLLLLL'


        supply=[]
        for i in range(n):
            supply.append(0)
        for i in range(len(energystatus)):
            if occupancystatus[i]==0 and chargingstatus[i]==0 and updatestatus[i]==0:
                supply[location[i]] +=1


        demand =[]
        cdemand=[]
        fopen =open('./historydemand/slot10/groundtruth/'+str(time),'r')
        for line in fopen:
            line =line.strip('\n')
            line =line.split(',')
            csum=0
            one=[]
            for k in line:
                one.append((float(k)))
                csum += (float(k))
            demand.append(csum)
            cdemand.append(one)
        fopen.close()

        # sdratio=0
        # for i in range(n):
        #     c=float(supply[i]+1)/(demand[i]+1)
        #     regionratio.append(max(0,1-c))
        #     sdratio += max(0,1-c)
        # sdratio /=n
        # print '----------------------------------------------------~~~~~',float(sum(supply)),sum(demand),sdratio
        # supplydemand.append([sum(supply),sum(demand),sdratio])
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
                costtime = ((60.0*cdistance/40.0))
                for index in range(len(energystatus)):
                    if cnum>0:
                        if energystatus[index]+1>int(costtime/10)+1 and location[index]==i and occupancystatus[index]==0 and chargingstatus[index]==0 and updatestatus[index]==0:
                            energystatus[index] -=L1
                            if energystatus[index]<0:
                                print 'Error---!!'
                                return
                            chargingstatus[index]=0

                            if costtime>10:
                                occupancystatus[index] =1
                                remainingtriptime[index] = costtime-10
                                destination[index] = pair[j][0]
                                location[index] = get_middle_region(location[index],destination[index],int(remainingtriptime[index])/10+2)
                            else:
                                occupancystatus[index] =0
                                remainingtriptime[index] =0
                                location[index] = pair[j][0]
                                # supply[location[index]] +=max(0,1-((60.0*cdistance/30.0)/20.0))
                            updatestatus[index] =1
                            cnum -=1



        for i in range(len(energystatus)):
            if updatestatus[i]==0:
                updatestatus[i] = 1
                if occupancystatus[i]==1 and chargingstatus[i]==0:
                    if remainingtriptime[i]>10:
                        energystatus[i] -=L1
                        if energystatus[i]<0:
                            print 'Error!'
                            return
                        occupancystatus[i] =1
                        remainingtriptime[i] -=10
                        chargingstatus[i]=0
                        location[i] = get_middle_region(location[i],destination[i],int(remainingtriptime[i]/10)+2)
                    else:
                        energystatus[i] -=L1
                        if energystatus[i]<0:
                            print i
                            print 'Error!!'
                            return
                        occupancystatus[i] =0
                        supply[destination[i]] +=1
                        # supply[destination[i]] += (1-(remainingtriptime[i])/20.0)
                        remainingtriptime[i] =0
                        location[i] = destination[i]
                        chargingstatus[i] = 0


                elif occupancystatus[i]==0 and chargingstatus[i]==2:
                    idledrivingtime[i]+=10.0
                    if remainingchargingtime[i]>1:
                        energystatus[i] += L2
                        occupancystatus[i] =0
                        # chargingstatus[i] = 2
                        remainingchargingtime[i] -=1
                    else:
                        energystatus[i] += L2
                        occupancystatus[i] =0
                        chargingstatus[i] = 0
                        remainingchargingtime[i] =0


                elif occupancystatus[i]==0 and chargingstatus[i]==0:

                    energystatus[i] -= L1
                    fopen1 =open('./transition/slot10/'+str(time)+'pv','r')
                    transition = []
                    for k in fopen1:
                        k=k.strip('\n')
                        k=k.split(',')
                        one=[]
                        for line in k:
                            one.append(float(line))
                        transition.append(one)
                    fopen1 =open('./transition/slot10/'+str(time)+'qv','r')
                    transition1 = []
                    for k in fopen1:
                        k=k.strip('\n')
                        k=k.split(',')
                        one=[]
                        for line in k:
                            one.append(float(line))
                        transition1.append(one)
                    fopen1 =open('./transition/slot10/'+str(time)+'po','r')
                    transition2 = []
                    for k in fopen1:
                        k=k.strip('\n')
                        k=k.split(',')
                        one=[]
                        for line in k:
                            one.append(float(line))
                        transition2.append(one)
                    fopen1 =open('./transition/slot10/'+str(time)+'qo','r')
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
                    mylist=[]
                    for j in range(n):
                        for c in range(possible[j]):
                            mylist.append(j)
                    if len(mylist)==0:
                        location[i] = location[i]
                    else:
                        cc = random.choice(mylist)

                        location[i] =cc

        for i in range(n):
            num=0
            for j in range(len(energystatus)):
                if chargingstatus[j]==2 and chargestation[j]==i:
                    num+=1
            if num>p[i]:
                print 'MMMMMMMMMMMMMMMMMMMMMMM'

        chargingresource=[]

        for i in range(n):
            gg=[]
            for j in range(timehorizon):
                gg.append(0)
                # chargingresource[i][j]=0
            chargingresource.append(gg)
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    futuresupply[i,l,k]=0
        # for i in range(n):
        #     for k in range(timehorizon):
        #         if chargingresource[i][k]>p[i]:
        #             print 'NNGGGGGGGGGGGGGGGNNNNNNNNNNNNNNNNNNNNNNNN'
        for id in range(n):
            # print id
            # print chargingresource
            scheduling=[]
            for j in range(p[id]):
                one=[]
                for k in range(20):
                    one.append(0)
                scheduling.append(one)
            stationid =id
            for j in range(len(energystatus)):
                if chargingstatus[j]==2 and chargestation[j]==stationid:
                    point=0
                    for z in range(p[id]):
                        if scheduling[z][0]==0:
                            point =z
                            break
                    for k in range(remainingchargingtime[j]):
                        scheduling[point][k]=1
                        futuresupply[id,energystatus[j]+remainingchargingtime[j]*L2,remainingchargingtime[j]] += 1

            # if sum(scheduling[point][0] for point in range(p[i]))>p[i]:
            #     print 'HAHHAHHAHHHHAHAHH'
            waitinfonew=[]
            for j in range(len(energystatus)):
                if chargingstatus[j]==1 and chargestation[j]==stationid:
                    info =[j, dispatchedtime[j],remainingchargingtime[j]]
                    waitinfonew.append(info)
            waitinfonew=sorted(waitinfonew,key=lambda x:(x[1],x[2]))
            for k in waitinfonew:
                j = k[0]
                point = 0
                starttime=0
                for z in range(timehorizon):
                    find =False
                    for y in range(p[id]):
                        if scheduling[y][z]==0:
                            point =y
                            starttime=z
                            find =True
                            break
                    if find:
                        break
                if remainingchargingtime[j]+ starttime<timehorizon:
                    futuresupply[id,energystatus[j]+remainingchargingtime[j]*L2,remainingchargingtime[j]+ starttime] += 1
                for k in range(starttime,min(timehorizon,remainingchargingtime[j]+starttime)):
                    scheduling[point][k]=1

            for k in range(timehorizon):
                cnum =sum(scheduling[j][k] for j in range(p[id]))
                chargingresource[id][k] = cnum
                # if chargingresource[id][k]>p[id]:
                #     print '---------------------------EEEEEEEOOOOOOOOOOOOOOOOOOOOOORRRRRRRRRRRRRRRRRRR'
            # print id
            # print chargingresource
            # print '--------------'

        # for i in range(n):
        #     print p[i],chargingresource[i]



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

        unratio=[]
        for i in range(n):
            if demand[i]>0:
                c = float(supply[i])/demand[i]
            else:
                c=0
            unratio.append(max(0,1-c))
        regionratio.append(unratio)

        if sum(demand)>0:
            print sum(supply),sum(demand),max(0,1-float(sum(supply))/sum(demand))
            supplydemand.append([sum(supply),sum(demand),max(0,1-float(sum(supply))/sum(demand))])
        else:
            print sum(supply),sum(demand),0.00
            supplydemand.append([sum(supply),sum(demand),0.0])

        if time==143:
            fwrite1=open('./resultdata/timeslot/p2charging10utilization3-'+str(timehorizon)+'-'+str(beta),'w')
            for i in range(len(energystatus)):
                fwrite1.write(str(idledrivingtime[i])+'\n')
            fwrite1.close()

            fwrite1=open('./resultdata/timeslot/p2charging10totalidle3-'+str(timehorizon)+'-'+str(beta),'w')
            for i in range(len(energystatus)):
                fwrite1.write(str(idletime[i])+'\n')
            fwrite1.close()

            fwrite1=open('./resultdata/timeslot/p2without10waiting3-'+str(timehorizon)+'-'+str(beta),'w')
            for i in range(len(energystatus)):
                fwrite1.write(str(withoutwaiting[i])+'\n')
            fwrite1.close()

    fwrite2 =open('./resultdata/timeslot/temporalsupply10demand3-'+str(timehorizon)+'-'+str(beta),'w')
    for k in supplydemand:
        fwrite2.write(str(k[0])+','+str(k[1])+','+str(k[2])+'\n')
    fwrite2.close()

    fwrite1=open('./resultdata/timeslot/region10ratio3-'+str(timehorizon)+'-'+str(beta),'w')
    for k in regionratio:
        for kk in k:
            fwrite1.write(str(kk)+',')
        fwrite1.write('\n')
    fwrite1.close()


            # if sum(scheduling[point,0] for point in range(p[i]))>p[i]:
            #     print 'HAHHAHHAHHHHAHAHH'
            # for j in range(len(energystatus)):
            #     if chargingstatus[j]==1 and chargestation[j]==stationid:
            #         point=0
            #         starttime=0
            #         for z in range(timehorizon):
            #             find =False
            #             for y in range(p[i]):
            #                 if scheduling[y,z]==0:
            #                     point =y
            #                     starttime=z
            #                     find =True
            #                     break
            #             if find:
            #                 break
            #         if remainingchargingtime[j]+ starttime<timehorizon:
            #             futuresupply[i,energystatus[j]*remainingchargingtime[j]*L2,remainingchargingtime[j]+ starttime] += 1
            #         for k in range(starttime,min(timehorizon,remainingchargingtime[j]+starttime)):
            #             scheduling[point,k]=1
