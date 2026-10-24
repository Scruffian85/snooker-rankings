"""Total up snooker.org money-ranking points by player nationality."""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://api.snooker.org/"
# snooker.org only answers requests carrying the X-Requested-By value they
# issued you. Set SNOOKER_API_HEADER to override the default.
DEFAULT_REQUESTED_BY = "AdamTinker319"
DEFAULT_SEASON = 2025
TIMEOUT = 30
RETRIES = 3


def fetch_json(url, requested_by, retries=RETRIES, timeout=TIMEOUT):
    request = urllib.request.Request(url)
    request.add_header("X-Requested-By", requested_by)
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as e:
            # 4xx means the request itself is wrong (e.g. bad header); retrying won't help
            if e.code < 500 or attempt == retries:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries:
                raise
        time.sleep(2 ** attempt)


def country_totals(players, rankings):
    player_country = {}
    for player in players:
        player_country[player["ID"]] = player.get("Nationality") or "Unknown"
    country_points = {}
    for ranking in rankings:
        # Players missing from the pro list (e.g. relegated mid-season) would
        # otherwise raise KeyError and kill the whole report
        country = player_country.get(ranking["PlayerID"], "Unknown")
        points = ranking.get("Sum") or 0
        country_points[country] = country_points.get(country, 0) + points
    return sorted(country_points.items(), key=lambda x: x[1], reverse=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season", type=int, default=DEFAULT_SEASON,
                        help=f"season start year (default {DEFAULT_SEASON})")
    args = parser.parse_args(argv)
    requested_by = os.environ.get("SNOOKER_API_HEADER", DEFAULT_REQUESTED_BY)

    try:
        players = fetch_json(f"{API_URL}?t=10&st=p&s={args.season}", requested_by)
        rankings = fetch_json(f"{API_URL}?rt=MoneyRankings&s={args.season}", requested_by)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"Error fetching data from snooker.org: {e}", file=sys.stderr)
        return 1
    if not isinstance(players, list) or not isinstance(rankings, list):
        print("Unexpected response from snooker.org (not a list)", file=sys.stderr)
        return 1
    if not rankings:
        print(f"No rankings returned for season {args.season}", file=sys.stderr)
        return 1

    for position, (country, points) in enumerate(country_totals(players, rankings), start=1):
        print(position, country, "-", f"£{points:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
