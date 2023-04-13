#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：newevaluation_dis 
@File    ：callmpc_fairness.py
@IDE     ：PyCharm 
@Author  ：Zihan Ding
@Date    ：3/27/23 11:23 PM 
@Description:
'''
import pandas as pd
import dir.data_process as dp
import fairness.mpc_alpha
import fairness.alpha_generator
import fairness.mpc_fairness
import math
import os
import json
import numpy as np
import copy

pd.set_option('mode.chained_assignment', None)

def call_mpc_fairness(slot,beta1,beta2,round):
    """

    :param future: time horizon we consider
    :param beta: beta for generate alpha, original p^2
    :param beta1: beta1 for fairness optimization
    :param beta2: beta2 for normal case
    :param round: iteration times
    """
    import os

    # 指定路径新建文件夹
    try:
        os.makedirs('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/supply/round-' + str(round))
    except:
        print('directory already exist')
    try:
        os.makedirs('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/vehicles_history/round-' + str(round))
    except:
        print('directory already exist')
    try:
        os.makedirs('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/demand/round-' + str(round))
    except:
        print('directory already exist')
    try:
        os.makedirs('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/decision/C/round-' + str(round))
    except:
        print('directory already exist')
    try:
        os.makedirs('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/decision/S/round-' + str(round))
    except:
        print('directory already exist')
    n, p = dp.obtain_regions()
    L, L1, L2, K = dp.exp_config()

    timehorizon = K

    distance = dp.obtain_distance()

    disruption = dp.obtain_disruption(slot)

    reachable = dp.obtain_reachable(n)

    vehicles = pd.read_csv('/Users/zihanding/Developer/Psquare/newevaluation_dis/datadir/vehicles_initial.csv')
    vlim = np.array(vehicles['location'])
    # vehicles = pd.read_csv('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/vehicles_history/round-0/54.csv')
    #这里只用 ： id	energy	location	vehicle_status
    # remain_trip_time	destination	dispatched_charging_time	dispatched_serving_time	update_status
    # vehicle_status: (0:C), (1:S), (2:O)
    num_of_v = len(vehicles)

    # initialize initial vaccant and occupied
    # vacant = {}
    # occupied = {}
    # for i in range(num_of_v):
    #     if vehicles['vehicle_status'][i] == 1:
    #         occupied[vehicles['location'][i], vehicles['energy_status'][i]] += 1
    #     else:
    #         vacant[vehicles['location'][i], vehicles['energy_status'][i]] += 1

    print'disruption region: ' + str(disruption[0]), 'disruption start time:', disruption[1], 'disruption end time:', disruption[2]
    total_serve = []
    total_demand = []

    for time in range(18,72):

        vehicles.to_csv('./resultdata/fairness_beta/vehicles_history/round-' + str(round)+'/'+str(time)+'.csv')

        if disruption[1] <= time <= disruption[2]:
            print 'Current Time slot:', str(time), '(Disruption happened in Region ' + str(disruption[0]) + ')', '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'
        else:
            print 'Current Time slot:', str(time), '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'

        vacant = {}
        occupied = {}
        for i in range(n):
            for l in range(L):
                vacant[i,l] = 0
                occupied[i,l] = 0
        for ind in range(num_of_v):
            if vehicles['vehicle_status'][ind] == 2: # occupied
                occupied[vehicles['location'][ind], vehicles['energy'][ind]] += 1
            else:
                vacant[vehicles['location'][ind], vehicles['energy'][ind]] += 1

        print "number of Vacant Vehicles:", sum(
            vacant[i, l] for i in range(n) for l in range(L)), "number of Occupied Vehicles:", sum(occupied[i, l] for i in range(n) for l in range(L))

        if_dis_time = disruption[1] <= time <= disruption[2]

        # update demand
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

        print '*********************************************************************************** mpc print generate XY for alpha ***********************************************************************************'

        #using for without disruption
        X,Y = fairness.mpc_alpha.mpc_iteration_optimize_utility(time,vacant,occupied,beta1, disruption, dis = False)
        print '*********************************************************************************** mpc print generate XY for alpha ***********************************************************************************'
        S, C = {}, {}
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    C[i,j,l] = X[i,j,l,0]
                    S[i,j,l] = Y[i,j,l,0]

        #using for pure rebalancing
        # X, Y = fairness.mpc_alpha.mpc_iteration_optimize_utility(time, vacant, occupied, beta1, disruption, dis=True)
        # S,C = Y,X

        # using for fairness + disruption
        # if disruption[1] < time <= disruption[2]:
        #     alpha = fairness.alpha_generator.generate_alpha(time,X,Y,vehicles,reachable,distance)
        #     print '*********************************************************************************** mpc print disruption SC for dispatch ***********************************************************************************'
        #
        #     C, S = fairness.mpc_fairness.mpc_iteration_optimize_utility(time, timehorizon, vacant, occupied, disruption, beta2, alpha)
        #     print '*********************************************************************************** mpc print disruption SC for dispatch ***********************************************************************************'
        #
        # with open('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/decision/C/round-' + str(round)+'/'+str(time)+'.json', 'w') as f:
        #     json_str = json.dumps({str(k): v for k, v in C.items()})
        #     f.write(json_str)
        # with open('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/decision/S/round-' + str(round)+'/'+str(time)+'.json', 'w') as f:
        #     json_str = json.dumps({str(k): v for k, v in S.items()})
        #     f.write(json_str)


        # print '*********************************************************************************** mpc print generate SC for dispatch ***********************************************************************************'
        # if if_dis_time:
        #     S,C = fairness.mpc_fairness.mpc_iteration_optimize_utility(time,timehorizon,vacant,occupied,disruption,beta2,alpha)
        # else:
        #     S,C = fairness.mpc_alpha.mpc_iteration_optimize_utility(time,vacant,occupied,beta1, disruption, dis = True)
        # print '*********************************************************************************** mpc print generate SC for dispatch ***********************************************************************************'
        #
        vehicles['update_status'] = [0] * num_of_v
        vehicles['decision'] = [0] * num_of_v

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
                if not reachable[i,j]: # reachable = 0:
                    if sum(S[i,j,l] for l in range(L)) > 0:
                        print('Optimization Error! Not reachable regions dispatched')  # 校验一下
                    continue

                for l in range(L):
                    # update serving decision
                    dispatch_vol = S[i, j, l]
                    # update serving decision
                    for ind in range(num_of_v):
                        if dispatch_vol <= 0:
                            break
                        if vehicles['location'][ind] == i and vehicles['energy'][ind] >= l and vehicles['vehicle_status'][ind] != 2 and vehicles['update_status'][ind] == 0:
                            vehicles['location'][ind] = j
                            vehicles['vehicle_status'][ind] = 1  # (send for Charging)
                            vehicles['dispatched_serving_time'][ind] = time
                            vehicles['decision'][ind] = 1
                            # 这里只是先完成这个slot所有的dispatch decision 至于谁serve 后面再定
                            dispatch_vol -= 1
                    # if dispatch_vol > 0:
                    #     print "Error, dispatch too much vehicles to serving, we don't have such vehicles in this region"

        #update charging decision
        for i in range(n):
            for j in range(n):
                if not reachable[i,j]: # reachable = 0:
                    if sum(C[i,j,l] for l in range(L)) > 0:
                        print('Optimization Error! Not reachable regions dispatched')  # 校验一下
                    continue
                for l in range(L):
                    # update charging decision
                    dispatch_vol = C[i, j, l]

                    for ind in range(num_of_v):
                        if dispatch_vol <= 0:
                            break
                        if vehicles['location'][ind] == i and vehicles['energy'][ind] == l and vehicles['vehicle_status'][ind] != 2 and vehicles['decision'][ind] == 0:
                            # if if_dis_time and j in disruption[0]:
                            #     vehicles['location'][ind] = j
                            # else:
                            vehicles['location'][ind] = j
                            vehicles['vehicle_status'][ind] = 0 # (send for Charging)
                            vehicles['dispatched_charging_time'][ind] = time
                            # vehicles['charging_station'][ind] = j
                            # vehicles['remain_charging_time'][ind] = q # we don't have the q!!!
                            dispatch_vol -= 1
                            # vehicles['update_status'][ind] = 1
                    # if dispatch_vol > 0:
                    #     print "Error, dispatch too much vehicles to charging, we don't have such vehicles in this region"

        # 再捡个漏：
        for ind in range(num_of_v):
            if vehicles['dispatched_charging_time'][ind] != time and vehicles['dispatched_serving_time'][ind] != time and vehicles['vehicle_status'][ind] != 2:
                if vehicles['energy'][ind] > 2*L1:
                    vehicles['vehicle_status'][ind] = 1 ## (serving)
                    vehicles['dispatched_serving_time'][ind] = time
                    vehicles['decision']= 1
        if time == 35:
            print 35
        if time == 36:
            vehicles.to_csv('36-check.csv')
        p_num = copy.deepcopy(p)

        if if_dis_time:
            for i in range(n):
                if i in disruption[0]:
                    p_num[i] = 0
        print 'Current charging supply p: ', p_num


        #update serving info
        vehicles.sort_values(['energy', 'dispatched_serving_time'],ascending=True, inplace=True)  # 优先给低energy的充电，同等energy level 就给先dispachted过来的先充
        serve = []
        supply = []
        for i in range(n):
            region_served = []
            for j in range(n):
                num_to_serve = cdemand[i][j]
                if num_to_serve <= 0:
                    region_served.append(0.0)
                    continue
                trip_distance = distance[i][j]
                trip_time = (60*trip_distance/40)  # 60分钟 40km.h的速度
                energy_lb = trip_time/20
                for ind in range(num_of_v):
                    if num_to_serve <= 0:
                        break
                    if vehicles['location'][ind] == i and vehicles['vehicle_status'][ind] == 1 and vehicles['update_status'][ind] == 0 and vehicles['energy'][ind] > energy_lb: # sent for serving
                        vehicles['energy'][ind] -= L1
                        vehicles['idle_driving_distance'][ind] += distance[vlim[ind]][i]
                        if vehicles['energy'][ind] < 0:
                            print('Error!! energy level doesn\'t support the trip ')
                        if trip_time > 20:
                            vehicles['vehicle_status'][ind] = 2  # occupied
                            vehicles['destination'][ind] = j
                            vehicles['remain_trip_time'][ind] = trip_time -20
                            vehicles['location'][ind] = dp.get_middle_region(i,j,int(vehicles['remain_trip_time'][ind]) / 20 + 2)
                        else:
                            #status 不变 ，位置走到了j ,remain trip也不用更新
                            vehicles['location'][ind] = j
                        num_to_serve -= 1
                        vehicles['update_status'][ind] = 1
                region_served.append(cdemand[i][j] - num_to_serve)
            serve.append(region_served)
            supply.append(sum(region_served))
        fwrite3 = open('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/supply/round-' + str(round) + '/' + str(time), 'w')
        for i in range(len(serve)):
            fwrite3.write(str(serve[i]) + '\n')
        fwrite3.close()

        fwrite1 = open('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/demand/round-' + str(round) + '/' + str(time), 'w')
        for i in range(len(cdemand)):
            fwrite1.write(str(cdemand[i]) + '\n')
        fwrite1.close()

        # update charging info:
        # 这里只用 ： id	energy	location	vehicle_status
        # remain_trip_time	destination	dispatched_charging_time	dispatched_serving_time	update_status
        # vehicle_status: (0:C), (1:S), (2:O)
        vehicles.sort_values(['energy', 'dispatched_charging_time'],ascending=True, inplace=True)  # 优先给低energy的充电，同等energy level 就给先dispachted过来的先充
        for i in range(n):
            num_of_charge = p_num[i]
            for ind in range(num_of_v):
                if num_of_charge <= 0:
                    break
                if vehicles['location'][ind] == i and vehicles['vehicle_status'][ind] == 0 and vehicles['update_status'][ind] == 0: # sent for charging
                    vehicles['energy'][ind] += L2
                    vehicles['idle_driving_distance'][ind] += distance[vlim[ind]][i]
                    if vehicles['energy'][ind] >= L:
                        vehicles['energy'][ind] = L-1
                    vehicles['update_status'][ind] = 1  # 更新完毕
                    num_of_charge -= 1


                # 这里只用 ： id	energy	location	vehicle_status
                # remain_trip_time	destination	dispatched_charging_time	dispatched_serving_time	update_status
                # vehicle_status: (0:C), (1:S), (2:O)

        vehicles.sort_values('id', ascending=True, inplace=True)
        wait_for_charing=0
        not_serving = 0
        for ind in range(num_of_v):
            if vehicles['update_status'][ind] == 0:
                vehicles['update_status'][ind] = 1
                if vehicles['vehicle_status'][ind] == 0:
                    wait_for_charing += 1
                    # vehicles['update_status'][ind] = 1
                if vehicles['vehicle_status'][ind] == 1:
                    not_serving += 1
                    vehicles['update_status'][ind] = 1
                if vehicles['vehicle_status'][ind] == 2:
                    vehicles['energy'][ind] -= L1
                    if vehicles['energy'][ind] < 0:
                        print('Error, low energy level')
                        vehicles['energy'][ind] = 0
                        vehicles['vehicle_status'][ind] = 0
                        # return
                    if vehicles['remain_trip_time'][ind] > 20: #送不完
                        vehicles['remain_trip_time'][ind] -= 20
                        vehicles['location'][ind] = dp.get_middle_region(vehicles['location'][ind],vehicles['destination'][ind], int(vehicles['remain_trip_time'][ind] / 20) + 2)
                    else:
                        vehicles['vehicle_status'][ind] = 0 # 送完了
                        vehicles['remain_trip_time'][ind] = 0
                        vehicles['location'][ind] = vehicles['destination'][ind]

        print 'wait for charge: ', wait_for_charing, " not_serving: ", not_serving
        print 'update completed? ',sum(vehicles['update_status'])

        alpha_k = []
        for i in range(n):
            if demand[i] == 0 or demand[i] < supply[i]:
                alpha_k.append(1.0)
            else:
                alpha_k.append(float(supply[i])/float(demand[i]))
        print 'alpha_k', alpha_k
        # print 'wait for charge: ', wait_for_charing, " not_serving: ", not_serving


