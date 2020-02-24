import pandas as pd

class ReportAnalytics:
    # init constructor which runs at instances of this class
    def __init__(self, file, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.trade, self.instrument,\
            self.contract, self.prices = ReportAnalytics.read_tables(file)
        self.positions = self.positions_held()
        self.daily_pnl = self.daily_pnl()
        self.monthly_pnl = self.monthly_pnl()
        self.yearly_pnl = self.yearly_pnl()
        self.valuation = self.valuation()
        self.ticker_summary = self.ticker_summary()

    @staticmethod
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

    # Position held in the portfolio (in contracts)
    def positions_held(self):
        ticker_df_loc = []

        for i in range(len(self.trade.iloc[:, 0])):
            if self.trade.iloc[i, 1] == self.ticker:
                ticker_df_loc.append(i)

        ticker_df = self.trade.iloc[ticker_df_loc]

        date_col_name = ticker_df.columns[0]
        # sort data frame by date
        ticker_df_sorted = ticker_df.sort_values(date_col_name)
        # mask date before start and after end
        date_mask = (ticker_df_sorted[date_col_name] >= self.start_date) & (ticker_df_sorted[date_col_name] <= self.end_date)

        ticker_df_sorted_masked = ticker_df_sorted.loc[date_mask]

        # loop through each row and sum the traded amount

        final = ticker_df_sorted_masked.iloc[:, 0:4]
        final['Current Position'] = 0
        current_eod_positions = 0
        for i in range(len(final.iloc[:, 4])):
            current_eod_positions += final.iloc[i, 2]
            final.iloc[i, 4] = current_eod_positions

        return final

    def daily_pnl(self):

        # mask date before start and after end
        date_mask = (self.prices.iloc[:, 0] >= self.start_date) & (self.prices.iloc[:, 0] <= self.end_date)

        final = self.prices.iloc[:, [0, self.prices.columns.get_loc(self.ticker)]][date_mask]

        positions = self.positions

        day_trades_final = final.copy()
        day_trades_final = day_trades_final.tail(0)

        for row in range(len(final)):
            all_day_pos = len(ReportAnalytics.single_ticker_day_trades(final.iloc[row, 0], positions))
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
        day_trades_final[self.contract.columns[3]] = \
            int(self.contract.iloc[:, 3][self.contract.iloc[:, 0] == self.ticker])
        # current position
        day_trades_final[positions.columns[4]] = 0
        # Daily PnL
        day_trades_final['Daily PnL'] = 0

        # first time looping through day_trades_final to fill in trades amount and averages prices,
        # taking into consideration multiple trades in a day
        row_range = iter(range(len(day_trades_final)))
        for row in row_range:
            all_day_pos = ReportAnalytics.single_ticker_day_trades(day_trades_final.iloc[row, 0], positions)
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
                    day_trades_final.iloc[row, 6] = ((eod_price_2 - eod_price_1)*current_pos_2 +
                                                     (eod_price_2 - trade_price) * traded_amount) * multiplier
                else:
                    day_trades_final.iloc[row, 6] = ((eod_price_2 - trade_price) * traded_amount) * multiplier

        return day_trades_final

    @staticmethod
    def single_ticker_day_trades(date, positions):
        all_day_pos = positions.copy()
        all_day_pos = all_day_pos.tail(0)
        for row in range(len(positions)):
            if positions.iloc[row, 0] == date:
                all_day_pos = all_day_pos.append(positions.iloc[row, :])
        return all_day_pos

    def monthly_pnl(self):

        pnl_month = self.daily_pnl.copy()

        date_split = self.end_date.split('-')

        start_month_date = date_split[0] + '-' + date_split[1] + '-01'

        date_mask = (pnl_month.iloc[:, 0] >= start_month_date) & (pnl_month.iloc[:, 0] <= self.end_date)

        final = pnl_month.loc[date_mask].reset_index(drop=True)

        final['Monthly PnL'] = 0

        monthly_sum = 0
        for row in range(len(final)):
            monthly_sum += final.iloc[row, 6]
            final.iloc[row, 7] = monthly_sum

        return final

    def yearly_pnl(self):

        pnl_year = self.daily_pnl.copy()

        date_split = self.end_date.split('-')

        start_year_date = date_split[0] + '-01' + '-01'

        date_mask = (pnl_year.iloc[:, 0] >= start_year_date) & (pnl_year.iloc[:, 0] <= self.end_date)

        final = pnl_year.loc[date_mask].reset_index(drop=True)

        final['Yearly PnL'] = 0

        yearly_sum = 0
        for row in range(len(final)):
            yearly_sum += final.iloc[row, 6]
            final.iloc[row, 7] = yearly_sum

        return final

    def valuation(self):

        value = self.daily_pnl.copy().iloc[:, 0:6]
        fx = 1
        value['valuation'] = 0

        for i in range(len(value)):
            if value.iloc[i, 1] != 'n.a.':
                value.iloc[i, 6] = abs(value.iloc[i, 5] * value.iloc[i, 1] * value.iloc[i, 4] * fx)
            else:
                value.iloc[i, 6] = 'n.a.'
        return value

    def ticker_summary(self):

        summary = self.daily_pnl.copy()
        summary[self.monthly_pnl.columns[7]] = self.monthly_pnl.iloc[:, 7]
        summary[self.yearly_pnl.columns[7]] = self.yearly_pnl.iloc[:, 7]
        summary[self.valuation.columns[6]] = self.valuation.iloc[:, 6]

        # format cells
        summary.iloc[:, 0] = pd.DatetimeIndex(summary.iloc[:, 0]).strftime("%Y-%m-%d")
        # rename ticker column to ticker

        summary.rename(columns={summary.columns[1]: "EOD Price"}, inplace=True)

        summary = summary.iloc[:,[0,5,9,6,7,8]]

        return summary


def all_tickers_in_set(file, ticker, instrument, asset):
    trade_df, instrument_df, contract_df, _ = ReportAnalytics.read_tables(file)

    available_contract = contract_df.iloc[:, 0]

    asset_mask = (instrument_df.iloc[:, 2] == asset)

    asset_instruments_code = list(instrument_df.iloc[:, 0][asset_mask])

    all_instrument_asset = []

    if ticker == 'All' and instrument != 'All':
        instrument_of_interest = list((instrument_df.iloc[:, 1] == instrument)[asset_mask])
        for i in range(len(asset_instruments_code)):
            if instrument_of_interest[i]:
                instrument_mask = (contract_df.iloc[:, 2] == asset_instruments_code[i])
                instrument_contract = list(available_contract[instrument_mask])
                all_instrument_asset = all_instrument_asset + instrument_contract
            else:
                continue
    elif ticker == 'All' and instrument == 'All':
        for i in range(len(asset_instruments_code)):
            instrument_mask = (contract_df.iloc[:, 2] == asset_instruments_code[i])
            instrument_contract = list(available_contract[instrument_mask])
            all_instrument_asset = all_instrument_asset + instrument_contract
    else:
        all_instrument_asset.append(ticker)

    return all_instrument_asset


def add_summary(df1, df2):

    df = df1.copy()

    for j in range(len(df1.iloc[0, :])):
        for i in range(len(df1.iloc[:, 0])):
            if j != 0:
                if type(df1.iloc[i, j]) == str and type(df2.iloc[i, j]) != str:
                    if j == 1:
                        print(df2.iloc[i, j])
                        df.iloc[i, j] = abs(df2.iloc[i, j])
                    else:
                        df.iloc[i, j] = df2.iloc[i, j]
                elif type(df1.iloc[i, j]) != str and type(df2.iloc[i, j]) == str:
                    if j == 1:
                        df.iloc[i, j] = abs(df1.iloc[i, j])
                    else:
                        df.iloc[i, j] = df1.iloc[i, j]
                elif type(df1.iloc[i, j]) == str and type(df2.iloc[i, j]) == str:
                    continue
                else:
                    if j == 1:
                        df.iloc[i, j] = abs(df.iloc[i, j]) + abs(df2.iloc[i, j])
                    else:
                        df.iloc[i, j] = df.iloc[i, j] + df2.iloc[i, j]
    return df


def summary_total(file, ticker, instrument, asset, start_date, end_date):

    tickers_list = all_tickers_in_set(file, ticker, instrument, asset)

    pnl_obj_final = ReportAnalytics(file, tickers_list[0], start_date, end_date).ticker_summary

    if len(tickers_list) > 1:
        for i in range(1, len(tickers_list)):
            pnl_obj = ReportAnalytics(file, tickers_list[i], start_date, end_date).ticker_summary
            pnl_obj_final = add_summary(pnl_obj_final, pnl_obj)
    else:
        pass

    return pnl_obj_final




if __name__ == '__main__':

    data_file_excel = 'data/data.xlsx'

    trade_df, instrument_df, contract_df, eod_prices_df = ReportAnalytics.read_tables(data_file_excel)

    start_date = "2019-04-30"
    end_date = "2019-07-29"
    ticker = "ESM9 Index"
    instrument = "S&P500"
    asset = "Equity"
    pd.set_option('display.max_columns', 30)
    pd.set_option('display.width', 2000)

    # pnl_obj = ReportAnalytics(data_file_excel, ticker, start_date, end_date)
    # # print(pnl_obj.ticker_summary)

    pnl_obj_sum = summary_total(data_file_excel, ticker, instrument, asset, start_date, end_date)



