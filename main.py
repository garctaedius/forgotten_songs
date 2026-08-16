import pandas as pd
from math import floor, ceil

# Gather hot100 data
hot100 = pd.read_csv("data\\hot_100.csv", parse_dates=["chart_date", "chart_debut"], dtype={"previous_week": "Int16"})
hot100["previous_week"] = hot100.previous_week.fillna(0)  # simpler than having na values
nineties = hot100[("1990-01-01" < hot100.chart_date) & (hot100.chart_date< "2000-01-01")].sort_values("chart_date")

def raw_score(chart_position: int) -> float:
    return -4357*(chart_position/(chart_position+10)) + 4139

scale_factor = 100/raw_score(1)
def score(chart_position: int) -> float:
    return raw_score(chart_position)*scale_factor


# TODO: add variable for how man weeks get bonuses
scores = {i: score(i) for i in range(1,12)}
bonus_value = {
    i: scores[i]-scores[i+1]
    for i in range(1,11)
}

def mod_triangle_numbers(k: int) -> float:
    return (k*(k-1))/2

def bonus(n_weeks: int, rank: int) -> float:
    if n_weeks==2:
        return 0.5 * bonus_value[rank]

    factor = mod_triangle_numbers(ceil(n_weeks/2)) + mod_triangle_numbers(floor(n_weeks/2))

    return factor * bonus_value[rank]
    

# Calculate score for each song in the nineties
song_id = 'SmoothSantana Featuring Rob Thomas'
occurances = hot100[hot100.song_id==song_id].copy()
occurances["score"] = occurances.chart_position.apply(score)
full_chart_score = occurances.score.sum()

streaks = []
current_streak = None
for chart in occurances[["chart_position", "previous_week"]].itertuples():
    if chart.chart_position > 10 or chart.chart_position != chart.previous_week:  # type: ignore
        if current_streak is not None:
            # streak ended
            streaks.append(current_streak)
            current_streak = None
        continue

    if current_streak is None:
        current_streak = (chart.chart_position, 2)
    else:
        current_streak = (chart.chart_position, current_streak[1]+1)

song_bonus = sum([bonus(streak[1], streak[0]) for streak in streaks])
total_score = full_chart_score + song_bonus


pass