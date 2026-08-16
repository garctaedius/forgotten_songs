from math import floor, ceil
from typing import cast

import pandas as pd

from utils import Streak


def score_songs(full_chart: pd.DataFrame, chart_to_score: pd.DataFrame | None = None):
    if chart_to_score is None:
        chart_to_score = full_chart

    song_scorer = BillboardScorer()
    song_scorer.score_songs(full_chart, chart_to_score)


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

    def score_songs(self, full_chart: pd.DataFrame, chart_to_score: pd.DataFrame):
        song_id = 'SmoothSantana Featuring Rob Thomas'
        occurrences = full_chart[full_chart.song_id == song_id].copy()
        occurrences["score"] = occurrences.chart_position.apply(self._chart_score)
        full_chart_score = occurrences.score.sum()

        streaks = self._get_song_streaks(occurrences)

        song_bonus = sum([self._bonus(streak.n_weeks, streak.chart_pos) for streak in streaks])
        total_score = full_chart_score + song_bonus

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
