from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class VariantRecord:
    row_index: int
    chrom: str
    pos: int
    ref: str
    alt: str
    key: str
    region_string: str


def make_variant_key(chrom: str, pos: int, ref: str, alt: str) -> str:
    return f"{chrom}:{pos}:{ref}:{alt}"


def make_region_string(
    chrom: str, pos: int, ref: str, alt: str, strand: str = "1"
) -> str:
    return f"{chrom} {pos} {pos} {ref}/{alt} {strand}"


def dataframe_to_variant_records(df: pd.DataFrame) -> list[VariantRecord]:
    records = []
    columns = zip(df["chr"], df["pos"], df["ref"], df["alt"], strict=True)
    for row_index, (chr_value, pos_value, ref_value, alt_value) in enumerate(columns):
        chrom = str(chr_value)
        pos = int(pos_value)
        ref = str(ref_value)
        alt = str(alt_value)
        records.append(
            VariantRecord(
                row_index=row_index,
                chrom=chrom,
                pos=pos,
                ref=ref,
                alt=alt,
                key=make_variant_key(chrom, pos, ref, alt),
                region_string=make_region_string(chrom, pos, ref, alt),
            )
        )
    return records


def chunk_records(
    records: Sequence[VariantRecord], batch_size: int = 200
) -> list[list[VariantRecord]]:
    return [
        list(records[i : i + batch_size]) for i in range(0, len(records), batch_size)
    ]
