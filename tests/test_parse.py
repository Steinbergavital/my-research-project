import json

from vep_annotate.parse import (
    extract_consequence_terms,
    match_batch_response,
    target_hit,
)
from vep_annotate.variants import VariantRecord


def _record(chrom, pos, ref, alt, row_index=0):
    key = f"{chrom}:{pos}:{ref}:{alt}"
    region_string = f"{chrom} {pos} {pos} {ref}/{alt} 1"
    return VariantRecord(
        row_index=row_index,
        chrom=chrom,
        pos=pos,
        ref=ref,
        alt=alt,
        key=key,
        region_string=region_string,
    )


def test_extract_consequence_terms_missense(fixtures_dir):
    data = json.loads((fixtures_dir / "vep_batch_ok.json").read_text())
    missense_entry = next(e for e in data if e["input"] == "1 935779 935779 G/A 1")
    terms = extract_consequence_terms(missense_entry)
    assert "missense_variant" in terms


def test_target_hit():
    assert target_hit(frozenset({"missense_variant"})) is True
    assert target_hit(frozenset({"synonymous_variant"})) is False
    assert target_hit(frozenset()) is False


def test_match_batch_response_ok_batch(fixtures_dir):
    data = json.loads((fixtures_dir / "vep_batch_ok.json").read_text())
    batch = [
        _record("1", 935779, "G", "A"),
        _record("1", 935779, "G", "Z"),
    ]
    results = match_batch_response(data, batch)
    assert len(results) == 2

    missense = next(r for r in results if r.key == "1:935779:G:A")
    assert missense.status == "ok"
    assert missense.most_severe_consequence == "missense_variant"
    assert missense.is_target_consequence is True

    non_target = next(r for r in results if r.key == "1:935779:G:Z")
    assert non_target.status == "ok"
    assert non_target.is_target_consequence is False


def test_match_batch_response_dropped_variant(fixtures_dir):
    data = json.loads((fixtures_dir / "vep_batch_dropped_variant.json").read_text())
    batch = [
        _record("1", 935779, "G", "A"),
        _record("99", 935779, "G", "A"),
    ]
    results = match_batch_response(data, batch)
    assert len(results) == 2

    resolved = next(r for r in results if r.key == "1:935779:G:A")
    assert resolved.status == "ok"

    missing = next(r for r in results if r.key == "99:935779:G:A")
    assert missing.status == "missing"
    assert missing.is_target_consequence is False


def test_match_batch_response_error_entry():
    entries = [
        {"input": "1 935779 935779 G/A 1", "error": "something went wrong"},
    ]
    batch = [_record("1", 935779, "G", "A")]
    results = match_batch_response(entries, batch)
    assert results[0].status == "error"
    assert results[0].error_message == "something went wrong"
