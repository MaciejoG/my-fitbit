#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import libraries
import gather_keys_oauth2 as Oauth2
import fitbit
import pandas as pd 
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime, date, timedelta
import myfitnesspal
import numpy as np


# In[2]:


# Make Postgre connection
host="46.101.121.37"
port=5432
database="postgres"
user="maciejo95"
password="Starku990i!"
conn = psycopg2.connect(host=host,port=port,database=database, user=user, password=password)
# create a cursor
cur = conn.cursor()
# execute a statement
print('PostgreSQL database version:')
cur.execute('SELECT version()')
# display the PostgreSQL database server version
db_version = cur.fetchone()
print(db_version)
# create engine to connect to SQLAlchemy
engine = create_engine("postgresql://"+user+":"+password+"@"+host+":"+str(port)+"/"+database)


# In[3]:


# Fitbit client's credentials (only for the first time)
CLIENT_ID='22BVRZ'
CLIENT_SECRET='537115c6ca15d92468947f56fc05317d'
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMkJWUloiLCJzdWIiOiI3WFZUMk4iLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcmFjdCBybG9jIHJ3ZWkgcmhyIHJudXQgcnBybyByc2xlIiwiZXhwIjoxNTk3MjExODg4LCJpYXQiOjE1OTcxODMwODh9.VHjTNl3NZgTHWK7dNQcJ_aKI7H-xrN8rlBJRSiaS3Fk"
EXPIRES_AT = 604800
REFRESH_TOKEN = "f6d1640ff94098b3ca5094a0261820453c1861509a79d49e5b847db827c381cd"


# In[4]:


# Create credentials table (to be used when running for the first time)
def createCredentialsTable():
    try:
        engine.execute('''CREATE TABLE IF NOT EXISTS fitbit_credentials (skey SERIAL PRIMARY KEY, client_id VARCHAR(50), client_secret VARCHAR(50), access_token VARCHAR(500), refresh_token VARCHAR(500), expires_at INT);''')
    except Exception as exc:
        print("Error:")
        print(exc)


# In[5]:


# Insert credentials into credentials table (to be used when running for the first time)
def insertCredentials():
    try:
        engine.execute('''INSERT INTO fitbit_credentials(client_id, client_secret, access_token, refresh_token, expires_at) VALUES (%s,%s,%s,%s,%s);''',(CLIENT_ID,CLIENT_SECRET,ACCESS_TOKEN,REFRESH_TOKEN,EXPIRES_AT,))
    except Exception as exc:
        print("Error:")
        print(exc)


# In[6]:


# Retrieve access_token, refresh_token and expires_at from db
try:
    cur.execute('''SELECT client_id, client_secret, access_token, refresh_token, expires_at FROM fitbit_credentials ORDER BY skey DESC LIMIT 1;''')
    fetched_data = cur.fetchall() 
    client_id = fetched_data[0][0]
    client_secret = fetched_data[0][1]
    access_token = fetched_data[0][2]
    refresh_token = fetched_data[0][3]
    expires_at = fetched_data[0][4]
except Exception as exc:
    print("Error:")
    print(exc)


# In[7]:


# Define callback function (to be used during fitbit authorization process)
def refreshCB(token):
    """ Called when the OAuth token has been refreshed """
    client_id='22BVRZ'
    client_secret='537115c6ca15d92468947f56fc05317d'
    access_token = token['access_token']
    refresh_token = token['refresh_token']
    expires_at = token['expires_at']
    try:
        engine.execute('''INSERT INTO fitbit_credentials(client_id, client_secret, access_token, refresh_token, expires_at) VALUES (%s,%s,%s,%s,%s);''',(client_id,client_secret,access_token,refresh_token,expires_at,))
    except Exception as exc:
        print("Error:")
        print(exc)


# In[8]:


