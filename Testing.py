import pandas as pd 
import csv 
from datetime import *
from dateutil import parser

    
month_dic = {

    "1": "January",
    "2": "February",
    "3": "March",
    "4": "April",
    "5": "May",
    "6": "June",
    "7": "July",
    "8": "August",
    "9": "September",
    "10": "October",
    "11": "November",
    "12": "December"

}



# Def for calculate the number of days between 2 dates
def diff_month(dt1, dt2):
    return (dt1.year - dt2.year) * 12 + (dt1.month - dt2.month)


# Def to get the number of date into a specific month
def numberOfDays(y, m):
    leap = 0
    if y % 400 == 0:
        leap = 1
    elif y % 100 == 0:
        leap = 0
    elif y % 4 == 0:
        leap = 1
    if m == 2:
        return 28 + leap
    list = [1, 3, 5, 7, 8, 10, 12]
    if m in list:
        return 31
    return 30

#Def to get the RSI with pandas
def RSI(data, length, column="price"):
    delta = data[column].diff(1)
    delta = delta[1:]
    up = delta.copy()
    down = delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    data['up'] = up
    data['down'] = down
    AVG_Gain = SMA(data, length, 'up')
    AVG_Lose = abs(SMA(data, length, 'down'))
    RS = AVG_Gain / AVG_Lose
    RSI = 100.0 - (100.0 / (1.0 + RS))
    data['RSI'] = RSI
    return data

#Calculate the SMA with pandas
def SMA(data, period, column):
    return data[column].rolling(window=period).mean()

#Get the percentage profit
def Percentage(number):
    x = number[0]
    y = number[1]
    percentage_prof = ((float(y) - float(x)) / float(y)) * 100
    return round(percentage_prof,2)


