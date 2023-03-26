# coding=utf-8

import dir.mpc
import dir.update_dis as ud
import dir.data_process as dp


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


def call_mpc(future, beta1, round):
    n, p = dp.obtain_regions()
    L, L1, L2, K = dp.exp_config()

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

    Vacant,Occupied = dp.calculate_VO(n,L,num_of_v,occupancystatus,location,energystatus)

    futuresupply, chargingresource = dp.initial_future_resource(n, L, timehorizon)

    disruption = dp.obtain_disruption()
    print'disruption region: ' + str(disruption[0]), 'disruption start time:', disruption[1], 'disruption end time:', disruption[2]

    passenger_served = []
    passenger_demand = []
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

        if disruption[1] <= time <= disruption[2]:
            print 'Current Time slot:',  str(time), '(Disruption happened in Region '+str(disruption[0])+')','~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'
        else:
            print 'Current Time slot:', str(time), '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`'

        print "number of Vacant Vehicles:",sum(Vacant[i, l] for i in range(n) for l in range(L)),"number of Occupied Vehicles:",sum(Occupied[i, l] for i in range(n) for l in range(L))

        # print "current time horizon:",ctimehorizon

        X, Y = dir.mpc.mpc_iteration(time, ctimehorizon, Vacant, Occupied, beta, chargingresource, futuresupply, disruption)

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


        Vacant, Occupied = ud.update_VO(n,L,num_of_v,occupancystatus,location,energystatus,chargingstatus)
        '''重新更新occupied和vaccant送下一次迭代'''

        futuresupply,chargingresource = ud.update_future_resource(n,L,L2,K,time,num_of_v,p,disruption,timehorizon,
                                                                  chargingstatus,chargestation,energystatus,remainingchargingtime,dispatchedtime)
        unratio = ud.calculate_region_ratio(n, demand, supply)
        print "unratio in each region ", unratio
        regionratio.append(unratio)

        for i in range(len(chargestation)):
            vehicle_status.append([time,i,location[i],chargingstatus[i],chargestation[i],occupancystatus[i],energystatus[i],remainingchargingtime[i],remainingtriptime[i]])

        print 'chargingstatus:', chargingstatus
        print 'chargingstation:',chargestation
        print 'energystatus:',energystatus
        print 'location:',location
        print 'occupystatus',occupancystatus

        if sum(demand) > 0:
            print 'supply:',sum(supply),'demand:', sum(demand), '1-c:',max(0, 1 - float(sum(supply)) / sum(demand))
            supplydemand.append([sum(supply), sum(demand), max(0, 1 - float(sum(supply)) / sum(demand))])
        else:
            print 'supply:',sum(supply),'demand', sum(demand), 'dmand=0, 1-c',0.00 #Why 0.00
            supplydemand.append([sum(supply), sum(demand), 0.0])

    # write idle driving time + waiting for charging time
    fwrite1 = open('./resultdata/beta/p2chargingutilization1-' + str(timehorizon) + '-' + str(beta)+'-'+str(round), 'w')
    for i in range(num_of_v):
        fwrite1.write(str(idledrivingtime[i]) + '\n')
    fwrite1.close()

    # write idle driving only, can calculate idle driving distance 暂时不用 有bug 要修改
    fwrite2 = open('./resultdata/beta/p2withoutwaitingtime-' + str(timehorizon) + '-' + str(beta)+'-'+str(round), 'w')
    for i in range(num_of_v):
        fwrite2.write(str(withoutwaitingtime[i]) + '\n')
    fwrite2.close()

    # every region every timelot, i to j  passenger served 和passenger demand n*n * 2* number of time slot
    fwrite3 = open('./resultdata/beta/chargestatus/passenger-served'+'-'+str(round),'w')
    for i in range(len(passenger_served)):
        for j in range(0,len(passenger_served[i])):
            fwrite3.write(str(passenger_served[i][j])+'\n')
        for j in range(0,len(passenger_demand[i])):
            fwrite3.write(str(passenger_demand[i][j])+'\n')
    fwrite3.close()
            # print('passenger served ration in each time slot:',passenger_served)

    # [total_region_supply, total_Region_demand, k[1]/k[2]]* number of time slot
    fwrite4 = open('./resultdata/beta/temporalsupplydemand1-' + str(timehorizon) + '-' + str(beta)+'-'+str(round), 'w')
    for k in supplydemand:
        fwrite4.write(str(k[0]) + ',' + str(k[1]) + ',' + str(k[2]) + '\n')
    fwrite4.close()

    # number of timeslot * number of regions. ratio of each time each region
    fwrite5 = open('./resultdata/beta/regionratio1-' + str(timehorizon) + '-' + str(beta)+'-'+str(round), 'w')
    for k in regionratio:
        for kk in k:
            fwrite5.write(str(kk) + ',')
        fwrite5.write('\n')
    fwrite5.close()

    # vehicle status in each time slot
    fwrite6 = open('./resultdata/beta/chargestatus/Vehicle_Status'+'-'+str(round), 'w')
    for i in range(num_of_v):
        fwrite6.write(str(vehicle_status[i])+'\n')
    fwrite6.close()

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
