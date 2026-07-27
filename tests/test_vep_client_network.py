import pytest
import requests

from vep_annotate.variants import VariantRecord
from vep_annotate.vep_client import (
    DEFAULT_HEADERS,
    fetch_records_resilient,
    post_vep_batch,
)

pytestmark = pytest.mark.network


@pytest.fixture
def session():
    s = requests.Session()
    s.headers.update(DEFAULT_HEADERS)
    return s


def test_post_vep_batch_known_missense_variant(session):
    response = post_vep_batch(["1 935779 935779 G/A 1"], session)
    assert response.status_code == 200
    data = response.json()
    assert data[0]["most_severe_consequence"] == "missense_variant"


def test_fetch_records_resilient_bisects_on_malformed_variant(session):
    records = [
        VariantRecord(
            0, "1", 935779, "G", "A", "1:935779:G:A", "1 935779 935779 G/A 1"
        ),
        VariantRecord(
            1, "1", 1336473, "G", "C", "1:1336473:G:C", "1 1336473 1336473 G/C 1"
        ),
        VariantRecord(
            2, "1", 1341803, "C", "T", "1:1341803:C:T", "1 1341803 1341803 C/T 1"
        ),
        VariantRecord(3, "0", 0, "G", "A", "bad:0:G:A", "banana"),
    ]
    results = fetch_records_resilient(records, session)
    assert len(results) == 4
    statuses = {r.key: r.status for r in results}
    assert statuses["1:935779:G:A"] == "ok"
    assert statuses["1:1336473:G:C"] == "ok"
    assert statuses["1:1341803:C:T"] == "ok"
    assert statuses["bad:0:G:A"] == "error"
