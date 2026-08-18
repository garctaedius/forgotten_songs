import pickle

import pandas as pd

from billboard_score import score_songs
from spotify_searcher import get_spotify_streams


def find_forgotten_songs():
    # Gather hot100 data from csv
    hot100 = pd.read_csv("data\\hot_100.csv",
                         parse_dates=["chart_date", "chart_debut"],
                         dtype={"previous_week": "Int16"}).sort_values("chart_date")
    hot100["previous_week"] = hot100.previous_week.fillna(0)  # simpler than having na values

    nineties = hot100[("1994-01-01" < hot100.chart_date) & (hot100.chart_date < "1995-01-01")]

    try:
        with open("caches/full_song_info", "rb") as f:
            full_song_info = pickle.load(f)
    except:
        full_song_info = pd.DataFrame()

    # Find songs missing from cached version
    charts_to_score = nineties[~nineties.song_id.isin(full_song_info.index)]

    if not charts_to_score.empty:
        print(f"Could not find cached data for " +
              f"{len(charts_to_score.song_id.unique())}(/{len(nineties.song_id.unique())}) songs")
        print("Scoring these songs\n")

        print("Calculating billboard score")
        songs = score_songs(hot100, charts_to_score)

        print("Gathering Spotify plays")
        songs = get_spotify_streams(songs)

        full_song_info = pd.concat([songs, full_song_info])

        with open("caches/full_song_info", "wb") as f:
            pickle.dump(full_song_info, f)
    else:
        print("Found cached data for all songs")

    faulty_songs = full_song_info[full_song_info.spotify_plays == 0]
    full_song_info = full_song_info[full_song_info.spotify_plays != 0]

    full_song_info["forgotten_index"] = full_song_info.billboard_score/full_song_info.spotify_plays
    full_song_info.sort_values("forgotten_index", ascending=False)

    # Plot scores maybe? like a scatter plot

    pass
