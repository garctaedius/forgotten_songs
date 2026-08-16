import pandas as pd

hot100 = pd.read_csv("data\\hot_100.csv", parse_dates=["chart_date", "chart_debut"])
# only keep 90s
hot100 = hot100[("1990-01-01" < hot100.chart_date) & (hot100.chart_date< "2000-01-01")].sort_values("chart_date")

from spotapi import Song

song = Song()

def search_song(artist, title, year, limit=1):
    query =  f'track:"{title}" artist:"{artist}" year:1985-{year}'

    results = song.query_songs(query, limit=limit)

    tracks = results["data"]["searchV2"]["tracksV2"]["items"]
    top_track = tracks[0]["item"]["data"]

    track_name = top_track["name"]
    first_artist_name = top_track["artists"]["items"][0]["profile"]["name"]
    plays = int(song.get_track_info(track_id=top_track["id"])["data"]["trackUnion"]["playcount"])

    return track_name, first_artist_name, plays

def test_random_song():
    random_song = hot100.sample().iloc[0]
    title, artist, year = random_song.song, random_song.performer, random_song.chart_debut.year
    print("Randomly chosen chart song:")
    print(f"\t'{title}', by '{artist}' ({year})")

    title, artist, plays = search_song(artist, title, year)
    print(f"Found song:")
    print(f"\t'{title}', by '{artist}'")
    print(f"\twith {plays:,} plays")