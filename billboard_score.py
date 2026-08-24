from math import floor, ceil
from typing import cast
import pickle

import pandas as pd

from utils import Streak


def score_songs(full_chart: pd.DataFrame, chart_to_score: pd.DataFrame | None = None) -> pd.DataFrame:
    if chart_to_score is None:
        chart_to_score = full_chart

    # Check if a cached version is available
    try:
        with open("caches\\billboard_scored_songs", "rb") as f:
            cached_songs = pickle.load(f)
    except:
        print("\tCould not find cached scores. Calculating scores...")
        cached_songs = pd.DataFrame()

    if not cached_songs.empty:
        # Check that the songs to score are indeed in the cached df
        desired_song_ids = chart_to_score.song_id.unique()
        if desired_song_ids.isin(cached_songs.index).all():  # type: ignore
            # Filter away potentially uninteresting songs
            print("\tFound cached version")
            return cached_songs.loc[desired_song_ids]

        desired_cached_songs = desired_song_ids[desired_song_ids.isin(cached_songs.index)]  # type: ignore
        if len(desired_cached_songs) == 0:
            print("\tCould not find cached scores. Calculating scores...")
        else:
            print(f"\tFound cached version for {len(desired_cached_songs)}(/{len(desired_song_ids)}). "
                  "Scoring the rest.")
            chart_to_score = chart_to_score[~chart_to_score.song_id.isin(desired_cached_songs)]

    song_scorer = BillboardScorer()
    scored_songs = song_scorer.score_songs(full_chart, chart_to_score)

    # Store cached scores
    all_scored_songs = pd.concat([cached_songs, scored_songs])
    with open("caches\\billboard_scored_songs", "wb") as f:
        pickle.dump(all_scored_songs, f)

    return scored_songs


class BillboardScorer():
    """Uses Carroll2015 method to rank songs, including a bonus for staying on the same high position for 
    consecutive weeks. The scores are based on Hesbacher1982, who had privileged access to the Billboard data."""

    _score_scale_factor: float
    _bonus_value_per_rank: dict[int, float]

    def __init__(self) -> None:
        self._score_scale_factor = 100/self._raw_score(1)

        scores = {i: self._chart_score(i) for i in range(1, 12)}
        self._bonus_value_per_rank = {
            i: scores[i]-scores[i+1]
            for i in range(1, 11)
        }

    def score_songs(self, full_chart: pd.DataFrame, chart_to_score: pd.DataFrame) -> pd.DataFrame:
        # Filter away irrelevant songs
        full_chart = full_chart[full_chart.song_id.isin(chart_to_score.song_id.unique())].copy()
        full_chart["computed_score"] = full_chart.chart_position.apply(self._chart_score)

        # Calculate base score
        base_scores = full_chart.groupby("song_id")["computed_score"].sum()

        # Calculate bonus score for staying at a high position for consecutive weeks
        song_bonuses = {}
        for song_id, occurrences in full_chart.groupby("song_id"):
            streaks = self._get_song_streaks(occurrences)
            song_bonus = sum(
                self._bonus(streak.n_weeks, streak.chart_pos) for streak in streaks
            )
            song_bonuses[song_id] = song_bonus

        # Create df with songs and their score
        scored_songs = chart_to_score[~chart_to_score.song_id.duplicated()]
        scored_songs = (
            scored_songs[["song", "performer", "chart_debut", "song_id"]]
            .set_index("song_id")
            .rename(columns={"song": "title", "performer": "artist"})
        )
        scored_songs["year"] = scored_songs.chart_debut.dt.year

        scored_songs["base_score"] = base_scores
        scored_songs["bonus_score"] = scored_songs.index.map(song_bonuses)
        scored_songs["billboard_score"] = scored_songs.base_score + scored_songs.bonus_score

        return scored_songs

    def _chart_score(self, chart_position: int) -> float:
        return self._raw_score(chart_position) * self._score_scale_factor

    def _bonus(self, n_weeks: int, rank: int) -> float:
        if n_weeks == 2:
            multiplier = 0.5
        else:
            multiplier = (self._modified_triangle_numbers(ceil(n_weeks/2)) +
                          self._modified_triangle_numbers(floor(n_weeks/2)))

        return multiplier * self._bonus_value_per_rank[rank]

    @staticmethod
    def _raw_score(chart_position: int) -> float:
        return -4357*(chart_position/(chart_position+10)) + 4139

    @staticmethod
    def _get_song_streaks(df: pd.DataFrame) -> list[Streak]:
        streaks = []

        current_streak = None
        for week in df[["chart_position", "previous_week"]].itertuples():
            chart_pos = cast(int, week.chart_position)

            if chart_pos > 10 or chart_pos != week.previous_week:
                if current_streak is not None:
                    # streak ended
                    streaks.append(current_streak)
                    current_streak = None
                continue

            if current_streak is None:
                current_streak = Streak(chart_pos, 2)
            else:
                current_streak = Streak(chart_pos, current_streak[1]+1)

        return streaks

    @staticmethod
    def _modified_triangle_numbers(k: int) -> float:
        return (k*(k-1))/2
