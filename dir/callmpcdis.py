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
        