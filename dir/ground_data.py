
import os
from datetime import datetime
#import dir.rec

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

def find_location(gpsrecord,ctime):
    for i in range(len(gpsrecord)):
        record = gpsrecord[i]
        if record[2]>=ctime:
            return  gps_to_region([record[0],record[1]])
    return -1

def ground_supply():
    demand={}
    fopen = open('./datadir/chargerindex','r')
    n=0

    for k in fopen:
        n=n+1
    fopen.close()

    for time in range(60*24/20):
        if time>0:
            fopen =open('./historydemand/slot20/groundtruth/'+str(time),'r')
        else:
            fopen =open('./historydemand/slot20/newgroundtruth/'+str(time),'r')
        data=[]
        for line in fopen:
            line =line.strip('\n')
            line =line.split(',')

            one=[]
            for k in line:
                one.append(int(float(k))+1)
            data.append(one)
        for i in range(n):
            for j in range(n):
                demand[time,i,j]= data[i][j]
        fopen.close()

    supply={}
    for time in range(60*24/20):
        for i in range(n):
            supply[time,i]=0
    evpath='./newprediction/startendworking/'
    for root,dirs,files in os.walk(evpath):
            for file in files:
                fopen = open(evpath+file,'r')
                workingstart=0
                workingend=0
                for k in fopen:
                    k=k.strip('\n')
                    k=k.split(',')
                    workingstart= float(k[0])
                    workingend= float(k[1])
                fopen.close()
                chargingpath = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/evcharging/20161213/'+file
                if os.path.exists(chargingpath):
                    charginghistory=[]
                    fopen = open(chargingpath,'r')
                    for k in fopen:
                        k=k.strip('\n')
                        k=k.split(',')
                        charginghistory.append([float(k[0]),float(k[1])])
                    fopen.close()

                    gpspath='/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gps/evgpsvehiclesorted/20161213/'+file
                    if os.path.exists(gpspath):
                        gpsrecord=[]
                        fopen = open(gpspath,'r')
                        for line in fopen:
                            line = line.strip('\n')
                            line = line.split(',')
                            ctime = datetime.strptime(line[4], '%Y-%m-%dT%H:%M:%S.000Z')
                            one =[float(line[2]),float(line[3]),ctime.hour*60+ctime.minute]
                            gpsrecord.append(one)
                        fopen.close()
                        for k in range(18,72):
                            cctime = k*20
                            find1=False
                            find2=False
                            if cctime<=workingend and cctime>=workingstart:
                                find1=True
                            for charging in charginghistory:
                                if cctime <=charging[1] and cctime>=charging[0]:
                                    find2=True
                            if find1==True and find2==False:
                                location1 = find_location(gpsrecord,cctime)
                                if location1!= -1:
                                    supply[k,location1]+=1

    supplydemand=[]
    regionratio=[]
    for k in range(72):
        cratio=0
        for i in range(n):
            kk=0
            cc = sum(demand[k,i,j] for j in range(n))
            if cc==0:
                c1 = max(0,1-((1+float(supply[k,i]))/(cc+1)))

            else:
                c1 = max(0,1-(float(supply[k,i])/cc))
            regionratio.append(c1)
            cratio+=c1
        cratio/=n
        supplydemand.append(cratio)

    regionrationew={}
    for i in range(len(regionratio)):
        x = i/n
        y = i%n
        regionrationew[x,y]= regionratio[i]
    regionratio=[]
    for i in range(n):
        sum1=0
        for j in range(18,72):
            sum1 += regionrationew[j,i]
        sum1 =sum1/54.0
        regionratio.append(sum1)
    regionratio=[]
    for j in range(18,72):
        for i in range(n):
            cc = regionrationew[j,i]
            regionratio.append(cc)
    # fwrite =open('./resultdata/figure1_compare/groundtruthnew','w')
    # for i in range(18):
    #     ck = supplydemand[i*3+18]+supplydemand[i*3+18+1]+supplydemand[i*3+18+2]
    #     ck=ck/3.0
    #     fwrite.write(str(ck)+'\n')
    # fwrite.close()

    fwrite =open('./resultdata/regionratio/regionratiogroundtime','w')
    for k in regionratio:
        fwrite.write(str(k)+'\n')
    fwrite.close()


