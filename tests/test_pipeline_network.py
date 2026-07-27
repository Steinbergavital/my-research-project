import pandas as pd
import pytest
import requests

from vep_annotate.pipeline import run_annotation

pytestmark = pytest.mark.network


class CountingSession(requests.Session):
    def __init__(self):
        super().__init__()
        self.post_count = 0

    def post(self, *args, **kwargs):
        self.post_count += 1
        return super().post(*args, **kwargs)


@pytest.fixture
def small_input_csv(tmp_path):
    df = pd.DataFrame(
        {
            "chr": ["1", "1", "1", "X", "1"],
            "pos": [935779, 1336473, 1341803, 154947763, 999999],
            "ref": ["G", "G", "C", "T", "A"],
            "alt": ["A", "C", "T", "C", "G"],
            "aaref": ["G", "P", "A", "Y", "K"],
            "aaalt": ["S", "R", "T", "C", "E"],
            "clnSig": [0, 0, 0, 1, 0],
        }
    )
    path = tmp_path / "small_input.csv"
    df.to_csv(path, index=False)
    return path


def test_run_annotation_end_to_end(tmp_path, small_input_csv):
    output_csv = tmp_path / "output.csv"
    checkpoint_dir = tmp_path / "checkpoints"

    merged = run_annotation(
        input_csv=small_input_csv,
        output_csv=output_csv,
        checkpoint_dir=checkpoint_dir,
        batch_size=2,
        delay_seconds=0.1,
    )

    assert output_csv.exists()
    assert len(merged) == 5
    assert "most_severe_consequence" in merged.columns
    assert "is_target_consequence" in merged.columns

    missense_row = merged[(merged["chr"] == "1") & (merged["pos"] == 935779)].iloc[0]
    assert missense_row["most_severe_consequence"] == "missense_variant"
    assert missense_row["is_target_consequence"] == True


def test_run_annotation_resume_skips_completed_batches(tmp_path, small_input_csv):
    output_csv = tmp_path / "output.csv"
    checkpoint_dir = tmp_path / "checkpoints"

    run_annotation(
        input_csv=small_input_csv,
        output_csv=output_csv,
        checkpoint_dir=checkpoint_dir,
        batch_size=2,
        delay_seconds=0.1,
    )

    counting_session = CountingSession()
    run_annotation(
        input_csv=small_input_csv,
        output_csv=output_csv,
        checkpoint_dir=checkpoint_dir,
        batch_size=2,
        delay_seconds=0.1,
        session=counting_session,
    )
    assert counting_session.post_count == 0
