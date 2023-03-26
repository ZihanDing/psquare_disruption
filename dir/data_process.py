#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：newevaluation_dis
@File    ：data_process.py
@IDE     ：PyCharm
@Author  ：Zihan Ding
@Date    ：3/22/23 6:32 PM
'''

from datetime import datetime
import os
import dir.update_dis as ud

CHARGING_ENERGY = 3
RIDING_ENERGY = 1
TOTAL_ENERGY = 15
DISRUPTION_REGION = [32, 6, 2, 1]
DISRUPTION_START = 12 * 3
DISRUPTION_END = 18 * 3


def exp_config():
    # experiment setup
    # input:
    # output:
    #         L:
    #         L1:
    #         L2:
    #         LK:
    L1 = RIDING_ENERGY
    L2 = CHARGING_ENERGY
    L = TOTAL_ENERGY
    K = L / L2

    return L, L1, L2, K


def obtain_regions():
    # obtain region and charging stations infomation
    # input:
    # output:
    #         n: number of regions
    #         p: number of charging poles in each region: List<>[]
    fopen = open('./datadir/chargerindex', 'r')
    p = {}  # number of charging poles in each region
    n = 0  # number of regions
    for k in fopen:
        k = k.strip().split(',')
        p[n] = int(float(k[-1]) / 5)
        n += 1
    return n, p


def obtain_vehicles():
    """
    obtain initial vehicle information
    :param energystatus:
    :param location:
    :param occupancystatus:
    :return: num_of_v number of vehicles
    """

    energystatus = []  # 车辆energy level
    location = []  # 车辆timeslot结束时目前位置
    occupancystatus = []  # 是否载客

    # path = '/Users/jiangxiao/Desktop/data/ev/20161213/'
    path = '/Users/zihanding/Developer/Psquare/newevaluation/datadir/ev/20161213/'

    #  读取多文件中的充电时间信息
    # 每个file代表一辆车
    for root, dirs, files in os.walk(path):
        cvalue = 0
        for file in files:
            chargingtime = []
            fopen = open(path + file, 'r')
            for k in fopen:
                k = k.strip().split(',')
                start = int(k[0])
                end = int(k[1])
                if end - start > 30:
                    chargingtime.append([start, end])
            fopen.close()
            # 如果没有充电时间》30的energystatus就说是满足了80%的电量
            if len(chargingtime) == 0:
                energystatus.append(int((0.8) / (1 / 15.0)))
            else:
                energystatus.append(cvalue % 6 + 8)
            cvalue += 1

            gpspath = '/Users/zihanding/Developer/Psquare/newevaluation/datadir/evgps/20161213/' + file
            if os.path.isfile(gpspath):
                fopen = open(gpspath, 'r')
                gpsrecord = []
                for k in fopen:
                    k = k.strip()
                    gpsrecord.append(k)
                fopen.close()
                gps = []
                # 处理文件：6点之后的才要
                for line in gpsrecord:
                    line = line.strip().split(',')
                    ctime = datetime.strptime(line[4], '%Y-%m-%dT%H:%M:%S.000Z')
                    if (ctime.hour >= 6):
                        gps.append(float(line[2]))
                        gps.append(float(line[3]))
                if len(gps) == 0:
                    print(file)
                else:
                    # 得到车的位置信息
                    location.append(ud.gps_to_region(gps))

            # 读取汽车使用情况的文件，里面存的应该是汽车被占用的时间段，如果属于6-24就放到occupancystatus
            # dealpath = '/Users/jiangxiao/Desktop/data/evdeal/20161213/' + file
            dealpath = '/Users/zihanding/Developer/Psquare/newevaluation/datadir/evdeal/20161213/' + file
            if os.path.isfile(dealpath):
                fopen = open(dealpath, 'r')
                dealrecord = []
                for k in fopen:
                    k = k.strip().split(',')
                    ctime1 = datetime.strptime(k[1], '%Y-%m-%dT%H:%M:%S.000Z')
                    ctime2 = datetime.strptime(k[2], '%Y-%m-%dT%H:%M:%S.000Z')
                    dealrecord.append([ctime1.hour * 60 + ctime1.minute, ctime2.hour * 60 + ctime2.minute])
                occu = 0
                for ck in dealrecord:
                    if ck[0] <= 360 and ck[1] > 360:
                        occu = 1
                occupancystatus.append(occu)
            else:
                occupancystatus.append(0)
    num_of_v = len(energystatus)
    return energystatus, location, occupancystatus, num_of_v


def obtain_distance():
    """
    obtain region to region distance matrix
    :return: distance
    """
    distance = []
    fopen = open('./datadir/distance', 'r')
    for k in fopen:
        k = k.strip().split(',')
        temp = []
        for value in k:
            temp.append(float(value))
        distance.append(temp)
    return distance


def calculate_VO(n, L, num_of_v, occupancystatus, location, energystatus):
    """
    Calculate Vaccant and Occupied
    :param n:
    :param L:
    :param num_of_v:
    :param occupancystatus:
    :param location:
    :param energystatus:
    :return:
    """
    Vacant = {}
    Occupied = {}
    for i in range(n):
        for j in range(L):
            Occupied[i, j] = 0
            Vacant[i, j] = 0
    for i in range(len(energystatus)):
        if occupancystatus[i] == 1:
            Occupied[location[i], energystatus[i]] += 1
        elif occupancystatus[i] == 0:
            Vacant[location[i], energystatus[i]] += 1
    return Vacant, Occupied


def obtain_disruption():
    '''In summer, typically between noon and 6 p.m. when air conditioners are on full-throttle.
    In winter, typically between 6 a.m. and 9 a.m., and again between 5 p.m. and 9 p.m. — before and after work.'''
    disruption = [DISRUPTION_REGION, DISRUPTION_START, DISRUPTION_END]
    return disruption


def initial_future_resource(n, L, timehorizon):
    chargingresource = []
    futuresupply = {}

    for i in range(n):
        for l in range(L):
            for k in range(timehorizon):
                futuresupply[i, l, k] = 0

    for i in range(n):
        one = []
        for k in range(timehorizon):
            one.append(0)
            chargingresource.append(
                one)  # TODO chargingresourse最后是37*4个[0,0,0,0] charging resource[j][k]存放的是 从region0开始 到region j在k中的所有scheduling(预计schedule的充电） 之和
    return futuresupply, chargingresource
