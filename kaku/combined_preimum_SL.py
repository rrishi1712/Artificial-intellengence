import pandas as pd
import datetime
import re
from operator import add

def get_expiry_date(s):
    date_idx = re.search(r"\d", s).start()
    return s[date_idx : date_idx + 7] 

def convert_to_datetime(s):

    try:
        out_val = datetime.datetime.strptime(s, '%Y/%m/%d')
    except:
        try:
            out_val = datetime.datetime.strptime(s, '%y/%m/%d')
        except:
            
            try:
                out_val = datetime.datetime.strptime(s.upper(),'%d%b%y')
            except:
                try:
                    out_val = datetime.datetime.strptime(s, '%Y-%m-%d')
                except:
                    pass


    return out_val


def date_to_string(s):
    return convert_to_datetime(s).strftime('%d%b%y').upper()


def weekday_data():
    data = pd.read_csv("/Users/upendrasingh/Documents/AlgoIIFL/Nifty_Bank/2016.csv")
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.loc[data['Date'].apply(datetime.date.weekday) == 3]
    data.to_csv("nifty_bank_2018_thursday.csv", index = False)
    thursday_date_open = data[['Date', 'Open']]

    return thursday_date_open

open_df = weekday_data()
# print("Niifty_Bank_2019.csv", open_df)


def calc_strike_price(open_df):
    percentage_open_price = abs((open_df['Open'] * 1.5) / 100)
    up_open_price = round((open_df['Open'] + percentage_open_price), -2)
    up_df = up_open_price
    down_open_price = round((open_df['Open'] - percentage_open_price), -2)
    down_df = down_open_price
    open_df["1.5% up(CE)"] = up_df
    open_df["1.5% down(PE)"] = down_df
    
    return open_df

df = calc_strike_price(open_df)
# print("CE & PE data -->>", df)

def fetch_banknifty_strike_price():

    # data = pd.read_csv("2016.csv", usecols = ['Ticker', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest'])
    # ticker_df = data.loc[(((data['Ticker'].str.contains('BANKNIFTY')) & ((data['Ticker'].str.contains('CE') | (data['Ticker'].str.contains('PE'))))))]
    # ticker_df['Date'] = ticker_df['Date'].apply(convert_to_datetime)
    # print(ticker_df['Date'])
    ticker_df = ticker_df.loc[ticker_df['Date'].apply(datetime.date.weekday) == 3]

    ticker_df.to_csv('2018_thursdays.csv', index = False)
    print(ticker_df)
    
    return ticker_df



banknifty_data = pd.read_csv('2018_thursdays.csv')
banknifty_data['Expiry Date'] = banknifty_data['Ticker'].apply(get_expiry_date)
banknifty_data['Date'] = banknifty_data['Date'].apply(date_to_string)
banknifty_data = banknifty_data.loc[banknifty_data['Expiry Date'] == banknifty_data['Date']]
banknifty_data.to_csv('2018_output.csv')

banknifty_data = pd.read_csv('2018_output.csv')

ce_out = []
pe_out = []
time = []
df['Date'] = df['Date'].astype(str).apply(date_to_string)
output_df = []
for idx, rows in df.iterrows():

    # print(banknifty_data.loc[banknifty_data.Time.astype(str) == '09:18:59'])
    if rows['1.5% up(CE)'] == rows['1.5% down(PE)']:
        sp_ce = sp_pe = str(int(rows['1.5% up(CE)']))
    elif rows['1.5% up(CE)'] >= rows['1.5% down(PE)']:
        sp_ce = str(int(rows['1.5% up(CE)']))
        sp_pe = str(int(rows['1.5% down(PE)']))
    else:
        sp_pe = str(int(rows['1.5% up(CE)']))
        sp_ce = str(int(rows['1.5% down(PE)']))

    # print(pd.to_timedelta(banknifty_data.Time) >= pd.to_timedelta('09:16:59')) 
    ce = banknifty_data.loc[(banknifty_data.Ticker.str.contains(sp_ce + "CE")) & (pd.to_timedelta(banknifty_data.Time) >= pd.to_timedelta('09:18:59')) & (pd.to_timedelta(banknifty_data.Time) <= pd.to_timedelta('15:14:59')) & (banknifty_data.Date == rows['Date'])]['Close'].tolist()
    pe = banknifty_data.loc[(banknifty_data.Ticker.str.contains(sp_pe + "PE")) & (pd.to_timedelta(banknifty_data.Time) >= pd.to_timedelta('09:18:59')) & (pd.to_timedelta(banknifty_data.Time) <= pd.to_timedelta('15:14:59')) & (banknifty_data.Date == rows['Date'])]['Close'].tolist()
    banknifty_time = banknifty_data.loc[(banknifty_data.Ticker.str.contains(sp_pe + "PE")) & (pd.to_timedelta(banknifty_data.Time) >= pd.to_timedelta('09:18:59')) & (pd.to_timedelta(banknifty_data.Time) <= pd.to_timedelta('15:14:59')) & (banknifty_data.Date == rows['Date'])]['Time'].tolist() 
    for j in range(len(banknifty_time)):
        new_list = []
        try:
            new_list.append(banknifty_time[j])
        except:
            new_list.append('')
        try:
            new_list.append(ce[j])
        except:
            new_list.append('')
        try:
            new_list.append(pe[j])
        except:
            new_list.append('')
        temp_list = list(rows)
        temp_list.extend(new_list)

        output_df.append(temp_list)


