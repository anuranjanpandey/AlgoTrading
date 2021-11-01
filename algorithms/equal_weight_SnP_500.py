import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
from algorithms.secrets import IEX_CLOUD_API_TOKEN
import streamlit as st
import io

def main():

    stocks = pd.read_csv('algorithms/sp_500_stocks.csv')

    #  for a single stock
    # symbol = 'AAPL'
    # api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}'
    # data = requests.get(api_url).json()
    # print(data)



    my_columns = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of shares to Buy']


    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


    symbol_groups = list(chunks(stocks['Ticker'], 100))
    symbol_strings = []
    for i in range(len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))

        
    final_dataframe = pd.DataFrame(columns=my_columns)
    for symbol_string in symbol_strings:
        batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(','):
            final_dataframe = final_dataframe.append(
                                            pd.Series([symbol, 
                                                    data[symbol]['quote']['latestPrice'], 
                                                    data[symbol]['quote']['marketCap'], 
                                                    'N/A'], 
                                                    index = my_columns), 
                                            ignore_index = True)
            
    # take input from the website
    # portfolio_size = input('Enter the value of your portfolio:')
    portfolio_size = st.number_input('Enter the value of your portfolio')
    try:
        val = float(portfolio_size)
    except ValueError:
        print('Please enter an Integer')
        portfolio_size = input('Enter the value of your portfolio:')
        val = float(portfolio_size)


    position_size = val/len(final_dataframe.index)
    for i in range(len(final_dataframe.index)):
        final_dataframe.loc[i, 'Number of shares to Buy'] = math.floor(position_size/final_dataframe.loc[i, 'Stock Price'])

    # show the final_dataframe on website 
    st.dataframe(final_dataframe)


    # link to a download button
    @st.cache
    def to_excel(df):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, 'Recommended Trades', index=False)


        background_color = '#0a0a23'
        font_color = '#ffffff'

        string_format = writer.book.add_format(
                {
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )

        dollar_format = writer.book.add_format(
                {
                    'num_format':'$0.00',
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )

        integer_format = writer.book.add_format(
                {
                    'num_format':'0',
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )


        column_formats = { 
                            'A': ['Ticker', string_format],
                            'B': ['Price', dollar_format],
                            'C': ['Market Capitalization', dollar_format],
                            'D': ['Number of Shares to Buy', integer_format]
                            }

        for column in column_formats.keys():
            writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
            writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)


        writer.save()
        processed_data = output.getvalue()
        return processed_data

    df_xlsx = to_excel(final_dataframe)
    st.download_button(label='📥 Download Results',
                                data=df_xlsx ,
                                file_name= 'equal_weight.xlsx')

if __name__ == "__main__":
    main()