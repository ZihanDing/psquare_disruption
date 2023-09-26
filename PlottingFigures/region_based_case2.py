#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：PlottingFigures
@File    ：region_based_case2.py
@IDE     ：PyCharm
@Author  ：Zihan Ding
@Date    ：3/31/23 5:08 PM
@Description:
'''
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：PlottingFigures 
@File    ：region_based_case1.py
@IDE     ：PyCharm 
@Author  ：Zihan Ding
@Date    ：3/31/23 5:03 PM 
@Description:
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

legend_font = {"family" : "Times New Roman","size":25}
legend_font1 = {"family" : "Times New Roman","size":19}
import numpy as np
def generate_rec(round,time):
    fopen = open('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/rec/supply/round-'+str(round)+'/'+str(time), 'r')
    csupply = []
    for line in fopen:
        line = line.strip()[1:-1]
        line = line.split(',')
        for i in range(len(line)):
            line[i] = float(line[i])
        csupply.append(line)
    fopen.close()

    cdemand = []
    fopen1 = open('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/rec/demand/round-'+str(round)+'/'+str(time), 'r')
    for line in fopen1:
        line = line.strip()[1:-1]
        line = line.split(',')
        for i in range(len(line)):
            line[i] = float(line[i])
        cdemand.append(line)
    fopen1.close()
    return csupply,cdemand # 37*37

def cal_region_rec(round):
    region = [32,6,2,1]
    region_ratio1 = []

    for x in range(18,72):
        cs,cd = generate_rec(round,x)
        s,d = 0,0
        for item in region:
            s += sum(cs[item][j] for j in range(37))
            d += sum(cd[item][j] for j in range(37))
#         print(s,d)
        if d == 0 or s>d:
            region_ratio1.append(1.0)
        else:
            region_ratio1.append(s/d)
    return region_ratio1

def generate_sd(round,time):
    fopen = open('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/supply/round-'+str(round)+'/'+str(time), 'r')
    csupply = []
    for line in fopen:
        line = line.strip()[1:-1]
        line = line.split(',')
        for i in range(len(line)):
            line[i] = float(line[i])
        csupply.append(line)
    fopen.close()

    cdemand = []
    fopen1 = open('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/demand/round-'+str(round)+'/'+str(time), 'r')
    for line in fopen1:
        line = line.strip()[1:-1]
        line = line.split(',')
        for i in range(len(line)):
            line[i] = float(line[i])
        cdemand.append(line)
    fopen1.close()
    return csupply,cdemand # 37*37


'''Served Passenger 处理， 保留每个timeslot的passenger serve情况'''


def passengerServeNew(exp, file_no, season):
    if exp == 'beta':
        fopen = open(
            '/Users/zihanding/Developer/Psquare/newevaluation/resultdata/beta/chargestatus/passenger-served-' + str(
                file_no), 'r')
    elif exp == 'baseline':
        fopen = open(
            '/Users/zihanding/Developer/Yukun/newevaluation/resultdata/beta/chargestatus/passenger-served-' + str(
                file_no), 'r')
    else:
        return 'Please provide valid experiment type.'  # passenger_served_ratio = []

    result_served = []  # served passenger 54*37*37
    result_total = []  # total passenger demand 54*37*37
    count = 0
    ab = 0
    temp_s = []
    temp_t = []

    for line in fopen:
        if count == 37:
            if ab == 0:
                result_served.append(temp_s)
                temp_s = []
                ab = 1
            else:
                result_total.append(temp_t)
                temp_t = []
                ab = 0
            count = 0
        count += 1
        line = line.strip()[1:-1].split(',')
        for i in range(0, len(line)):
            line[i] = float(line[i])
        if ab == 0:
            temp_s.append(line)
        else:
            temp_t.append(line)
    if ab == 0:
        result_served.append(temp_s)
        temp_s = []
        ab = 1
    else:
        result_total.append(temp_t)
        temp_t = []
        ab = 0

    fopen.close()

    # result_served,result_total 54*37*37矩阵 分别是每个timeslot从i到j的passenger served和passenger demand
    return result_served, result_total


def passenger_serve(exp, file_no, season):
    served, demand = passengerServeNew(exp, file_no, season)
    result = []

    for i in range(len(demand)):
        ratio = []
        for j in range(len(demand[0])):
            cs, cd = 0, 0
            for k in range(len(demand[0][0])):
                cs += served[i][j][k]
                cd += demand[i][j][k]
            if cd == 0:
                if cs != 0:
                    print('error!!!!!')
                ratio.append(1.0)
            else:
                ratio.append(cs / cd)
        result.append(ratio)
    return result

    # result 54*37的矩阵 每个timeslot，每个region的passenger serve情况


def passenger_serve_totalratio(exp, file_no, season):
    served, demand = passengerServeNew(exp, file_no, season)
    result = []
    for i in range(len(demand)):
        cs, cd = 0, 0
        for j in range(len(demand[0])):
            for k in range(len(demand[0][0])):
                cs += served[i][j][k]
                cd += demand[i][j][k]
        if cd == 0:
            result.append(1.0)
        else:
            result.append(cs / cd)
    return result

def cal_region_by_loc_base(region):
    region_ratio1 = []
    res = 0
    supply, demand = passengerServeNew('beta', 41, 'Summer')
    for x in range(54):
        cs, cd = supply[x], demand[x]
        s, d = 0, 0
        for item in region:
            s += sum(cs[item][j] for j in range(37))
            d += sum(cd[item][j] for j in range(37))
        #         print(s,d)
        if d == 0 or s > d:
            region_ratio1.append(1.0)
        else:
            region_ratio1.append(s / d)
    return sum(region_ratio1) / (72 - 18)


def cal_region_by_loc(region, round):
    region_ratio1 = []
    res = 0

    for x in range(18, 72):
        cs, cd = generate_sd(round, x)
        s, d = 0, 0
        for item in region:
            s += sum(cs[item][j] for j in range(37))
            d += sum(cd[item][j] for j in range(37))
        #         print(s,d)
        if d == 0 or s > d:
            region_ratio1.append(1.0)
        else:
            region_ratio1.append(s / d)
    return sum(region_ratio1) / (72 - 18)


def cal_region_by_loc_rec(region, round):
    region_ratio1 = []
    res = 0

    for x in range(18, 72):
        cs, cd = generate_rec(round, x)
        s, d = 0, 0
        for item in region:
            s += sum(cs[item][j] for j in range(37))
            d += sum(cd[item][j] for j in range(37))
        #         print(s,d)
        if d == 0 or s > d:
            region_ratio1.append(1.0)
        else:
            region_ratio1.append(s / d)
    return sum(region_ratio1) / (72 - 18)


import numpy as np


def cal_region_by_loc_base(region):
    region_ratio1 = []
    res = 0
    supply, demand = passengerServeNew('beta', 32, 'Winter')
    for x in range(len(supply)):
        cs, cd = supply[x], demand[x]
        s, d = 0, 0
        for item in region:
            s += sum(cs[item][j] for j in range(37))
            d += sum(cd[item][j] for j in range(37))
        #         print(s,d)
        if d == 0 or s > d:
            region_ratio1.append(1.0)
        else:
            region_ratio1.append(s / d)
    return sum(region_ratio1) / (72 - 18)


x = [m for m in range(18, 72)]
oracle, afc, baseline, rec, region_base1 = [], [], [], [], []
regions = [[32, 6, 2, 1], [8, 14, 17, 12, 36, 34], [3, 22, 24, 0, 13, 7, 9, 10, 26, 29, 11, 18, 33],
           [35, 27, 20, 5, 30, 23], [4, 15, 25, 19, 28]]
for region in regions:
    oracle.append(cal_region_by_loc(region, 16))
    afc.append(cal_region_by_loc(region, 25))
    baseline.append(cal_region_by_loc(region, 19))
    rec.append(cal_region_by_loc_rec(region, 7))
    region_base1.append(cal_region_by_loc_base(region))

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)


legend_font = {"family" : "Times New Roman","size":27}
legend_font1 = {"family" : "Times New Roman","size":22}

X = ['Affected\nRegion', 'North\nwest', 'South\nwest', 'North\neast', 'South\neast']
Ygirls = oracle
Zboys = afc
Nbio = region_base1
REC = rec

X_axis = np.arange(len(X))

plt.figure(figsize=(8, 5.5))

plt.bar(X_axis - 0.4, Ygirls, 0.15, label='Oracle', edgecolor='C0', color='w', hatch='xxx')
plt.bar(X_axis - 0.2, Zboys, 0.15, label='AFC', edgecolor='C1', color='w', hatch='\\\\\\')
plt.bar(X_axis + 0.0, Nbio, 0.15, label='R2D', edgecolor='C2', color='w', hatch='///')
plt.bar(X_axis + 0.2, REC, 0.15, label='R2E', edgecolor='C3', color='w', hatch='xxx')

plt.ylim(0.5, 1.1)

yt = [0.5,0.7,0.9,1.1]
plt.xticks(X_axis, X, fontproperties=legend_font)
plt.yticks(np.arange(0.5, 1.2, step=0.2),fontproperties=legend_font)
# plt.xlabel("", fontproperties=legend_font)
plt.ylabel("Ratio of served passengers", fontproperties=legend_font)
# plt.title("Number of Students in each group",fontproperties = legend_font)
plt.legend(prop=legend_font1,ncol = 5, loc="best",columnspacing = 0.4)
ax = plt.gca()
# ax.yaxis.set_major_locator(MultipleLocator(0.2))
plt.tight_layout()
plt.show()


plt.savefig("/Users/zihanding/Desktop/research/CPS/Thesis/3.15 update figure/3.16update/evaluation_fig/region_evaluation_case2.pdf")

