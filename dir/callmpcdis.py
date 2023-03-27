#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：newevaluation_dis 
@File    ：callmpcdis.py
@IDE     ：PyCharm 
@Author  ：Zihan Ding
@Date    ：3/26/23 4:12 PM
@Description: This file if written for our CDC paper, fairness aware charging problem
This call_mpc_dis function calls the mpc_dis function, in this file we did the parameter updating process.
'''

import dir.data_process as dp
import dir.mpc_dis
import math

def gps_to_region(gps):
    fopen = open('./datadir/chargerindex', 'r')
    chargergps = []
    for k in fopen:
        k = k.split(',')
        chargergps.append([float(k[0]), float(k[1])])
    near = 1000
    loc = 0
    for i in range(len(chargergps)):
        cgps = chargergps[i]
        if abs(cgps[0] - gps[0]) + abs(cgps[1] - gps[1]) < near:
            loc = i
            near = abs(cgps[0] - gps[0]) + abs(cgps[1] - gps[1])
    return loc


def get_middle_region(current, future, costtime):
    fopen = open('./datadir/chargerindex', 'r')
    chargergps = []
    for k in fopen:
        k = k.split(',')
        chargergps.append([float(k[0]), float(k[1])])
    startx = chargergps[current][0]
    starty = chargergps[current][1]
    endx = chargergps[future][0]
    endy = chargergps[future][1]
    middlex = startx + (endx - startx) / costtime
    middley = starty + (endy - endx) / costtime
    return gps_to_region([middlex, middley])


def call_mpc_dis(future,beta1,beta2,round):
    n,p = dp.obtain_regions()
    L, L1, L2, K = dp.exp_config()

    timehorizon = future

    energystatus,location,occupancystatus,num_of_v = dp.obtain_vehicles()

    distance = dp.obtain_distance()

    Vacant,Occupied = dp.calculate_VO(n,L,num_of_v,occupancystatus,location,energystatus)

    chargingstatus = [0]*num_of_v #是否在充电 (1,waiting for free charging point) (2, charging) (0,not charging) (3, heading to charging)
    remainingchargingtime = [0]*num_of_v #剩余充电时间
    remainingtriptime = [0]*num_of_v #剩余trip 时间
    destination = [0]*num_of_v # 目的地
    chargestation = [-1]* num_of_v # 充电region 没有的时候置-1
    idledrivingtime = [0]*num_of_v #  等待充电时间 idle driving + waiting for charging
    withoutwaitingtime = [0] * num_of_v # idle driving
    dispatchedtime = [-1] * num_of_v # dispatch去充电的开始时间戳

    disruption = dp.obtain_disruption()
    print'disruption region: ' + str(disruption[0]), 'disruption start time:', disruption[1], 'disruption end time:', disruption[2]

    for time in range(18,72):
        ctimehorizon = timehorizon
        fwrite1 = open('./status', 'w')
        for i in range(num_of_v):
            fwrite1.write(
                str(energystatus[i]) + ',' + str(chargingstatus[i]) + ',' + str(chargestation[i]) + ',' + str(occupancystatus[i]) + ',' + str(
                    location[i]) + ',' + str(remainingchargingtime[i]) + ',' + str(remainingtriptime[i]) + ',' + str(destination[i]) + ',' + str(
                    idledrivingtime[i]) + ',' + str(withoutwaitingtime[i]) + ',' + str(dispatchedtime[i])+ '\n')
        fwrite1.close()

        if disruption[1] <= time <= disruption[2]:
            print 'Current Time slot:',  str(time), '(Disruption happened in Region '+str(disruption[0])+')','~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'
        else:
            print 'Current Time slot:', str(time), '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'

        print "number of Vacant Vehicles:",sum(Vacant[i, l] for i in range(n) for l in range(L)),"number of Occupied Vehicles:",sum(Occupied[i, l] for i in range(n) for l in range(L))

        S,C = dir.mpc_dis.mpc_iteration()

        updatestatus = [0] * num_of_v

        # obtain demand in each time slot.
        demand = []
        cdemand = []
        fopen = open('./historydemand/slot20/groundtruth/' + str(time), 'r')
        for line in fopen:
            line = line.strip().split(',')
            csum = 0
            one = []
            for k in line:
                one.append((float(k)))
                csum += (float(k))
            demand.append(csum)  # 37 每个line所有的数据加起来是csum 从i出去的demandd
            cdemand.append(one)  # 37x37 i到j的demand
        fopen.close()

        # update disruption infomation
        if disruption[1] <= time <= disruption[2]:
            for j in range(num_of_v):
                if chargestation[j] in disruption[0] and (
                        chargingstatus[j] == 2 or chargingstatus[j] == 1):  # 在disruption region 充电
                    # print 'charging in disruption region, have to leave,',j
                    chargingstatus[j] = 0  # not charging
                    # Vacant[chargestation[j], energystatus[j]] += 1  # vehicle become vacant
                    location[j] = chargestation[j]  # vehicle is in region j
                    chargestation[j] = -1  # not charging in any region
                    occupancystatus[j] = 0  # 未载客

        #update charging vehicles
        for i in range(n):  # TODO 这个大循环耗时太严重
            for j in range(n):
                for l in range(L):
                    for q in range(1, 1 + ((L - l - 1) / L2)):
                        '''mpc_iteration返回的X确定要dispatch的车的数量'''
                        if l < 2 * L1:
                            dispatchnum = math.ceil(C[i, j, l, q])  # remaining energy<2xl1就要去充电了
                        else:
                            dispatchnum = int(C[i, j, l, q])

                        '''开始dispatch'''
                        for index in range(num_of_v):
                            if dispatchnum > 0:
                                if energystatus[index] == l and location[index] == i and occupancystatus[index] == 0 and \
                                        chargingstatus[index] == 0 and updatestatus[index] == 0:
                                    idledrivingtime[index] += 60.0 * distance[i][j] / 40.0
                                    withoutwaitingtime[index] += 60.0 * distance[i][j] / 40.0
                                    '''如果这里出现了dispatch到disuption location的车辆 那么不能更新他们的charging station'''
                                    if j in disruption[0] and time >= disruption[1] and time <= disruption[2]:
                                        print('Disruption area, Cannot dispatch', i, j, l, q)
                                        chargingstatus[index] = 3  # heading to charging
                                        location[index] = j
                                        occupancystatus[index] = 0
                                    else:  # 正常dispatch
                                        chargestation[index] = j
                                        chargingstatus[index] = 3  # heading to charge
                                        location[index] = j
                                        occupancystatus[index] = 0
                                        dispatchedtime[index] = time
                                        remainingchargingtime[index] = q
                                        # 因为没有更新energy 所以不能 update status
                                    dispatchnum -= 1

        #update serving vehicles
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    dispatchnum = C[i,j,l]
                    cnum = demand[i][j]
                    trip_distance = distance[i][j]
                    trip_time = (60.0*trip_distance/40) # 乘 60是因为 60分钟 40km/h的速度 point！！！记住奥

                    if l < trip_time: # we might need constraint here, l 需要支持走过i-j的energy < 这个energy level的不能dispatch
                        print 'dispatch the wrong energy level of vehicles'
                    if cnum < dispatchnum: # we might need constraint here dispatched num <= demand
                        # 我觉得这里还要加constraint 说明已经在本地的车辆 满足demand的话就不需要再dispatch过来了。
                        print 'Dispatch too much vehicles'

                    for ind in range(num_of_v):
                        if energystatus[ind] == l and location[ind] == i and occupancystatus[ind] == 0 and chargingstatus[ind] == 0 and updatestatus[ind] == 0:
                            energystatus[ind] -= L1
                        if trip_time > 20: #这一个timeslot送不完
                            occupancystatus[ind] = 1
                            remainingtriptime[ind] = trip_time - 20
                            destination[ind] = j
                            location[ind] = get_middle_region(i, j, int(remainingtriptime[ind])/20 + 2)
                            # 优先选择已经在本地的车辆 还是优先选择dispatched 来的车辆
            # We know dispatch to this region needs one time slot.
            # 我们在这里选择的应当是 上一个slot就dispatch过来的车！！！

