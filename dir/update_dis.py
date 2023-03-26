#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：newevaluation_dis
@File    ：update_dis.py
@IDE     ：PyCharm
@Author  ：Zihan Ding
@Date    ：3/23/23 9:22 PM
'''


# coding=utf-8
import math
import random
import copy

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


def update_status_withdisruption(time,L,L1,L2,p,distance,disruption,X,Y,
                                 energystatus,chargingstatus,chargestation,occupancystatus,
                                 location,remainingchargingtime,remainingtriptime,destination,idledrivingtime,
                                 withoutwaitingtime,dispatchedtime):
    n = len(p) # number of charging station
    num_of_v = len(energystatus) # number of vehicles
    updatestatus = [0] * num_of_v

    '''update disruption region vehicles status 将正在disruption region充电的车辆disconnecting， 置为可用状态'''
    '''另外 还要将在等待freepoints的车也置为可用状态'''
    if time >= disruption[1] and time <= disruption[2]:
        for j in range(num_of_v):
            if chargestation[j] in disruption[0] and (
                    chargingstatus[j] == 2 or chargingstatus[j] == 1):  # 在disruption region 充电
                # print 'charging in disruption region, have to leave,',j
                chargingstatus[j] = 0  # not charging
                # Vacant[chargestation[j], energystatus[j]] += 1  # vehicle become vacant
                location[j] = chargestation[j]  # vehicle is in region j
                chargestation[j] = -1  # not charging in any region
                occupancystatus[j] = 0  # 未载客

    for i in range(n):  # TODO 这个大循环耗时太严重
        for j in range(n):
            for l in range(L):
                for q in range(1, 1 + ((L - l - 1) / L2)):
                    '''mpc_iteration返回的X确定要dispatch的车的数量'''
                    if l < 2 * L1:
                        dispatchnum = math.ceil(X[i, j, l, q])  # remaining energy<2xl1就要去充电了
                    else:
                        dispatchnum = int(X[i, j, l, q])

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
    for i in range(n):
        connectingvehicle = 0
        for j in range(num_of_v):
            if chargingstatus[j] == 2 and chargestation[j] == i:
                connectingvehicle += 1
        if i in disruption[0] and time >= disruption[1] and time <= disruption[2]:  # 如果disruption发生了那么没有freepoints了
            freepoints = 0
        else:
            freepoints = p[i] - connectingvehicle

        waitinginfo = []
        for j in range(num_of_v):
            # if chargestation[j] == i and (chargingstatus[j] == 1 or chargingstatus[j] == 3 ):
            # TODO 这里我认为应当是 dispatched time不能是当下时候的3 否则刚刚heading to charging就冲上了
            # (chargingstatus[j] == 3 and dispatchedtime[j] != time) 这里表示 上一个slot的时候在heading to charge
            # 这里条件 ： 充电region是i && （上个slot就已经在这里waiting了 或者｜ 上个slot正在heading到这里充电）
            if chargestation[j] == i and (
                    chargingstatus[j] == 1 or (chargingstatus[j] == 3 and dispatchedtime[j] != time)):
                info = [j, dispatchedtime[j], remainingchargingtime[j]]
                waitinginfo.append(info)
        waitinginfo = sorted(waitinginfo, key=lambda x: (x[2], x[1]))
        # waitinginfo = sorted(waitinginfo, key=lambda x: (x[1], x[2]))
        # TODO 这里我认为应当优先 dispatched time 排序 mar 24 先看下结果

        for record in waitinginfo:
            id1 = record[0]
            '''如果i是disruption location 那么dispatch到这的车并不做任何update charging status还是3 charging station 还是-1'''
            if freepoints > 0:
                chargingstatus[id1] = 2  # charging
                # remainingchargingtime[id1] = futurecharginglength[id1]
                # updatestatus[id1]=1
                freepoints -= 1
            else:
                if i not in disruption[0] or time < disruption[1] or time > disruption[2]:
                    idledrivingtime[id1] += 20.0
                    chargingstatus[id1] = 1  # waiting for charging
                    updatestatus[id1] = 1  # 这辆车的状态就确定了 为等待charging 或者是 跑到了j但是并不能充电 所以要在这里等着下一个slot重新规划

    supply = []
    for i in range(n):
        supply.append(0)
    for i in range(len(energystatus)):
        if occupancystatus[i] == 0 and chargingstatus[i] == 0 and updatestatus[i] == 0:
            supply[location[i]] += 1

    '''update demand 每个时间'''
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

    total_slot_served = [] #37region * 37destination
    total_demand = []

    for i in range(n):
        pair = []
        temp = []
        temp_demand = []
        for j in range(n):
            pair.append([j, cdemand[i][j]])
        pair = sorted(pair, key=lambda x: x[1], reverse=True)
        for j in range(n):
            cnum = pair[j][1]
            total = copy.deepcopy(pair[j][1]) # this time slot total passenger demand
            # print('total:',total)
            cdistance = distance[i][pair[j][0]]
            costtime = (60.0 * cdistance / 40.0)
            for index in range(len(energystatus)):
                if cnum > 0:
                    '''如果有passenger demand 从i到j 那么用车车去载客'''
                    if energystatus[index] + 1 > int(costtime / 20) + 1 and location[index] == i and \
                            occupancystatus[index] == 0 and chargingstatus[index] == 0 and updatestatus[index] == 0:
                        energystatus[index] -= L1 # 走过一个region减掉一个l1
                        if energystatus[index] < 0:
                            print('Error---!!')
                            return
                        chargingstatus[index] = 0

                        if costtime > 20: #这个slot送不完
                            occupancystatus[index] = 1 #在载客
                            remainingtriptime[index] = costtime - 20 #slot结束这个triptime-20
                            destination[index] = pair[j][0] # 乘客的终点
                            location[index] = get_middle_region(location[index], destination[index],
                                                                int(remainingtriptime[index]) / 20 + 2) #目前在哪里
                        else: # 这个slot就能送结束
                            occupancystatus[index] = 0 #slot结束不载客
                            remainingtriptime[index] = 0 #slot结束trip也结束了
                            location[index] = pair[j][0] #slot结束在乘客的目的地
                            # supply[location[index]] +=max(0,1-((60.0*cdistance/30.0)/20.0))
                        updatestatus[index] = 1 # 安排了 一辆车
                        cnum -= 1
            if cnum<0:
                temp.append(float(total))
            else:
                temp.append(float(total) - float(cnum))
            temp_demand.append(float(total))
        total_slot_served.append(temp)
        total_demand.append(temp_demand)

        for i in range(len(energystatus)):
            if updatestatus[i] == 0:
                updatestatus[i] = 1
                if occupancystatus[i] == 1 and chargingstatus[i] == 0: # 不在充电 在载客 上一个slot就在载客了 没载完
                    if remainingtriptime[i] > 20: #在载客 这个slot还要继续跑完
                        energystatus[i] -= L1
                        if energystatus[i] < 0:
                            print('Error!')
                            return
                        occupancystatus[i] = 1
                        remainingtriptime[i] -= 20
                        chargingstatus[i] = 0
                        location[i] = get_middle_region(location[i], destination[i], int(remainingtriptime[i] / 20) + 2)
                    else: # 在载客 但是这个slot乘客就下车
                        energystatus[i] -= L1
                        if energystatus[i] < 0:
                            print(i)
                            print('Error!!')
                            return
                        occupancystatus[i] = 0 #slot结束乘客已经下车 occupancy status置为零
                        supply[destination[i]] += 1 #在乘客目的地空出来一辆车
                        # supply[destination[i]] += (1-(remainingtriptime[i])/20.0)
                        remainingtriptime[i] = 0
                        location[i] = destination[i]
                        # chargingstatus[i] = 0


                elif occupancystatus[i] == 0 and chargingstatus[i] == 2: #没载客 在充电
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

                elif occupancystatus[i] == 0 and chargingstatus[i] == 0: #没载客 没充电 就规划一条路线给它
                    if energystatus[i]>L1:
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
    for i in range(n):
        num = 0
        for j in range(num_of_v):
            if chargingstatus[j] == 2 and chargestation[j] == i:  # 在充电 在region i 充电
                num += 1
        if num > p[i]:
            print('MMMMMMMMMMMMMMMMMMMMMMM')

    return demand, cdemand, supply,total_slot_served,total_demand,\
           energystatus,chargingstatus,chargestation,occupancystatus,location,\
           remainingchargingtime,remainingtriptime,destination,idledrivingtime,\
           withoutwaitingtime,dispatchedtime
    # return time, ctimehorizon, Vacant, Occupied, beta, chargingresource, futuresupply

def calculate_region_ratio(n,demand,supply):
    unratio = []
    for i in range(n):
        if demand[i] > 0:
            c = float(supply[i]) / demand[i]
        else:
            c = 0
        unratio.append(max(0, 1 - c))
    return unratio

def update_mpc_parameters():
    return 0