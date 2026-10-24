# snooker-rankings

Prints a table of countries ranked by the total prize money their professional
players have earned on the snooker.org money rankings for a season.

```
1 England - £12,345,678
2 China - £6,789,012
...
```

## How it works

1. Fetches the professional player list for the season from `api.snooker.org` (`?t=10&st=p&s=<season>`).
2. Fetches the money rankings for the same season (`?rt=MoneyRankings&s=<season>`).
3. Adds each player's ranking points to their nationality and prints countries sorted high to low.
   Players in the rankings who aren't in the pro list are counted under `Unknown`.

## Running it

Needs Python 3.8+ and no third-party packages.

```
python3 rankings.py                # 2025 season (the default)
python3 rankings.py --season 2026  # another season
```

Exits with status 1 and a message on stderr if the API can't be reached or returns
something unexpected. Network calls time out after 30s and are retried up to 3 times.

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `SNOOKER_API_HEADER` | contents of `~/.config/snooker-org-id` | `X-Requested-By` header snooker.org requires. It's personal, so it isn't in the repo: set the variable or put the value in that file. Request your own at <https://api.snooker.org/>. |

See `.env.example`. The script reads the environment directly; it does not load `.env` itself.

## Tests

```
python3 -m unittest -v
```
