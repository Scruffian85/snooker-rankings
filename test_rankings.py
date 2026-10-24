import io
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

import rankings

PLAYERS = [
    {"ID": 1, "Nationality": "England"},
    {"ID": 2, "Nationality": "China"},
    {"ID": 3, "Nationality": "England"},
    {"ID": 4, "Nationality": ""},
]
RANKINGS = [
    {"PlayerID": 1, "Sum": 500000},
    {"PlayerID": 2, "Sum": 700000},
    {"PlayerID": 3, "Sum": 300000},
    {"PlayerID": 4, "Sum": 1000},
    {"PlayerID": 99, "Sum": 2000},
    {"PlayerID": 5, "Sum": None},
]


class CountryTotalsTest(unittest.TestCase):
    def test_sums_and_sorts(self):
        result = rankings.country_totals(PLAYERS, RANKINGS)
        self.assertEqual(result, [("England", 800000), ("China", 700000), ("Unknown", 3000)])

    def test_empty(self):
        self.assertEqual(rankings.country_totals([], []), [])


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class FetchJsonTest(unittest.TestCase):
    @mock.patch("rankings.time.sleep")
    def test_retries_then_succeeds(self, _sleep):
        calls = [urllib.error.URLError("down"), FakeResponse(b"[1]")]
        with mock.patch("rankings.urllib.request.urlopen", side_effect=calls) as urlopen:
            self.assertEqual(rankings.fetch_json("http://x", "me"), [1])
        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(urlopen.call_args.kwargs["timeout"], rankings.TIMEOUT)

    @mock.patch("rankings.time.sleep")
    def test_no_retry_on_4xx(self, _sleep):
        err = urllib.error.HTTPError("http://x", 403, "Forbidden", {}, None)
        with mock.patch("rankings.urllib.request.urlopen", side_effect=err) as urlopen:
            with self.assertRaises(urllib.error.HTTPError):
                rankings.fetch_json("http://x", "me")
        self.assertEqual(urlopen.call_count, 1)

    @mock.patch("rankings.time.sleep")
    def test_gives_up_after_retries(self, _sleep):
        err = urllib.error.URLError("down")
        with mock.patch("rankings.urllib.request.urlopen", side_effect=err) as urlopen:
            with self.assertRaises(urllib.error.URLError):
                rankings.fetch_json("http://x", "me")
        self.assertEqual(urlopen.call_count, rankings.RETRIES)


class MainTest(unittest.TestCase):
    def run_main(self, side_effect, argv=()):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("rankings.fetch_json", side_effect=side_effect) as fetch, \
                redirect_stdout(out), redirect_stderr(err):
            code = rankings.main(list(argv))
        return code, out.getvalue(), err.getvalue(), fetch

    def test_prints_table(self):
        code, out, _, fetch = self.run_main([PLAYERS, RANKINGS], ["--season", "2026"])
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines()[0], "1 England - £800,000")
        self.assertIn("s=2026", fetch.call_args_list[0].args[0])

    def test_network_error_exits_cleanly(self):
        code, out, err, _ = self.run_main(urllib.error.URLError("down"))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("Error fetching", err)

    def test_non_list_response(self):
        code, _, err, _ = self.run_main([{"error": "x"}, RANKINGS])
        self.assertEqual(code, 1)
        self.assertIn("Unexpected", err)

    def test_empty_rankings(self):
        code, _, err, _ = self.run_main([PLAYERS, []])
        self.assertEqual(code, 1)
        self.assertIn("No rankings", err)


if __name__ == "__main__":
    unittest.main()
