import pandas as pd

data_file_excel = 'data.xlsx'

tables_df = pd.read_excel(data_file_excel, skiprows=1)

trade_df = tables_df.iloc[:, 0:4]
print(trade_df)

instrument_df = tables_df.iloc[:, 5:9]
print(instrument_df)


contract_df = tables_df.iloc[:, 10:14]
print(contract_df)

eod_prices_df = tables_df.iloc[:, 15:32]
print(eod_prices_df)

fx_conversion_df = tables_df.iloc[:, 50:54]
print(fx_conversion_df)
