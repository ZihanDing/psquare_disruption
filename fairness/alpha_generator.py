#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：newevaluation_dis
@File    ：alpha_generator.py
@IDE     ：PyCharm
@Author  ：Zihan Ding
@Date    ：3/23/23 11:37 PM
@Description:
"""
import dir.update_dis as ud

# def update_fairness(time, L, L1, L2, p, distance, disruption, X, Y,
#                     energystatus, chargingstatus, chargestation, occupancystatus,
#                     location, remainingchargingtime, remainingtriptime, destination, idledrivingtime,
#                     withoutwaitingtime, dispatchedtime):
#     n = len(p)  # number of charging station
#     num_of_v = len(energystatus)  # number of vehicles
#     updatestatus = [0] * num_of_v
#
#     if disruption[1] <= time <= disruption[2]:
#         for j in range(num_of_v):
#             if chargestation[j] in disruption[0] and (
#                     chargingstatus[j] == 2 or chargingstatus[j] == 1):  # 在disruption region 充电
#                 # print 'charging in disruption region, have to leave,',j
#                 chargingstatus[j] = 0  # not charging
#                 # Vacant[chargestation[j], energystatus[j]] += 1  # vehicle become vacant
#                 location[j] = chargestation[j]  # vehicle is in region j
#                 chargestation[j] = -1  # not charging in any region
#                 occupancystatus[j] = 0  # 未载客

# dispatch for serving:

import dir.data_process as dp
import math

def generate_alpha(time,X,Y,vehicls,reachable,distance):
    n, p = dp.obtain_regions()
    L, L1, L2, K = dp.exp_config()

    vehicles = vehicls
    num_of_v = len(vehicles)

    current = time
    S,C = {},{}
    alpha = []
    # we
    # want
    # alpha[i, k]
    # alpha: 4 * 37
    for k in range(K):


        demand = []
        cdemand = []
        fopen = open('./historydemand/slot20/groundtruth/' + str(time+k), 'r')
        for line in fopen:
            line = line.strip().split(',')
            csum = 0
            one = []
            for s in line:
                one.append((float(s)))
                csum += (float(s))
            demand.append(csum)  # 37 每个line所有的数据加起来是csum 从i出去的demandd
            cdemand.append(one)  # 37x37 i到j的demand
        fopen.close()


        for i in range(n):
            for j in range(n):
                for l in range(L):
                    S[i,j,l] = X[i,j,l,k]
                    C[i,j,l] = Y[i,j,l,k]
                    # transfer decision matrix
        # 接下来的update和之前一样 copy过来修改一下 不能有disruption
        vehicles['update_status'] = [0] * num_of_v
        # 这里只用 ： id	energy	location	vehicle_status
        # remain_trip_time	destination	dispatched_charging_time	dispatched_serving_time	update_status
        # vehicle_status: (0:C), (1:S), (2:O)

        # if if_dis_time:  # 在disruption happen的时候
        #     for i in range(num_of_v):
        #         if vehicles['location'][i] in disruption[0] and vehicles[]:
        #             vehicles['charging_status'] = 0  # 停止充电
        #             vehicles['charging_station'][i] = -1  # 停止充电
        #             vehicles['occupy_status'][i] = 0  # 可用

        # update decisions
        for i in range(n):
            for j in range(n):
                if reachable[i, j]:  # 不可达 则不用dispatch了
                    if sum(C[i, j, l] for l in range(L)) > 0 or sum(S[i, j, l] for l in range(L)) > 0:
                        print('Optimization Error! Not reachable regions dispatched')  # 校验一下
                    continue

                for l in range(L):

                    # update charging decision
                    if l < 2 * L1:
                        dispatch_vol = math.ceil(C[i, j, l])
                    else:
                        dispatch_vol = int(C[i, j, l])

                    for ind in range(num_of_v):
                        if dispatch_vol <= 0:
                            break
                        v = vehicles.iloc[ind]
                        if v['location'] == i and v['energy'] == l and v['vehicle_status'] != 2 and v[
                            'update_status'] == 0:
                            # vehicles['idle_driving_distance'][ind] += distance[i][j]
                            # if if_dis_time and j in disruption[0]:
                            #     vehicles['location'][ind] = j
                            # else:
                            vehicles['location'][ind] = j
                            vehicles['vehicle_status'][ind] = 0  # (send for Charging)
                            vehicles['dispatched_charging_time'][ind] = time
                            # vehicles['charging_station'][ind] = j
                            # vehicles['remain_charging_time'][ind] = q # we don't have the q!!!
                            dispatch_vol -= 1
                            # vehicles['update_status'][ind] = 1
                    if dispatch_vol > 0:
                        print "Error, dispatch too much vehicles to charging, we don't have such vehicles in this region"

                    # update serving decision
                    dispatch_vol = int(S[i, j, l])
                    # update serving decision
                    for ind in range(num_of_v):
                        if dispatch_vol <= 0:
                            break
                        if vehicles['location'][ind] == i and vehicles['energy'][ind] == l and \
                                vehicles['vehicle_status'][ind] != 2 and vehicles['update_status'][ind] == 0:
                            vehicles['location'][ind] = j
                            vehicles['vehicle_status'][ind] = 1  # (send for Charging)
                            vehicles['dispatched_serving_time'][ind] = time
                            # vehicles['idle_driving_distance'][ind] += distance[i][j]
                            # 这里只是先完成这个slot所有的dispatch decision 至于谁serve 后面再定
                            dispatch_vol -= 1
                    if dispatch_vol > 0:
                        print "Error, dispatch too much vehicles to serving, we don't have such vehicles in this region"

        p_num = p
        # if_dis_time = disruption[1] <= time <= disruption[2]
        # if if_dis_time:
        #     for i in range(n):
        #         if i in disruption[0]:
        #             p_num[i] = 0
        print 'Current charging supply p: ', p_num

        # update charging info:
        # 这里只用 ： id	energy	location	vehicle_status
        # remain_trip_time	destination	dispatched_charging_time	dispatched_serving_time	update_status
        # vehicle_status: (0:C), (1:S), (2:O)
        vehicles.sort_values(['energy', 'dispatched_charging_time'], ascending=True,
                             inplace=True)  # 优先给低energy的充电，同等energy level 就给先dispachted过来的先充
        for i in range(n):
            num_of_charge = p_num[i]
            for ind in range(num_of_v):
                if num_of_charge <= 0:
                    break
                if vehicles['location'][ind] == i and vehicles['vehicle_status'][ind] == 0 and \
                        vehicles['update_status'][ind] == 0:  # sent for charging
                    vehicles['energy'][ind] += L2
                    vehicles['update_status'] = 1  # 更新完毕
                    num_of_charge -= 1

        supply = []
        # update serving info
        vehicles.sort_values(['energy', 'dispatched_serving_time'], ascending=True,
                             inplace=True)  # 优先给低energy的充电，同等energy level 就给先dispachted过来的先充
        for i in range(n):
            region_served = 0
            for j in range(n):
                num_to_serve = cdemand[i][j]
                if num_to_serve <= 0:
                    continue
                trip_distance = distance[i][j]
                trip_time = (60 * trip_distance / 40)  # 60分钟 40km.h的速度
                energy_lb = trip_time / 20
                for ind in range(num_of_v):
                    if num_to_serve <= 0:
                        break
                    if vehicles['location'][ind] == i and vehicles['vehicle_status'][ind] == 1 and \
                            vehicles['update_status'][ind] == 0 and vehicles['energy'][
                        ind] > energy_lb:  # sent for serving
                        vehicles['energy'][ind] -= L1
                        if vehicles['energy'][ind] < 0:
                            print('Error!! energy level doesn\'t support the trip ')
                        if trip_time > 20:
                            vehicles['vehicle_status'][ind] = 2  # occupied
                            vehicles['destination'][ind] = j
                            vehicles['remain_trip_time'][ind] = trip_time - 20
                            vehicles['location'][ind] = dp.get_middle_region(i, j, int(
                                vehicles['remain_trip_time'][ind]) / 20 + 2)
                        else:
                            # status 不变 ，位置走到了j ,remain trip也不用更新
                            vehicles['location'][ind] = j
                        num_to_serve -= 1
                        vehicles['update_status'][ind] = 1
                region_served  += cdemand[i][j] - num_to_serve
            supply.append(region_served)

                # 这里只用 ： id	energy	location	vehicle_status
                # remain_trip_time	destination	dispatched_charging_time	dispatched_serving_time	update_status
                # vehicle_status: (0:C), (1:S), (2:O)

        vehicles.sort_values('id', ascending=True, inplace=True)
        wait_for_charing = 0
        not_serving = 0
        for ind in range(num_of_v):
            if vehicles['update_status'][ind] == 0 and vehicles['vehicle_status'][ind] == 0:
                wait_for_charing += 1
                vehicles['update_status'] = 1
            if vehicles['update_status'][ind] == 0 and vehicles['vehicle_status'][ind] == 1:
                not_serving += 1
                vehicles['update_status'] = 1
            print 'wait for charge: ', wait_for_charing, " not_serving: ", not_serving

        alpha_k= [x1/x2 for x1 in supply for x2 in demand]
        alpha.append(alpha_k)
    return alpha

    # 返回supply/demand


