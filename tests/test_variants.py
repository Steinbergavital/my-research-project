from vep_annotate.variants import (
    chunk_records,
    dataframe_to_variant_records,
    make_region_string,
    make_variant_key,
)


def test_make_variant_key():
    assert make_variant_key("1", 935779, "G", "A") == "1:935779:G:A"


def test_make_region_string():
    assert make_region_string("1", 935779, "G", "A") == "1 935779 935779 G/A 1"


def test_make_region_string_custom_strand():
    assert (
        make_region_string("1", 935779, "G", "A", strand="-1")
        == "1 935779 935779 G/A -1"
    )


def test_dataframe_to_variant_records(sample_dataframe):
    records = dataframe_to_variant_records(sample_dataframe)
    assert len(records) == 5
    assert records[0].row_index == 0
    assert records[0].chrom == "1"
    assert records[0].key == "1:935779:G:A"
    assert records[0].region_string == "1 935779 935779 G/A 1"
    assert records[3].chrom == "X"


def test_chunk_records(sample_dataframe):
    records = dataframe_to_variant_records(sample_dataframe)
    batches = chunk_records(records, batch_size=2)
    assert [len(b) for b in batches] == [2, 2, 1]
