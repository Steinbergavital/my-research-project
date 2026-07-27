import json
import os
from collections.abc import Sequence
from pathlib import Path

from vep_annotate.parse import AnnotationResult


def checkpoint_file_path(checkpoint_dir: Path, batch_index: int) -> Path:
    return checkpoint_dir / f"batch_{batch_index:05d}.jsonl"


def serialize_results(results: Sequence[AnnotationResult]) -> str:
    lines = []
    for result in results:
        lines.append(
            json.dumps(
                {
                    "key": result.key,
                    "most_severe_consequence": result.most_severe_consequence,
                    "consequence_terms": sorted(result.consequence_terms),
                    "is_target_consequence": result.is_target_consequence,
                    "status": result.status,
                    "error_message": result.error_message,
                }
            )
        )
    return "\n".join(lines) + ("\n" if lines else "")


def deserialize_results(text: str) -> list[AnnotationResult]:
    results = []
    for line in text.splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        results.append(
            AnnotationResult(
                key=data["key"],
                most_severe_consequence=data["most_severe_consequence"],
                consequence_terms=frozenset(data["consequence_terms"]),
                is_target_consequence=data["is_target_consequence"],
                status=data["status"],
                error_message=data["error_message"],
            )
        )
    return results


def write_checkpoint(
    checkpoint_dir: Path, batch_index: int, results: Sequence[AnnotationResult]
) -> None:
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    final_path = checkpoint_file_path(checkpoint_dir, batch_index)
    tmp_path = final_path.with_suffix(".tmp")
    tmp_path.write_text(serialize_results(results))
    os.replace(tmp_path, final_path)


def read_checkpoint(
    checkpoint_dir: Path, batch_index: int
) -> list[AnnotationResult] | None:
    path = checkpoint_file_path(checkpoint_dir, batch_index)
    if not path.exists():
        return None
    return deserialize_results(path.read_text())


def load_all_checkpoints(checkpoint_dir: Path) -> list[AnnotationResult]:
    results = []
    for path in sorted(checkpoint_dir.glob("batch_*.jsonl")):
        results.extend(deserialize_results(path.read_text()))
    return results