# Authorize fitbit
try:
    cur.execute('''SELECT client_id, client_secret, access_token, refresh_token, expires_at FROM fitbit_credentials ORDER BY skey DESC LIMIT 1;''')
    fetched_data = cur.fetchall() 
    client_id = fetched_data[0][0]
    client_secret = fetched_data[0][1]
    access_token = fetched_data[0][2]
    refresh_token = fetched_data[0][3]
    expires_at = fetched_data[0][4]
    # Fitbit authorization process
    authd_client = fitbit.Fitbit(client_id=client_id, client_secret=client_secret, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at, refresh_cb=refreshCB, redirect_uri='https://google.com', system='en_UK')
except Exception as exc:
    print("Error:")
    print(exc)


# In[9]:


# Function to initialize dates for improting and create date-range
def daterange(start_date, end_date):
    if (start_date > end_date):
        # Flip dates
        temp_date = start_date
        start_date = end_date
        end_date = temp_date
    datetime_range_list = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]
    dates_list = []
    for d in datetime_range_list:
        dates_list.append(d)
        # dates_list.append(d.strftime("%Y-%m-%d")) # uncomment to get the list of strings
    return dates_list


# In[22]:


# Select last entry date from db
try:
    cur.execute('''SELECT date FROM hr ORDER BY date DESC LIMIT 1;''')
    fetched_data = cur.fetchall() 
    last_entry_date = fetched_data[0][0]
    today = date.today()
    # Some data will output error if attempted to fetch before "today" is over, fetch only data until yesterday
    base_date = today - timedelta(days=1)
    # Need to add "1" as we don't want to fetch the same day again (fitbit fetches inclusive base_date and end_date)
    end_date = last_entry_date + timedelta(days=1)
    print("Last entry date: " + str(last_entry_date))
    print("Today's date:", today)
    print("Attempt to update from " + str(end_date) + " (inclusive) to " + str(base_date) + " (inclusive)")
    if (base_date >= end_date):
        # Create dates range list
        dates_list = daterange(base_date, end_date)
        print("Will update data for " + str(len(dates_list)) + " day(s):")
        print(dates_list)
    else:
        print("Too early for an update")
except Exception as exc:
    print("Error:")
    print(exc)


# In[15]:


# Activity data
def getActivityData(authd_client,base_date,end_date):

    # Get activity data
    # Get the top level time series for calories burned inclusive of BMR, tracked activity, and manually logged activities
    calories_total = authd_client.time_series(resource="activities/calories", user_id=None, base_date=base_date, period=None, end_date=end_date)
    # Get only BMR calories
    calories_bmr = authd_client.time_series(resource="activities/caloriesBMR", user_id=None, base_date=base_date, period=None, end_date=end_date)
    # Get the number of calories burned during the day for periods of time when the user was active above sedentary level. This value is calculated minute by minute for minutes that fall under this criteria. This includes BMR for those minutes as well as activity burned calories.
    calories_activity = authd_client.time_series(resource="activities/activityCalories", user_id=None, base_date=base_date, period=None, end_date=end_date)
    # Get steps count, distance, minutes (sedentary and lightly/fairly/very active)
    steps = authd_client.time_series(resource="activities/steps", user_id=None, base_date=base_date, period=None, end_date=end_date)
    distance = authd_client.time_series(resource="activities/distance", user_id=None, base_date=base_date, period=None, end_date=end_date)
    sedentary_minutes = authd_client.time_series(resource="activities/minutesSedentary", user_id=None, base_date=base_date, period=None, end_date=end_date)
    lightly_active_minutes = authd_client.time_series(resource="activities/minutesLightlyActive", user_id=None, base_date=base_date, period=None, end_date=end_date)
    fairly_active_minutes = authd_client.time_series(resource="activities/minutesFairlyActive", user_id=None, base_date=base_date, period=None, end_date=end_date)
    very_active_minutes = authd_client.time_series(resource="activities/minutesVeryActive", user_id=None, base_date=base_date, period=None, end_date=end_date)

    # Insert activity data into pandas df
    df_activity_data = pd.DataFrame(columns=['date', 'calories_total', 'calories_bmr', 'calories_activity', 'steps', 'distance', 'sedentary_minutes', 'lightly_active_minutes', 'fairly_active_minutes', 'very_active_minutes'])
    for i in range(len(calories_total['activities-calories'])):
        # Get date
        day = dates_list[i]
        # Get the top level time series for calories burned inclusive of BMR, tracked activity, and manually logged activities
        daily_calories_total = int(calories_total['activities-calories'][i]['value'])
        # Get only BMR calories
        daily_calories_bmr = int(calories_bmr['activities-caloriesBMR'][i]['value'])
        # Get the number of calories burned during the day for periods of time when the user was active above sedentary level. This value is calculated minute by minute for minutes that fall under this criteria. This includes BMR for those minutes as well as activity burned calories.
        daily_calories_activity = int(calories_activity['activities-activityCalories'][i]['value'])
        # Get steps count, distance, minutes (sedentary and lightly/fairly/very active)
        daily_steps = int(steps['activities-steps'][i]['value'])
        daily_distance = float(distance['activities-distance'][i]['value'])
        daily_sedentary_minutes = int(sedentary_minutes['activities-minutesSedentary'][i]['value'])
        daily_lightly_active_minutes = int(lightly_active_minutes['activities-minutesLightlyActive'][i]['value'])
        daily_fairly_active_minutes = int(fairly_active_minutes['activities-minutesFairlyActive'][i]['value'])
        daily_very_active_minutes = int(very_active_minutes['activities-minutesVeryActive'][i]['value'])
        # Append to df
        df_activity_data = df_activity_data.append({'date':day, 'calories_total':daily_calories_total, 'calories_bmr':daily_calories_bmr, 'calories_activity':daily_calories_activity, 'steps':daily_steps, 'distance':daily_distance, 'sedentary_minutes':daily_sedentary_minutes, 'lightly_active_minutes':daily_lightly_active_minutes, 'fairly_active_minutes':daily_fairly_active_minutes, 'very_active_minutes':daily_very_active_minutes}, ignore_index=True)

    # Insert activity data into db
    df_activity_data.to_sql(name="activities", con=engine, if_exists="append", index=False, chunksize=None, method=None) 


