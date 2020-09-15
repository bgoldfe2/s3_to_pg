#!/usr/bin/env python
"""
Data generation tool for badging data
author: Bruce Goldfeder
date: Aug 25, 2020
"""
import random
import datetime as dt
import pandas as pd
from faker import Faker

#initialize constants
fake=Faker()
Faker.seed(4321)
emp_status = ["IN","OUT"]   # list of status valid values

def first_name_and_gender():
    """Return gender consistent name"""
    fn=''
    mn=''
    g = 'M' if random.randint(0,1) == 0 else 'F'
    if g=='M':
        fn = fake.first_name_male()
        mn = fake.first_name_male()
    else:
        fn = fake.first_name_female()
        mn = fake.first_name_female()

    return fn,mn

def make_g_number():
    """Return formatted approximately unique identifier"""
    return fake.bothify(text='??#########')

def make_kiosk(cur_state,bl_n=4):
    """Return kiosk based on building and user state"""
    if not bl_n:
        bl_n = random.randint(1, 4)
    k=''
    if cur_state == emp_status[0]:
        k = 'Bldg'+str(bl_n)+'_EXIT'
    else:
        k= 'Bldg'+str(bl_n)+'_ENTRY'
    return k

def get_exit_dt(in_dt):
    """Return +8 hours +- 0 to 60 minutes"""

    exit_dt = in_dt + dt.timedelta(hours=9) - dt.timedelta(minutes=random.randint(0,120))
    return exit_dt

def make_badge_data(n_recs=10):
    #set constants
    d = dt.date(2020, 8, 24)
    t = dt.time(8, 0)
    cur_time = dt.datetime.combine(d, t)

    # initial entry of employees
    cols = ['kiosk','tmstamp','emp_id','fname','middle','lname','emp_occupancy']
    df = pd.DataFrame(columns=cols)
    data = []
    for a in range(n_recs):
        fname,mname = first_name_and_gender()
        values = [make_kiosk(emp_status[1]),cur_time,make_g_number(),fname,\
            mname,fake.last_name(),emp_status[0]]
        zipped = zip(cols, values)
        a_dictionary = dict(zipped)
        #print(a_dictionary)
        data.append(a_dictionary)
        cur_time += dt.timedelta(seconds=random.randint(1, 12))

    df_in = df.append(data, True)
    print(df_in)

    # variable duty hours and facility exits
    df_out = pd.DataFrame(columns=cols)
    df_out = df_out.append(df_in, ignore_index = True)
    for b in range(n_recs):
        exit_time = get_exit_dt(df_in['tmstamp'].iloc[b])
        df_out.loc[df_out.index[b], 'tmstamp'] = exit_time
        df_out.loc[df_out.index[b], 'emp_occupancy'] = emp_status[1]
        bl_num = df_in['kiosk'].iloc[b][4]
        df_out.loc[df_out.index[b], 'kiosk'] = make_kiosk(emp_status[0],bl_num)
    df_day = df_in.append(df_out, ignore_index=True)
    df_day.sort_values(['tmstamp'], ignore_index=True, inplace=True)
    df_day = df_day.reset_index(drop=True)
    print(df_day)
    return df_day

def save_data(df):
    df.to_csv('../../data/sec_data.csv', index=False)

def main():
    save_data(make_badge_data())


if __name__ == "__main__":
    main()
