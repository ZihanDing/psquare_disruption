import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math
import numpy as np


font1 = {'family' : 'serif',
        'weight' : 'bold',
        'size'   : 25,
        }


def plotsupplydemand():


    fopen =open('./resultdata/betacompare/newslot20timehorizon12beta01','r')
    fopen1 = open('/home/yuan/Dropbox/CPS/EV/project_code/ev-data/supplydemandprediction','w')
    cratio=[]
    for k in fopen:
        fopen1.write(k)
        k=k.strip('\n')
        k=k.split(',')
        cratio.append(float(k[2]))
    ncratio=[]
    fopen1.close()
    for i in range(len(cratio)/3):
        ncratio.append((cratio[i*3]+cratio[i*3+1]+cratio[i*3+2])/3)
    newratio=[]

    groundcurve=[]
    # fopen2 =open('./resultdata/betacompare/slot20timehorizon8beta1','r')
    fopen2 =open('./supplydemand','r')

    for line in fopen2:
        line=line.strip('\n')
        line = line.split(',')
        groundcurve.append(float(line[2]))
    xx=[]
    for i in range(18):
        xx.append(i+6)
        newratio.append((groundcurve[i*3]+groundcurve[i*3+1]+groundcurve[i*3+2])/3)

    plt.figure(1)
    plt.plot(xx[1:18],ncratio[1:18],'-sk',label='beta 0')
    plt.plot(xx[1:18],newratio[1:18],'-b^',label='ground')
    plt.legend()
    plt.xlim(6,24)


    # plt.figure(2)


    # fopen =open('./resultdata/betacomparedistance/distanceslot20timehorizon8beta01','r')
    # cratio=[]
    # for k in fopen:
    #     #fopen1.write(k)
    #     k=k.strip('\n')
    #
    #     cratio.append(float(k))
    # ncratio=[]
    # for i in range(len(cratio)/3):
    #     ncratio.append((cratio[i*3]+cratio[i*3+1]+cratio[i*3+2])/3)
    #
    #
    # groundcurve=[]
    # fopen2 =open('./resultdata/betacomparedistance/distanceslot20timehorizon8beta1','r')
    # for line in fopen2:
    #     line=line.strip('\n')
    #     groundcurve.append(float(line))
    #
    # xx=[]
    # newratio=[]
    # for i in range(18):
    #     xx.append(i+6)
    #     newratio.append((groundcurve[i*3]+groundcurve[i*3+1]+groundcurve[i*3+2])/3)
    #
    # plt.figure(1)
    # plt.plot(xx[1:18],ncratio[1:18],'-sk',label='beta 0.1')
    # plt.plot(xx[1:18],newratio[1:18],'-b^',label='beta 1')
    # plt.legend()
    # plt.xlim(6,24)

    plt.show()


def threetoone(data):
    out=[]
    for i in range(len(data)/3):
        cc = (data[3*i]+data[3*i+1]+data[3*i+2])/3.0
        out.append(cc)
    return out

def sixtoone(data):
    out=[]
    for i in range(len(data)/6):
        cc = (data[6*i]+data[6*i+1]+data[6*i+2]+data[6*i+3]+data[6*i+4]+data[6*i+5])/6.0
        out.append(cc)
    return out