def SimpleStrat(Buyat, Sellat, Datestart, Datend,sl,tp):
    day_lst = []
    prof_lst = []
    lstTs = []
    datas_ = []
    doll_prof_lst = []

    year_start = int(Datestart[:4])
    month_start = int(Datestart[5:7])
    day_start = int(Datestart[8:10])

    year_end = int(Datend[:4])
    month_end = int(Datend[5:7])
    day_end = int(Datend[8:10])

    # Update a date by adding value to day,month and day
    dt1 = date(year_start, month_start, day_start)
    dt2 = date(year_end, month_end, day_end)
    delta = dt2 - dt1
    diff_days = (delta.days + 1)
    diff_months = diff_month(datetime(year_end, month_end, day_end), datetime(year_start, month_start, day_start))

    # Calculate number of days for each month
    if diff_months == 0:  # means it's the on the same month
        day_lst.append(diff_days)

    elif diff_months == 1:  # means difference of months is minimum  1 month
        time1 = numberOfDays(year_start, month_start) - day_start
        time2 = day_end
        day_lst.append(time1)
        day_lst.append(time2)

    elif diff_months > 1:  # means the difference of months is more than 1 month
        time1 = (numberOfDays(year_start, month_start) + 1) - day_start
        time2 = day_end
        months = month_start
        years = year_start
        for x in range(diff_months - 1):
            if months < 12:
                months += 1
            elif months == 12:
                months = 1
                years += 1
            day_lst.append(numberOfDays(years, months))
        day_lst.insert(0, time1)
        day_lst.insert(len(day_lst), time2)

    else:
        print("Error date!")

    month = month_start - 1
    year = year_start
    days = day_start - 1

    sum = 0
    gross_lose = 0
    gross_prof = 0
    number_trade = 0
    num_wins = 0
    num_loses = 0
    sum_doll = 0
    gross_lose_doll = 0
    gross_prof_doll = 0
    totalTrades = 0

    for times in range(diff_months + 1):
        if month < 12:
            month += 1
        elif month == 12:
            month = 1
            year += 1
        for day in range(1, day_lst[times] + 1):
            if days == 31:
                days = 1
            elif days < 31:
                days += 1

            if month < 10:
                Month = f"0{month}"
            else:
                Month = f"{month}"

            if days < 10:
                Day = f"0{days}"
            else:
                Day = f"{days}"

            date_index = f"{year}-{Month}-{Day}"
            files = f"BTCUSD{year}-{Month}-{Day}"
            print(files)

            table = pd.read_csv(f"Archive Datas/{month_dic[str(month)]} {year}/{files}.csv")
            ts = table['timestamp']

            # Convert column timestamp(float64) to int64 column
            ts_int = ts.astype('int64')

            # Create variable for search a certain timestamp
            DateBuy = datetime.strptime(f"{date_index} {Buyat}", '%Y-%m-%d %H:%M:%S')
            DateSell = datetime.strptime(f"{date_index} {Sellat}", '%Y-%m-%d %H:%M:%S')

            # Convert time to timestamp gmt
            ts_buy = DateBuy.replace(tzinfo=timezone.utc).timestamp()
            ts_sell = DateSell.replace(tzinfo=timezone.utc).timestamp()


            # Filter the column timestamp
            buyPrices = table.loc[ts_int == ts_buy]["price"].to_string(index=True)
            sellPrices = table.loc[ts_int == ts_sell]["price"].to_string(index=True)


            # Rectification of hours if failed
            count_hb_sec = int(str(Buyat)[6:8])
            count_hs_sec = int(str(Sellat)[6:8])
            count_hb_min = int(str(Buyat)[3:5])
            count_hs_min = int(str(Sellat)[3:5])
            count_hb_h = int(str(Buyat)[:2])
            count_hs_h = int(str(Sellat)[:2])
            hourBuy = str(Buyat)[:2] 
            minuteBuy = str(Buyat)[3:5]
            secondBuy = str(Buyat)[6:8]
            hourSell = str(Sellat)[:2]
            minuteSell = str(Sellat)[3:5]
            secondSell = str(Sellat)[6:8]

            if buyPrices == 'Series([], )':
                while buyPrices == 'Series([], )':
                    if count_hb_sec < 59:  # Update second
                        count_hb_sec += 1
                        if count_hb_sec < 10:
                            secondBuy = f"0{count_hb_sec}"
                        else:
                            secondBuy = f"{count_hb_sec}"
                           
                    elif count_hb_sec > 59:  # Switch update minute
                        count_hb_sec = 0
                        count_hb_min += 1
                        if count_hb_min < 10:
                            minuteBuy = f"0{count_hb_min}"
                        else:
                            minuteBuy = f"{count_hb_min}"

                    elif count_hb_min > 59:
                        count_hb_min = 0
                        count_hb_h += 1
                        if count_hb_h < 10:
                            hourBuy = f"0{count_hb_h}"
                        else:
                            hourBuy = f"{count_hb_h}"
                        
                    hour_rectif = f"{hourBuy}:{minuteBuy}:{secondBuy}"
                    DateBuy = datetime.strptime(f"{date_index} {hour_rectif}", '%Y-%m-%d %H:%M:%S')

                    ts_buy = DateBuy.replace(tzinfo=timezone.utc).timestamp()
                    buyPrices = table.loc[ts_int == ts_buy]["price"].to_string(index=True)
                    lstTs.append(ts_buy)
                buyPrices = buyPrices.split()
                lp_buy = float(buyPrices[1])
                indexBuy = int(buyPrices[0])
                print(f"The rectified hour is ==> {DateBuy}")
                print(f"The buy last price is (rectification) ==> {lp_buy}")

            else:
                lstTs.append(ts_buy)
                buyPrices = buyPrices.split()
                lp_buy = float(buyPrices[1])
                indexBuy = int(buyPrices[0])
                print(f"The buy last price is ==> {lp_buy}")


            if sellPrices == 'Series([], )':
                while sellPrices == 'Series([], )':
                    if count_hs_sec < 59:  # Update second
                        count_hs_sec += 1
                        if count_hs_sec < 10:
                            secondSell = f"0{count_hs_sec}"
                        else:
                            secondSell = f"{count_hs_sec}"
                        
                    elif count_hs_sec > 59:  # Switch to the minute update
                        count_hs_sec = 0
                        count_hs_min += 1
                        if count_hs_min < 10:
                            minuteSell = f"0{count_hs_min}"
                        else:
                            minuteSell = f"{count_hs_min}"

                    elif count_hs_min > 59:
                        count_hs_min = 0
                        count_hs_h = 0
                        if count_hs_h < 10:
                            hourSell = f"0{count_hs_h}"
                        else:
                            hourSell = f"{count_hs_h}"
                        
                    
                    hour_rectif = f"{hourSell}:{minuteSell}:{secondSell}"
                    DateSell = datetime.strptime(f"{date_index} {hour_rectif}", '%Y-%m-%d %H:%M:%S')
                    ts_sell = DateSell.replace(tzinfo=timezone.utc).timestamp()
                    sellPrices = table.loc[ts_int == ts_sell]["price"].to_string(index=True)
                sellPrices = sellPrices.split()
                lp_sell = float(sellPrices[1])
                indexSell = int(sellPrices[0])
                print(f"The rectified hour is ==> {DateSell}")
                print(f"The sell last price is (rectification) ==> {lp_sell}")

            else:
                sellPrices = sellPrices.split()
                lp_sell = float(sellPrices[1])
                indexSell = int(sellPrices[0])
                print(f"The sell last price is ==> {lp_sell}")



            # We gonna slice the dataframe to get the period between the time buy and sell
            frame = table.iloc[indexSell:indexBuy][['timestamp','price']]
            framePrices = list(frame['price'])
            framePrices.reverse()
            if sl and tp != 0:
                for index in range(len(framePrices)):
                    percentage_prof = ((framePrices[index] - lp_buy) / framePrices[index]) * 100
                    if percentage_prof <= sl:
                        tsLoss = frame.iloc[-index]['timestamp']
                        timeLoss = datetime.utcfromtimestamp(tsLoss).strftime("%H:%M:%S")
                        print(f"The stop loss hits. At {timeLoss}")
                        break
                    elif percentage_prof >= tp:
                        tsProf = frame.iloc[-index]['timestamp']
                        timeProf = datetime.utcfromtimestamp(tsProf).strftime("%H:%M:%S")
                        print(f"The take profit hits. At {timeProf}")
                        break
            else:
                percentage_prof = ((lp_sell - lp_buy) / lp_sell) * 100
                

            dollar_prof = (framePrices[index] - lp_buy)
            print(f"The dollar profit is ==> {dollar_prof}$")
            print(f"The percentage profit is => {round(percentage_prof,3)}%")
            prof_lst.append(round(percentage_prof,3))
            doll_prof_lst.append(dollar_prof)
            totalTrades += 2
           

    lst_lst = [lstTs,prof_lst]
    for x,y in zip(*lst_lst):
        value = {'time':float(x),'value':float(y)}
        datas_.append(value)

     # Get the sum profit, gross lose and wins
    for x in prof_lst:
        sum += x
        if x < 0:
            num_loses += 1
            gross_lose += x
        if x > 0:
            num_wins += 1
            gross_prof += x
    sum = round(sum,1)
    gross_lose = round(gross_lose,1)
    gross_prof = round(gross_prof,1)


    # Get sum, gross lose and wins in dollars value
    for i in doll_prof_lst:
        sum_doll += i
        if i > 0:
            gross_prof_doll += i
        if i < 0:
            gross_lose_doll += i

    return datas_,sum,totalTrades,gross_lose, gross_prof, num_loses, num_wins, sum_doll, gross_prof_doll, gross_lose_doll




