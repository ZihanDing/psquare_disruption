#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：newevaluation_dis 
@File    ：callmpcdis.py
@IDE     ：PyCharm 
@Author  ：Zihan Ding
@Date    ：3/26/23 4:12 PM 
'''

import dir.data_process as dp

def call_mpc_dis(future,beta1,beta2,round):
    n,p = dp.obtain_regions()
    L, L1, L2, K = dp.exp_config()

    timehorizon = future

    energystatus,location,occupancystatus,num_of_v = dp.obtain_vehicles()

    distance = dp.obtain_distance()

