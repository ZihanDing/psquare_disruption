import dir.mpc
import os
import random
from datetime import datetime

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

def call_rec():
    fopen = open('./datadir/chargerindex','r')
    n=0
    p=[]
    pp=[]
    for k in fopen:
        n=n+1
        k=k.split(',')
        k=k[2]
        k=k.strip('\n')
        num =float(k)
        if num>40:
            num=int(num/5)
        else:
            num=int(num/5)
        p.append(num)
        # if float(k)>80:
        #     p.append(int(float(k)/4))
        #     #p[i] = 70
        #     pp.append(int(float(k)/4))
        # else:
        #     p.append(int(float(k)/1))
        #     pp.append(int(float(k)/1))

    energystatus=[]
    location=[]
    occupancystatus=[]
    L1=1
    L2=3
    L=15

    path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/evcharging/20161213/'

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
                    #energy= int((0.6)/(1.0/15.0))
                    energy = cvalue%L
                    energystatus.append(energy)
                else:
                    #energy=int((0.8)/(1/15.0))
                    energy = cvalue%L
                    energystatus.append(energy)
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

    idledrivingtime=[]

    onroadtime=[]

    chargingstation=[]
    destination=[]
    dispatchedtime=[]
    for i in range(len(energystatus)):
        dispatchedtime.append(0)
        destination.append(-1)
        chargingstation.append(-1)
        onroadtime.append(0)
        chargingstatus.append(0)
        remainingchargingtime.append(0)
        remainingtriptime.append(0)
        idledrivingtime.append(0)
    distance =[]
    fopen = open('./datadir/distance','r')
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        one =[]
        for value in k:
            one.append(float(value))
        distance.append(one)

    kmin=100
    for i in range(n):
        for j in range(n):
            if i!=j:
                if distance[i][j]<kmin:
                    kmin=distance[i][j]
    print kmin
    regionratio=[]
    averagedistance=[]
    print len(energystatus),len(location),len(occupancystatus),len(chargingstatus)

    occutime=[]
    for i in range(n):
        occutime.append(0)

    supplydemand=[]

    for time in range(18,72):


        print 'Current Time slot:', str(time),'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'
        updatestatus=[]
        for i in range(len(energystatus)):
            updatestatus.append(0)

        csupply=[]
        cdemand=[]
        for i in range(n):
            csupply.append(0)

        fopen =open('./historydemand/slot20/groundtruth/'+str(time),'r')
        for line in fopen:
            line =line.strip('\n')
            line =line.split(',')

            one=[]
            for k in line:
                one.append((float(k)))
            cdemand.append(one)
        fopen.close()
        # for i in range(n):
        #     pair=[]
        #     for j in range(n):
        #         pair.append([j,cdemand[i][j]])
        #     pair = sorted(pair,key= lambda  x:x[1],reverse=True)
        #     for j in range(n):
        #         cnum = pair[j][1]
        #         cdistance = distance[i][pair[j][0]]
        #         costtime = int((60.0*cdistance/20.0)/20)+1
        #         for index in range(len(energystatus)):
        #             if cnum>0:
        #                 if energystatus[index]+1>costtime and location[index]==i and occupancystatus[index]==0 and chargingstatus[index]==0 and updatestatus[index]==0 and energystatus[index]>5:
        #                     energystatus[index] -=L1
        #                     if energystatus[index]<0:
        #                         print 'Error---!!'
        #                         return
        #                     chargingstatus[index]=0
        #
        #                     if costtime>1:
        #                         occupancystatus[index] =1
        #                         remainingtriptime[index] = costtime-1
        #                         destination[index] = pair[j][0]
        #                         location[index] = get_middle_region(location[index],destination[index],remainingtriptime[index]+1)
        #                     else:
        #                         occupancystatus[index] =0
        #                         remainingtriptime[index] =0
        #                         location[index] = pair[j][0]
        #                     updatestatus[index] =1
        #                     cnum -=1

        for i in range(len(energystatus)):
            if chargingstatus[i]==3:
                if onroadtime[i]<20:
                    chargingstatus[i]=1

        for i in range(len(energystatus)):
            if occupancystatus[i]==1 and updatestatus[i]==0:
                energystatus[i] -=L1
                updatestatus[i] =1
                if remainingtriptime[i]>1:
                    location[i] = get_middle_region(location[index],destination[index],remainingtriptime[index]+1)
                    remainingtriptime[i] -=1
                else:
                    occupancystatus[i]=0
                    remainingtriptime[i] =0
                    location[i]= destination[i]
                    csupply[location[i]] +=1


        for i in range(len(energystatus)):
            if updatestatus[i]==0 and energystatus[i]<=2 and chargingstatus[i]==0:
                costcharging = 4
                remainingchargingtime[i]=costcharging
                chargingdemand=[]
                for j in range(n):
                    chargingdemand.append(0)
                for j in range(len(energystatus)):
                    if chargingstatus[j]==1 or chargingstatus[j]==2 or chargingstatus[j]==3:
                        chargingdemand[chargingstation[j]] += remainingchargingtime[j]
                for j in range(n):
                    chargingdemand[j] =chargingdemand[j]/float(p[j])

                cmin = min(chargingdemand)
                cloc =0
                if cmin>1:
                    for j in range(n):
                        if chargingdemand[j]==cmin:
                            cloc =j
                else:
                    near = 1000
                    for j in range(n):
                        if chargingdemand[j]<1:
                            if distance[location[i]][j] < near:
                                cloc =j
                                near = distance[location[i]][j]
                dispatchedtime[i] =time
                chargingstation[i] = cloc
                travelingtime = distance[location[i]][cloc]
                idledrivingtime[i] += 60.0*travelingtime/40.0
                if travelingtime*60.0/40.0<20:
                    chargingstatus[i] = 1
                    onroadtime[i] = 0
                else:
                    chargingstatus[i]=3
                    onroadtime[i] = travelingtime*60.0/40.0
                updatestatus[i] =1


        for i in range(n):
            pair=[]
            for j in range(n):
                pair.append([j,cdemand[i][j]])
            pair = sorted(pair,key= lambda  x:x[1],reverse=True)
            for j in range(n):
                cnum = pair[j][1]
                cdistance = distance[i][pair[j][0]]
                costtime = int((60.0*cdistance/40.0)/20)+1
                for index in range(len(energystatus)):
                    if cnum>0:
                        if energystatus[index]+1>costtime and location[index]==i and occupancystatus[index]==0 and chargingstatus[index]==0 and updatestatus[index]==0 and energystatus[index]>5:
                            energystatus[index] -=L1
                            if energystatus[index]<0:
                                print 'Error---!!'
                                return
                            chargingstatus[index]=0
                            csupply[location[index]] += 1
                            if costtime>1:
                                occupancystatus[index] =1
                                remainingtriptime[index] = costtime-1
                                destination[index] = pair[j][0]
                                location[index] = get_middle_region(location[index],destination[index],remainingtriptime[index]+1)
                            else:
                                occupancystatus[index] =0
                                remainingtriptime[index] =0
                                location[index] = pair[j][0]
                                # csupply[location[i]]+= (1-((60.0*cdistance/20.0)/20))
                            updatestatus[index] =1
                            cnum -=1


        for i in range(len(energystatus)):
            if updatestatus[i]==0 and energystatus[i]>2 and chargingstatus[i]==0:
                # pick up passengers
                csupply[location[i]]+=1
                energystatus[i] -= L1
                fopen1 =open('./transition/slot20/'+str(time)+'pv','r')
                transition = []
                for k in fopen1:
                    k=k.strip('\n')
                    k=k.split(',')
                    one=[]
                    for line in k:
                        one.append(float(line))
                    transition.append(one)
                fopen1 =open('./transition/slot20/'+str(time)+'qv','r')
                transition1 = []
                for k in fopen1:
                    k=k.strip('\n')
                    k=k.split(',')
                    one=[]
                    for line in k:
                        one.append(float(line))
                    transition1.append(one)
                fopen1 =open('./transition/slot20/'+str(time)+'po','r')
                transition2 = []
                for k in fopen1:
                    k=k.strip('\n')
                    k=k.split(',')
                    one=[]
                    for line in k:
                        one.append(float(line))
                    transition2.append(one)
                fopen1 =open('./transition/slot20/'+str(time)+'qo','r')
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
                    # possible.append(int(transition[loc][j]*1000+transition1[loc][j]*1000+transition2[loc][j]*1000+transition3[loc][j]*1000))
                mylist=[]
                for j in range(n):
                    for c in range(possible[j]):
                        mylist.append(j)
                if len(mylist)==0:
                    location[i] = location[i]
                else:
                    cc = random.choice(mylist)
                    # while cc==location[i]:
                    #     cc =random.choice(mylist)
                    # if cc ==location[i]:
                    #     samenum+=1
                    location[i] = cc
                    #location[i] =random.choice(mylist)

                updatestatus[i]=1

        for i in range(len(p)):
            stationid =i
            connectingvehicle=0
            for j in range(len(energystatus)):
                if chargingstatus[j]==2 and chargingstation[j]==stationid:
                    connectingvehicle+=1
            freepoints = p[i] - connectingvehicle
            waitinginfo =[]
            for j in range(len(energystatus)):
                if chargingstation[j] == stationid and (chargingstatus[j]==1):
                    info =[j, dispatchedtime[j],remainingchargingtime[j]]
                    waitinginfo.append(info)
            waitinginfo=sorted(waitinginfo,key=lambda x:(x[1],x[2]))
            for record in waitinginfo:
                if freepoints>0:
                    id1 =record[0]
                    chargingstatus[id1]= 2
                    # remainingchargingtime[id1] -= 1
                    updatestatus[id1]=1
                    freepoints-=1
                else:
                    id1= record[0]
                    idledrivingtime[id1]+=20.0

                    chargingstatus[id1]= 1
                    updatestatus[id1]=1

        for i in range(len(energystatus)):
            if chargingstatus[i]==2:
                idledrivingtime[i]+=20
                if remainingchargingtime[i]<=1:
                    remainingchargingtime[i]=0
                    chargingstatus[i]=0
                    location[i] = chargingstation[i]
                    energystatus[i]+=L2
                else:
                    remainingchargingtime[i] -=1
                    location[i] =chargingstation[i]
                    energystatus[i]+=L2
            elif chargingstatus[i]==3:
                onroadtime[i] -=20

        one=[]
        for i in range(n):
            ccsupply = csupply[i]
            ccdemand = sum(cdemand[i][j] for j in range(n))
            if ccdemand!=0:
                one.append(max(0,1-ccsupply/ccdemand))
            else:
                one.append(0)
        regionratio.append(one)
        a1= sum(csupply)
        a2= sum(cdemand[i][j] for i in range(n) for j in range(n))

        if a2!=0:
            a3=max(0,1-float(a1)/a2)
        else:
            a3=0
        supplydemand.append([sum(csupply),sum(cdemand[i][j] for i in range(n) for j in range(n)),a3])





    fwrite2 =open('./resultdata/rec/temporalsupplydemand','w')
    for k in supplydemand:
        fwrite2.write(str(k[0])+','+str(k[1])+','+str(k[2])+'\n')
    fwrite2.close()

    fwrite2 =open('./resultdata/rec/regionratio','w')
    for k in regionratio:
        for c in k:
            fwrite2.write(str(c)+',')
        fwrite2.write('\n')
    fwrite2.close()

    fwrite2 =open('./resultdata/rec/utilization','w')
    for i in range(len(energystatus)):
        fwrite2.write(str(1-(idledrivingtime[i])/(60.0*18))+'\n')
    fwrite2.close()



