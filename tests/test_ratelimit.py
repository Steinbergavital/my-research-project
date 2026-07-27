from vep_annotate.vep_client import compute_backoff_seconds


def test_compute_backoff_seconds_low_remaining():
    headers = {"x-ratelimit-remaining": "5", "x-ratelimit-reset": "30"}
    assert compute_backoff_seconds(headers) == 30.0


def test_compute_backoff_seconds_plenty_remaining():
    headers = {"x-ratelimit-remaining": "50000", "x-ratelimit-reset": "30"}
    assert compute_backoff_seconds(headers) == 0.0


def test_compute_backoff_seconds_missing_headers():
    assert compute_backoff_seconds({}) == 0.0
