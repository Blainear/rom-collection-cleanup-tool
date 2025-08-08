import tgdb_query

def test_enforce_rate_limit_monotonic(monkeypatch):
    times = [1000, 1000, 1000.5, 1001.5]

    def fake_time():
        return times.pop(0)

    sleep_calls = []

    def fake_sleep(duration):
        sleep_calls.append(duration)

    monkeypatch.setattr(tgdb_query.time, "time", fake_time)
    monkeypatch.setattr(tgdb_query.time, "sleep", fake_sleep)

    tgdb_query._last_request_time = 0
    tgdb_query._hour_start = 0
    tgdb_query._requests_this_hour = 0
    tgdb_query.MIN_REQUEST_INTERVAL = 1
    tgdb_query.MAX_REQUESTS_PER_HOUR = 500

    tgdb_query._enforce_rate_limit()
    assert tgdb_query._requests_this_hour == 1

    tgdb_query._enforce_rate_limit()
    assert sleep_calls == [0.5]
    assert tgdb_query._requests_this_hour == 2
