#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from datetime import datetime
import os.path
from os import path


def chargerstationdata():
    fopen = open('./datadir/chargerlocation','r')
    fwrite = open('./datadir/chargerindex','w')
    n=0
    for k in fopen:
        n=n+1
        k = k.split(',')
        if k[4]=='1':
            fwrite.write(k[2]+','+k[3]+','+k[5])
    fwrite.close()
    return n


def findgps(file,time,record1,record2):
    data=[]
    path= '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gpssorted/'+time+'/'+file
    fopen = open(path,'r')
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        data.append(k)

    startline = data[0]
    starttime = float(startline[3])
    near1 = starttime
    near2= starttime
    loc1=0
    loc2=0
    for i in range(len(data)):
        cline = data[i]
        ctime = float(cline[3])
        if abs(ctime-record1)<abs(near1-record1):
            loc1= i
            near1 = ctime
        if abs(ctime-record2)<abs(near2-record2):
            loc2= i
            near2 = ctime
    line1 = data[loc1]
    line2 = data[loc2]
    out=[]
    out.append((line1[1]))
    out.append((line1[2]))
    out.append((line2[1]))
    out.append((line2[2]))
    return out




def demand_combine_gps():
    fopen = open('./datadir/chargerindex','r')
    n=0
    stationinfo=[]
    for k in fopen:
        n=n+1
        k =k.split(',')
        one =[]
        one.append(float(k[0]))
        one.append(float(k[1]))
        stationinfo.append(one)

    datelist=['20161213','20161214','20161215','20161216','20161217','20161218']
    path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/transaction/'
    for time in datelist:
        for root,dirs,files in os.walk(path+time+'/'):
            for file in files:
                missnum=0
                fopen = open(path+time+'/'+file,'r')
                fwrite = open('/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/dealwithgps/'+time,'w')
                for k in fopen:
                    k=k.split(',')
                    if os.path.exists('/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gpssorted/'+time+'/'+k[0]):
                        record1 = datetime.strptime(k[1], '%Y-%m-%dT%H:%M:%S.000Z')
                        record2 = datetime.strptime(k[2],'%Y-%m-%dT%H:%M:%S.000Z')
                        record1 = record1.hour*60+record1.minute
                        record2 = record2.hour*60+record2.minute
                        gpsrecord= findgps(k[0],time,record1,record2)
                        newrecord = k[0]+','+k[1]+','+gpsrecord[0]+','+gpsrecord[1]+','+k[2]+','+gpsrecord[2]+','+gpsrecord[3]+'\n'
                        fwrite.write(newrecord)
                    else:
                        missnum+=1
                # print missnum
                fwrite.close()
        #         break
        #     break
        # break

def evdemand_combine_gps():
    fopen = open('./datadir/chargerindex','r')
    n=0
    stationinfo=[]
    for k in fopen:
        n=n+1
        k =k.split(',')
        one =[]
        one.append(float(k[0]))
        one.append(float(k[1]))
        stationinfo.append(one)

    datelist=['20161213']
    path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/transaction/'
    for time in datelist:
        for root,dirs,files in os.walk(path+time+'/'):
            for file in files:
                missnum=0
                fopen = open(path+time+'/'+file,'r')
                fwrite = open('/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/dealwithgps/evdemandwithoutregion/'+time,'w')
                for k in fopen:
                    k=k.strip('\n')
                    k=k.split(',')
                    if k[5]=='蓝的':
                        if os.path.exists('/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gpssorted/'+time+'/'+k[0]):
                            record1 = datetime.strptime(k[1], '%Y-%m-%dT%H:%M:%S.000Z')
                            record2 = datetime.strptime(k[2],'%Y-%m-%dT%H:%M:%S.000Z')
                            record1 = record1.hour*60+record1.minute
                            record2 = record2.hour*60+record2.minute
                            gpsrecord= findgps(k[0],time,record1,record2)
                            newrecord = k[0]+','+k[1]+','+gpsrecord[0]+','+gpsrecord[1]+','+k[2]+','+gpsrecord[2]+','+gpsrecord[3]+'\n'
                            fwrite.write(newrecord)
                        else:
                            missnum+=1
                print missnum
                fwrite.close()