final_output = pd.DataFrame(output_df)
print(final_output)
final_output.to_csv('2018_final_output.csv', index= False)

df.reset_index(inplace = True)
# df['09:19 Closed Price Of CE'] = ce_out
# df['09:19 Closed Price Of PE'] = pe_out
# df['Time'] = time
# print(df)
def calc_SL_hit(df):
    df['index'] = range(len(df))
    n = 0
    df['High'] = max(df['Combined Premium'].iloc[1:])
    df['Low']  = min(df['Combined Premium'].iloc[1:])
    cp = df.iloc[0]['Combined Premium']
    cp_1_5 = df.iloc[0]['1.5 times of combined premium']
    cp_1_75 = df.iloc[0]['1.75 times of combined premium']
    cp_double = df.iloc[0]['Double of combined premium']
    for i, row in df.iterrows():
        if row['index'] != 0:
            if (row['Combined Premium'] >= cp_1_5) or (row['Combined Premium'] >= cp_1_75) or (row['Combined Premium'] >= cp_double):
                n = row['index']
                # break
    if n != 0:
        df['SL hit'].iloc[n] = 'Yes'  
    else:
        df['SL hit'].iloc[n] = 'SL not hit'         
    return df.head(n+1)

headers = ['Date', '1.5% UP(CE)', '1.5% DOWN(PE)', 'Time', 'CE Closed Price', 'PE Closed Price']
df = pd.read_csv('2018_final_output.csv', names= headers, header= None, skiprows= [0])
df['Combined Premium'] = df['CE Closed Price'] + df['PE Closed Price']
df['Double of combined premium'] = df['Combined Premium'] * 2
df['1.5 times of combined premium'] = df['Combined Premium'] * 1.5
# df['new_date'] = df['date']
df['1.75 times of combined premium'] = df['Combined Premium'] * 1.75

df['SL hit'] = ''
out_df = pd.DataFrame(columns = df.columns)

grouped_df = df.groupby(['Date'])
for group, df in grouped_df:
    out_df = out_df.append(calc_SL_hit(df))
out_df.reset_index(inplace=True)
out_df['Date'] = out_df['level_0'].astype('datetime64[ns]')
out_df = out_df.drop(columns= ['level_0', 'index'])

out_df = out_df.sort_values(['Date', 'Time'])
out_df.to_csv('2018_SL_hit_output.csv', index=False)
exit()
new_time = []

for i in df['Time']:
   new_time.append(list(i))
df['Time'] = new_time

new_time = []
for i in df['09:19 Closed Price Of CE']:
    new_time.append(list(i))
df['09:19 Closed Price Of CE'] = new_time

new_time = []
for i in df['09:19 Closed Price Of PE']:
    new_time.append(list(i))
df['09:19 Closed Price Of PE'] = new_time

print(type(df['Time'].iloc[0]))
out_df = df.explode("Time").reset_index().drop('index', 1).explode("09:19 Closed Price Of CE").reset_index().drop("index",1).explode("09:19 Closed Price Of PE").reset_index()
# out_df = df.apply(lambda x: x.explode() if x.name in ['ce_out', 'pe_out'] else x)
out_df['Combined Price'] = out_df['09:19 Closed Price Of CE'] + out_df['09:19 Closed Price Of PE']

# out_df = out_df.groupby('level_0').nth([0,-1]).reset_index()
out_df.to_csv("2018_combined_premium.csv", index = False)
print(out_df)


