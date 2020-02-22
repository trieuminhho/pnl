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
    eod_prices_df.iloc[:, 0] = pd.to_datetime(eod_prices_df.iloc[:, 0])

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

    final = ticker_df_sorted_masked.iloc[:, 0:4]
    final['Current Position'] = 0
    current_eod_positions = 0

    for i in range(len(final.iloc[:, 4])):
        current_eod_positions += final.iloc[i, 2]
        final.iloc[i, 4] = current_eod_positions
    return final


def valuation(trade_df, contract_df, eod_prices_df, ticker, start_date, end_date):

    positions_open = int(positions_held(ticker, start_date, end_date, trade_df).iloc[:, 3].tail(1))

    eod_price = eod_prices_df.loc[eod_prices_df.iloc[:, 0] == end_date][ticker].values
    multiple = float(contract_df.loc[contract_df.iloc[:, 0] == ticker].iloc[:, 3])
    fx = 1

    if eod_price != 'n.a.':
        value = positions_open * eod_price * multiple * fx
        return value
    else:
        print("No EOD data on selected valuation date.")
        return False


def daily_pnl(trade_df, contract_df, eod_prices_df, ticker, start_date, end_date):

    # mask date before start and after end
    date_mask = (eod_prices_df.iloc[:, 0] >= start_date) & (eod_prices_df.iloc[:, 0] <= end_date)

    dates = eod_prices_df.iloc[:, 0][date_mask]

    final = eod_prices_df.iloc[:, [0, eod_prices_df.columns.get_loc(ticker)]][date_mask]

    positions = positions_held(ticker, start_date, end_date, trade_df)

    day_trades_final = final.copy()
    day_trades_final = day_trades_final.tail(0)

    for row in range(len(final)):
        all_day_pos = len(single_ticker_day_trades(final.iloc[row, 0], positions))
        if all_day_pos == 0 or all_day_pos == 1:
            day_trades_final = day_trades_final.append(final.iloc[row, :])
        else:
            for row2 in range(all_day_pos):
                day_trades_final = day_trades_final.append(final.iloc[row, :])
    # traded amount
    day_trades_final[positions.columns[2]] = 0
    # average price traded
    day_trades_final[positions.columns[3]] = 0
    # contract multiplier
    day_trades_final[contract_df.columns[3]] = int(contract_df.iloc[:, 3][contract_df.iloc[:, 0] == ticker])
    # current position
    day_trades_final[positions.columns[4]] = 0
    # Daily PnL
    day_trades_final['Daily PnL'] = 0

    # first time looping through day_trades_final to fill in trades amount and averages prices,
    # taking into consideration multiple trades in a day
    row_range = iter(range(len(day_trades_final)))
    for row in row_range:
        all_day_pos = single_ticker_day_trades(day_trades_final.iloc[row, 0], positions)
        print(len(all_day_pos))
        if len(all_day_pos) == 1:
            # traded amount
            day_trades_final.iloc[row, 2] = all_day_pos.iloc[0, 2]
            # average price
            day_trades_final.iloc[row, 3] = all_day_pos.iloc[0, 3]
        elif len(all_day_pos) > 1:
            for row2 in range(len(all_day_pos)):
                # traded amount
                day_trades_final.iloc[row + row2, 2] = all_day_pos.iloc[row2, 2]
                # average price
                day_trades_final.iloc[row + row2, 3] = all_day_pos.iloc[row2, 3]
                next(row_range)

    # second time looping to fill in current position and calculate pnl
    current_pos_2 = 0
    for row in range(len(day_trades_final)):
        # current position
        current_pos_2 += day_trades_final.iloc[row, 2]
        day_trades_final.iloc[row, 5] = current_pos_2

        # calculate daily pnl
        eod_price_1 = day_trades_final.iloc[row - 1, 1]
        eod_price_2 = day_trades_final.iloc[row, 1]
        if eod_price_1 != 'n.a.' and eod_price_2 != 'n.a.':
            traded_amount = day_trades_final.iloc[row, 2]
            trade_price = day_trades_final.iloc[row, 3]
            multiplier = day_trades_final.iloc[row, 4]
            current_pos_1 = day_trades_final.iloc[row -1, 5]

            if row > 0 and current_pos_1:
                day_trades_final.iloc[row, 6] = ((eod_price_2 - eod_price_1)*current_pos_2 + (eod_price_2 - trade_price)
                                                 * traded_amount) * multiplier
            else:
                day_trades_final.iloc[row, 6] = ((eod_price_2 - trade_price) * traded_amount) * multiplier

    return day_trades_final


def single_ticker_day_trades(date, positions):
    all_day_pos = positions.copy()
    all_day_pos = all_day_pos.tail(0)
    for row in range(len(positions)):
        if positions.iloc[row, 0] == date:
            all_day_pos = all_day_pos.append(positions.iloc[row, :])

    return all_day_pos





if __name__ == '__main__':

    data_file_excel = 'data.xlsx'

    trade_df, instrument_df, contract_df, eod_prices_df = read_tables(data_file_excel)

    start_date = "2019-04-30"
    end_date = "2019-05-29"
    ticker = "CCN9 Comdty"

    pd.set_option('display.max_columns', 30)
    pd.set_option('display.width', 2000)

    #pos_held = positions_held(ticker, start_date, end_date, trade_df)


    #value = valuation(trade_df, contract_df, eod_prices_df, ticker, start_date, end_date)

    pnl_d = daily_pnl(trade_df, contract_df, eod_prices_df, ticker, start_date, end_date)

    print(pnl_d)