def three_compare():
    fopen= open('./resultdata/figure1_compare/groundtruth')
    ground=[]
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k= float(k)
        r.append(k)
    ground= threetoone(r)
    fopen.close()

    fopen= open('./resultdata/figure1_compare/rec')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        c1 = float(k[0])
        c2 = float(k[1])
        k= float(k[2])
        r.append(c1/c2)
    rec= sixtoone(r)
    fopen.close()

    fopen= open('./resultdata/timehorizon/newslot20beta00_3horizon6')
    # fopen= open('./resultdata/figure1_compare/slot20timehorizon12beta01')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        c1 = float(k[0])
        c2 = float(k[1])
        k= float(k[2])
        r.append(c1/c2)
        # r.append(k)
    p2charging= threetoone(r)
    fopen.close()

    x=[]
    for i in range(18):
        x.append(i+6)


    for i in range(len(ground)):
        ground[i] = max(0,1-ground[i])
    for i in range(len(rec)):
        rec[i] = max(0,1-rec[i])
    for i in range(len(p2charging)):
        p2charging[i] = max(0,1-p2charging[i])

    plt.plot(x[0:18],ground[6:24],'-C0^',linewidth=2.5,markersize=8,label='Ground')
    plt.plot(x[0:18],rec[0:18],'-.C1s',linewidth=2.5,markersize=8,label='REC')
    plt.plot(x[0:18],p2charging[0:18],'-C3o',linewidth=2.5,markersize=8,label=r'$p^2Charging$')
    plt.xlabel('Time of day (hour)',fontdict=font1)
    plt.ylabel('Ratio of unserved\n passengers',fontdict=font1,color='k')

    #ax2.plot(x[21:72],rationew[21:72],'-ro',linewidth=2.5,markersize=8,label='ratio of charging vehicles')

    plt.tick_params('y', colors='k',direction='in')
    plt.tick_params(axis='x', colors='k',direction='in')
    plt.xlim([5, 24])
    plt.ylim([-0.05,0.6])
    plt.legend(loc=[0.0,0.75],fontsize=18,ncol=2)
    #ax1.tick_params('x',xlim=[5.24])
    #plt.xlabel('Time of day (hour)',fontdict=font1)

    #plt.plot(x[21:72],y1[21:72])

    #plt.ylim(0,2)
    #ax = plt.axes()
    # plt.xaxis.grid( linestyle=':', linewidth=1.5,color='k')
    # #ax2.grid( linestyle=':', linewidth=1.5,color='r')
    plt.tick_params(direction='in', length=6, width=2,labelsize=20)
    ax = plt.axes()
    ax.grid( linestyle=':', linewidth=1.5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    plt.tight_layout()
    plt.show()


def three_comparedistance():
    fopen= open('./resultdata/distance/ground')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        #k= float(k)
        r.append([float(k[0]),float(k[1])])
    #rec= sixtoone(r)
    ground=[]
    for i in range(len(r)/3):
        totaldistance=0
        totalnum=0
        for j in range(3):
            totaldistance+=r[3*i+j][0]
            totalnum+=r[3*i+j][1]
        ground.append(totaldistance/totalnum)
    ground[8]=3
    fopen= open('./resultdata/recresult/distance')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        #k= float(k)
        r.append([float(k[0]),float(k[1])])
    #rec= sixtoone(r)
    rec=[]
    for i in range(len(r)/6):
        totaldistance=0
        totalnum=0
        for j in range(6):
            totaldistance+=r[6*i+j][0]
            totalnum+=r[6*i+j][1]

        if totalnum!=0:
            rec.append(totaldistance/totalnum)
        else:
            rec.append(totaldistance/(totalnum+1))
        # if rec[len(rec)-1]<1:
        #     rec[len(rec)-1]=2.5

    fopen.close()

    # fopen= open('./resultdata/betacomparedistance/newdistanceslot20timehorizon12beta01_3')
    # fopen = open('./resultdata/timehorizon/newdistanceslot20beta00_3horizon8')
    fopen= open('./resultdata/timehorizon/newdistanceslot20beta00_3horizon6','r')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        #k= float(k)
        r.append([float(k[0]),float(k[1])])
    #rec= sixtoone(r)
    p2charging=[]
    for i in range(len(r)/3):
        totaldistance=0
        totalnum=0
        for j in range(3):
            totaldistance+=r[3*i+j][0]
            totalnum+=r[3*i+j][1]
        if totalnum>1:
            p2charging.append((totaldistance/totalnum))
        else:
            p2charging.append(0)

    x=[]
    for i in range(18):
        x.append(i+6)
    # ground[0]=1.2
    # rec[0]=1.2
    # p2charging[0]=1.2
    plt.plot(x[0:18],ground[6:24],'-C0^',linewidth=2.5,markersize=8,label='Ground')
    plt.plot(x[0:18],rec[0:18],'-.C1s',linewidth=2.5,markersize=8,label='REC')
    plt.plot(x[0:18],p2charging[0:18],'-C3o',linewidth=2.5,markersize=8,label=r'$p^2Charging$')
    plt.xlabel('Time of day (hour)',fontdict=font1)
    plt.ylabel('Average driving distance\nto charging station (km)',fontdict=font1,color='k')

    #ax2.plot(x[21:72],rationew[21:72],'-ro',linewidth=2.5,markersize=8,label='ratio of charging vehicles')

    plt.tick_params('y', colors='k',direction='in')
    plt.tick_params(axis='x', colors='k',direction='in')
    plt.xlim([5, 24])
    #plt.ylim([0.45,1.4])
    plt.legend(loc=[0.0,1.0],fontsize=15,ncol=3)
    #ax1.tick_params('x',xlim=[5.24])
    #plt.xlabel('Time of day (hour)',fontdict=font1)

    #plt.plot(x[21:72],y1[21:72])

    #plt.ylim(0,12)
    #ax = plt.axes()
    # plt.xaxis.grid( linestyle=':', linewidth=1.5,color='k')
    # #ax2.grid( linestyle=':', linewidth=1.5,color='r')
    plt.tick_params(direction='in', length=6, width=2,labelsize=20)
    ax = plt.axes()
    ax.grid( linestyle=':', linewidth=1.5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    plt.tight_layout()
    plt.show()



def show_demanddistribution():
    fopen = open('./resultdata/chargeroccupiedtime/ground')
    ground=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        demand = float(k[0])
        num = float(k[1])
        if num>30:
            num=int(num/3)
        else:
            num=int(num/2)
        if demand!=0 :
            #print demand/num
            if demand/(num*60*18)>1.0:
                cc = ground.append(1)
            else:
                ground.append(demand/(num*60*18))
    groundnum = len(ground)
    groundmean = sum(ground)/groundnum
    groundstd=0
    for k in ground:
        groundstd = groundstd +(k-groundmean)**2
    groundstd =groundstd/groundnum
    groundstd = math.sqrt(groundstd)
    # groundmean = np.average(ground)
    # groundstd = np.std(ground)
    # print max(ground),min(ground)
    print groundmean,groundstd
    fopen = open('./resultdata/chargeroccupiedtime/rec')
    rec=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        demand = float(k[0])
        num = float(k[1])
        if demand!=0:
            rec.append(demand/(num*60*18))

    recmean = np.average(rec)
    recstd = np.std(rec)
    # print max(rec),min(rec)
    fopen = open('./resultdata/chargeroccupiedtime/p2charging1')
    p2charging=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        demand = float(k[0])
        num = float(k[1])
        if demand!=0 and num!=0:
            p2charging.append(demand/(num*60*18))
        elif demand!=0 and num==0:
            p2charging.append(demand/(1*60*18))
    # for i in range(len(p2charging)):
    #     if p2charging[i]>=1:
    #         p2charging[i]=1.1
    p2chargingmean = np.average(p2charging)
    p2chargingstd = np.std(p2charging)
    # print max(p2charging),min(p2charging)
    mean=[groundmean,recmean,p2chargingmean]
    std=[groundstd,recstd,p2chargingstd]
    N=3
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    # p1 = plt.bar(ind, mean, width, yerr=std)
    data=[ground,rec,p2charging]
    boxprops = dict(linestyle='-', linewidth=3, color='k')
    medianprops = dict(linestyle='-', linewidth=2.5, color='r')
    plt.boxplot(data,positions=ind,showfliers=False,boxprops=boxprops,medianprops=medianprops,capprops=boxprops)
    # plt.ylim(-0.1,1.1)
    # plt.subplot(131)
    # plt.boxplot(ground)
    # plt.grid()
    #
    # plt.ylim([0.0,1])
    # fi2=plt.subplot(132)
    # plt.boxplot(rec)
    # plt.grid()
    # # fi2.axes.get_yaxis().set_visible(False)
    # fi2.yaxis.grid(True)
    #
    # plt.ylim([0.0,1])
    # fi3=plt.subplot(133)
    # plt.boxplot(p2charging)
    # plt.grid()
    # # fi3.axes.get_yaxis().set_visible(False)
    # fi3.yaxis.grid(True)
    # plt.ylim([0.0,1])
    plt.ylabel('ratio of busy time for\neach charging point',fontdict=font1)
    # plt.title('Scores by group and gender')
    plt.xticks(ind, ('Ground', 'REC', r'$p^2Charging$'))
    plt.tick_params(direction='in', length=6, width=2,labelsize=22)
    ax = plt.axes()
    ax.grid( linestyle=':', linewidth=2)
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    # ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    plt.tight_layout()
    #plt.yticks(np.arange(0, 81, 10))
    #plt.legend((p1[0], p2[0]), ('Men', 'Women'))

    plt.show()


def show_chargingnum():
    fopen = open('./resultdata/chargenum/ground')
    ground=[]
    for k in fopen:
        k=k.strip('\n')
        num = float(k)
        if int(num)!=0:
            ground.append(num+1)

    groundmean = np.average(ground)
    groundstd = np.std(ground)

    fopen = open('./resultdata/chargenum/rec')
    rec=[]
    for k in fopen:
        k=k.strip('\n')
        num = float(k)
        rec.append(num)

    recmean = np.average(rec)
    recstd = np.std(rec)

    fopen = open('./resultdata/chargenum/p2charging1')
    p2charging=[]
    for k in fopen:
        k=k.strip('\n')
        num = float(k)
        p2charging.append(num)

    p2chargingmean = np.average(p2charging)
    p2chargingstd = np.std(p2charging)

    mean=[groundmean,recmean,p2chargingmean]
    std=[groundstd,recstd,p2chargingstd]
    N=3
    #ind = np.arange([0, 0.8, 1.6])    # the x locations for the groups
    width = 0.1       # the width of the bars: can also be len(x) sequence
    ind = [0,0.2,0.4]
    value1 = dict( elinewidth=2,capthick=2)
    plt.bar(ind, mean, width, yerr=std,capsize=10,linewidth=3,ecolor='r',color='w',edgecolor='C0',error_kw=value1)


    plt.ylabel('Average number of\ncharges for each EV',fontdict=font1,color='k')
    plt.tick_params(direction='in', length=6, width=2,labelsize=25)
    plt.xticks(ind, ('Ground', 'REC', r'$p^2Charging$'))
    #plt.yticks(np.arange(0, 81, 10))
    #plt.legend((p1[0], p2[0]), ('Men', 'Women'))
    plt.tight_layout()
    plt.show()


def timehorizon():
    fopen= open('./resultdata/timehorizon/newslot20beta01_3horizon1')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[2])
        r.append(k)
    p2charging1= threetoone(r)
    fopen.close()

    fopen= open('./resultdata/timehorizon/newslot20beta00_3horizon6')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[2])
        r.append(k)
    p2charging6= threetoone(r)
    fopen.close()

    fopen= open('./resultdata/timehorizon/newslot20beta01_3horizon4')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[2])
        r.append(k)
    p2charging4= threetoone(r)
    fopen.close()


    fopen= open('./resultdata/timehorizon/newslot20beta01_3horizon8')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[2])
        r.append(k)
    p2charging8= threetoone(r)
    fopen.close()


    x=[]
    for i in range(18):
        x.append(i+6)


    # for i in range(len(p2charging2)):
    #     p2charging2[i] = max(0,1-p2charging2[i])
    # for i in range(len(p2charging4)):
    #     p2charging4[i] = max(0,1-p2charging4[i])
    # for i in range(len(p2charging6)):
    #     p2charging6[i] = max(0,1-p2charging6[i])

    plt.plot(x[0:18],p2charging1[0:18],'-C0^',linewidth=2.5,markersize=8,label='m=1')
    plt.plot(x[0:18],p2charging4[0:18],'-.C1s',linewidth=2.5,markersize=8,label='m=4')
    plt.plot(x[0:18],p2charging8[0:18],'-ks',linewidth=2.5,markersize=8,label='m=8')
    # plt.plot(x[0:18],p2charging6[0:18],'-C3o',linewidth=2.5,markersize=8,label='m=6')
    plt.xlabel('Time of day (hour)',fontdict=font1)
    plt.ylabel('Average ratio of unserved\npassengers in each region',fontdict=font1,color='k')


    plt.tick_params('y', colors='k',direction='in')
    plt.tick_params(axis='x', colors='k',direction='in')
    plt.xlim([5, 24])
    plt.ylim([0.05,0.35])
    plt.legend(loc=[0.15,0.0],fontsize=20,ncol=2)

    plt.tick_params(direction='in', length=6, width=2,labelsize=20)
    ax = plt.axes()
    ax.grid( linestyle=':', linewidth=1.5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    plt.tight_layout()
    plt.show()



def differentbeta():
    fopen= open('./resultdata/newbeta/data1/distance001','r')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[0])
        r.append(k)
    beta001= threetoone(r)
    fopen.close()

    fopen= open('./resultdata/newbeta/data1/distance010','r')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[0])
        r.append(k)
    beta010= threetoone(r)
    fopen.close()


    fopen= open('./resultdata/newbeta/data1/distance100','r')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[0])
        r.append(k)
    beta100  = threetoone(r)
    fopen.close()


    x=[]
    for i in range(18):
        x.append(i+6)


    # for i in range(len(p2charging12)):
    #     p2charging12[i] = max(0,1-p2charging12[i])
    # for i in range(len(p2charging4)):
    #     p2charging4[i] = max(0,1-p2charging4[i])
    # for i in range(len(p2charging8)):
    #     p2charging8[i] = max(0,1-p2charging8[i])


    plt.plot(x[0:18],beta001[0:18],'-C0^',linewidth=2.5,markersize=8,label=r'$\beta=0.01$')
    # plt.plot(x[0:18],beta010[0:18],'-C1s',linewidth=2.5,markersize=8,label=r'$\beta=0.1$')
    plt.plot(x[0:18],beta100[0:18],'-ro',linewidth=2.5,markersize=8,label=r'$\beta=1$')
    plt.xlabel('Time of day (hour)',fontdict=font1)
    plt.ylabel('Total driving distance to\ncharging stations (km)',fontdict=font1,color='k')


    plt.tick_params('y', colors='k',direction='in')
    plt.tick_params(axis='x', colors='k',direction='in')
    plt.xlim([5, 24])
    plt.legend(loc=0,fontsize=18,ncol=2)

    plt.tick_params(direction='in', length=6, width=2,labelsize=20)
    ax = plt.axes()
    ax.grid( linestyle=':', linewidth=1.5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    plt.tight_layout()
    plt.show()


def timeslot():
    fopen= open('./resultdata/timeslot/figure2/timeslot10')
    r=[]
    demand1=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        demand1.append(float(k[1]))
        k= float(k[2])

        r.append(k)
    # p2charging10= sixtoone(r)
    p2charging10 =r
    fopen.close()

    fopen= open('./resultdata/timeslot/figure2/timeslot20_1')
    r=[]
    demand2=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        demand2.append(float(k[1]))
        k= float(k[2])
        r.append(k)
    # p2charging20= threetoone(r)
    p2charging20 = r
    fopen.close()

    fopen= open('./resultdata/timeslot/figure2/timeslot30')
    r=[]
    demand3=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        demand3.append(float(k[1]))
        k= float(k[2])
        r.append(k)
    # p2charging4= threetoone(r)
    p2charging30 = r
    fopen.close()

    print sum(demand1),sum(demand2),sum(demand3)
    # fopen= open('./resultdata/timehorizon/newslot20beta01_3horizon8')
    # r=[]
    # for k in fopen:
    #     k=k.strip('\n')
    #     k=k.split(',')
    #     k= float(k[2])
    #     r.append(k)
    # p2charging8= threetoone(r)
    # fopen.close()


    x1=[]
    for i in range(18*6):
        x1.append(i/6.0+6)

    x2=[]
    for i in range(18*3):
        x2.append(i/3.0+6)
    x3=[]
    for i in range(18*2):
        x3.append(i/2.0+6)
    # for i in range(len(p2charging2)):
    #     p2charging2[i] = max(0,1-p2charging2[i])
    # for i in range(len(p2charging4)):
    #     p2charging4[i] = max(0,1-p2charging4[i])
    # for i in range(len(p2charging6)):
    #     p2charging6[i] = max(0,1-p2charging6[i])

    # plt.plot(x[0:18],p2charging1[0:18],'-C0^',linewidth=2.5,markersize=8,label='m=1')
    plt.plot(x1,p2charging10,'-.C1s',linewidth=2.5,markersize=8,label='Period:10')
    plt.plot(x2,p2charging20,'-k^',linewidth=2.5,markersize=8,label='Period:20')
    plt.plot(x3,p2charging30,'-C3o',linewidth=2.5,markersize=8,label='Period:30')
    plt.xlabel('Time of day (hour)',fontdict=font1)
    plt.ylabel('Average ratio of unserved\npassengers in each region',fontdict=font1,color='k')


    plt.tick_params('y', colors='k',direction='in')
    plt.tick_params(axis='x', colors='k',direction='in')
    plt.xlim([5, 24])
    # plt.ylim([0.05,0.35])
    plt.legend(loc=[0.02,0.98],fontsize=20,ncol=2)

    plt.tick_params(direction='in', length=6, width=2,labelsize=20)
    ax = plt.axes()
    ax.grid( linestyle=':', linewidth=1.5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    plt.tight_layout()
    plt.show()


def newbeta():
    fopen= open('./resultdata/newbeta/ratiobeta10','r')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[2])
        r.append(k)
    beta1000= r
    fopen.close()

    fopen= open('./resultdata/newbeta/ratiobeta0.1','r')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[2])
        r.append(k)
    beta010= r
    fopen.close()


    fopen= open('./resultdata/newbeta/ratiobeta1','r')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[2])
        r.append(k)
    beta100  = r
    fopen.close()

    fopen= open('./resultdata/newbeta/ratiobeta0.5','r')
    r=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        k= float(k[2])
        r.append(k)
    beta050  = r
    fopen.close()

    x=[]
    for i in range(54):
        x.append(i/3.0+6)


    # for i in range(len(p2charging12)):
    #     p2charging12[i] = max(0,1-p2charging12[i])
    # for i in range(len(p2charging4)):
    #     p2charging4[i] = max(0,1-p2charging4[i])
    # for i in range(len(p2charging8)):
    #     p2charging8[i] = max(0,1-p2charging8[i])


    plt.plot(x[0:54],beta1000[0:54],'-C0^',linewidth=2.5,markersize=8,label=r'$\beta=10.0$')
    plt.plot(x[0:54],beta010[0:54],'-C1s',linewidth=2.5,markersize=8,label=r'$\beta=0.1$')
    plt.plot(x[0:54],beta100[0:54],'-ro',linewidth=2.5,markersize=8,label=r'$\beta=1.0$')
    plt.plot(x[0:54],beta050[0:54],'-k*',linewidth=2.5,markersize=8,label=r'$\beta=0.5$')
    plt.xlabel('Time of day (hour)',fontdict=font1)
    plt.ylabel('Total driving distance to\ncharging stations (km)',fontdict=font1,color='k')


    plt.tick_params('y', colors='k',direction='in')
    plt.tick_params(axis='x', colors='k',direction='in')
    plt.xlim([5, 24])
    plt.legend(loc=0,fontsize=18,ncol=2)

    plt.tick_params(direction='in', length=6, width=2,labelsize=20)
    ax = plt.axes()
    ax.grid( linestyle=':', linewidth=1.5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    plt.tight_layout()
    plt.show()