def gpsdataunsorted():
    datelist=['20161213','20161214','20161215','20161216','20161217','20161218']
    path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gps/'
    for time in datelist:
        for root,dirs,files in os.walk(path+time+'/'):
            for file in files:
                fopen = open(path+time+'/'+file,'r')
                for k in fopen:
                    line =k
                    k=k.split(',')
                    writepath = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gpsunsorted/'+time+'/'+k[0]
                    fwrite = open(writepath,'a')
                    fwrite.write(line)
                    fwrite.close()
#粤BX8R35,红的,114.0448,22.540899,2016-12-13T16:49:51.000Z,0
def gpsdatasorted():
    datelist=['20161213','20161214','20161215','20161216','20161217','20161218']
    path= '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gpsunsorted/'
    for time in datelist:
        for root,dirs,files in os.walk(path+time+'/'):
            for file in files:
                fopen = open(path+time+'/'+file,'r')
                gpsdata=[]
                for k in fopen:
                    k=k.split(',')
                    one=[]
                    one.append(k[0])
                    one.append(k[2])
                    one.append(k[3])
                    ctime = k[4]
                    ctime=ctime.split('.')
                    ctime = ctime[0]
                    ctime = datetime.strptime(ctime, '%Y-%m-%dT%H:%M:%S')
                    ctime = ctime.hour*60+ctime.minute
                    one.append(ctime)
                    gpsdata.append(one)


                newgpsdata=sorted(gpsdata,key=lambda x: x[3])
                fwrite= open('/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gpssorted/'+time+'/'+file,'w')
                for i in range(len(newgpsdata)):
                    line = newgpsdata[i]
                    fwrite.write(line[0]+','+line[1]+','+line[2]+','+str(line[3])+'\n')
                fwrite.close()


def gpstoregion(charger,record):
    # 2 3 5 6
    record = record.strip('\n')
    line = record
    record=record.split(',')
    x1=float(record[2])
    y1=float(record[3])
    x2=float(record[5])
    y2=float(record[6])
    dist1=100
    loc1=-1
    dist2=100
    loc2=-1
    for i in range(len(charger)):
        gps=charger[i]
        if abs(gps[0]-x1)**2+abs(gps[1]-y1)**2<dist1:
            dist1=abs(gps[0]-x1)**2+abs(gps[1]-y1)**2
            loc1=i
        if abs(gps[0]-x2)**2+abs(gps[1]-y2)**2<dist2:
            dist2=abs(gps[0]-x2)**2+abs(gps[1]-y2)**2
            loc2=i
    if loc1==-1 or loc2==-1:
        return ''
    else:
        return record[0]+','+record[1]+','+record[2]+','+record[3]+','+str(loc1)+','+record[4]+','+record[5]+','+record[6]+','+str(loc2)+'\n'

def demandwithregion():
    fopen= open('./datadir/chargerindex','r')
    charger=[]
    for k in fopen:
        k=k.split(',')
        one =[float(k[0]),float(k[1])]
        charger.append(one)
    fopen.close()
    path ='/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/dealwithgps/demandwithoutregion/'
    for root,dirs,files in os.walk(path):
        for file in files:
            fopen = open(path+file,'r')
            fwrite = open('/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/dealwithgps/demandwithregion/'+file,'w')
            for k in fopen:
                line = gpstoregion(charger,k)
                if line !='':
                    fwrite.write(line)
            fwrite.close()

def evdemandwithregion():
    fopen= open('./datadir/chargerindex','r')
    charger=[]
    for k in fopen:
        k=k.split(',')
        one =[float(k[0]),float(k[1])]
        charger.append(one)
    fopen.close()
    path ='/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/dealwithgps/evdemandwithoutregion/'
    for root,dirs,files in os.walk(path):
        for file in files:
            fopen = open(path+file,'r')
            fwrite = open('/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/dealwithgps/evdemandwithregion/'+file,'w')
            for k in fopen:
                line = gpstoregion(charger,k)
                if line !='':
                    fwrite.write(line)
            fwrite.close()

