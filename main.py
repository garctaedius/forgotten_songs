import pandas as pd
from math import floor, ceil

# Gather hot100 data
hot100 = pd.read_csv("data\\hot_100.csv", parse_dates=["chart_date", "chart_debut"])
nineties = hot100[("1990-01-01" < hot100.chart_date) & (hot100.chart_date< "2000-01-01")].sort_values("chart_date")

def score(chart_position: int) -> float:
    return -4357*(chart_position/(chart_position+10)) + 4139

def triangle_numbers(k: int) -> float:
    return (k*(k+1))/2

def bonus(n: int) -> float:
    bonus_value = 8.8  # TODO: figure out the values for #2-#10
    if n==2:
        return 0.5 * bonus_value

    factor = triangle_numbers(ceil(n/2)) + triangle_numbers(floor(n/2))

    return factor * bonus_value
    

# Calculate score for each song in the nineties
song_id = 'SmoothSantana Featuring Rob Thomas'
occurances = nineties[nineties.song_id==song_id].copy()
occurances["score"] = occurances.chart_position.apply(score)
occurances["bonus"] = 0


pass