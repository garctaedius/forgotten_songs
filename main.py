import os
import argparse


def create_dirs():
    if not os.path.exists("caches"):
        os.makedirs("caches")

# TODO: create args
# num ranks that get bonus score
# period of course
# Force new data from spotify


if __name__ == "__main__":
    create_dirs()

    parser = argparse.ArgumentParser(
        description="Score songs based on their billboard popularity, find their spotify streams, " +
        "and compare them to find the most forgotten songs."
    )
    parser.add_argument("-d", "--date",
                        type=str,
                        help="")
    parser.add_argument("-fn", "--force_new",
                        action="store_true",
                        help="")

    args = parser.parse_args()
    force_new = args.force_new
