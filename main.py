import argparse
from datetime import datetime

from forgotten_songs_finder import find_forgotten_songs
from utils import create_dirs
import config


if __name__ == "__main__":
    create_dirs()

    parser = argparse.ArgumentParser(
        description="Score songs based on their billboard popularity, find their spotify streams, "
        "and compare them to find the most forgotten songs."
    )
    parser.add_argument("-p", "--period",
                        type=str,
                        default="1990-01-01/2000-01-01",
                        help="The period for which to analyse songs, on the format YYYY-MM-DD/YYYY-MM-DD. "
                        "Only songs that were on the charts within the period are analyzed, but their score is "
                        "calculated from all charts, not just the chosen period. "
                        "Longer periods can lead to longer computation and load times. "
                        "Note that changes in the Billboard methodology can make it hard to compare songs from "
                        "different periods. "
                        "Also keep in mind that Billboard has been using Spotify streams in their scoring since 2007, "
                        "making the two measures hard to compare. "
                        "Default: 1990-01-01/2000-01-01")
    parser.add_argument("-fn", "--force_new",
                        action="store_true",
                        help="Load new data from Spotify, even if cached results exist.")

    args = parser.parse_args()
    config.FORCE_NEW = args.force_new

    start_date, end_date = args.period.split("/")
    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)

    if end_date <= start_date:
        raise ValueError(f"Start date is after end date! (start date: {start_date}, end date: {end_date})")

    find_forgotten_songs(start_date, end_date)
