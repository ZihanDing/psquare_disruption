import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math
import numpy as np


font1 = {'family' : 'serif',
        'weight' : 'bold',
        'size'   : 25,
        }

def threetoone(data):
    out=[]
    for i in range(len(data)/3):
        cc = (data[3*i]+data[3*i+1]+data[3*i+2])/3.0
        out.append(cc)
    return out

def temporal():

    fopen =open('./resultdata/temporal/ground','r')
    ground=[]
    for k in fopen:
        k=k.strip('\n')
        k=float(k)
        ground.append(k)

    fopen =open('./resultdata/beta/temporalsupplydemand1-4-1','r')
    p2charging8=[]

    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        p2charging8.append(float(k[2]))
        # p2charging.append(1-float(k)/(60.0*18))

    p2charging8= threetoone(p2charging8)


    fopen =open('./resultdata/rec/recratio','r')
    rec=[]

    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        rec.append(float(k[2]))
        # p2charging.append(1-float(k)/(60.0*18))

    rec= threetoone(rec)

    X=[]
    for i in range(18):
        X.append(i+6.0)

    plt.plot(X,ground[6:24],'-sk')
    plt.plot(X,p2charging8,'-or')
    plt.plot(X,rec,'-*g')
    plt.tight_layout()
    plt.show()




def utilization():
    ground=[]
    fopen = open('./resultdata/beta/p2withoutwaitingtime3-6-0.01','r')
    for k in fopen:
        k=k.strip('\n')
        ground.append(1-float(k)/(60.0*18))

    p2charging=[]
    fopen = open('./resultdata/beta/p2chargingutilization3-6-0.01','r')
    for k in fopen:
        k=k.strip('\n')
        p2charging.append(1-float(k)/(60.0*18))

    rec=[]
    fopen = open('./resultdata/beta/p2charging','r')
    for k in fopen:
        k=k.strip('\n')
        rec.append(float(k))


    groundmean = np.mean(ground)
    groundstd = np.std(ground)

    p2chargingmean = np.mean(p2charging)
    p2chargingstd = np.std(p2charging)

    recmean = np.mean(rec)
    recstd = np.std(rec)



    mean=[groundmean,recmean,p2chargingmean]
    std=[groundstd,recstd,p2chargingstd]
    N=3
    #ind = np.arange([0, 0.8, 1.6])    # the x locations for the groups
    width = 0.1       # the width of the bars: can also be len(x) sequence
    ind = [0,0.4,0.8]
    value1 = dict( elinewidth=2,capthick=2)
    plt.bar(ind, mean, width, yerr=std,capsize=10,linewidth=3,ecolor='r',color='w',edgecolor='C0',error_kw=value1)


    plt.ylabel('Average number of\ncharges for each EV',fontdict=font1,color='k')
    plt.tick_params(direction='in', length=6, width=2,labelsize=25)
    plt.xticks(ind, ('Ground',  'REC',r'$p^2$Charging'))
    #plt.yticks(np.arange(0, 81, 10))
    #plt.legend((p1[0], p2[0]), ('Men', 'Women'))
    plt.tight_layout()
    plt.show()



def betaratio():
    fopen = open('./resultdata/beta/temporalsupplydemand1-4-0.1','r')
    p2charging2=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        p2charging2.append(float(k[2]))
    p2charging2=threetoone(p2charging2)

    # fopen = open('./resultdata/beta/temporalsupplydemand-8-0.01','r')
    # p2charging001=[]
    # for k in fopen:
    #     k=k.strip('\n')
    #     k=k.split(',')
    #     p2charging001.append(float(k[2]))
    # p2charging001=threetoone(p2charging001)


    fopen = open('./resultdata/beta/temporalsupplydemand1-4-1','r')
    p2charging1=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        p2charging1.append(float(k[2]))
    p2charging1=threetoone(p2charging1)
    #
    fopen = open('./resultdata/beta/temporalsupplydemand1-4-10','r')
    p2charging10=[]
    for k in fopen:
        k=k.strip('\n')
        k=k.split(',')
        p2charging10.append(float(k[2]))
    p2charging10=threetoone(p2charging10)

    X=[]
    for i in range(18):
        X.append(i*3/3.0+6)

    plt.plot(X,p2charging1,'-sk',label='beta=1')
    # plt.plot(X,p2charging001,'-or',label='beta=0.01')
    plt.plot(X,p2charging2,'-*b',label='beta=0.1')
    plt.plot(X,p2charging10,'-^g',label='beta=10')
    plt.legend()
    plt.tight_layout()
    plt.show()