def demand_timeslot_region_to_region():
    timeslot=20
    totallength = 60*24
    fopen = open('./datadir/chargerindex','r')
    n=0

    for k in fopen:
        n=n+1


    datelist=['20161213','20161214','20161215','20161216','20161217','20161218']
    path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/dealwithgps/demandwithregion/'
    for date in datelist:
        demand={}
        for k in range(totallength/timeslot):
            for i in range(n):
                for j in range(n):
                    demand[k,i,j] =0
        fopen = open(path+date,'r')
        writepath = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/demand/slot'+str(timeslot)+'/'+date+'/'
        for k in fopen:
            k=k.split(',')
            i = int(float(k[4]))
            j = int(float(k[8]))
            ctime = datetime.strptime(k[1], '%Y-%m-%dT%H:%M:%S.000Z')
            ctime =ctime.hour*60+ctime.minute
            loc = int(ctime/timeslot)
            # if i==-1 or j==-1:
            #     print date,k[0]
            demand[loc,i,j] = demand[loc,i,j]+1
        for k in range(totallength/timeslot):
            fwrite = open(writepath+str(k),'w')
            for i in range(n):
                for j in range(n):
                    if j==(n-1):
                        fwrite.write(str(demand[k,i,j])+'\n')
                    else:
                        fwrite.write(str(demand[k,i,j])+',')
            fwrite.close()


def evdemand_timeslot_region_to_region():
    timeslot=20
    totallength = 60*24
    fopen = open('./datadir/chargerindex','r')
    n=0

    for k in fopen:
        n=n+1
    demand={}
    for k in range(totallength/timeslot):
        for i in range(n):
            for j in range(n):
                demand[k,i,j] =0

    datelist=['20161213']
    path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/dealwithgps/evdemandwithregion/'
    for date in datelist:
        fopen = open(path+date,'r')
        writepath = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/evdemand/slot'+str(timeslot)+'/'+date+'/'
        for k in fopen:
            k=k.split(',')
            i = int(float(k[4]))
            j = int(float(k[8]))
            ctime = datetime.strptime(k[1], '%Y-%m-%dT%H:%M:%S.000Z')
            ctime =ctime.hour*60+ctime.minute
            loc = int(ctime/timeslot)
            # if i==-1 or j==-1:
            #     print date,k[0]
            demand[loc,i,j] = demand[loc,i,j]+1
        for k in range(totallength/timeslot):
            fwrite = open(writepath+str(k),'w')
            for i in range(n):
                for j in range(n):
                    if j==(n-1):
                        fwrite.write(str(demand[k,i,j])+'\n')
                    else:
                        fwrite.write(str(demand[k,i,j])+',')
            fwrite.close()


