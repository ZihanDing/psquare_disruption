#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：PlottingFigures 
@File    ：evaluation_service_quality.py
@IDE     ：PyCharm 
@Author  ：Zihan Ding
@Date    ：3/31/23 1:38 PM 
@Description:
'''

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：PlottingFigures 
@File    ：motivation_service_quality.py
@IDE     ：PyCharm 
@Author  ：Zihan Ding
@Date    ：3/31/23 12:23 PM 
@Description:
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

def transfer(region_ratio):
    n = len(region_ratio)
    res = []
    count,temp = 0,0
    for i in range(n):
        if count == 3:
            res.append(temp/3)
            count = 0
            temp = 0
        temp += region_ratio[i]
        count += 1
    res.append(temp/3)
    return res

region_mix_oracle = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9675299939243492, 0.9987434422388949, 0.902294273142627, 0.973685000239637, 0.9785210923831933, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8854176161656208, 0.9202637967244799, 0.8072437457613347, 0.746957580221855, 0.8449642919068631, 0.7516854519520457, 0.7378876129018518, 0.8516651730788611, 0.790421152029828, 0.8029014423193462, 0.9673613921490322, 0.9046953431738358, 0.8877447800882933, 0.9493435237646802, 1.0, 0.9866695351218784, 1.0, 0.9339558093745194, 0.9687306083909434, 1.0, 0.8959838893068435, 0.9420928484709954, 0.8275484619622828, 0.8452048802553156, 0.8563472412799848, 0.9584873613140755, 0.7522237599926366, 0.8793295561851308, 0.9958010562643076, 0.8770234056291931, 0.9405028628704439, 0.9909636832298659]
region_mix_afc = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9055596547862103, 1.0, 0.8548051008719625, 1.0, 0.9355632771495798, 1.0, 1.0, 1.0, 1.0, 0.8938066301924442, 0.8216644545259254, 0.7935693157335025, 0.6677726467206514, 0.634680771123948, 0.6627142441066082, 0.76260315154049, 0.6235572499147652, 0.6680463985119646, 0.7092048168547608, 0.74953729933863, 0.7480691486975372, 0.8559378794011935, 0.7990066348591354, 0.8402798489879862, 0.8105244235915429, 0.8192257692974735, 0.8000071711380291, 1.0, 1.0, 1.0, 1.0, 0.9426023780619869, 0.9372268794205733, 0.8604857141796871, 0.9306656285137728, 0.9110909005398926, 0.9368253756421957, 0.7779094493582388, 0.8685622554971496, 0.991470340611707, 0.8690865422298341, 0.9043853831566752, 1.0]
y_dis_area = [1.0, 1.0, 0.9454545454544819, 0.9213483146068379, 0.8970588235294568, 0.7723615909871703, 0.8674698795180587, 0.853333333333411, 0.7321128296800316, 0.8561879857630584, 0.8804347826086385, 0.8777777777778379, 0.838150289017232, 0.7927461139897262, 0.8305084745761732, 0.857954545454594, 0.7394746106861455, 0.7833333333333214, 0.7721518987343483, 0.8188976377950671, 0.5578231292517951, 0.6232876712329104, 0.7294117647057262, 0.6700503619767803, 0.641149904334797, 0.7132489000064302, 0.6594594594590988, 0.5777777777780323, 0.5867346938775425, 0.7860292179985425, 0.8843930635837725, 0.7560975609757878, 0.7189806758400774, 0.7465753424655781, 0.5460526315788959, 0.4373631972607961, 0.5026248229461299, 0.7590795951485158, 0.7075968254656559, 0.8499999999998109, 0.8857142857141659, 0.9176470588233296, 0.8333333333334195, 0.7798165137615328, 0.8135593220339382, 0.8320610687022825, 0.9423076923077692, 0.9363636363635502, 0.9065420560748787, 0.8034188034187567, 0.8645833333333164, 0.8859649122807309, 0.809523809524046, 0.6999999999998372]
region_rec1 = [0.9632613314453353, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9357817222535704, 0.44552969619989274, 0.48100461015040635, 0.38339551989872195, 0.4707174508078392, 0.48479456266332466, 0.4981151633583422, 0.4558960537983799, 0.5488728573482603, 0.5393247127097578, 0.6309811349594338, 0.538689561626822, 0.6262575232126133, 0.7951625750889612, 0.7784767424256772, 0.7189563977101847, 0.606198782851981, 0.4584707723753726, 0.3772987072580152, 0.4380653477992833, 0.4667131287427799, 0.37584272597602275, 0.4008278391071788, 0.5295808894417645, 0.37817563739358145, 0.5169901970056278, 0.5570389373880782, 0.36779670493515754, 0.5197607313327749, 0.5373642587347246, 0.5256304068902865, 0.42514666809049534, 0.49340526578901506, 0.4749107950093099, 0.62591373363884, 0.6039531290240778, 0.577909608602914, 0.5649638665666072, 0.506410252842591, 0.6460941151951692, 0.42230822857643086, 0.5058683295824288, 0.4513342559955819, 0.3553209227033794, 0.5586623191854695, 0.41668532846635875, 0.5477263588131978, 0.7716032463055433]

region_mix_afc1 = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9675299939243492, 0.9987434422388949, 0.8896304938704497, 0.9773441526219587, 0.9785210923831933, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9876293442158562, 0.9295048003730377, 0.9302305526456834, 0.7809205801386826, 0.7441494690180134, 0.8693675927561587, 0.7374489850590146, 0.7348510383631611, 0.8950226727992395, 0.7461303116143635, 0.6462377462570347, 0.8468803357038263, 0.7355934098703151, 0.7276650238658849, 0.8463487075071913, 0.8002841330131388, 0.6902919019533851, 0.9201341443092442, 0.7589260743776226, 0.8108427913048607, 0.9322535196155437, 0.6316686419613246, 0.8364968877071471, 1.0, 0.9876819817636374, 0.9707059375736874, 1.0, 0.9173460487715079, 0.9618788614596533, 1.0, 0.9087708592266299, 0.963828553880588, 1.0]
region_psquare2 = [1.0, 1.0, 0.9090909090908031, 0.9213483146068379, 0.8970588235294568, 0.7723615909871703, 0.8493975903614286, 0.853333333333411, 0.7321128296800316, 0.8561879857630584, 0.8804347826086385, 0.8777777777778379, 0.838150289017232, 0.7927461139897262, 0.8474576271185521, 0.857954545454594, 0.7394746106861455, 0.7444444444444365, 0.7721518987343483, 0.8151357319710373, 0.6870748299321768, 0.698630136986107, 0.7705165805697405, 0.8580246913581387, 0.8219895287956043, 0.7553191489364254, 0.7246558456469987, 0.8500000000000908, 0.8520408163265722, 0.8895348837208586, 0.959537572254243, 0.8536585365854564, 0.8428571428572268, 0.7465753424655781, 0.675262785149813, 0.6834532374099483, 0.5026248229461299, 0.7669902912621914, 0.521737344030729, 0.6463745278562578, 0.6380952380951551, 0.7411764705879206, 0.5686274509806148, 0.7798165137615328, 0.7796610169491998, 0.8320610687022825, 0.9423076923077692, 0.9363636363635502, 0.9065420560748787, 0.7777777777777669, 0.8437499999999806, 0.8859649122807309, 0.8380952380954533, 0.7374999999998382]
region_mix_rec = [0.9632613314453353, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9877695957121021, 0.3998343427434935, 0.38889734437692425, 0.37404440965728963, 0.43065639116461885, 0.49851516349341873, 0.4395133794338314, 0.44164930211718056, 0.5543615859217429, 0.5558346528947503, 0.6426659707920159, 0.5925585177895042, 0.6709902034420856, 0.7872109493380715, 0.706395562571448, 0.6996986370572333, 0.6943731512668148, 0.4634541503359744, 0.4562682041259718, 0.5096721834972431, 0.48501560437975166, 0.39719742631556965, 0.4737056280357568, 0.5342263358403765, 0.5059376770535753, 0.5639893058243213, 0.6861089350755598, 0.5073057999105621, 0.5457487678994137, 0.584383631374013, 0.6321771109896688, 0.4731470983587772, 0.46006707215462217, 0.5307826532456993, 0.5761251411902957, 0.46806367499366025, 0.46367166271629146, 0.5124090882813415, 0.49405878326106434, 0.5546657026675509, 0.3577889158772539, 0.5657737896645585, 0.41830979823980763, 0.33378632132741703, 0.5456701722276678, 0.464306508862514, 0.5477263588131975, 0.7967642217285502]

region_mix_oracle = transfer(region_mix_oracle)
region_mix_afc = transfer(region_mix_afc)
y_dis_area = transfer(y_dis_area)
region_rec1 = transfer(region_rec1)
region_mix_afc1 = transfer(region_mix_afc1)
region_psquare2 = transfer(region_psquare2)
region_mix_rec = transfer(region_mix_rec)

print(sum(region_mix_afc)/len(region_mix_afc), sum(y_dis_area)/len(y_dis_area))
print(sum(region_mix_afc1)/len(region_mix_afc1),sum(region_psquare2)/len(region_psquare2))


legend_font = {"family" : "Times New Roman","size":27}
legend_font1 = {"family" : "Times New Roman","size":24}
legend_large= {"family" : "Times New Roman","size":30}
legend_middle = {"family" : "Times New Roman","size":27}



def figuretest():
    disruption = 32



    x = [m for m in range(6,24)]
    plt.figure(figsize=(12, 10), dpi=90)

    plt.subplot(2, 1, 2)

    plt.plot(x, region_mix_oracle, 's-', color='b', label="Oracle")
    plt.plot(x, region_mix_afc, 'o-', color='r', label="AFC")
    plt.plot(x, y_dis_area, '^--', color='black', label="R2D")
    plt.plot(x, region_rec1, 'p-', color='green', label="R2E")
    #     plt.plot(x,region18,'o-',color = 'black',label="beta: 0.001")
    #     plt.plot(x,region2,'o-',color = 'black',label="Fairness aware, beta =0.1")
    plt.ylabel("Ratio of served passengers", fontproperties=legend_middle)

    plt.vlines([12, 18], 0.35, 1.05, linestyles='dashed', colors='black')
    #     x = range(6,24,1)
    # plt.xlim(6,24)
    xt = range(6,24,2)
    yt = xt
    plt.xticks(xt, yt, fontproperties=legend_large)
    plt.xticks(x, fontproperties=legend_large)
    plt.yticks(np.arange(0.3, 1.2, step=0.2), fontproperties=legend_large)
    #     plt.grid(linestyle = '--', linewidth = 0.4)
    plt.legend(loc="best", ncol = 4,columnspacing = 0.4,prop=legend_font1,borderaxespad=0)  # 图例
    plt.xlabel("Time of day (hour)",fontproperties = legend_large)
    plt.ylim(0.3, 1.1)
    plt.text(13, 1.02, 'Duration with', fontproperties=legend_font, color='black')
    plt.text(13, 0.95, 'power failure', fontproperties=legend_font, color='black')

    plt.subplot(2, 1, 1)
    plt.plot(x, region_mix_oracle, 's-', color='b', label="Oracle")
    plt.plot(x, region_mix_afc1, 'o-', color='r', label="AFC")
    plt.plot(x, region_psquare2, '^--', color='black', label='R2D')
    plt.plot(x, region_mix_rec, 'p-', color='green', label="R2E")
    #     plt.plot(x,region18,'o-',color = 'black',label="beta: 0.001")
    #     plt.plot(x,region2,'o-',color = 'black',label="Fairness aware, beta =0.1")
    plt.ylabel("Ratio of served passengers", fontproperties=legend_middle)
    #     plt.title("Ratio of Served Passengers (RSP) in Disruption area")

    #     x = range(6,24,1)
    # plt.xlim(6,24)
    plt.vlines([16, 20], 0.35, 1.05, colors='blue')
    xt = range(6,24,2)
    yt = xt
    plt.xticks(xt, yt, fontproperties=legend_large)
    plt.xticks(x, fontproperties=legend_large)
    plt.yticks(np.arange(0.3, 1.2, step=0.2), fontproperties=legend_large)
    #     plt.grid(linestyle = '--', linewidth = 0.4)
    # plt.legend(loc="best", ncol = 4,prop=legend_font1)  # 图例
    plt.ylim(0.3, 1.1)
    plt.text(16.1, 0.41, 'Duration with', fontproperties=legend_font1, color='b')
    plt.text(16.1, 0.34, 'power failure', fontproperties=legend_font1, color='b')

    # plt.show()
    plt.savefig("/Users/zihanding/Desktop/research/CPS/Thesis/3.15 update figure/3.16update/evaluation_fig/service_quality_evaluation.pdf")

figuretest()

