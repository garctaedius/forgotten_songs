from typing import NamedTuple
import os


class Streak(NamedTuple):
    chart_pos: int
    n_weeks: int


def create_dirs():
    if not os.path.exists("caches"):
        os.makedirs("caches")