def get_prediction_error():
    datelist=['20161214','20161215']
    timeslot=20
    totallength = 60*24
    fopen = open('./datadir/chargerindex','r')
    n=0

    for k in fopen:
        n=n+1
    demand={}
    for k in range(totallength/timeslot):
        for i in range(n):
            for j in range(n):
                demand[k,i,j] =0

    for date in datelist:
        csum=0
        for k in range(totallength/timeslot):
            path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/demand/slot'+str(timeslot)+'/'+date+'/'+str(k)
            fopen = open(path,'r')
            data=[]
            for c in fopen:
                data.append(c)
            for i in range(len(data)):
                line = data[i]
                line=line.strip('\n')
                line = line.split(',')
                for j in range(len(line)):
                    csum = csum + float(line[j])
                    demand[k,i,j] = demand[k,i,j]+int(float(line[j]))
        # print csum
    ground ={}
    for k in range(totallength/timeslot):
        for i in range(n):
            for j in range(n):
                ground[k,i,j] =0
    for k in range(totallength/timeslot):
        path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/demand/slot'+str(timeslot)+'/20161213'+'/'+str(k)
        fopen = open(path,'r')
        data=[]
        for c in fopen:
            data.append(c)
        for i in range(len(data)):
            line = data[i]
            line=line.strip('\n')
            line = line.split(',')
            for j in range(len(line)):
                ground[k,i,j] = ground[k,i,j]+int(float(line[j]))

    # print sum(demand),sum(ground)
    evground ={}
    for k in range(totallength/timeslot):
        for i in range(n):
            for j in range(n):
                evground[k,i,j] =0
    for k in range(totallength/timeslot):
        path = '/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/evdemand/slot'+str(timeslot)+'/20161213'+'/'+str(k)
        fopen = open(path,'r')
        data=[]
        for c in fopen:
            data.append(c)
        for i in range(len(data)):
            line = data[i]
            line=line.strip('\n')
            line = line.split(',')
            for j in range(len(line)):
                evground[k,i,j] = evground[k,i,j]+int(float(line[j]))


    evworking=[]
    totalworking=[]
    # for i in range(60*24/timeslot):
    #     evworking.append(0)
        # totalworking.append(0)
    fopen =open('./newprediction/prediction/prediction/evworking','r')
    for k in fopen:
        k=k.strip('\n')
        evworking.append(float(k))


    fopen =open('./newprediction/prediction/prediction/regularworking','r')
    for k in fopen:
        k=k.strip('\n')
        totalworking.append(float(k))
        # totalworking[j] = float(k)
        # k=k.split(',')
        # for j in range(len(k)):
        #     totalworking[j]+=float(k[j])
    # print totalworking
    # for k in range(totallength/timeslot):
    #     print sum(sum(demand[k,i,j] for i in range(n)) for j in range(n))/2.0, sum(sum(ground[k,i,j] for i in range(n)) for j in range(n))
    # print sum(sum(sum(ground[k,i,j] for k in range(totallength/timeslot))for i in range(n)) for j in range(n))
    kkk=0
    for k in range(totallength/timeslot):
        fwrite1 = open('./historydemand/slot'+str(timeslot)+'/prediction/'+str(k),'w')
        fwrite2 = open('./historydemand/slot'+str(timeslot)+'/groundtruth/'+str(k),'w')
        cc=0
        for i in range(n):
            for j in range(n):
                alpha=1
                beta= 1 # 0.75
                if j==(n-1):
                    #value1 = 706*(demand[k,i,j]/2.0-evground[k,i,j])/(totalworking[k]-evworking[k])
                    if k>54 and k<72:
                        # value1 =alpha*beta* 706*(demand[k,i,j]/2.0-evground[k,i,j])/(totalworking[k]-evworking[k])
                        # value2 =alpha* beta*706*(ground[k,i,j]-evground[k,i,j])/(totalworking[k]-evworking[k])
                        value1 =alpha*beta* 706*(demand[k,i,j]/2.0)/(totalworking[k])
                        value2 =alpha* beta*706*(ground[k,i,j])/(totalworking[k])
                    else:
                        value1 =alpha* 706*(demand[k,i,j]/2.0)/(totalworking[k])
                        value2 =alpha* 706*(ground[k,i,j])/(totalworking[k])
                    if value1<0:
                        value1 =0

                    if value2<0:
                        value2=0
                    kkk+=value2

                    fwrite1.write(str((value1))+'\n')
                    fwrite2.write(str((value2))+'\n')
                else:
                    # value1 = 706*(demand[k,i,j]/2.0-evground[k,i,j])/(totalworking[k]-evworking[k])
                    if k>63 and k<72:
                        # value1 =alpha*beta* 706*(demand[k,i,j]/2.0-evground[k,i,j])/(totalworking[k]-evworking[k])
                        # value2 =alpha* beta*706*(ground[k,i,j]-evground[k,i,j])/(totalworking[k]-evworking[k])
                        value1 =alpha*beta* 706*(demand[k,i,j]/2.0)/(totalworking[k])
                        value2 =alpha* beta*706*(ground[k,i,j])/(totalworking[k])
                    else:
                        value1 =alpha* 706*(demand[k,i,j]/2.0)/(totalworking[k])
                        value2 =alpha* 706*(ground[k,i,j])/(totalworking[k])
                    if value1<0:
                        value1 =0

                    if value2<0:
                        value2=0
                    kkk+=value2
                    cc+=value2
                    fwrite1.write(str((value1))+',')
                    fwrite2.write(str((value2))+',')
        print cc
    print kkk