def FundingStrat(TimeFrame ,Datestart, Datend,sl,tp):
    lst_2d_ts = []
    day_lst = []
    lst_2d_prof = []
    doll_prof_lst = []
    datas_ = []
    markers = []
    count = 0
    
    _8am = "08:00:00"
    _4pm = "16:00:00"
    _12pm = "23:59:59"
    _00am = "00:00:30"

    if TimeFrame == "1":
        before_8am = "07:00:00"
        after_8am = "09:00:00"
        before_4pm = "15:00:00"
        after_4pm = "17:00:00"
        before_12pm = "23:00:00"
        after_12pm = "01:00:00"

    elif TimeFrame == "2":
        before_8am = "07:30:00"
        after_8am = "08:30:00"
        before_4pm = "15:30:00"
        after_4pm = "16:30:00"
        before_12pm = "23:30:00"
        after_12pm = "00:30:00"

    elif TimeFrame == "3":
        before_8am = "07:45:00"
        after_8am = "08:15:00"
        before_4pm = "15:45:00"
        after_4pm = "16:15:00"
        before_12pm = "23:45:00"
        after_12pm = "00:15:00"

    year_start = int(Datestart[:4])
    month_start = int(Datestart[5:7])
    day_start = int(Datestart[8:10])

    year_end = int(Datend[:4])
    month_end = int(Datend[5:7])
    day_end = int(Datend[8:10])

    # Count number of days between two date
    dt1 = date(year_start, month_start, day_start)
    dt2 = date(year_end, month_end, day_end)
    delta = dt2 - dt1
    diff_days = (delta.days + 1)
    diff_months = diff_month(datetime(year_end, month_end, day_end), datetime(year_start, month_start, day_start))

    # Calculate number of days for each month
    if diff_months == 0:  # means it's the on the same month
        day_lst.append(diff_days)

    elif diff_months == 1:  # means difference of months is minimum  1 month
        time1 = numberOfDays(year_start, month_start) - day_start
        time2 = day_end
        day_lst.append(time1)
        day_lst.append(time2)

    elif diff_months > 1:  # means the difference of months is more than 1 month
        time1 = (numberOfDays(year_start, month_start) + 1) - day_start
        time2 = day_end
        months = month_start
        years = year_start
        for x in range(diff_months - 1):
            if months < 12:
                months += 1
            elif months == 12:
                months = 1
                years += 1
            day_lst.append(numberOfDays(years, months))
        day_lst.insert(0, time1)
        day_lst.insert(len(day_lst), time2)

    else:
        print("Error date!")

    month = month_start - 1
    year = year_start
    days = day_start - 1


    sum = 0
    gross_lose = 0 
    gross_prof = 0
    number_trade = 0
    num_wins = 0
    num_loses = 0 
    sum_doll = 0 
    gross_lose_doll = 0
    gross_prof_doll = 0


    for times in range(diff_months + 1):
        if month < 12:
            month += 1
        elif month == 12:
            month = 1
            year += 1
        for day in range(1,day_lst[times] + 1):
            prof_lst = []
            lstTs = []  
            if days == 31:
                days = 1
            elif days < 31:
                days += 1

            if month < 10:
                Month = f"0{month}"
            else:
                Month = f"{month}"

            if days < 10:
                Day = f"0{days}"
            else:
                Day = f"{days}"

            date_index = f"{year}-{Month}-{Day}"
            files = f"BTCUSD{year}-{Month}-{Day}"
            print(files)

            table = pd.read_csv(f"Archive Datas/{month_dic[str(month)]} {year}/{files}.csv")
            ts = table['timestamp']

            # Convert column timestamp(float64) to int64 column
            ts_int = ts.astype('int64')

            # Create variable for search a certain timestamp
            
            TimeBefore8am = datetime.strptime(f"{date_index} {before_8am}", '%Y-%m-%d %H:%M:%S')
            Time8am = datetime.strptime(f"{date_index} {_8am}", '%Y-%m-%d %H:%M:%S')
            TimeAfter8am = datetime.strptime(f"{date_index} {after_8am}", '%Y-%m-%d %H:%M:%S')

           
            TimeBefore4pm = datetime.strptime(f"{date_index} {before_4pm}", '%Y-%m-%d %H:%M:%S')
            Time4pm = datetime.strptime(f"{date_index} {_4pm}", '%Y-%m-%d %H:%M:%S')
            TimeAfter4pm = datetime.strptime(f"{date_index} {after_4pm}", '%Y-%m-%d %H:%M:%S')

           
            TimeBefore12pm = datetime.strptime(f"{date_index} {before_12pm}", '%Y-%m-%d %H:%M:%S')
            TimeMidnight = datetime.strptime(f"{date_index} {_00am}", '%Y-%m-%d %H:%M:%S')
            Time12pm = datetime.strptime(f"{date_index} {_12pm}", '%Y-%m-%d %H:%M:%S')
            TimeAfter12pm = datetime.strptime(f"{date_index} {after_12pm}", '%Y-%m-%d %H:%M:%S')
             

            # Convert time to timestamp gmt
            ts_before_8am = TimeBefore8am.replace(tzinfo=timezone.utc).timestamp()
            ts_8am = Time8am.replace(tzinfo=timezone.utc).timestamp()
            ts_after_8am = TimeAfter8am.replace(tzinfo=timezone.utc).timestamp()

            ts_before_4pm = TimeBefore4pm.replace(tzinfo=timezone.utc).timestamp()
            ts_4pm = Time4pm.replace(tzinfo=timezone.utc).timestamp()
            ts_after_4pm = TimeAfter4pm.replace(tzinfo=timezone.utc).timestamp()

            ts_before_12pm = TimeBefore12pm.replace(tzinfo=timezone.utc).timestamp()
            ts_12pm = Time12pm.replace(tzinfo=timezone.utc).timestamp()
            ts_00am = TimeMidnight.replace(tzinfo=timezone.utc).timestamp()
            ts_after_12pm = TimeAfter12pm.replace(tzinfo=timezone.utc).timestamp()

            #Add to list day 
            lstTs.append(ts_before_8am)
            lstTs.append(ts_8am)
            lstTs.append(ts_before_4pm)
            lstTs.append(ts_4pm)
            lstTs.append(ts_before_12pm)
            lstTs.append(ts_12pm)

            lst_2d_ts.append(lstTs)


            # Filter the column timestamp
            Before8amPrices = table.loc[ts_int == ts_before_8am]["price"].to_string(index=True).split()
            _8amPrices = table.loc[ts_int == ts_8am]["price"].to_string(index=True).split()
            After8amPrices = table.loc[ts_int == ts_after_8am]["price"].to_string(index=True).split()
           
            Before4pmPrices = table.loc[ts_int == ts_before_4pm]["price"].to_string(index=True).split()
            _4pmPrices = table.loc[ts_int == ts_4pm]["price"].to_string(index=True).split()
            After4pmPrices = table.loc[ts_int == ts_after_4pm]["price"].to_string(index=True).split()
           
            Before12pmPrices = table.loc[ts_int == ts_before_12pm]["price"].to_string(index=True).split()
            _12pmPrices = table.loc[ts_int == ts_12pm]["price"].to_string(index=True).split()
            _00amPrices = table.loc[ts_int == ts_00am]["price"].to_string(index=True).split()
            After12pmPrices = table.loc[ts_int == ts_after_12pm]["price"].to_string(index=True).split()

            # Calculate the profit between last prices
 
            try:
                LpBefore8am = float(Before8amPrices[1])
                indexBefore8am = int(Before8amPrices[0])
                Lp8am = float(_8amPrices[1])
                index8am = int(_8amPrices[0])
            
                frameBefore8am = table.iloc[index8am:indexBefore8am][['timestamp','price']]
                print(frameBefore8am)
                frameBefore8amPrices = list(frameBefore8am['price'])
                frameBefore8amPrices.reverse()
                if sl and tp != 0:
                    for index in range(len(frameBefore8amPrices)):
                        percentage_prof1 = ((frameBefore8amPrices[index] - LpBefore8am) / frameBefore8amPrices[index]) * 100
                        if percentage_prof1 <= sl:
                            tsLoss = frameBefore8am.iloc[-index]['timestamp']
                            timeLoss = datetime.utcfromtimestamp(tsLoss).strftime("%H:%M:%S")
                            print(f'Stop loss hits at {timeLoss}')
                            break
                        elif percentage_prof1 >= tp:
                            tsProfit = frameBefore8am.iloc[-index]['timestamp']
                            timeProfit = datetime.utcfromtimestamp(tsProfit).strftime("%H:%M:%S")
                            print(f"Take profit hits at {timeProfit}")
                            break
                    dollar_prof1 = (frameBefore8amPrices[index] - LpBefore8am)
                else:
                    percentage_prof1 = ((Lp8am - LpBefore8am) / Lp8am) * 100
                    dollar_prof1 = (Lp8am - LpBefore8am)
                
                
                print(f"The percentage prof between buy and sell prices is ==> {round(percentage_prof1, 3)}%")
                prof_lst.append(round(percentage_prof1,3))
                doll_prof_lst.append(dollar_prof1)

            except Exception as e:
                prof_lst.append(0)
                doll_prof_lst.append(0)
                print(f"Problem occured ==> {e}")
                pass


            try:
                Lp8am = float(_8amPrices[1])
                index8am = int(_8amPrices[0])
                LpAfter8am = float(After8amPrices[1])
                indexAfter8am = int(After8amPrices[0])

                frame8am = table.iloc[indexAfter8am:index8am][['timestamp','price']]
                frame8amPrices = list(frame8am['price'])
                frame8amPrices.reverse()
                if sl and tp != 0:
                    for index in range(len(frame8amPrices)):
                        percentage_prof2 = ((frame8amPrices[index] - Lp8am) / frame8amPrices[index]) * 100
                        if percentage_prof2 <= sl:
                            tsLoss = frame8am.iloc[-index]['timestamp']
                            timeLoss = datetime.utcfromtimestamp(tsLoss).strftime("%H:%M:%S")
                            print(f'Stop loss hits at {timeLoss}')
                            break
                        elif percentage_prof2 >= tp:
                            tsProfit = frame8am.iloc[-index]['timestamp']
                            timeProfit = datetime.utcfromtimestamp(tsProfit).strftime("%H:%M:%S")
                            print(f"Take profit hits at {timeProfit}")
                            break
                    dollar_prof2 = (frame8amPrices[index] - Lp8am)
                else:
                    percentage_prof2 = ((LpAfter8am - Lp8am) / LpAfter8am) * 100
                    dollar_prof2 = (LpAfter8am - Lp8am)
            
                print(f"The percentage prof between buy and sell prices is ==> {round(percentage_prof2, 3)}%")
                prof_lst.append(round(percentage_prof2, 3))
                doll_prof_lst.append(dollar_prof2)
                
            except Exception as e:
                prof_lst.append(0)
                doll_prof_lst.append(0)
                print(f"Problem occured ==> {e}")
                pass

            try:
                LpBefore4pm = float(Before4pmPrices[1])
                indexBefore4pm = int(Before4pmPrices[0])
                Lp4pm = float(_4pmPrices[1])
                index4pm = int(_4pmPrices[0])
                
                frameBefore4pm = table.iloc[index4pm:indexBefore4pm][['timestamp','price']]
                frameBefore4pmPrices = list(frameBefore4pm['price'])
                frameBefore4pmPrices.reverse()
                if sl and tp != 0:
                    for index in range(len(frameBefore4pmPrices)):
                        percentage_prof3 = ((frameBefore4pmPrices[index] - LpBefore4pm) / frameBefore4pmPrices[index]) * 100
                        if percentage_prof3 <= sl:
                            tsLoss = frameBefore4pm.iloc[-index]['timestamp']
                            timeLoss = datetime.utcfromtimestamp(tsLoss).strftime("%H:%M:%S")
                            print(f'Stop loss hits at {timeLoss}')
                            break
                        elif percentage_prof3 >= tp:
                            tsProfit = frameBefore4pm.iloc[-index]['timestamp']
                            timeProfit = datetime.utcfromtimestamp(tsProfit).strftime("%H:%M:%S")
                            print(f"Take profit hits at {timeProfit}")
                            break
                    dollar_prof3 = (frameBefore4pmPrices[index] - LpBefore4pm)
                else:
                    percentage_prof3 = ((Lp4pm - LpBefore4pm) / Lp4pm) * 100
                    dollar_prof3 = (Lp4pm - LpBefore4pm)

                print(f"The percentage prof between buy and sell prices is ==> {round(percentage_prof3, 3)}%")
                prof_lst.append(round(percentage_prof3, 3))
                doll_prof_lst.append(dollar_prof3)
            except Exception as e:
                prof_lst.append(0)
                doll_prof_lst.append(0)
                print(f"Problem occured ==> {e}")
                pass

            try:
                Lp4pm = float(_4pmPrices[1])
                index4pm = int(_4pmPrices[0])
                LpAfter4pm = float(After4pmPrices[1])
                indexAfter4pm = int(After4pmPrices[0])

                frame4pm = table.iloc[indexAfter4pm:index4pm][['timestamp','price']]
                frame4pmPrices = list(frame4pm['price'])
                frame4pmPrices.reverse()
                if sl and tp != 0:
                    for index in range(len(frame4pmPrices)):
                        percentage_prof4 = ((frame4pmPrices[index] - Lp4pm) / frame4pmPrices[index]) * 100
                        if percentage_prof4 <= sl:
                            tsLoss = frame4pm.iloc[-index]['timestamp']
                            timeLoss = datetime.utcfromtimestamp(tsLoss).strftime("%H:%M:%S")
                            print(f'Stop loss hits at {timeLoss}')
                            break
                        elif percentage_prof4 >= tp:
                            tsProfit = frame4pm.iloc[-index]['timestamp']
                            timeProfit = datetime.utcfromtimestamp(tsProfit).strftime("%H:%M:%S")
                            print(f"Take profit hits at {timeProfit}")
                            break

                    dollar_prof4 = (frame4pmPrices[index] - Lp4pm)
                else:
                    percentage_prof4 = ((LpAfter4pm - Lp4pm) / LpAfter4pm) * 100
                    dollar_prof4 = (LpAfter4pm - Lp4pm)


                print(f"The percentage prof between buy and sell prices is ==> {round(percentage_prof4, 3)}%")
                prof_lst.append(round(percentage_prof4, 3))
                doll_prof_lst.append(dollar_prof4)
                
            except Exception as e:
                prof_lst.append(0)
                doll_prof_lst.append(0)
                print(f"Problem occured ==> {e}")
                pass


            try:
                LpBefore12pm = float(Before12pmPrices[1])
                indexBefore12pm = int(Before12pmPrices[0])
                Lp12pm = float(_12pmPrices[1])
                index12pm = int(_12pmPrices[0])

                frameBefore12pm = table.iloc[index12pm:indexBefore12pm][['timestamp','price']]
                frameBefore12pmPrices = list(frameBefore12pm['price'])
                frameBefore12pmPrices.reverse()
                if sl and tp != 0:
                    for index in range(len(frameBefore12pmPrices)):
                        percentage_prof5 = ((frameBefore12pmPrices[index] - LpBefore12pm) / frameBefore12pmPrices[index]) * 100
                        if percentage_prof5 <= sl:
                            tsLoss = frameBefore12pm.iloc[-index]['timestamp']
                            timeLoss = datetime.utcfromtimestamp(tsLoss).strftime("%H:%M:%S")
                            print(f'Stop loss hits at {timeLoss}')
                            break
                        elif percentage_prof5 >= tp:
                            tsProfit = frameBefore12pm.iloc[-index]['timestamp']
                            timeProfit = datetime.utcfromtimestamp(tsProfit).strftime("%H:%M:%S")
                            print(f"Take profit hits at {timeProfit}")
                            break

                    dollar_prof5 = (frameBefore12pmPrices[index] - LpBefore12pm)
                else:
                    percentage_prof5 = ((Lp12pm - LpBefore12pm) / Lp12pm) * 100
                    dollar_prof5 = (Lp12pm - LpBefore12pm)

                print(f"The percentage prof between buy and sell prices is ==> {round(percentage_prof5, 3)}%")
                prof_lst.append(round(percentage_prof5, 3))
                doll_prof_lst.append(dollar_prof5)

            except Exception as e:
                prof_lst.append(0)
                doll_prof_lst.append(0)
                print(f"Problem occured ==> {e}")
                pass

            lst_2d_prof.append(prof_lst)

            if len(lst_2d_prof) >= 2:
                try:
                    LpMidnight = float(_00amPrices[1])
                    indexMidnight = int(_00amPrices[0])
                    LpAfter12pm = float(After12pmPrices[1])
                    indexAfter12pm = int(After12pmPrices[0])

                    frameMidnight = table.iloc[indexAfter12pm:indexMidnight][['timestamp','price']]
                    frameMidnightPrices = list(frameMidnight['price'])
                    frameMidnightPrices.reverse()
                    if sl and tp != 0:
                        for index in range(len(frameMidnightPrices)):
                            percentage_prof6 = ((frameMidnightPrices[index] - LpMidnight) / frameMidnightPrices[index]) * 100
                            if percentage_prof6 <= sl:
                                tsLoss = frameMidnight.iloc[-index]['timestamp']
                                timeLoss = datetime.utcfromtimestamp(tsLoss).strftime("%H:%M:%S")
                                print(f'Stop loss hits at {timeLoss}')
                                break
                            elif percentage_prof6 >= tp:
                                tsProfit = frameMidnight.iloc[-index]['timestamp']
                                timeProfit = datetime.utcfromtimestamp(tsProfit).strftime("%H:%M:%S")
                                print(f"Take profit hits at {timeProfit}")
                                break
                        dollar_prof6 = (frameMidnightPrices[index] - LpMidnight)
                    else:
                        percentage_prof6 = ((LpAfter12pm - LpMidnight) / LpAfter12pm) * 100
                        dollar_prof6 = (LpAfter12pm - LpMidnight)

                    print(f"The percentage prof between buy and sell prices is ==> {round(percentage_prof6, 3)}%")
                    index_ = len(lst_2d_prof) - 2 
                    lst_2d_prof[index_].append(round(percentage_prof6,3))
                    doll_prof_lst.append(dollar_prof6)
                   
                except Exception as e:
                    index_ = len(lst_2d_prof) - 2 
                    lst_2d_prof[index_].append(0)
                    doll_prof_lst.append(0)
                    print(f"Problem occured ==> {e}")
                    pass

         
    lst_lst = [lst_2d_ts,lst_2d_prof]
    index = 0 
    for x,i in zip(*lst_lst):
        lst_lst2 = [x,i]
        for z,y in zip(*lst_lst2):
            value = {"time":float(z),"value":float(y)}
            datas_.append(value)


    # Get the number of trades, net profit, gross profit and lose in %
    for arrays in lst_2d_prof:
        for x in arrays:
            sum += x
            if x > 0:
                num_wins += 1 
                gross_prof += x
            if x < 0:
                num_loses += 1
                gross_lose += x
            

    # Get sum, gross profit and lose in dollars
    for dolls in doll_prof_lst:
        sum_doll += dolls
        if dolls > 0:
            gross_prof_doll += dolls
        if dolls < 0:
            gross_lose_doll += dolls



    return datas_,sum,gross_lose,gross_prof, num_loses,num_wins ,sum_doll,gross_prof_doll, gross_lose_doll




