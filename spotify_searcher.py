import re

import pandas as pd
from spotapi import Song


def get_spotify_streams(songs: pd.DataFrame) -> pd.DataFrame:
    spotify_searcher = SpotifySearcher()

    rows = [
        [song.Index, *spotify_searcher.search_song(song.artist, song.title, song.year)]
        for song in songs[["title", "artist", "year"]].itertuples()
    ]

    spotify_results = pd.DataFrame(
        rows,
        columns=["song_id", "spotify_title", "spotify_artist",
                 "spotify_plays", "spotify_search_status"]
    ).set_index("song_id")

    songs = pd.merge(songs, spotify_results, left_index=True, right_index=True)

    return songs


class SpotifySearcher():
    song: Song

    def __init__(self):
        self.song = Song()

    def search_song(self, artist, title, year, n_results=1) -> tuple[str | None, str | None, int | None, str]:
        # NOTE: some reasons songs are not found:
        # year is wrong; sometimes on spotify it can only find one from like 2005
        # special characters, like & -> and
        # information in brackets, like the spotify title will have (radio edit), or the billboard one will say (featuring XYZ)

        artist, title = self.clean_query(artist, title)

        query = f'track:"{title}" artist:"{artist}" year:1950-{year+1}'
        results = self.query_song(query)

        if results is None:
            return None, None, None, "song query error"

        # Get track from query results
        tracks = results["data"]["searchV2"]["tracksV2"]["items"]
        if len(tracks) == 0:
            # No track found; try a less restrictive query for results
            results = self.loose_query(title, artist)

            if results is None:
                return None, None, None, "song query error"

            tracks = results["data"]["searchV2"]["tracksV2"]["items"]
            if len(tracks) == 0:
                # Still no track: give up
                return None, None, None, "could not find song"

        # Find the number one search result
        top_track = tracks[0]["item"]["data"]

        # Get names from track
        track_name = top_track["name"]
        first_artist_name = top_track["artists"]["items"][0]["profile"]["name"]

        plays = self.get_song_plays(top_track["id"])
        if plays is None:
            return track_name, first_artist_name, None, "play query error"

        return track_name, first_artist_name, plays, "success"

    def query_song(self, query: str, max_attempts: int = 2, n_results: int = 1):
        # Attempt gathering song a certain number of times
        attempts = 0
        results = None
        while (results is None) and attempts < max_attempts:
            try:
                results = self.song.query_songs(query, limit=n_results)
                results = None if "errors" in results else results
            except:
                attempts += 1

        return results

    def loose_query(self, title: str, artist: str):
        # Strip parentheses from title. reg ex credit to ChatGPT
        title = re.sub(r'\([^)]*\)', '', title).strip()

        loose_query = f"{title} {artist}"
        return self.query_song(loose_query)

    def get_song_plays(self, track_id: str, max_attempts: int = 2) -> int | None:
        # Attempt gathering song data a certain number of times
        attempts = 0
        plays = None
        while plays is None and attempts < max_attempts:
            try:
                plays = int(self.song.get_track_info(track_id=track_id)["data"]["trackUnion"]["playcount"])
            except:
                attempts += 1

        return plays

    @staticmethod
    def clean_query(artist: str, title: str) -> tuple[str, str]:
        # Strip parentheses from artist. (reg ex credit to ChatGPT)
        artist = re.sub(r'\([^)]*\)', '', artist).strip()

        # Remove everything after a "feat", or "/" (again, thanks ChatGPT)
        artist = re.split(r'/|feat', artist, flags=re.IGNORECASE)[0].strip()

        return artist, title