def get_driving_distance():
    fopen = open('./datadir/chargerindex','r')

    gps=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        one =[float(k[0]),float(k[1])]
        gps.append(one)
    n= len(gps)
    W={}
    for i in range(n):
        for j in range(n):
            if i!=j:
                gps1 = gps[i]
                gps2= gps[j]
                W[i,j]= abs(gps1[0]-gps2[0])+abs(gps1[1]-gps2[1])
                W[i,j]=1.112*W[i,j]/0.01
            else:
                if i==0:
                    loc=1
                    cloc=1
                else:
                    loc=0
                    cloc=0
                for k in range(n):
                    if k!=i:
                        gps3=gps[k]
                        cgps = gps[loc]
                        center = gps[i]
                        if abs(gps3[0]-center[0])+abs(gps3[1]-center[1])< abs(cgps[0]-center[0])+abs(cgps[1]-center[1]):
                            loc = k

                for k in range(n):
                    if k!=i and k!=loc:
                        gps3=gps[k]
                        cgps = gps[cloc]
                        center = gps[i]
                        if abs(gps3[0]-center[0])+abs(gps3[1]-center[1])< abs(cgps[0]-center[0])+abs(cgps[1]-center[1]):
                            cloc = k
                gps1=gps[i]
                gps2=gps[cloc]
                W[i,j]=(abs(gps1[0]-gps2[0])+abs(gps1[1]-gps2[1]))
                W[i,j]=(1.112*W[i,j]/0.01)/2
    fwrite = open('datadir/distance','w')
    for i  in range(n):
        for j in range(n):
            if j==(n-1):
                fwrite.write(str(W[i,j])+'\n')
            else:
                fwrite.write(str(W[i,j])+',')
    fwrite.close()

#/home/yuan/Dropbox/CPS/EV/evaluation/datadir/distance
def get_reachable_matric():
    timeslot =20
    threshold = timeslot*40.0/60
    fopen = open('/home/yuan/Dropbox/CPS/EV/evaluation/datadir/distance','r')
    data =[]
    for k in fopen:
        k =k.strip('\n')
        k = k.split(',')
        data.append(k)
    C={}
    n = len(data)
    for i in range(n):
        for j in range(n):
            if float(data[i][j])<=threshold:
                C[i,j]=1
            else:
                C[i,j]=0
    fwrite =open('datadir/reachable','w')
    for i in range(n):
        for j in range(n):
            if j==(n-1):
                fwrite.write(str(C[i,j])+'\n')
            else:
                fwrite.write(str(C[i,j])+',')
    fwrite.close()