# In[16]:


# Fat data
def getFatData(authd_client,base_date,end_date):

    # Download fat, weight and bmi data
    # Body-weight (incl. fat)
    body_weight = authd_client.time_series(resource="body/weight", user_id=None, base_date=base_date, period=None, end_date=end_date)
    # Fat
    fat = authd_client.time_series(resource="body/fat", user_id=None, base_date=base_date, period=None, end_date=end_date)
    # BMI
    bmi = authd_client.time_series(resource="body/bmi", user_id=None, base_date=base_date, period=None, end_date=end_date)

    # Insert fat, weight and bmi data into pandas df
    df_body_data = pd.DataFrame(columns=['date', 'weight', 'fat', 'bmi'])
    dates_list = daterange(end_date, base_date)
    for i in range(len(body_weight['body-weight'])):
        # Get date
        day = dates_list[i]
        # Get weight
        daily_weight = float(body_weight['body-weight'][i]['value'])
        # Get fat
        daily_fat = float(fat['body-fat'][i]['value'])
        # Get bmi
        daily_bmi = float(bmi['body-bmi'][i]['value'])
        # Append to df
        df_body_data = df_body_data.append({'date':day, 'weight':daily_weight, 'fat':daily_fat, 'bmi':daily_bmi}, ignore_index=True)

    # Insert fat, weight and bmi data into db
    df_body_data.to_sql(name="body", con=engine, if_exists="append", index=False, chunksize=None, method=None) 


# In[17]:


# Sleep data

