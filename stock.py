import yfinance as yf
import streamlit as st
import pandas as pd

def main():
    st.write("""
    # Stock Price Dashboard

    Shown are the stock closing price and volume of stocks!
    Please select the stock

    """)
    #define the ticker symbol
    tikcerSymbol = 'GOOGL'

    #get data on this ticker
    tickerData = yf.Ticker(tikcerSymbol)

    # get the historical prices for this ticker
    tickerDf = tickerData.history(period='1d', start='2010-5-31', end='2020-5-31')

    st.line_chart(tickerDf.Close)
    st.line_chart(tickerDf.Volume)

if __name__ == "__main__":
    main()
