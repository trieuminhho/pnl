import pandas as pd


def read_tables(file):

    # Read in from excel file and skip first row
    tables_df = pd.read_excel(file, skiprows=1)

    # Trade table
    trade_df = tables_df.iloc[:, 0:4]
    trade_df.dropna(how='all', inplace=True)
    trade_df.iloc[:, 0] = pd.to_datetime(trade_df.iloc[:, 0])

    # Instruments table
    instrument_df = tables_df.iloc[:, 5:9]
    instrument_df.dropna(how='all', inplace=True)

    # Contract table
    contract_df = tables_df.iloc[:, 10:14]
    contract_df.dropna(how='all', inplace=True)

    # EOD prices table
    eod_prices_df = tables_df.iloc[:, 15:32]
    eod_prices_df.dropna(how='all', inplace=True)

    return trade_df, instrument_df, contract_df, eod_prices_df


#Position held in the portfolio (in contracts)
def positions_held(ticker, start_date, end_date, trade_df):

    ticker_df_loc = []

    for i in range(len(trade_df.iloc[:, 0])):
        if trade_df.iloc[i, 1] == ticker:
            ticker_df_loc.append(i)

    ticker_df = trade_df.iloc[ticker_df_loc]

    date_col_name = ticker_df.columns[0]
    # sort data frame by date
    ticker_df_sorted = ticker_df.sort_values(date_col_name)
    # mask date before start and after end
    date_mask = (ticker_df_sorted[date_col_name] >= start_date) & (ticker_df_sorted[date_col_name] <= end_date)

    ticker_df_sorted_masked = ticker_df_sorted.loc[date_mask]

    # loop through each row and sum the traded amount

    final = ticker_df_sorted_masked.iloc[:, 0:3]
    final['Current Position'] = 0
    current_eod_positions = 0

    for i in range(len(final.iloc[:, 2])):
        current_eod_positions += final.iloc[i, 2]
        final.iloc[i, 3] = current_eod_positions

    return final


def valuation(trade_df, contract_df, eod_prices_df, ticker, start_date, end_date):
    positions_open = int(positions_held(ticker, start_date, end_date, trade_df).iloc[:, 3].tail(1))
    eod_price = eod_prices_df.loc[eod_prices_df.iloc[:, 0] == end_date][ticker]
    multiple = float(contract_df.loc[contract_df.iloc[:, 0] == ticker].iloc[:,3])
    fx = 1
    value = positions_open * eod_price * multiple * fx
    return value


def daily_pnl(trade_df, contract_df, eod_prices_df, ticker, start_date, end_date):
    value = valuation(trade_df, contract_df, eod_prices_df, ticker, start_date, end_date)
    print(value)







if __name__ == '__main__':

    data_file_excel = 'data.xlsx'

    trade_df, instrument_df, contract_df, eod_prices_df = read_tables(data_file_excel)

    start_date = "2019-04-30"
    end_date = "2019-05-17"
    ticker = "CCN9 Comdty"

    pos_held = positions_held(ticker, start_date, end_date, trade_df)
    print(pos_held)

    value = valuation(trade_df, contract_df, eod_prices_df, ticker, start_date, end_date)

    pnl_d = daily_pnl(trade_df, contract_df, eod_prices_df, ticker, start_date, end_date)



