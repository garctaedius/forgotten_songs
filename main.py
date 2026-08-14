import pandas as pd

hot_100 = pd.read_csv("data\\hot_100.csv", parse_dates=["chart_date"])
# only keep 90s
hot_100 = hot_100[("1990-01-01" < hot_100.chart_date) & (hot_100.chart_date< "2000-01-01")].sort_values("chart_date")