def start_end_gps(data):
    start=0
    end =0
    for i in range(len(data)-3):
        line1 = data[i].strip('\n')
        line2 = data[i+1].strip('\n')
        line3 = data[i+2].strip('\n')
        line1 = line1.split(',')
        line2 = line2.split(',')
        line3 = line3.split(',')
        if (line1[2]!=line2[2] and line1[2]!=line3[2] and line2[2]!=line3[2]) or (line1[1]!=line2[1] and line1[1]!=line3[1] and line2[1]!=line3[1]):
            starttime = float(line1[3])
            # starttime = starttime.split('.')
            # starttime = starttime[0]
            # ctime = datetime.strptime(starttime, '%Y-%m-%dT%H:%M:%S')
            # start = (ctime.hour*60+ctime.minute)
            start = starttime
            break

    for i in range(len(data)-1,2,-1):
        line1 = data[i].strip('\n')
        line2 = data[i-1].strip('\n')
        line3 = data[i-2].strip('\n')
        line1 = line1.split(',')
        line2 = line2.split(',')
        line3 = line3.split(',')
        if (line1[2]!=line2[2] and line1[2]!=line3[2] and line2[2]!=line3[2]) or (line1[1]!=line2[1] and line1[1]!=line3[1] and line2[1]!=line3[1]):
            starttime = float(line1[3])
            # starttime = starttime.split('.')
            # starttime = starttime[0]
            # ctime1 = datetime.strptime(starttime, '%Y-%m-%dT%H:%M:%S')
            # end = (ctime1.hour*60+ctime1.minute)
            end = starttime
            break
    return start,end

