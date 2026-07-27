import random
import time
from collections.abc import Mapping, Sequence

import requests

from vep_annotate.parse import AnnotationResult, match_batch_response
from vep_annotate.variants import VariantRecord

DEFAULT_SERVER = "https://rest.ensembl.org"
DEFAULT_ENDPOINT = "/vep/homo_sapiens/region"
MAX_BATCH_SIZE = 200
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "vep-annotate/0.1 (research use; ClinVar benchmark annotation)",
}


class VepBatchError(Exception):
    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"VEP request failed with status {status_code}: {body[:200]}")


def post_vep_batch(
    region_strings: Sequence[str],
    session: requests.Session,
    server: str = DEFAULT_SERVER,
    endpoint: str = DEFAULT_ENDPOINT,
    timeout: float = 60.0,
) -> requests.Response:
    return session.post(
        f"{server}{endpoint}",
        json={"variants": list(region_strings)},
        timeout=timeout,
    )


def compute_backoff_seconds(
    headers: Mapping[str, str], remaining_threshold: int = 50
) -> float:
    remaining = headers.get("x-ratelimit-remaining")
    reset = headers.get("x-ratelimit-reset")
    if remaining is None or reset is None:
        return 0.0
    if int(remaining) < remaining_threshold:
        return float(reset)
    return 0.0


def fetch_batch_with_retry(
    region_strings: Sequence[str],
    session: requests.Session,
    server: str = DEFAULT_SERVER,
    endpoint: str = DEFAULT_ENDPOINT,
    max_retries: int = 6,
    base_delay: float = 2.0,
) -> list[dict]:
    if max_retries < 1:
        raise ValueError("max_retries must be at least 1")
    response = None
    for attempt in range(max_retries):
        response = post_vep_batch(
            region_strings, session, server=server, endpoint=endpoint
        )
        if response.status_code == 200:
            sleep_hint = compute_backoff_seconds(response.headers)
            if sleep_hint > 0:
                time.sleep(sleep_hint)
            return response.json()
        if response.status_code == 429:
            wait = float(response.headers.get("Retry-After", base_delay * 2**attempt))
            time.sleep(wait)
            continue
        if 500 <= response.status_code < 600:
            time.sleep(base_delay * 2**attempt + random.uniform(0, 1))
            continue
        raise VepBatchError(response.status_code, response.text)
    assert response is not None
    raise VepBatchError(response.status_code, response.text)


def fetch_records_resilient(
    records: Sequence[VariantRecord],
    session: requests.Session,
    server: str = DEFAULT_SERVER,
    endpoint: str = DEFAULT_ENDPOINT,
    max_retries: int = 6,
    base_delay: float = 2.0,
) -> list[AnnotationResult]:
    if not records:
        return []
    try:
        raw = fetch_batch_with_retry(
            [r.region_string for r in records],
            session,
            server=server,
            endpoint=endpoint,
            max_retries=max_retries,
            base_delay=base_delay,
        )
        return match_batch_response(raw, records)
    except VepBatchError as e:
        if len(records) == 1:
            return [
                AnnotationResult(
                    key=records[0].key,
                    most_severe_consequence=None,
                    consequence_terms=frozenset(),
                    is_target_consequence=False,
                    status="error",
                    error_message=str(e),
                )
            ]
        if e.status_code != 400:
            raise
        mid = len(records) // 2
        return fetch_records_resilient(
            records[:mid],
            session,
            server=server,
            endpoint=endpoint,
            max_retries=max_retries,
            base_delay=base_delay,
        ) + fetch_records_resilient(
            records[mid:],
            session,
            server=server,
            endpoint=endpoint,
            max_retries=max_retries,
            base_delay=base_delay,
        )
