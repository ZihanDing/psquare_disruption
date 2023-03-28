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

def generate_alpha(time,X,Y,vehicls):
    n, p = dp.obtain_regions()
    L, L1, L2, K = dp.exp_config()

    current = time
    S,C = {},{}
    for k in range(K):
        alpha = []
        # we want alpha[i,k] alpha: 4*37
        for i in range(n):
            for j in range(n):
                for l in range(L):
                    S[i,j,l] = X[i,j,l,k]
                    C[i,j,l] = X[i,j,l,k]
                    # transfer decision matrix
        # 接下来的update和之前一样 copy过来修改一下 不能有disruption




    # 返回supply/demand
    return


