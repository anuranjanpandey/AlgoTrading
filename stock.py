import yfinance as yf
import streamlit as st
import pandas as pd
import datetime

def main():
    st.write("""
    # Stock Price Dashboard

    Shown are the stock closing price and volume of stocks!

    """)
    stocks = pd.read_csv('algorithms/sp_500_stocks.csv')
    stock = st.selectbox('Please select the stock', (stocks['Ticker']))
    #define the ticker symbol
    tikcerSymbol = stock

    #get data on this ticker
    tickerData = yf.Ticker(tikcerSymbol)

    # get the historical prices for this ticker
    cur_date = datetime.datetime.now().strftime("%Y-%m-%d")
    tickerDf = tickerData.history(period='1d', start='2010-5-31', end=cur_date)

    st.line_chart(tickerDf.Close)
    st.line_chart(tickerDf.Volume)

if __name__ == "__main__":
    main()