def evworkingovertime(input):
    evworkingnum=[]
    timeslot= input
    for i in range(60*24/timeslot):
        evworkingnum.append(0)
    datelist=['20161215']
    path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/evdeal/'
    for time in datelist:
        for root,dirs,files in os.walk(path+time+'/'):
            for file in files:
                fopen = open(path+time+'/'+file,'r')
                data=[]
                for k in fopen:
                    data.append(k)

                starttime = stringtotime(data[0])/timeslot
                endtime = stringtotime1(data[len(data)-1])/timeslot
                for i in range(starttime,endtime+1):
                    evworkingnum[i] +=1
    fwrite =open('./newprediction/prediction/prediction/newevworking'+str(timeslot),'w')
    for i in range(len(evworkingnum)):
        if i==len(evworkingnum)-1:
            fwrite.write(str(evworkingnum[i])+'\n')
        else:
            fwrite.write(str(evworkingnum[i])+',')


def minutestringtotime(startline):
    startline = startline.split(',')
    startline = startline[1]
    startline = startline.strip('Z')
    startline = startline.split('.')
    startline = startline[0]
    starttime = datetime.strptime(startline, '%Y-%m-%dT%H:%M:%S')
    return  (starttime.hour*60+starttime.minute)


def stringtotime(startline):
    startline = startline.split(',')
    startline = startline[1]
    startline = startline.strip('Z')
    startline = startline.split('.')
    startline = startline[0]
    starttime = datetime.strptime(startline, '%Y-%m-%dT%H:%M:%S')
    return  (starttime.hour*60+starttime.minute)


def stringtotime1(startline):
    startline = startline.split(',')
    startline = startline[2]
    startline = startline.strip('Z')
    startline = startline.split('.')
    startline = startline[0]
    starttime = datetime.strptime(startline, '%Y-%m-%dT%H:%M:%S')
    return  (starttime.hour*60+starttime.minute)

def minutestringtotime1(startline):
    startline = startline.split(',')
    startline = startline[2]
    startline = startline.strip('Z')
    startline = startline.split('.')
    startline = startline[0]
    starttime = datetime.strptime(startline, '%Y-%m-%dT%H:%M:%S')
    return  (starttime.hour*60+starttime.minute)



def regularworkingovetime(input):
    regularnum=[]
    timeslot=input
    for i in range(60*24/timeslot):
        regularnum.append(0)
    datelist=['20161215']
    path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/transaction/'
    for time in datelist:
        for root,dirs,files in os.walk(path+time+'/'):
            for file in files:
                fopen = open(path+time+'/'+file,'r')

                dealone=[]
                cid=''
                for k in fopen:
                    line =k
                    k=k.split(',')
                    if len(dealone)==0:
                        cid = k[0]
                        dealone.append(line)
                    else:
                        if cid == k[0]:
                            dealone.append(line)
                        else:
                            cwork=[]
                            for i in range(24*60):
                                cwork.append(0)
                            for record in dealone:
                                cstart = minutestringtotime(record)
                                cend = minutestringtotime1(record)
                                for i in range(cstart,cend+1):
                                    cwork[i]=1

                            starttime = stringtotime(dealone[0])/timeslot
                            endtime = stringtotime1(dealone[len(dealone)-1])/timeslot
                            for i in range(starttime,endtime+1):
                                regularnum[i] +=1
                            dealone=[]
                            cid =k[0]
                            dealone.append(line)
                            #return



    fwrite =open('./newprediction/prediction/prediction/workingvehicle'+str(timeslot),'w')
    for i in range(len(regularnum)):
        if i==len(regularnum)-1:
            fwrite.write(str(regularnum[i])+'\n')
        else:
            fwrite.write(str(regularnum[i])+',')

def workingnum():
    evworkingovertime(10)
    regularworkingovetime(10)
    evworkingovertime(30)
    regularworkingovetime(30)
    evworkingovertime(20)
    regularworkingovetime(20)