def getSleepData(authd_client,base_date,end_date):

    # Insert sleep data into pandas df
    df_sleep_data = pd.DataFrame(columns=['date','total_in_bed_minutes','total_asleep_minutes','total_awake_minutes','total_sleep_efficiency','total_deep_sleep_minutes','total_light_sleep_minutes','total_rem_sleep_minutes','total_wake_minutes','total_sleep_recordings'])

    # Get sleep series data for every month between start and end dates - the granuality of data should be days, not sleep logs
    for day in dates_list:
        # This is probably very inefficient, but I couldn't find an easy eay to fetch sleep-details (deep, rem, light, wake) using time_series...
        sleep_data = authd_client.get_sleep(date=day)
        date = day
        total_in_bed_minutes = sleep_data['summary']['totalTimeInBed']
        # On some days the sleep was not logged, in these cases append None
        if (total_in_bed_minutes > 0):
            total_asleep_minutes = sleep_data['summary']['totalMinutesAsleep']
            total_awake_minutes = total_in_bed_minutes - total_asleep_minutes
            total_sleep_efficiency = total_asleep_minutes / total_in_bed_minutes
            total_sleep_recordings = sleep_data['summary']['totalSleepRecords']
            total_minutes_stages = []
            # For some reason, these stages are not always present, if they are missing - append None
            for stage in ['deep','light','rem','wake']:
                try:
                    total_minutes_stages.append(sleep_data['summary']['stages'][stage])
                except:
                    total_minutes_stages.append(None)      
        else:
            total_in_bed_minutes = None
            total_asleep_minutes = None
            total_awake_minutes = None
            total_sleep_efficiency = None
            total_sleep_recordings = None
            total_minutes_stages = [None, None, None, None]
        # Append to dataframe
        df_sleep_data = df_sleep_data.append({'date':date,'total_in_bed_minutes':total_in_bed_minutes,'total_asleep_minutes':total_asleep_minutes,'total_awake_minutes':total_awake_minutes,'total_sleep_efficiency':total_sleep_efficiency,'total_deep_sleep_minutes':total_minutes_stages[0],'total_light_sleep_minutes':total_minutes_stages[1],'total_rem_sleep_minutes':total_minutes_stages[2],'total_wake_minutes':total_minutes_stages[3],'total_sleep_recordings':total_sleep_recordings}, ignore_index=True)

    # Insert sleep data into db
    df_sleep_data.to_sql(name="sleep", con=engine, if_exists="append", index=False, chunksize=None, method=None) 


# In[18]:


# Hr data

def getHrData(authd_client,base_date,end_date):

    # Donwload Hr data
    hr = authd_client.time_series(resource="activities/heart", user_id=None, base_date=base_date, period=None, end_date=end_date)
    
    # Insert hr data into pandas df
    df_hr_data = pd.DataFrame(columns=['date', 'out_of_range_calories', 'out_of_range_minutes', 'fat_burn_calories', 'fat_burn_minutes', 'cardio_calories', 'cardio_minutes', 'peak_calories', 'peak_minutes', 'resting_hr'])
    for i in range(len(hr['activities-heart'])):
        # Get date
        day = dates_list[i]
        # Get remaining data
        temp_calories = []
        temp_minutes = []
        for j in range(4):
            try:
                temp_calories.append(float(hr['activities-heart'][i]['value']['heartRateZones'][j]['caloriesOut']))
            except:
                temp_calories.append(None)
            try:
                temp_minutes.append(int(hr['activities-heart'][i]['value']['heartRateZones'][j]['minutes']))
            except:
                temp_minutes.append(None)
        try:
            resting_hr = int(hr['activities-heart'][i]['value']['restingHeartRate'])
        except:
            resting_hr = None
        # Append to df
        df_hr_data = df_hr_data.append({'date':day, 'out_of_range_calories':temp_calories[0], 'out_of_range_minutes':temp_minutes[0], 'fat_burn_calories':temp_calories[1], 'fat_burn_minutes':temp_minutes[1], 'cardio_calories':temp_calories[2], 'cardio_minutes':temp_minutes[2], 'peak_calories':temp_calories[3], 'peak_minutes':temp_minutes[3], 'resting_hr':resting_hr}, ignore_index=True)

    # Insert hr data into db
    df_hr_data.to_sql(name="hr", con=engine, if_exists="append", index=False, chunksize=None, method=None) 


# In[19]:


# Food data

