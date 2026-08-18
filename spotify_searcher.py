import pandas as pd
from spotapi import Song


def get_spotify_streams(songs: pd.DataFrame) -> pd.DataFrame:
    spotify_searcher = SpotifySearcher()

    songs = songs.iloc[:50].copy()  # TODO: remove

    rows = [
        [song.Index, *spotify_searcher.search_song(song.artist, song.title, song.year)]
        for song in songs[["title", "artist", "year"]].itertuples()
    ]

    spotify_results = pd.DataFrame(
        rows,
        columns=["song_id", "spotify_title", "spotify_artist",
                 "spotify_plays", "spotify_search_status"]
    ).set_index("song_id")

    songs = pd.merge(songs, spotify_results, left_index=True, right_index=True).head()

    return songs


class SpotifySearcher():
    song: Song

    def __init__(self):
        self.song = Song()

    def search_song(self, artist, title, year, limit=1) -> tuple[str | None, str | None, int | None, str]:
        # TODO: some reasons songs are not found:
        # year is wrong; sometimes on spotify it can only find one from like 2005
        # special characters, like & -> and
        # information in brackets, like the spotify title will have (radio edit), or the billboard one will say (featuring XYZ)
        query = f'track:"{title}" artist:"{artist}" year:1950-{year+1}'

        # Attempt gathering song a certain number of times
        attempts = 0
        results = None
        while results is None and attempts < 3:
            try:
                results = self.song.query_songs(query, limit=limit)
            except:
                attempts += 1
        if results is None:
            return None, None, None, "song query error"

        tracks = results["data"]["searchV2"]["tracksV2"]["items"]
        if len(tracks) == 0:
            return None, None, None, "could not find song"

        top_track = tracks[0]["item"]["data"]

        track_name = top_track["name"]
        first_artist_name = top_track["artists"]["items"][0]["profile"]["name"]

        # Attempt gathering song data a certain number of times
        attempts = 0
        plays = None
        while plays is None and attempts < 3:
            try:
                plays = int(self.song.get_track_info(track_id=top_track["id"])["data"]["trackUnion"]["playcount"])
            except:
                attempts += 1
        if plays is None:
            return track_name, first_artist_name, None, "play query error"

        return track_name, first_artist_name, plays, "success"