def call_transition(info,trajectoryinfo,n,K,timeslot,charger):
    cpv={}
    cpo={}
    cqv={}
    cqo={}
    for i in range(n):
        for j in range(n):
            for k in range(K):
                cpv[i,j,k]=0
                cpo[i,j,k]=0
                cqv[i,j,k]=0
                cqo[i,j,k]=0
    transaction=[]
    for line in info:
        time1 = line[1]
        time2 = line[5]
        ctime1 = datetime.strptime(time1, '%Y-%m-%dT%H:%M:%S.000Z')
        ctime2 = datetime.strptime(time2, '%Y-%m-%dT%H:%M:%S.000Z')
        one=[ctime1.hour*60+ctime1.minute,ctime2.hour*60+ctime2.minute]
        transaction.append(one)
    movingstart=0
    movingend=0
    for i in range(len(trajectoryinfo)-2):
        line1= trajectoryinfo[i]
        line2=trajectoryinfo[i+1]
        line3= trajectoryinfo[i+2]
        if (line1[1]!=line2[1] and line1[1]!=line3[1] and line2[1]!=line3[1]) or (line1[2]!=line2[2] and line1[2]!=line3[2] and line2[2]!=line3[2]):
            ctime = line1[3]
            movingstart=float(ctime)
            break

    for i in range(len(trajectoryinfo)-1,1,-1):
        line1= trajectoryinfo[i]
        line2=trajectoryinfo[i-1]
        line3= trajectoryinfo[i-2]
        if (line1[1]!=line2[1] and line1[1]!=line3[1] and line2[1]!=line3[1]) or (line1[2]!=line2[2] and line1[2]!=line3[2] and line2[2]!=line3[2]):
            ctime = line1[3]
            movingend=float(ctime)
            break



    for index in range(K-1):
        starttime = index*timeslot
        endtime = (index+1)*timeslot
        if starttime>=movingstart and endtime<=movingend:
            startgps=[]
            endgps=[]
            for line in trajectoryinfo:
                ctime =float(line[3])
                if ctime>=starttime:
                    startgps=[float(line[1]),float(line[2])]
                    break
            for line in trajectoryinfo:
                ctime =float(line[3])
                if ctime>=endtime:
                    endgps=[float(line[1]),float(line[2])]
                    break
            startoccupied=0
            endoccupied=0
            for line in transaction:
                if starttime>=line[0] and starttime<=line[1]:
                    startoccupied=1
                if endtime>=line[0] and endtime<=line[1]:
                    endoccupied=1
            startregion=0
            endregion =0
            for i in range(n):
                if abs(charger[i][0]-startgps[0])+abs(charger[i][1]-startgps[1])< \
                    abs(charger[startregion][0]-startgps[0]) +abs(charger[startregion][1]-startgps[1]):
                    startregion =i
                if abs(charger[i][0]-endgps[0])+abs(charger[i][1]-endgps[1])< \
                    abs(charger[endregion][0]-endgps[0]) +abs(charger[endregion][1]-endgps[1]):
                    endregion =i
            if startoccupied and endoccupied:
                cqo[startregion,endregion,index] +=1
            elif startoccupied==0 and endoccupied==0:
                cpv[startregion,endregion,index] +=1

            elif startoccupied==1 and endoccupied==0:
                cqv[startregion,endregion,index] +=1

            elif startoccupied==0 and endoccupied==1:
                cpo[startregion,endregion,index] +=1
    return cpv,cpo,cqv,cqo



