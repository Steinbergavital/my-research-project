from vep_annotate.checkpoint import (
    deserialize_results,
    load_all_checkpoints,
    read_checkpoint,
    serialize_results,
    write_checkpoint,
)
from vep_annotate.parse import AnnotationResult

RESULTS = [
    AnnotationResult(
        key="1:1:G:A",
        most_severe_consequence="missense_variant",
        consequence_terms=frozenset({"missense_variant"}),
        is_target_consequence=True,
        status="ok",
        error_message=None,
    ),
    AnnotationResult(
        key="1:2:G:A",
        most_severe_consequence=None,
        consequence_terms=frozenset(),
        is_target_consequence=False,
        status="error",
        error_message="boom",
    ),
    AnnotationResult(
        key="1:3:G:A",
        most_severe_consequence=None,
        consequence_terms=frozenset(),
        is_target_consequence=False,
        status="missing",
        error_message=None,
    ),
]


def test_serialize_deserialize_round_trip():
    text = serialize_results(RESULTS)
    round_tripped = deserialize_results(text)
    assert round_tripped == RESULTS


def test_write_read_checkpoint_round_trip(tmp_path):
    write_checkpoint(tmp_path, 0, RESULTS)
    round_tripped = read_checkpoint(tmp_path, 0)
    assert round_tripped == RESULTS


def test_read_checkpoint_missing_returns_none(tmp_path):
    assert read_checkpoint(tmp_path, 0) is None


def test_load_all_checkpoints_concatenates_in_order(tmp_path):
    write_checkpoint(tmp_path, 0, RESULTS[:1])
    write_checkpoint(tmp_path, 1, RESULTS[1:2])
    write_checkpoint(tmp_path, 2, RESULTS[2:3])
    assert load_all_checkpoints(tmp_path) == RESULTS
