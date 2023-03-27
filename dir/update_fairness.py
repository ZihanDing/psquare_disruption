#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：newevaluation_dis 
@File    ：update_fairness.py
@IDE     ：PyCharm 
@Author  ：Zihan Ding
@Date    ：3/23/23 11:37 PM
@Description:
'''


def update_fairness(time, L, L1, L2, p, distance, disruption, X, Y,
                    energystatus, chargingstatus, chargestation, occupancystatus,
                    location, remainingchargingtime, remainingtriptime, destination, idledrivingtime,
                    withoutwaitingtime, dispatchedtime):
    n = len(p)  # number of charging station
    num_of_v = len(energystatus)  # number of vehicles
    updatestatus = [0] * num_of_v

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