def get_region_transition():
    totallength = 60*24
    timeslot =20
    fopen = open('./datadir/chargerindex','r')
    n=0
    charger=[]
    for k in fopen:
        k=k.split(',')
        one =[float(k[0]),float(k[1])]
        charger.append(one)
        n=n+1
    fopen.close()
    K= totallength/timeslot
    pv={}
    po={}
    qv={}
    qo={}
    for i in range(n):
        for j in range(n):
            for k in range(K):
                pv[i,j,k]=0
                po[i,j,k]=0
                qv[i,j,k]=0
                qo[i,j,k]=0
    datelist=['20161213','20161214']
    for date in datelist:
        path ='/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/dealwithgps/demandwithregion/'+date
        fopen = open(path,'r')
        info=[]
        id =''
        for line in fopen:
            line = line.strip('\n')
            line = line.split(',')
            if line[0]!=id:
                if id=='':
                    id=line[0]
                    info.append(line)
                else:
                    #call function
                    print id
                    gpspath ='/media/yuan/696d9c4b-3e39-41a3-ab8b-178a0c2f1195/taxiData/gpssorted/'+date+'/'+id
                    cfopen =open(gpspath,'r')
                    tranjectoryinfo=[]
                    for cline in cfopen:
                        cline = cline.strip('\n')
                        cline =cline.split(',')
                        tranjectoryinfo.append(cline)
                    cpv,cpo,cqv,cqo = call_transition(info,tranjectoryinfo,n,K,timeslot,charger)
                    for i in range(n):
                        for j in range(n):
                            for k in range(K):
                                pv[i,j,k]= pv[i,j,k]+cpv[i,j,k]
                                po[i,j,k]= po[i,j,k]+cpo[i,j,k]
                                qv[i,j,k]= qv[i,j,k]+cqv[i,j,k]
                                qo[i,j,k]= qo[i,j,k]+cqo[i,j,k]
                    id=line[0]
                    info=[]
                    info.append(line)
            else:
                info.append(line)

    for i in range(n):
        for k in range(K):
            sum1=0
            sum2=0
            for j in range(n):
                sum1 = sum1+ pv[i,j,k] + po[i,j,k]
                sum2 = sum2+ qv[i,j,k] + qo[i,j,k]
            for j in range(n):
                pv[i,j,k] =float(pv[i,j,k])/(1+sum1)
                po[i,j,k] =float(po[i,j,k])/(1+sum1)
                qv[i,j,k] =float(qv[i,j,k])/(1+sum2)
                qo[i,j,k] =float(qo[i,j,k])/(1+sum2)
    for k in range(K):
        fwrite1= open('./transition/slot'+str(timeslot)+'/'+str(k)+'pv','w')
        fwrite2= open('./transition/slot'+str(timeslot)+'/'+str(k)+'po','w')
        fwrite3= open('./transition/slot'+str(timeslot)+'/'+str(k)+'qv','w')
        fwrite4= open('./transition/slot'+str(timeslot)+'/'+str(k)+'qo','w')
        for i in range(n):
            for j in range(n):
                if j==n-1:
                    fwrite1.write(str(pv[i,j,k])+'\n')
                    fwrite2.write(str(po[i,j,k])+'\n')
                    fwrite3.write(str(qv[i,j,k])+'\n')
                    fwrite4.write(str(qo[i,j,k])+'\n')
                else:
                    fwrite1.write(str(pv[i,j,k])+',')
                    fwrite2.write(str(po[i,j,k])+',')
                    fwrite3.write(str(qv[i,j,k])+',')
                    fwrite4.write(str(qo[i,j,k])+',')
        fwrite1.close()
        fwrite2.close()
        fwrite3.close()
        fwrite4.close()



def get_ground_prediction():

    n=0 # number of regions
    fopen =  open('./datadir/chargerindex','r')
    for k in fopen:
        n=n+1

    inputdemand =[]
    ground=[]
    for i in range(n):
        one=[]
        for j in range(72):
            one.append(0)
        inputdemand.append(one)
    for i in range(n):
        one=[]
        for j in range(72):
            one.append(0)
        ground.append(one)

    for k in range(72):

        fopen = open('./historydemand/slot20/prediction/'+str(k),'r')
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
        for k in range(72):
            demand[i,k] = inputdemand[i][k]

    for k in range(72):

        fopen = open('./historydemand/slot20/groundtruth/'+str(k),'r')
        loc =0
        for line in fopen:
            line =line.strip('\n')
            line = line.split(',')
            valuesum =0
            for value in line:
                valuesum = valuesum + float(value)
            ground[loc][k]= valuesum
            loc = loc+1
    ccground={}
    for i in range(n):
        for k in range(72):
            ccground[i,k] = ground[i][k]

    fwrite1 = open('./resultdata/predictionerror/error','w')
    fwrite2 = open('./resultdata/predictionerror/errorratio','w')
    cerror=[]
    cerrorratio=[]
    for i in range(n):
        for k in range(72):
            error = abs(demand[i,k]-ccground[i,k])
            if ccground[i,k]==0:
                errorratio= 0
            else:
                errorratio = error/ccground[i,k]
            cerror.append(error)
            cerrorratio.append(errorratio)
    for i in range(len(cerror)):
        fwrite1.write(str(cerror[i])+'\n')
        fwrite2.write(str(cerrorratio[i])+'\n')
    fwrite1.close()
    fwrite2.close()

