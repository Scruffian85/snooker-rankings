# Audit — snooker-rankings (2026-10-24)

## What this repo is

One 25-line Python script (`rankings.py`), one commit (2026-05-04). It calls the
snooker.org API twice and prints countries ranked by their pro players' total
money-ranking points. No Docker, no dependencies, no deployment config, no CI.

It is small but not a stub: it does one useful thing. **Recommendation: keep it.**
It doesn't need reviving or archiving; it's a finished hobby script. If you want
to use it on maggie, a cron job that runs it weekly is all it needs.

## Findings, by severity

### Medium

1. **snooker.org `X-Requested-By` value is committed in a public repo.**
   `AdamTinker319` is the access identifier snooker.org issued you. It isn't a
   password, but anyone can copy it and send traffic as you, which could get it
   rate-limited or revoked. It's in git history, so removing it now won't hide it.
   *Fixed (partly):* it can now be overridden with `SNOOKER_API_HEADER`.
   The old value is kept as the default so the script still runs unchanged.
   **Your decision:** if you care, ask snooker.org for a new value, put it in
   `SNOOKER_API_HEADER` on maggie, and delete `DEFAULT_REQUESTED_BY` so nothing
   real is in the repo. (No history rewrite done, per your rules.)

2. **Crash on any ranked player not in the pro list** (`KeyError`).
   The money rankings and the pro player list are separate endpoints; a player
   relegated or added mid-season would kill the whole report.
   *Fixed:* such players are counted under `Unknown`.

3. **No timeout on network calls.** `urlopen` with no timeout can hang forever
   if the API stalls — bad for a cron job. *Fixed:* 30s timeout, up to 3 tries
   with backoff on network errors and 5xx. 4xx (e.g. a rejected header) fails
   immediately.

### Low

4. **Raw tracebacks on any API failure, and no exit code to tell cron it failed.**
   *Fixed:* clear message on stderr, exit status 1. Also checks the API actually
   returned lists and that rankings aren't empty (a wrong/future season returns
   nothing, which previously printed an empty table and exited 0).

5. **Season hard-coded to 2025.** It's now Oct 2026, so the 2026/27 season is
   running. *Fixed:* `--season` flag; default left at 2025 so behaviour is the same.
   **Your decision:** whether the default should move to 2026.

6. **Null/missing `Sum` or `Nationality`** would crash (`TypeError`) or produce a
   blank country. *Fixed:* treated as 0 / `Unknown`.

7. **Responses not closed** (no `with`). Harmless for a one-shot script.
   *Fixed* as part of the fetch rewrite.

8. **Duplicated request code** for the two calls. *Fixed:* one `fetch_json` helper.

### Info / not fixed

9. **Commit author email** (`millar_adam@hotmail.com`) is public in git metadata.
   That's normal for GitHub. If you'd rather not expose it, set GitHub's
   "keep my email private" option and use the `@users.noreply.github.com`
   address for future commits. Not changed.

10. **No IPs, hostnames, Tailscale names, tokens or personal paths** found in the
    code or history.

11. **Dependencies:** none (stdlib only). Nothing to update or pin.

12. **Money vs points:** the script reads the `Sum` field of `MoneyRankings`
    and prints it with `£`. That's correct for the money list. Not changed.

13. **Line length / lint:** a few lines exceed 88 chars. No linter is configured
    in the repo, so I didn't reformat.

## Verification limits

The sandbox couldn't reach `api.snooker.org` (blocked by the network proxy), so
the changes were tested with mocked API responses only (9 unit tests in
`test_rankings.py`). Run `python3 rankings.py` once on maggie to confirm the
output matches what it printed before.