def RSIStrat(rsiBuy, rsiSell, length, Datestart, Datend,sl,tp,capital,size):
    lstProfit = []
    day_lst = []
    datas_ = []
    markerDatas_ = []
    markerPosition = []
    RSI_ = []
    Wins = 0
    Loses = 0
    index_rsi = 0
    on_position = False
    year_start = int(Datestart[:4])
    month_start = int(Datestart[5:7])
    day_start = int(Datestart[8:10])

    year_end = int(Datend[:4])
    month_end = int(Datend[5:7])
    day_end = int(Datend[8:10])

    # Update a date by adding value to day,month and day
    dt1 = date(year_start, month_start, day_start)
    dt2 = date(year_end, month_end, day_end)
    delta = dt2 - dt1
    diff_days = (delta.days + 1)
    diff_months = diff_month(datetime(year_end, month_end, day_end), datetime(year_start, month_start, day_start))

    # Calculate number of days for each month
    if diff_months == 0:  # means it's the on the same month
        day_lst.append(diff_days)

    elif diff_months == 1:  # means difference of months is minimum  1 month
        time1 = numberOfDays(year_start, month_start) - day_start
        time2 = day_end
        day_lst.append(time1)
        day_lst.append(time2)

    elif diff_months > 1:  # means the difference of months is more than 1 month
        time1 = (numberOfDays(year_start, month_start) + 1) - day_start
        time2 = day_end
        months = month_start
        years = year_start
        for x in range(diff_months - 1):
            if months < 12:
                months += 1
            elif months == 12:
                months = 1
                years += 1
            day_lst.append(numberOfDays(years, months))
        day_lst.insert(0, time1)
        day_lst.insert(len(day_lst), time2)

    else:
        print("Error date!")

    month = month_start - 1
    year = year_start
    days = day_start - 1
    for times in range(diff_months + 1):
        if month < 12:
            month += 1
        elif month == 12:
            month = 1
            year += 1
        for day in range(day_lst[times]):
            if days == 31:
                days = 1
            elif days < 31:
                days += 1

            if month < 10:
                Month = f"0{month}"
            else:
                Month = f"{month}"

            if days < 10:
                Day = f"0{days}"
            else:
                Day = f"{days}"

            date_index = f"{year}-{Month}-{Day}"
            files = f"BTCUSD{date_index}.csv"
            print(files)
            table = pd.read_csv(f"Archive Datas/{month_dic[str(month)]} {year}/{files}")
            ts_table = table['timestamp']

            # Convert the column timestamp to integer elements
            table_int = ts_table.astype("int64")
            table.drop(columns="timestamp", inplace=True)
            table["timestamp"] = table_int
            table.drop_duplicates(subset='timestamp', inplace=True)
            data = RSI(table, length)
            data.drop(columns=['up', 'down'], inplace=True)

            lstData = [data['RSI'].to_string(index=False).split(), data['timestamp'].to_string(index=False).split(),
                       data['price'].to_string(index=False).split()]
            lstTs = []
            exitPos = []
            lstData[0].reverse()
            lstData[1].reverse()
            lstData[2].reverse()
            lst_lst = [lstData[1], lstData[2]]
            index = 0
            indexBuy = 0
            frame = []
            Indexs = []
            lstRSI = [lstData[0],lstData[1]]


            for x, y in zip(*lst_lst):
                value = {'time': float(x), 'value': float(y)}
                datas_.append(value)
            

            for u,z in zip(*lstRSI):
                rsiValue = {'time':float(z),'value':float(u)}
                RSI_.append(rsiValue)


            for rsi in lstData[0]:
                if float(rsi) <= rsiBuy and not on_position:
                    Wins += 1
                    on_position = True
                    lstTs.append(lstData[1][index])
                    indexBuy = index
                if float(rsi) >= rsiSell and on_position:
                    Loses += 1
                    lstTs.append(lstData[1][index])
                    indexSell = index
                    on_position = False
                    Indexs.append(indexBuy)
                    frame.append(lstData[2][indexBuy:indexSell])
                index += 1

            count = 0
            for periods in frame:
                Count = 0
                buyPrice = periods[0]
                sellPrice = periods[-1]
                Index = Indexs[count]
                count += 1
                if sl and tp != 0:
                    for price in periods:
                        percentage_prof = ((float(price) - float(buyPrice)) / float(size)) * 100
                        if percentage_prof <= sl:
                            tsLoss = lstData[1][Index + Count]
                            print(f"The stop loss hits.At {tsLoss}")
                            exitPos.append(tsLoss)
                            lstProfit.append(sl)
                            break
                        if percentage_prof >= tp:
                            tsProf = lstData[1][Index + Count]
                            print(f"The take profit hits.At {tsProf}")
                            exitPos.append(tsProf)
                            lstProfit.append(tp)
                            break
                        Count += 1
                    dollar_prof = ((float(price) - float(buyPrice)) / float(price))
                else:
                    dollar_prof = ((float(sellPrice) - float(buyPrice)) / float(size))
                    percentage_prof = dollar_prof * 100
                    lstProfit.append(percentage_prof)

                    

            # Check stop loss and take profit
            for x in lstTs:
                if (index_rsi % 2) == 0:
                    markers = {'time': float(x), 'position': 'aboveBar', 'color': 'rgba(63,190,232,0.8)',
                               'shape': 'arrowUp', 'size': 1, 'text': 'Buy'}
                    markerDatas_.append(markers)
                else:
                    markers = {'time': float(x), 'position': 'aboveBar', 'color': 'rgba(240,55,55,0.8)',
                               'shape': 'arrowDown', 'size': 1, 'text': 'Sell'}
                    markerDatas_.append(markers)

                index_rsi += 1

            for i in exitPos:
                marker = {'time': float(i), 'position': 'aboveBar', 'color': 'rgba(240,55,55,0.8)',
                           'shape': 'arrowDown', 'size': 1, 'text': 'Exit Position'}
                markerPosition.append(marker)

            
    grossLose = 0
    grossWins = 0
    sum = 0

    for prof in lstProfit:
        sum += prof
        if prof < 0:
            grossLose += prof
        elif prof > 0:
            grossWins += prof
    
    
    print("This is the net profit ==>",sum)
     

            
    return datas_,markerDatas_,sum,grossWins,grossLose,Wins,Loses,RSI_


