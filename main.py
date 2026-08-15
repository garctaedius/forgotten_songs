import pandas as pd

hot_100 = pd.read_csv("data\\hot_100.csv", parse_dates=["chart_date"])
# only keep 90s
hot_100 = hot_100[("1990-01-01" < hot_100.chart_date) & (hot_100.chart_date< "2000-01-01")].sort_values("chart_date")

from spotapi import Song

song = Song()

def search_song(artist, title, limit=1):
    query = f'"{title}" "{artist}"'

    results = song.query_songs(query, limit=limit)

    tracks = results["data"]["searchV2"]["tracksV2"]["items"]
    top_track = tracks[0]["item"]["data"]

    track_name = top_track["name"]
    first_artist_name = top_track["artists"]["items"][0]["profile"]["name"]
    plays = int(song.get_track_info(track_id=top_track["id"])["data"]["trackUnion"]["playcount"])

    return track_name, first_artist_name, plays

pass