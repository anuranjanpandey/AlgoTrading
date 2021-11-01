import numpy as np
import pandas as pd
import xlsxwriter
import requests
from scipy import stats
import math
from statistics import mean
from algorithms.secrets import IEX_CLOUD_API_TOKEN
import streamlit as st
import io


def main():
        
    stocks = pd.read_csv('algorithms/sp_500_stocks.csv')


    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]   
            
    symbol_groups = list(chunks(stocks['Ticker'], 100))
    symbol_strings = []
    for i in range(0, len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))

    my_columns = ['Ticker', 'Price', 'Price-to-Earnings Ratio', 'Number of Shares to Buy']



    final_dataframe = pd.DataFrame(columns = my_columns)

    for symbol_string in symbol_strings:
        batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(','):
            final_dataframe = final_dataframe.append(
                                            pd.Series([symbol, 
                                                    data[symbol]['quote']['latestPrice'],
                                                    data[symbol]['quote']['peRatio'],
                                                    'N/A'
                                                    ], 
                                                    index = my_columns), 
                                            ignore_index = True)
            
        
    final_dataframe.sort_values('Price-to-Earnings Ratio', inplace=True)
    final_dataframe = final_dataframe[final_dataframe['Price-to-Earnings Ratio'] > 0]
    final_dataframe = final_dataframe[:50]
    final_dataframe.reset_index(inplace=True)
    final_dataframe.drop('index', axis=1, inplace=True)


    def portfolio_input():
        global portfolio_size
        portfolio_size = input("Enter the value of your portfolio:")

        try:
            val = float(portfolio_size)
        except ValueError:
            print("That's not a number! \n Try again:")
            portfolio_size = input("Enter the value of your portfolio:")

    # take input from website
    portfolio_size = st.number_input('Enter the value of your portfolio')
    position_size = float(portfolio_size) / len(final_dataframe.index)


    for row in final_dataframe.index:
        final_dataframe.loc[row, 'Number of Shares to Buy'] = math.floor(position_size / final_dataframe.loc[row, 'Price'])




    rv_columns = [
        'Ticker',
        'Price',
        'Number of Shares to Buy', 
        'Price-to-Earnings Ratio',
        'PE Percentile',
        'Price-to-Book Ratio',
        'PB Percentile',
        'Price-to-Sales Ratio',
        'PS Percentile',
        'EV/EBITDA',
        'EV/EBITDA Percentile',
        'EV/GP',
        'EV/GP Percentile',
        'RV Score'
    ]

    rv_dataframe = pd.DataFrame(columns=rv_columns)

    for symbol_string in symbol_strings:
        batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=advanced-stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(','):
            enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
            ebitda = data[symbol]['advanced-stats']['EBITDA']
            gross_profit = data[symbol]['advanced-stats']['grossProfit']
            
            try:
                ev_to_ebitda = enterprise_value/ebitda
            except TypeError:
                ev_to_ebitda = np.NaN
            
            try:
                ev_to_gross_profit = enterprise_value/gross_profit
            except TypeError:
                ev_to_gross_profit = np.NaN
            
            rv_dataframe = rv_dataframe.append(
                pd.Series([
                    symbol,
                    data[symbol]['quote']['latestPrice'],
                    'N/A',
                    data[symbol]['quote']['peRatio'],
                    'N/A',
                    data[symbol]['advanced-stats']['priceToBook'],
                    'N/A',
                    data[symbol]['advanced-stats']['priceToSales'],
                    'N/A',
                    ev_to_ebitda,
                    'N/A',
                    ev_to_gross_profit,
                    'N/A',
                    'N/A'
                ], index=rv_columns),ignore_index=True
            )



    for column in ['Price-to-Earnings Ratio', 'Price-to-Book Ratio','Price-to-Sales Ratio',  'EV/EBITDA','EV/GP']:
        rv_dataframe[column].fillna(rv_dataframe[column].mean(), inplace = True)


    metrics =  {
        'Price-to-Earnings Ratio': 'PE Percentile',
        'Price-to-Book Ratio': 'PB Percentile',
        'Price-to-Sales Ratio': 'PS Percentile',
        'EV/EBITDA': 'EV/EBITDA Percentile',
        'EV/GP': 'EV/GP Percentile'
    }

    for metric in metrics.keys():
        for row in rv_dataframe.index:
            rv_dataframe.loc[row, metrics[metric]] = stats.percentileofscore(rv_dataframe[metric], rv_dataframe.loc[row, metric]) / 100


    for row in rv_dataframe.index:
        value_percentiles = []
        for metric in metrics.keys():
            value_percentiles.append(rv_dataframe.loc[row, metrics[metric]])
        rv_dataframe.loc[row, 'RV Score'] = mean(value_percentiles)



    rv_dataframe.sort_values('RV Score', ascending=True, inplace=True)
    rv_dataframe = rv_dataframe[:50]
    rv_dataframe.reset_index(drop=True, inplace=True)


    # take input from website
    # portfolio_input()


    position_size = float(portfolio_size) / len(rv_dataframe.index)
    for row in rv_dataframe.index:
        rv_dataframe.loc[row, 'Number of Shares to Buy'] = position_size // rv_dataframe.loc[row, 'Price']

    # show dataframe on website
    st.dataframe(rv_dataframe)

    # downloadable excel sheet
    @st.cache
    def to_excel(df):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, 'Value Strategy', index=False)


        background_color = '#0a0a23'
        font_color = '#ffffff'

        string_template = writer.book.add_format(
                {
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )

        dollar_template = writer.book.add_format(
                {
                    'num_format':'$0.00',
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )

        integer_template = writer.book.add_format(
                {
                    'num_format':'0',
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )

        float_template = writer.book.add_format(
                {
                    'num_format':'0',
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )

        percent_template = writer.book.add_format(
                {
                    'num_format':'0.0%',
                    'font_color': font_color,
                    'bg_color': background_color,
                    'border': 1
                }
            )

        column_formats = {
                            'A': ['Ticker', string_template],
                            'B': ['Price', dollar_template],
                            'C': ['Number of Shares to Buy', integer_template],
                            'D': ['Price-to-Earnings Ratio', float_template],
                            'E': ['PE Percentile', percent_template],
                            'F': ['Price-to-Book Ratio', float_template],
                            'G': ['PB Percentile',percent_template],
                            'H': ['Price-to-Sales Ratio', float_template],
                            'I': ['PS Percentile', percent_template],
                            'J': ['EV/EBITDA', float_template],
                            'K': ['EV/EBITDA Percentile', percent_template],
                            'L': ['EV/GP', float_template],
                            'M': ['EV/GP Percentile', percent_template],
                            'N': ['RV Score', percent_template]
                        }

        for column in column_formats.keys():
            writer.sheets['Value Strategy'].set_column(f'{column}:{column}', 25, column_formats[column][1])
            writer.sheets['Value Strategy'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

        writer.save()
        processed_data = output.getvalue()
        return processed_data

    df_xlsx = to_excel(rv_dataframe)
    st.download_button(label='📥 Download Results',
                                data=df_xlsx ,
                                file_name= 'value_strategy.xlsx')

if __name__ == "__main__":
    main()