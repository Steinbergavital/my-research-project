import time
from pathlib import Path

import pandas as pd
import requests

from vep_annotate.checkpoint import (
    load_all_checkpoints,
    read_checkpoint,
    write_checkpoint,
)
from vep_annotate.merge import merge_annotations, results_to_dataframe
from vep_annotate.variants import chunk_records, dataframe_to_variant_records
from vep_annotate.vep_client import (
    DEFAULT_HEADERS,
    DEFAULT_SERVER,
    fetch_records_resilient,
)


def run_annotation(
    input_csv: Path,
    output_csv: Path,
    checkpoint_dir: Path = Path(".vep_cache"),
    batch_size: int = 200,
    delay_seconds: float = 1.0,
    server: str = DEFAULT_SERVER,
    resume: bool = True,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    df = pd.read_csv(input_csv, dtype={"chr": str, "ref": str, "alt": str})
    records = dataframe_to_variant_records(df)
    batches = chunk_records(records, batch_size=batch_size)

    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    if session is None:
        session = requests.Session()
        session.headers.update(DEFAULT_HEADERS)

    for batch_index, batch in enumerate(batches):
        if resume and read_checkpoint(checkpoint_dir, batch_index) is not None:
            continue
        results = fetch_records_resilient(batch, session, server=server)
        write_checkpoint(checkpoint_dir, batch_index, results)
        time.sleep(delay_seconds)

    all_results = load_all_checkpoints(checkpoint_dir)
    merged = merge_annotations(df, results_to_dataframe(all_results))
    merged.to_csv(output_csv, index=False)
    return merged
