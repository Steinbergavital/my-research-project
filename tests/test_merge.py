import pandas as pd

from vep_annotate.merge import merge_annotations, results_to_dataframe
from vep_annotate.parse import AnnotationResult


def test_merge_annotations_preserves_all_rows_and_marks_unmatched():
    input_df = pd.DataFrame(
        {
            "chr": ["1", "1", "1", "X"],
            "pos": [1, 2, 3, 4],
            "ref": ["G", "G", "G", "T"],
            "alt": ["A", "A", "A", "C"],
        }
    )
    results = [
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
            most_severe_consequence="synonymous_variant",
            consequence_terms=frozenset({"synonymous_variant"}),
            is_target_consequence=False,
            status="ok",
            error_message=None,
        ),
        AnnotationResult(
            key="1:3:G:A",
            most_severe_consequence=None,
            consequence_terms=frozenset(),
            is_target_consequence=False,
            status="error",
            error_message="boom",
        ),
        # no result for X:4:T:C -- simulates a run interrupted before that batch
    ]
    results_df = results_to_dataframe(results)
    merged = merge_annotations(input_df, results_df)

    assert len(merged) == 4
    assert merged.loc[0, "is_target_consequence"] == True
    assert merged.loc[0, "status"] == "ok"
    assert merged.loc[1, "is_target_consequence"] == False
    assert merged.loc[2, "status"] == "error"
    assert merged.loc[3, "status"] == "missing"
    assert merged.loc[3, "is_target_consequence"] == False
    assert "key" not in merged.columns
