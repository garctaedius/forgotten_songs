import pickle
from datetime import datetime

import pandas as pd

from billboard_score import score_songs
from spotify_searcher import get_spotify_streams
import config


def find_forgotten_songs(start_date: datetime, end_date: datetime):
    # Gather hot100 data from csv
    hot100 = pd.read_csv(
        "data/hot_100.csv",
        parse_dates=["chart_date", "chart_debut"],
        dtype={"previous_week": "Int16"}
    ).drop(columns="chart_url").sort_values("chart_date")
    hot100["previous_week"] = hot100.previous_week.fillna(0)  # simpler than having na values

    selected_charts = hot100[(start_date < hot100.chart_date) & (hot100.chart_date < end_date)]

    if config.FORCE_NEW:
        charts_to_score = selected_charts
        full_song_info = pd.DataFrame()
    else:
        try:
            with open("caches/full_song_info", "rb") as f:
                full_song_info = pickle.load(f)
        except:
            full_song_info = pd.DataFrame()

        # Find songs missing from cached version
        charts_to_score = selected_charts[~selected_charts.song_id.isin(full_song_info.index)]

    if charts_to_score.empty:
        print("Found cached data for all songs")
    else:
        if not config.FORCE_NEW:
            print(f"Could not find cached data for " +
                  f"{len(charts_to_score.song_id.unique())}(/{len(selected_charts.song_id.unique())}) songs")
            print("Scoring these songs\n")

        print("Calculating billboard score")
        songs = score_songs(hot100, charts_to_score)

        print("Gathering Spotify plays")
        songs = get_spotify_streams(songs)

        full_song_info = pd.concat([songs, full_song_info])

        with open("caches/full_song_info", "wb") as f:
            pickle.dump(full_song_info, f)

    faulty_songs = full_song_info[full_song_info.spotify_plays == 0]
    full_song_info = full_song_info[full_song_info.spotify_plays != 0]

    full_song_info["forgotten_index"] = full_song_info.billboard_score/full_song_info.spotify_plays
    full_song_info.sort_values("forgotten_index", ascending=False)

    # Plot scores maybe? like a scatter plot

    pass
