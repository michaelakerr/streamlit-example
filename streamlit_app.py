import datetime

import pandas as pd
import streamlit as st


def update_first_number():
    day = st.session_state.date.day
    month = st.session_state.date.month
    if day < 10:
        if month < 10:
            st.session_state.date = '0{}0{}0000'.format(month, day)
        else:
            st.session_state.date = '{}0{}0000'.format(month, day)
    else:
        st.session_state.date = '{}0{}0000'.format(month, day)


def update_number():
    day = st.session_state.select_input.day
    month = st.session_state.select_input.month
    if day < 10:
        if month < 10:
            st.session_state.date = '0{}0{}0000'.format(month, day)
        else:
            st.session_state.date = '{}0{}0000'.format(month, day)
    else:
        st.session_state.date = '0{}{}0000'.format(month, day)


# https://github.com/mkhorasani/Streamlit-Authenticator
if "date" not in st.session_state:
    st.session_state.date = datetime.datetime(2020, 7, 4).date()
    update_first_number()


df = pd.read_csv('./data/{}.csv'.format(st.session_state.date), skipfooter=1, skiprows=16,
                 parse_dates=True, usecols=['Date', 'P_Avg[W]'])

df['Date'] = pd.to_datetime(df['Date'])

selectedDate = df['Date'][1].date()


# APP

st.title('Chia Solar Monitoring App', anchor=None)
st.subheader('Usage for {}'.format(selectedDate))

st.session_state.select_input = st.date_input(
    'Selected Date', selectedDate, on_change=update_number)
# st.write('Your birthday is:', d)

st.line_chart(df[['Date', 'P_Avg[W]']], x='Date')
st.dataframe(df)
