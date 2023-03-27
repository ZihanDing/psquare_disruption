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
import dir.update_fairness as uf
import dir.update_dis as ud
import dir.mpc_dis
import math
import random
import dir.mpc

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

    chargingstatus = [0]*num_of_v #是否在充电
    # (1,waiting for free charging point) (2, charging) (0,not charging) (3, heading to charging) (4, heading to serve)
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


        # generate alpha first
        futuresupply,chargingresource = ud.update_future_resource(n,L,L2,K,time,
                                                                  num_of_v,p,disruption,timehorizon,
                                                                  chargingstatus,chargestation,
                                                                  energystatus,remainingchargingtime,
                                                                  dispatchedtime)
        X, Y = dir.mpc.mpc_iteration(time, ctimehorizon,distance, Vacant, Occupied, beta1, chargingresource, futuresupply, disruption)
        alpha = uf.generate_alpha(time,L,L1,L2,p,distance,disruption,X,Y,
            energystatus, chargingstatus, chargestation, occupancystatus,
            location, remainingchargingtime, remainingtriptime, destination, idledrivingtime,
            withoutwaitingtime, dispatchedtime)

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

        supply = [0] * n
        for i in range(num_of_v):
            if occupancystatus[i] == 0 and chargingstatus[i] == 0 and updatestatus[i] == 0:
                supply[location[i]] += 1

        # update disruption infomation 释放connecting vehicles
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


        #update serving decision:
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    dispatchnum = C[i,j,l]
                    cdistance = distance[i][j]
                    costtime = (60.0*cdistance/40)
                    #C3: dispatch的距离不能超过1个timeslot能到达的距离。if distance(i,j) > 1timeslot ride: decision[i,j,k] = 0
                    for ind in range(num_of_v):
                        if dispatchnum >0:
                            if updatestatus[ind] == 0 and energystatus[ind] == l and location[ind] == i and chargingstatus == 0:
                                location[ind] = j
                                chargingstatus[ind] = 4 # heading to serve
                                dispatchedtime[ind] = time
                                idledrivingtime[ind] += costtime
                                withoutwaitingtime[ind] += costtime

                                dispatchnum -= 1




        #update serving vehicles
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    cnum = demand[i][j]
                    trip_distance = distance[i][j]
                    trip_time = (60.0*trip_distance/40) # 乘 60是因为 60分钟 40km/h的速度 point！！！记住奥

                    if l < trip_time: # C1: we might need constraint here, l 需要支持走过i-j的energy < 这个energy level的不能dispatch
                        print 'dispatch the wrong energy level of vehicles'
                    # if cnum < dispatchnum: # we might need constraint here dispatched num <= demand
                    #     # C2: 我觉得这里还要加constraint 说明已经在本地的车辆 满足demand的话就不需要再dispatch过来了。
                    #     print 'Dispatch too much vehicles'

                    for ind in range(num_of_v):
                        #有两种情况可以serve passengers ：1）原本就在region i 并且available的车  2)dispatch 来region i serve的车
                        avail = location[ind] == i and occupancystatus[ind] == 0 and chargingstatus[ind] == 0
                        dispat = destination[ind] == j and occupancystatus[ind] == 0 and chargingstatus[ind] == 4
                        if energystatus[ind] == l and updatestatus[ind] == 0 and (avail or dispat):
                            energystatus[ind] -= L1
                        if trip_time > 20: #这一个timeslot送不完
                            occupancystatus[ind] = 1
                            remainingtriptime[ind] = trip_time - 20
                            destination[ind] = j
                            location[ind] = get_middle_region(i, j, int(remainingtriptime[ind])/20 + 2)
                            # 优先选择已经在本地的车辆 还是优先选择dispatched 来的车辆
                        else:
                            occupancystatus[index] = 0  # slot结束不载客
                            remainingtriptime[index] = 0  # slot结束trip也结束了
                            location[index] = j  # slot结束在乘客的目的地
                            # supply[location[index]] +=max(0,1-((60.0*cdistance/30.0)/20.0))
                        updatestatus[index] = 1  # 安排了 一辆车
                        cnum -= 1

            # We know dispatch to this region needs one time slot.
            # 我们在这里选择的应当是 上一个slot就dispatch过来的车！！！

        for i in range(num_of_v):
            if updatestatus[i] == 0:
                updatestatus[i] = 1
                if occupancystatus[i] == 1 and chargingstatus[i] == 0:  # 不在充电 在载客 上一个slot就在载客了 没载完
                    if remainingtriptime[i] > 20:  # 在载客 这个slot还要继续跑完
                        energystatus[i] -= L1
                        if energystatus[i] < 0:
                            print('Error!')
                            return
                        occupancystatus[i] = 1
                        remainingtriptime[i] -= 20
                        chargingstatus[i] = 0
                        location[i] = get_middle_region(location[i], destination[i], int(remainingtriptime[i] / 20) + 2)
                    else:  # 在载客 但是这个slot乘客就下车
                        energystatus[i] -= L1
                        if energystatus[i] < 0:
                            print(i)
                            print('Error!!')
                            return
                        occupancystatus[i] = 0  # slot结束乘客已经下车 occupancy status置为零
                        supply[destination[i]] += 1  # 在乘客目的地空出来一辆车
                        # supply[destination[i]] += (1-(remainingtriptime[i])/20.0)
                        remainingtriptime[i] = 0
                        location[i] = destination[i]
                        # chargingstatus[i] = 0


                elif occupancystatus[i] == 0 and chargingstatus[i] == 2:  # 没载客 在充电
                    idledrivingtime[i] += 20.0
                    if remainingchargingtime[i] > 1:
                        energystatus[i] += L2
                        occupancystatus[i] = 0
                        # chargingstatus[i] = 2
                        remainingchargingtime[i] -= 1
                    else:
                        energystatus[i] += L2
                        occupancystatus[i] = 0
                        chargingstatus[i] = 0
                        remainingchargingtime[i] = 0
                        chargestation[i] = -1

                elif occupancystatus[i] == 0 and chargingstatus[i] == 0:  # 没载客 没充电 就规划一条路线给它
                    if energystatus[i] > L1:
                        energystatus[i] -= L1
                    fopen1 = open('./transition/slot20/' + str(time) + 'pv', 'r')
                    transition = []
                    for k in fopen1:
                        k = k.strip().split(',')
                        one = []
                        for line in k:
                            one.append(float(line))
                        transition.append(one)
                    fopen1 = open('./transition/slot20/' + str(time) + 'qv', 'r')
                    transition1 = []
                    for k in fopen1:
                        k = k.strip('').split(',')
                        one = []
                        for line in k:
                            one.append(float(line))
                        transition1.append(one)
                    fopen1 = open('./transition/slot20/' + str(time) + 'po', 'r')
                    transition2 = []
                    for k in fopen1:
                        k = k.strip().split(',')
                        one = []
                        for line in k:
                            one.append(float(line))
                        transition2.append(one)
                    fopen1 = open('./transition/slot20/' + str(time) + 'qo', 'r')
                    transition3 = []
                    for k in fopen1:
                        k = k.strip().split(',')
                        one = []
                        for line in k:
                            one.append(float(line))
                        transition3.append(one)
                    loc = location[i]
                    transitionrow = transition[loc]
                    max1 = max(transitionrow)
                    for cc in range(len(transitionrow)):
                        if transitionrow[cc] == max1:
                            location[i] = cc
                            break
                    possible = []
                    for j in range(n):
                        possible.append(int(transition[loc][j] * 1000))
                    mylist = []
                    for j in range(n):
                        for c in range(possible[j]):
                            mylist.append(j)
                    if len(mylist) == 0:
                        location[i] = location[i]
                    else:
                        cc = random.choice(mylist)
                        location[i] = cc