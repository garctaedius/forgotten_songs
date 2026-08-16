import pandas as pd

from billboard_score import score_songs

# Gather hot100 data
hot100 = pd.read_csv("data\\hot_100.csv", parse_dates=["chart_date", "chart_debut"], dtype={"previous_week": "Int16"})
hot100["previous_week"] = hot100.previous_week.fillna(0)  # simpler than having na values

nineties = hot100[("1990-01-01" < hot100.chart_date) & (hot100.chart_date < "2000-01-01")].sort_values("chart_date")

score_songs(hot100, nineties)


pass