def ground_charging():
    numofcharge=[]
    occutime=[]
    p=[]
    fopen = open('./datadir/chargerindex','r')
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        p.append(float(k[2]))
        occutime.append(0)
    chargingpath ='/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/evcharging/20161215/'
    for root,dirs,files in os.walk(chargingpath):
            for file in files:
                gpspath='/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gpssorted/20161215/'
                if os.path.exists(gpspath+file):
                    fopen = open(gpspath+file,'r')
                    gpsrecord=[]
                    for k in fopen:
                        gpsrecord.append(k)
                    fopen.close()
                    workingstart,workingend = start_end_gps(gpsrecord)
                    fopen = open(chargingpath+file,'r')
                    n=0
                    data=[]
                    for k in fopen:
                        n=n+1

                        k=k.strip('\n')
                        k=k.split(',')
                        data.append(k)
                    for k in data:
                        loc = int(float(k[2]))
                        start = float(k[0])
                        end = float(k[1])
                        if workingend-workingstart!=0 and n<4:
                            occutime[loc] +=(end-start)*4/n
                        else:
                            occutime[loc] +=(end-start)
                    if workingend-workingstart!=0:
                        fwritenew = open('./newprediction/evworkingstartend/'+file,'w')
                        fwritenew.write(str(workingstart)+','+str(workingend)+'\n')
                        fwritenew.close()
                        if workingend-workingstart>18*60:
                            numofcharge.append(int(n))
                        else:
                            numofcharge.append(int(n*60*18/(workingend-workingstart)))

    fwrite3= open('./resultdata/chargenum/ground','w')
    for k in numofcharge:
        fwrite3.write(str(k)+'\n')
    fwrite3.close()

    fwrite3= open('./resultdata/chargeroccupiedtime/ground','w')
    for i in range(len(occutime)):
        k=occutime[i]
        fwrite3.write(str(k)+','+str(p[i])+'\n')
    fwrite3.close()



def soc():
    fopen = open('./resultdata/soc/before','r')
    fopen1 = open('./resultdata/soc/beforenew','w')
    for k in fopen:
        k=k.strip('\n')
        k=float(k)
        k=min(1,(k*15/12))
        fopen1.write(str(k)+'\n')
    fopen1.close()

    fopen = open('./resultdata/soc/after','r')
    fopen1 = open('./resultdata/soc/afternew','w')
    for k in fopen:
        k=k.strip('\n')
        k=float(k)
        k=min(1,(k*15/12))
        fopen1.write(str(k)+'\n')
    fopen1.close()
