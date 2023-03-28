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

def call_mpc_fairness(future,beta, beta1,beta2,round):
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
        os.makedirs('/Users/zihanding/Developer/Psquare/newevaluation_dis/resultdata/fairness_beta/vehicles_history/round-' + str(round))
    except:
        print('directory already exist')

    n, p = dp.obtain_regions()
    L, L1, L2, K = dp.exp_config()

    timehorizon = future

    distance = dp.obtain_distance()

    disruption = dp.obtain_disruption()

    reachable = dp.obtain_reachable(n)

    vehicles = pd.read_csv('/Users/zihanding/Developer/Psquare/newevaluation_dis/datadir/vehicles_initial.csv')
    num_of_v = len(vehicles)

    # initialize initial vaccant and occupied
    vacant = {}
    occupied = {}
    for i in range(num_of_v):
        if vehicles['occupy_status'][i] == 1:
            occupied[vehicles['location'][i], vehicles['energy_status'][i]] += 1
        elif vehicles['occupy_status'][i] == 0:
            vacant[vehicles['location'][i], vehicles['energy_status'][i]] += 1

    print'disruption region: ' + str(disruption[0]), 'disruption start time:', disruption[1], 'disruption end time:', disruption[2]

    for time in range(18,72):

        vehicles.to_csv('./resultdata/fairness_beta/vehicles_history/round-' + str(round)+'/'+str(time)+'.csv')

        if disruption[1] <= time <= disruption[2]:
            print 'Current Time slot:', str(time), '(Disruption happened in Region ' + str(disruption[0]) + ')', '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'
        else:
            print 'Current Time slot:', str(time), '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'

        print "number of Vacant Vehicles:", sum(
            vacant[i, l] for i in range(n) for l in range(L)), "number of Occupied Vehicles:", sum(occupied[i, l] for i in range(n) for l in range(L))

        X,Y = fairness.mpc_alpha.mpc_iteration_optimize_utility(time,vacant,occupied,beta)

        alpha = fairness.alpha_generator.generate_alpha()
        S,C = fairness.mpc_fairness.mpc_iteration_optimize_utility()

        vehicles['update_status'] = [0] * num_of_v

        if_dis_time = disruption[1] <= time <= disruption[2]
        if if_dis_time:  # 在disruption happen的时候
            for i in range(num_of_v):
                if vehicles['charging_station'][i] in disruption[0]:
                    vehicles['charging_status'] = 0  # 停止充电
                    vehicles['charging_station'][i] = -1  # 停止充电
                    vehicles['occupy_status'][i] = 0  # 可用

        for i in range(n):
            for j in range(n):
                if reachable[i,j]: #不可达 则不用dispatch了
                    if sum(C[i,j,l,q] for l in range(L) for q in range(1,1 + ((L - l - 1) / L2)))>0:
                        print('Optimization Error! Not reachable regions dispatched') # 校验一下
                    continue

                for l in range(L):
                    # update charging decision
                    for q in range(1, 1 + ((L - l - 1) / L2)):
                        if l < 2*L1:
                            dispatch_vol = math.ceil(C[i, j, l, q])
                        else:
                            dispatch_vol = int(C[i, j, l, q])

                        for ind in range(num_of_v):
                            if dispatch_vol < 0:
                                break
                            if vehicles['location'][ind] == i and vehicles['energy'][ind] == l and vehicles['occupy_status'][ind] == 0 and vehicles['update_status'][ind] == 0:
                                vehicles['idle_driving_distance'][ind] += distance[i][j]
                                if if_dis_time and j in disruption[0]:
                                    vehicles['location'][ind] = j
                                else:
                                    vehicles['location'][ind] = j
                                    vehicles['charging_status'][ind] = 2  # waiting for charging
                                    vehicles['charging_station'][ind] = j
                                    vehicles['dispatched_charging_time'][ind] = time
                                    vehicles['remain_charging_time'][ind] = q # TODO ,we don't have the q!!!
                                dispatch_vol -= 1
                                vehicles['update_status'][ind] = 1

                    #update serving decision
                    for ind in range(num_of_v):
                        if vehicles['location'][ind] == i and vehicles['energy'][ind] == l and vehicles['occupy_status'][ind] == 0 and vehicles['update_status'][ind] == 0:
                            dispatch_vol = int(S[i,j,l])
                            


