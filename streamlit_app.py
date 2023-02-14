import datetime

import pandas as pd
import streamlit as st

def update_first_number():
    day = st.session_state.date.day
    month = st.session_state.date.month
    year = st.session_state.date.year
    if day < 10:
        if month < 10:
            st.session_state.file_date = '{}/0{}0{}0000'.format(year, month, day)
        else:
            st.session_state.file_date = '{}/{}0{}0000'.format(year, month, day)
    else:
        st.session_state.file_date = '{}/{}{}0000'.format(year, month, day)


def update_number(date):
    st.write(date)
    st.session_state.date = date
    st.session_state.file_date = date
    day = date.day
    month = date.month
    year = date.year
    string = str(year) + "/"
    if month < 10:
        string = string + "0" + str(month)
    else: 
        string = string + str(month)
    if day < 10:
        string = string + "0" + str(day) + "0000"
    else: 
        string = string + str(day) + "0000" 
    st.session_state.file_date = string

if "date" not in st.session_state:
    st.session_state.date = datetime.datetime(2023, 1, 7).date()
    st.session_state.file_date = datetime.datetime(2023, 1, 7).date()
    update_first_number()

# Usage Data
def usage_data(date):
    df = pd.read_csv('./data/{}.CSV'.format(st.session_state.file_date), skipfooter=1, skiprows=16,
                    parse_dates=True, usecols=['Date', 'P_Avg[W]'])

    df['Date'] = pd.to_datetime(df['Date'])
    return df

def getSolarFileNumber(date):
    day = date.day
    month = date.month
    year = date.year
    string = str(year)
    if month < 10:
        string = string + "0" + str(month-1)
    else: 
        string = string + str(month-1)
    if day < 10:
        string = string + "" + str(day - 1)
    else: 
        string = string + str(day-1)
    return string

# Solar Data
def solar_data(date):
    df = usage_data(date)
    st.write(str(date))
    solar = getSolarFileNumber(date)
    st.write(solar)
    dfsolar = pd.read_csv('./solardata/{}.CSV'.format(solar),
                    parse_dates=True, usecols=['Date', ' data'])
    dfsolar['Date'] = pd.to_datetime(dfsolar['Date'], unit='ms', utc=True)
    dfsolar['Date'] = dfsolar['Date'].dt.tz_convert('Pacific/Auckland')
    dfsolar['Date'] = dfsolar['Date'].dt.tz_localize(None)

    New_df = pd.DataFrame(pd.date_range(
    pd.to_datetime(df['Date'][0]),
    pd.to_datetime(df['Date'][len(df['Date'])-1]),
    freq='300S',),columns=['Date']).merge(
        dfsolar,on=['Date'],how='outer').fillna(0)
    
    overall_df = pd.DataFrame(New_df.merge(
        df,on=['Date'],how='outer'))
    st.session_state.overall_df = overall_df
    selectedDate = overall_df['Date'][1].date()
    st.session_state.date = overall_df['Date'][1].date()
    update_number(selectedDate)
    return overall_df

# APP
st.title('Chia Solar Monitoring App', anchor=None)
st.subheader('Usage for {}'.format(st.session_state.date))

date_input = st.date_input(
    'Selected Date', st.session_state.date)

update_number(date_input)
datea = solar_data(st.session_state.date)

st.write(datea)
st.line_chart(datea[['Date', 'P_Avg[W]', ' data']], x='Date')
