# coding=utf-8
import copy

import dir.mpc
import os
from datetime import datetime
import dir.update_dis as ud
import dir.data_process as dp
import random
import math

import numpy as np
# import pandas as pd


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


def call_mpc(future, beta1,beta2, round):
    n,p = dp.obtain_regions()
    L,L1,L2,K = dp.exp_config()

    timehorizon = future

    energystatus,location,occupancystatus,num_of_v = dp.obtain_vehicles()

    distance = dp.obtain_distance()

    chargingstatus = [0]*num_of_v #是否在充电 (1,waiting for free charging point) (2, charging) (0,not charging) (3, heading to charging)
    remainingchargingtime = [0]*num_of_v #剩余充电时间
    remainingtriptime = [0]*num_of_v #剩余trip 时间
    destination = [0]*num_of_v # 目的地
    chargestation = [-1]* num_of_v # 充电region 没有的时候置-1
    idledrivingtime = [0]*num_of_v #  等待充电时间 idle driving + waiting for charging
    withoutwaitingtime = [0] * num_of_v # idle driving
    dispatchedtime = [0] * num_of_v # dispatch去充电的开始时间戳

    supplydemand = []
    regionratio = []
    beta = beta1
    chargingresource = []
    futuresupply = {}

    Vacant,Occupied = dp.calculate_VO(n,L,num_of_v,occupancystatus,location,energystatus,chargingstatus)

    for i in range(n):
        for l in range(L):
            for k in range(timehorizon):
                futuresupply[i, l, k] = 0

    for i in range(n):
        one = []
        for k in range(timehorizon):
            one.append(0)
            chargingresource.append(one)# TODO chargingresourse最后是37*4个[0,0,0,0] charging resource[j][k]存放的是 从region0开始 到region j在k中的所有scheduling(预计schedule的充电） 之和


    disruption = dp.obtain_disruption()
    print'disruption region: '+ str(disruption[0])
    print'disruption start time:',disruption[1],'disruption end time:',disruption[2]


    '''out print parameters'''
    chgstatus = []
    chgstation = []
    passenger_served = []
    passenger_demand = []
    energy_total = []
    occupy_total = []
    vehicle_status = []

    '''Begin iteration'''
    for time in range(18, 72):
        ctimehorizon = timehorizon
        fwrite1 = open('./status', 'w')
        for i in range(num_of_v):
            fwrite1.write(
                str(energystatus[i]) + ',' + str(chargingstatus[i]) + ',' + str(chargestation[i]) + ',' + str(occupancystatus[i]) + ',' + str(
                    location[i]) + ',' + str(remainingchargingtime[i]) + ',' + str(remainingtriptime[i]) + ',' + str(destination[i]) + ',' + str(
                    idledrivingtime[i]) + ',' + str(withoutwaitingtime[i]) + ',' + str(dispatchedtime[i])+ '\n')
        fwrite1.close()

        if time >= disruption[1] and time <= disruption[2]:
            print 'Current Time slot:',  str(time), '(Disruption happened in Region '+str(disruption[0])+')','~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'
        else:
            print 'Current Time slot:', str(time), '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'

        print "number of Vacant Vehicles:",sum(Vacant[i, l] for i in range(n) for l in range(L)),"number of Occupied Vehicles:",sum(Occupied[i, l] for i in range(n) for l in range(L))

        # print "current time horizon:",ctimehorizon

        X, Y = dir.mpc.mpc_iteration(time, ctimehorizon, Vacant, Occupied, beta, chargingresource, futuresupply,disruption)

        demand, cdemand, supply, total_slot_served, total_demand, \
        energystatus, chargingstatus, chargestation, occupancystatus, location, \
        remainingchargingtime, remainingtriptime, destination, idledrivingtime, \
        withoutwaitingtime, dispatchedtime = dir.update_dis.update_status_withdisruption(
            time,L,L1,L2,p,distance,disruption,X,Y,
            energystatus, chargingstatus, chargestation, occupancystatus,
            location, remainingchargingtime, remainingtriptime, destination, idledrivingtime,
            withoutwaitingtime, dispatchedtime
        )

        print'Passenger served ratio in this time slot:',total_slot_served
        print'total demand',total_demand
        # print len(total_slot_served),len(total_slot_served[0])
        passenger_served.append(total_slot_served)
        passenger_demand.append(total_demand)

        '''计算prefix sum'''
        chargingresource = []
        for i in range(n):
            gg = []
            for j in range(timehorizon):
                gg.append(0)
                # chargingresource[i][j]=0
            chargingresource.append(gg)
        for i in range(n):
            for l in range(L):
                for k in range(K):
                    futuresupply[i, l, k] = 0
        # for i in range(n):
        #     for k in range(timehorizon):
        #         if chargingresource[i][k]>p[i]:
        #             print ('NNGGGGGGGGGGGGGGGNNNNNNNNNNNNNNNNNNNNNNNN')

        '''更新各个region的charging points的状态'''
        for id in range(n):
            # print id
            # print chargingresource
            scheduling = [] # scheduling 的长度取决于第id个region有多少个charging points X 4 个time horizion
            ''' scheduling 模拟charging position的每个charging point的可用状态'''
            for j in range(p[id]):
                one = []
                for k in range(timehorizon):
                    one.append(0)
                scheduling.append(one)
            stationid = id
            for j in range(num_of_v):
                if chargingstatus[j] == 2 and chargestation[j] == stationid: #在region id处充电的vehicle
                    point = 0 # 循环每个point
                    num_of_cps = p[id]
                    if id in disruption[0] and time >= disruption[1] and time<= disruption[2]:
                        num_of_cps = 0
                    for z in range(num_of_cps):
                        if scheduling[z][0] == 0: #在第0个horizon的 第 pid个 charging point 是空的
                            point = z
                            break
                    for k in range(remainingchargingtime[j]):
                        # 如果在disruption region就不会进到这个循环
                        scheduling[point][k] = 1
                        futuresupply[id, energystatus[j] + remainingchargingtime[j] * L2, remainingchargingtime[j]] += 1
            waitinfonew = []
            for j in range(len(energystatus)):
                if chargingstatus[j] == 1 and chargestation[j] == stationid:
                    info = [j, dispatchedtime[j], remainingchargingtime[j]]
                    waitinfonew.append(info)
            waitinfonew = sorted(waitinfonew, key=lambda x: (x[1], x[2]))

            #waitinfornew中不会出现 disruption的信息
            for k in waitinfonew:
                j = k[0]
                point = 0
                starttime = 0
                for z in range(timehorizon):
                    find = False
                    for y in range(p[id]):
                        if scheduling[y][z] == 0:
                            point = y
                            starttime = z
                            find = True
                            break
                    if find:
                        break
                if remainingchargingtime[j] + starttime < timehorizon:
                    futuresupply[
                        id, energystatus[j] + remainingchargingtime[j] * L2, remainingchargingtime[j] + starttime] += 1
                for k in range(starttime, min(timehorizon, remainingchargingtime[j] + starttime)):
                    scheduling[point][k] = 1

            for k in range(timehorizon):
                cnum = sum(scheduling[j][k] for j in range(p[id]))
                chargingresource[id][k] = cnum
                # if chargingresource[id][k]>p[id]:
                #     print '---------------------------EEEEEEEOOOOOOOOOOOOOOOOOOOOOORRRRRRRRRRRRRRRRRRR'
            # print id
            # print chargingresource
            # print '--------------'

        # for i in range(n):
        #     print p[i],chargingresource[i]

        '''重新更新occupied和vaccant送下一次迭代'''
        for i in range(n):
            for j in range(L):
                Occupied[i, j] = 0
                Vacant[i, j] = 0
        for i in range(len(energystatus)):
            if occupancystatus[i] == 1 and chargingstatus[i] == 0: # 在载客 不在充电
                Occupied[location[i], energystatus[i]] += 1
            elif occupancystatus[i] == 0 and chargingstatus[i] == 0: # 不在载客 不在充电
                if energystatus[i] == 0: #彻底没电了 不载客也不充电
                    print("energystatus = 0", i)
                Vacant[location[i], energystatus[i]] += 1

        unratio = ud.calculate_region_ratio(n, demand, supply)
        regionratio.append(unratio)

        print 'chargingstatus:', chargingstatus
        chgstatus.append(chargingstatus[:])
        chgstation.append(chargestation[:])
        energy_total.append(energystatus[:])
        print 'chargingstation:',chargestation
        # print(disruption[0] in chargestation)
        print 'energystatus:',energystatus
        print 'location:',location
        occupy_total.append(occupancystatus[:])
        print 'occupystatus',occupancystatus

        for i in range(len(chargestation)):
            vehicle_status.append([time,i,location[i],chargingstatus[i],chargestation[i],occupancystatus[i],energystatus[i],remainingchargingtime[i],remainingtriptime[i]])

        if sum(demand) > 0:
            print('supply:',sum(supply),'demand:', sum(demand), '1-c:',max(0, 1 - float(sum(supply)) / sum(demand)))
            supplydemand.append([sum(supply), sum(demand), max(0, 1 - float(sum(supply)) / sum(demand))])
        else:
            print('supply:',sum(supply),'demand', sum(demand), 'dmand=0, 1-c',0.00) #Why 0.00
            supplydemand.append([sum(supply), sum(demand), 0.0])

        if time == 71:
            fwrite1 = open('./resultdata/beta/p2chargingutilization1-' + str(timehorizon) + '-' + str(beta)+'-'+str(round), 'w')
            for i in range(len(energystatus)):
                fwrite1.write(str(idledrivingtime[i]) + '\n')
            fwrite1.close()

        if time == 71:
            fwrite1 = open('./resultdata/beta/p2withoutwaitingtime-' + str(timehorizon) + '-' + str(beta)+'-'+str(round), 'w')
            for i in range(len(energystatus)):
                fwrite1.write(str(withoutwaitingtime[i]) + '\n')
            fwrite1.close()

            # fwrite2 = open('./resultdata/beta/chargestatus/chargingstatus'+'-'+str(round),'w')
            # for i in range(len(chgstatus)):
            #     fwrite2.write(str(chgstatus[i])+'\n')
            # fwrite2.close()
            # fwrite3 = open('./resultdata/beta/chargestatus/chargingstation'+'-'+str(round),'w')
            # for i in range(len(chgstation)):
            #     fwrite3.write(str(chgstation[i])+'\n')
            # fwrite3.close()
            #
            # fwrite4 = open('./resultdata/beta/chargestatus/energystatus'+'-'+str(round),'w')
            # for i in range(len(energy_total)):
            #     fwrite4.write(str(energy_total[i])+'\n')
            # fwrite4.close()
            #
            # fwrite5 = open('./resultdata/beta/chargestatus/occupystatus'+'-'+str(round),'w')
            # for i in range(len(occupy_total)):
            #     fwrite5.write(str(occupy_total[i])+'\n')
            # fwrite5.close()
            fwrite6 = open('./resultdata/beta/chargestatus/passenger-served'+'-'+str(round),'w')
            for i in range(len(passenger_served)):
                for j in range(0,len(passenger_served[i])):
                    fwrite6.write(str(passenger_served[i][j])+'\n')
                for j in range(0,len(passenger_demand[i])):
                    fwrite6.write(str(passenger_demand[i][j])+'\n')
            fwrite6.close()


            # print('passenger served ration in each time slot:',passenger_served)


    fwrite2 = open('./resultdata/beta/temporalsupplydemand1-' + str(timehorizon) + '-' + str(beta)+'-'+str(round), 'w')
    for k in supplydemand:
        fwrite2.write(str(k[0]) + ',' + str(k[1]) + ',' + str(k[2]) + '\n')
    fwrite2.close()

    fwrite1 = open('./resultdata/beta/regionratio1-' + str(timehorizon) + '-' + str(beta)+'-'+str(round), 'w')
    for k in regionratio:
        for kk in k:
            fwrite1.write(str(kk) + ',')
        fwrite1.write('\n')
    fwrite1.close()

    fwrite3 = open('./resultdata/beta/chargestatus/Vehicle_Status'+'-'+str(round), 'w')
    for i in range(len(vehicle_status)):
        fwrite3.write(str(vehicle_status[i])+'\n')
    fwrite3.close()

    # vehicle_status = np.array(vehicle_status)
    # # [time, i, location[i], chargingstatus[i], chargestation[i], occupancystatus[i], energystatus[i],
    # #  remainingchargingtime[i], remainingtriptime[i]])
    # df = pd.DataFrame(vehicle_status, columns=['Timeslot','Vehicle_ID','Charge_Status','Charge_Station','Occupy_Status','EnergyStatus','Remain_Charging_Time','Remain_Trip_Time'])
    # df.to_csv('./resultdata/beta/chargestatus/occupystatus/Vehicle_Status'+'-'+str(round),index = False)

    # if sum(scheduling[point,0] for point in range(p[i]))>p[i]:
    #     print 'HAHHAHHAHHHHAHAHH'
    # for j in range(len(energystatus)):
    #     if chargingstatus[j]==1 and chargestation[j]==stationid:
    #         point=0
    #         starttime=0
    #         for z in range(timehorizon):
    #             find =False
    #             for y in range(p[i]):
    #                 if scheduling[y,z]==0:
    #                     point =y
    #                     starttime=z
    #                     find =True
    #                     break
    #             if find:
    #                 break
    #         if remainingchargingtime[j]+ starttime<timehorizon:
    #             futuresupply[i,energystatus[j]*remainingchargingtime[j]*L2,remainingchargingtime[j]+ starttime] += 1
    #         for k in range(starttime,min(timehorizon,remainingchargingtime[j]+starttime)):
    #             scheduling[point,k]=1
