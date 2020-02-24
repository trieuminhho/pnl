# Install requirements: 
pip install -r requirements.txt
# Generating dash application
Running dash_generator.py will host an application locally on a browser. The script dash_generator.py calls report_generator.py, which has the ReportAnalytics class that does all of the data processing.
# ReportAnalytics
The ReportAnalytics class can be instantized using ReportAnalytics(data_file_name, ticker_name, start_date, end_date). At creation the class will calculate:
  - The positons held at each date, stored in the .positons attribute
  - Daily PnL, stored in .daily_pnl
  - Month to date PnL, stored in .monthly_pnl
  - Year to date PnL, stored in .yearly_pnl
 The ReportAnalytics class can only run on one ticker at a time, and that ticker needs to be specified in the data file.
 # Grouping all tickers in an instrument and asset class
  - summary_total: a function in report_generator.py accepts a ticker, instrument, asset class, start_date, end_date; which finds   all the required tickers that needs to be looped through and added together. 
  - all_tickers_in_set: finds all the tickers that are grouped in the instrument and asset class.
  - add_summary: adds two summary data frames together. Loops through each column and does summation based on whether the values needs to be taken as absolute or not.
# Data file
The data file is stored in the data/ directory, which should strictly follow the same layout if additional data is added.
