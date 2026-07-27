from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
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
