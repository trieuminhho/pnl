# Install requirements: 
pip install -r requirements.txt
# Generating dash application
Running dash_generator.py will host an application locally on a browser. The script dash_generator.py calls report_generator.py, which has the ReportAnalytics class that does all of the data processing.
# ReportAnalytics class
The ReportAnalytics class can be instantized using ReportAnalytics(data_file_name, ticker_name, start_date, end_date). At creation the class will calculate:
  - The positons held at each date, stored in the .positons attribute
  - Daily PnL, stored in .daily_pnl
  - Month to date PnL, stored in .monthly_pnl
  - Year to date PnL, stored in .yearly_pnl
# The data file is stored in the data directory, which should strictly follow the same layout if additional data is added.
