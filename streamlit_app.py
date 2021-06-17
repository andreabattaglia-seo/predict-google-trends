from collections import namedtuple
import altair as alt 
import pandas as pd
import streamlit as st
from pytrends import *
from pytrends.request import TrendReq
import socket, math, datetime
from prophet import Prophet
from requests import get


st.title('Predict Google Trends')
st.text('Get Google Trends data for keywords')


period = 16
ip = get('https://api.ipify.org').text
ip

def main():
    user_input = st.text_input('enter the keyword and press "Make request"')
    if st.button('Make request'):
        with st.spinner("Training ongoing"):
            pytrend = TrendReq(hl='it-IT', tz=360)
            st.write(pytrend.build_payload([f'{user_input}'], cat=0, timeframe='today 5-y', geo='IT', gprop=''))
            data = pytrend.interest_over_time()

            data = data.drop('isPartial', 1)
            data_t = data.T

            #data_t
            #st.text('data')
            #data

            #st.text('data_graph')
            data_graph = data.copy()
            data_graph.reset_index(inplace=True)
            #data_graph
            #print(data_graph.info())
            #st.line_chart(data_graph)
            chart_trend = alt.Chart(data_graph).mark_line().encode(
                x=alt.X('date'),
                y=alt.Y(f'{user_input}')
            ).properties(title="Google Trends")
            st.altair_chart(chart_trend, use_container_width=True)


            data_predict = data.copy()
            data_predict.reset_index(inplace=True)
            #st.text('data_predict')
            #data_predict
            

            data_predict = data_predict.rename(columns={'date': 'ds'})
            data_predict = data_predict.rename(columns={f'{user_input}': 'y'})
            #data_predict.columns = ['ds', 'y']
            #data_predict

            m = Prophet(weekly_seasonality=True)
            m.fit(data_predict)

            future = m.make_future_dataframe(periods=period, freq='W')
            future.tail()
            forecast = m.predict(future)
            forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
            df_prophet = forecast[['ds', 'yhat']]


            #st.text('data_prophet')
            df_prophet = df_prophet.rename(columns={'ds': 'date'})
            df_prophet = df_prophet.rename(columns={'yhat': f'{user_input}'})
            #df_prophet
            print(df_prophet.info())

            chart_prophet = alt.Chart(df_prophet).mark_line().encode(
                x=alt.X('date'),
                y=alt.Y(f'{user_input}')
            ).properties(title="Trend Forecast")
            #st.altair_chart(chart_prophet, use_container_width=True)

            full_df = pd.merge(df_prophet, data_graph, left_on='date', right_on='date', how='left')#.drop('id1', axis=1)
            #full_df

            a = alt.Chart(full_df).mark_area(opacity=0.6).encode(x='date', y=f'{user_input}_x')
            b = alt.Chart(full_df).mark_area(opacity=1).encode(x='date', y=f'{user_input}_y')
            c = alt.layer(a, b).properties(title="Forecast and Trend Comparison")
            st.altair_chart(c, use_container_width=True)


            #
            #
            #
            #Data test
            data_predict = data.copy()
            data_predict.reset_index(inplace=True)
            #st.text('data_predict_1')
            data_predict.drop(index=data_predict.index[-period:], axis=0, inplace=True)
            #st.text('data_predict_2')
            #data_predict

            data_predict = data_predict.rename(columns={'date': 'ds'})
            data_predict = data_predict.rename(columns={f'{user_input}': 'y'})
            #data_predict.columns = ['ds', 'y']
            #data_predict

            m = Prophet(weekly_seasonality=True)
            m.fit(data_predict)

            future = m.make_future_dataframe(periods=period, freq='W')
            future.tail()
            forecast = m.predict(future)
            forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
            df_prophet = forecast[['ds', 'yhat']]


            #st.text('data_prophet')
            df_prophet = df_prophet.rename(columns={'ds': 'date'})
            df_prophet = df_prophet.rename(columns={'yhat': f'{user_input}'})
            #st.text('data_predict_3')
            #df_prophet
            print(df_prophet.info())

            chart_prophet = alt.Chart(df_prophet).mark_line().encode(
                x=alt.X('date'),
                y=alt.Y(f'{user_input}')
            ).properties(title="Trend Forecast")
            #st.altair_chart(chart_prophet, use_container_width=True)

            full_df = pd.merge(df_prophet, data_graph, left_on='date', right_on='date', how='left')#.drop('id1', axis=1)
            #full_df

            a = alt.Chart(full_df).mark_area(opacity=0.6).encode(x='date', y=f'{user_input}_x')
            b = alt.Chart(full_df).mark_area(opacity=0.8).encode(x='date', y=f'{user_input}_y')
            c = alt.layer(a, b).properties(title="Forecast and Trend test")
            st.text('-----PREDICTION TEST-----')
            st.altair_chart(c, use_container_width=True)



if __name__ == "__main__":
    main()
