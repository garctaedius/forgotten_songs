import os

import pandas as pd

from billboard_score import score_songs
from spotify_searcher import get_spotify_streams

if not os.path.exists("caches"):
    os.makedirs("caches")

# TODO: create args
# num ranks that get bonus score
# period of course

# TODO: cache spotify results as well and check if they are available before looking into billboard score

# Gather hot100 data from csv
hot100 = pd.read_csv("data\\hot_100.csv",
                     parse_dates=["chart_date", "chart_debut"],
                     dtype={"previous_week": "Int16"}).sort_values("chart_date")
hot100["previous_week"] = hot100.previous_week.fillna(0)  # simpler than having na values

nineties = hot100[("1990-01-01" < hot100.chart_date) & (hot100.chart_date < "2000-01-01")]

print("Calculating billboard score")
songs = score_songs(hot100, nineties)

print("Gathering Spotify plays")
songs = get_spotify_streams(songs)

# Plot scores maybe? like a scatter plot


pass