def betautilization():


    p2charging1=[]
    fopen = open('./resultdata/beta/p2chargingutilization1-4-1','r')
    for k in fopen:
        k=k.strip('\n')
        p2charging1.append(1-float(k)/(60.0*18))



    p2charging1mean = np.mean(p2charging1)
    p2charging1std = np.std(p2charging1)

    p2charging2=[]
    fopen = open('./resultdata/beta/p2chargingutilization1-4-2','r')
    for k in fopen:
        k=k.strip('\n')
        p2charging2.append(1-float(k)/(60.0*18))



    p2charging2mean = np.mean(p2charging2)
    p2charging2std = np.std(p2charging2)

    p2charging5=[]
    fopen = open('./resultdata/beta/p2chargingutilization1-4-20','r')
    for k in fopen:
        k=k.strip('\n')
        p2charging5.append(1-float(k)/(60.0*18))



    p2charging5mean = np.mean(p2charging5)
    p2charging5std = np.std(p2charging5)
    #
    #
    mean=[p2charging1mean,p2charging2mean,p2charging5mean]
    #
    #
    #
    # p2charging001=[]
    # fopen = open('./resultdata/beta/p2chargingutilization-8-0.01','r')
    # for k in fopen:
    #     k=k.strip('\n')
    #     p2charging001.append(1-float(k)/(60.0*18))



    # p2charging001mean = np.mean(p2charging001)
    # p2charging001std = np.std(p2charging001)


    # mean=[p2charging1mean,p2charging01mean]
    # ,p2charging10mean,p2charging001mean]


    std=[p2charging1std,p2charging2std,p2charging5std]
        # ,p2charging10std,p2charging001std]
    N=4
    #ind = np.arange([0, 0.8, 1.6])    # the x locations for the groups
    width = 0.1       # the width of the bars: can also be len(x) sequence
    ind = [0,0.3,0.6]
    value1 = dict( elinewidth=2,capthick=2)
    plt.bar(ind, mean, width, yerr=std,capsize=10,linewidth=3,ecolor='r',color='w',edgecolor='C0',error_kw=value1)


    plt.ylabel('Average number of\ncharges for each EV',fontdict=font1,color='k')
    plt.tick_params(direction='in', length=6, width=2,labelsize=25)
    plt.xticks(ind, ('1',  '0.1','10','0.01'))
    #plt.yticks(np.arange(0, 81, 10))
    #plt.legend((p1[0], p2[0]), ('Men', 'Women'))
    plt.tight_layout()
    plt.show()


def betaregionratio():
    data=[]
    fopen=open('./resultdata/beta/regionratio1-4-1','r')
    data1=[]
    for k in fopen:
        one=[]
        k=k.strip(',\n')
        k=k.split(',')
        for kk in k:
            one.append(float(kk))
        data1.append(one)

    for i in range(54):
        sum1=0
        for j in range(37):
            sum1 += data1[i][j]
        data.append(100*sum1/37)


    data2=[]
    fopen=open('./resultdata/beta/regionratio1-4-2','r')
    data1=[]
    for k in fopen:
        one=[]
        k=k.strip(',\n')
        k=k.split(',')
        for kk in k:
            one.append(float(kk))
        data1.append(one)

    for i in range(54):
        sum1=0
        for j in range(37):
            sum1 += data1[i][j]
        data2.append(100*sum1/37)

    data5=[]
    fopen=open('./resultdata/beta/regionratio1-4-5','r')
    data1=[]
    for k in fopen:
        one=[]
        k=k.strip(',\n')
        k=k.split(',')
        for kk in k:
            one.append(float(kk))
        data1.append(one)

    for i in range(54):
        sum1=0
        for j in range(37):
            sum1 += data1[i][j]
        data5.append(100*sum1/37)

    data=threetoone(data)
    data2=threetoone(data2)
    data5=threetoone(data5)

    X=[]
    for i in range(18):
        X.append(i*3/3.0+6)

    plt.plot(X,data,'-sk',label='beta=1')
    # plt.plot(X,p2charging001,'-or',label='beta=0.01')
    plt.plot(X,data2,'-*b',label='beta=2')
    plt.plot(X,data5,'-^g',label='beta=5')
    plt.legend()
    plt.tight_layout()
    plt.show()
