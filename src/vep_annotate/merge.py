from collections.abc import Sequence

import pandas as pd

from vep_annotate.parse import AnnotationResult
from vep_annotate.variants import make_variant_key


def results_to_dataframe(results: Sequence[AnnotationResult]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "key": [r.key for r in results],
            "most_severe_consequence": [r.most_severe_consequence for r in results],
            "consequence_terms": [
                "|".join(sorted(r.consequence_terms)) for r in results
            ],
            "is_target_consequence": [r.is_target_consequence for r in results],
            "status": [r.status for r in results],
            "error_message": [r.error_message for r in results],
        }
    )


def merge_annotations(input_df: pd.DataFrame, results_df: pd.DataFrame) -> pd.DataFrame:
    keys = [
        make_variant_key(
            str(row["chr"]), int(row["pos"]), str(row["ref"]), str(row["alt"])
        )
        for _, row in input_df.iterrows()
    ]
    keyed_df = input_df.copy()
    keyed_df["key"] = keys
    merged = keyed_df.merge(results_df, on="key", how="left")
    merged["status"] = merged["status"].fillna("missing")
    merged["is_target_consequence"] = merged["is_target_consequence"].fillna(False)
    return merged.drop(columns=["key"])