def getFoodData(authd_client,base_date,end_date):

    # MyFitnessPal client login
    client = myfitnesspal.Client('blackez43', password='Starku990i!')

    # Get data from MyFitnessPal
    df_mfp = pd.DataFrame(columns=['date', 'calories_total', 'calories_breakfast', 'calories_lunch', 'calories_dinner', 'calories_snack1', 'calories_snack2', 'carbohydrates_total', 'carbohydrates_breakfast', 'carbohydrates_lunch', 'carbohydrates_dinner', 'carbohydrates_snack1', 'carbohydrates_snack2','fat_total', 'fat_breakfast', 'fat_lunch', 'fat_dinner', 'fat_snack1', 'fat_snack2', 'protein_total', 'protein_breakfast', 'protein_lunch', 'protein_dinner', 'protein_snack1', 'protein_snack2', 'sodium_total', 'sodium_breakfast', 'sodium_lunch', 'sodium_dinner', 'sodium_snack1', 'sodium_snack2', 'sugar_total', 'sugar_breakfast', 'sugar_lunch', 'sugar_dinner', 'sugar_snack1', 'sugar_snack2'])
    for day in dates_list:
        # Retrieve daily data
        daily_data = client.get_date(day)
        # Transform data
        gen_data = []
        for gen_temp in ['calories','carbohydrates','fat','protein','sodium','sugar']:
            try:
                gen_data.append(daily_data.totals[gen_temp])
            except:
                gen_data.append(None)
        # Transform meals data (5 meals)
        meal_data = [[],[],[],[],[]]
        for meal in range(5):
            for gen_temp in ['calories','carbohydrates','fat','protein','sodium','sugar']:
                try:
                    meal_data[meal].append(daily_data.meals[meal].totals[gen_temp])
                except:
                    meal_data[meal].append(None)
        # Insert data into df
        df_mfp = df_mfp.append({'date':day, 
    'calories_total':gen_data[0], 'calories_breakfast':meal_data[0][0], 'calories_lunch':meal_data[1][0], 'calories_dinner':meal_data[2][0], 'calories_snack1':meal_data[3][0], 'calories_snack2':meal_data[4][0], 'carbohydrates_total':gen_data[1], 'carbohydrates_breakfast':meal_data[0][1], 'carbohydrates_lunch':meal_data[1][1], 'carbohydrates_dinner':meal_data[2][1], 'carbohydrates_snack1':meal_data[3][1], 'carbohydrates_snack2':meal_data[4][1],
    'fat_total':gen_data[2], 'fat_breakfast':meal_data[0][2], 'fat_lunch':meal_data[1][2], 'fat_dinner':meal_data[2][2], 'fat_snack1':meal_data[3][2], 'fat_snack2':meal_data[4][2], 
    'protein_total':gen_data[3], 'protein_breakfast':meal_data[0][3], 'protein_lunch':meal_data[1][3], 'protein_dinner':meal_data[2][3], 'protein_snack1':meal_data[3][3], 'protein_snack2':meal_data[4][3], 
    'sodium_total':gen_data[4], 'sodium_breakfast':meal_data[0][4], 'sodium_lunch':meal_data[1][4], 'sodium_dinner':meal_data[2][4], 'sodium_snack1':meal_data[3][4], 'sodium_snack2':meal_data[4][4], 
    'sugar_total':gen_data[5], 'sugar_breakfast':meal_data[0][5], 'sugar_lunch':meal_data[1][5], 'sugar_dinner':meal_data[2][5], 'sugar_snack1':meal_data[3][5], 'sugar_snack2':meal_data[4][5]}, ignore_index=True)

    # Insert mfp data into db
    df_mfp.to_sql(name="food", con=engine, if_exists="append", index=False, chunksize=None, method=None) 


# In[23]:


print("Current time: " + str(datetime.now()))
if (base_date >= end_date):
    print("Getting fitbit and mfp data")
    getActivityData(authd_client,base_date,end_date)
    getFatData(authd_client,base_date,end_date)
    getSleepData(authd_client,base_date,end_date)
    getHrData(authd_client,base_date,end_date)
    getFoodData(authd_client,base_date,end_date)
    print("Data inserted successfully")
else:
    print("No data to update")
print("--------------------------------------")
# %%
