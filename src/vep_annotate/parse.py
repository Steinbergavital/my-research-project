from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from vep_annotate.variants import VariantRecord

TARGET_CONSEQUENCES: frozenset[str] = frozenset(
    {"missense_variant", "start_lost", "stop_gained", "stop_lost"}
)

Status = Literal["ok", "error", "missing"]


@dataclass(frozen=True)
class AnnotationResult:
    key: str
    most_severe_consequence: str | None
    consequence_terms: frozenset[str]
    is_target_consequence: bool
    status: Status
    error_message: str | None


def extract_consequence_terms(vep_entry: dict) -> frozenset[str]:
    terms = set()
    most_severe = vep_entry.get("most_severe_consequence")
    if most_severe:
        terms.add(most_severe)
    for transcript_consequence in vep_entry.get("transcript_consequences", []):
        terms.update(transcript_consequence.get("consequence_terms", []))
    return frozenset(terms)


def target_hit(terms: frozenset[str]) -> bool:
    return bool(terms & TARGET_CONSEQUENCES)


def match_batch_response(
    response_entries: list[dict], batch: Sequence[VariantRecord]
) -> list[AnnotationResult]:
    entries_by_input = {}
    for entry in response_entries:
        entries_by_input[entry.get("input")] = entry

    results = []
    for record in batch:
        entry = entries_by_input.get(record.region_string)
        if entry is None:
            results.append(
                AnnotationResult(
                    key=record.key,
                    most_severe_consequence=None,
                    consequence_terms=frozenset(),
                    is_target_consequence=False,
                    status="missing",
                    error_message=None,
                )
            )
            continue
        if "error" in entry:
            results.append(
                AnnotationResult(
                    key=record.key,
                    most_severe_consequence=None,
                    consequence_terms=frozenset(),
                    is_target_consequence=False,
                    status="error",
                    error_message=str(entry["error"]),
                )
            )
            continue
        terms = extract_consequence_terms(entry)
        results.append(
            AnnotationResult(
                key=record.key,
                most_severe_consequence=entry.get("most_severe_consequence"),
                consequence_terms=terms,
                is_target_consequence=target_hit(terms),
                status="ok",
                error_message=None,
            )
        )
    return results
