"""
Tests ensuring that all standard and hard benchmark diffs are well-formed and valid unified diffs.
"""

from pathlib import Path
import pytest
from kevgate.diff_parser import parse_unified_diff

BENCHMARKS_DIR = Path(__file__).parent.parent / "src" / "kevgate" / "benchmarks"


@pytest.mark.parametrize(
    "category,expected_count",
    [
        ("true_positives", 10),
        ("false_positives", 10),
        ("hard_true_positives", 10),
        ("hard_false_positives", 10),
    ],
)
def test_benchmark_diffs_exist_and_well_formed(category: str, expected_count: int):
    cat_dir = BENCHMARKS_DIR / category
    assert cat_dir.is_dir(), f"Benchmark directory {cat_dir} does not exist"
    diff_files = sorted(cat_dir.glob("*.diff"))
    assert len(diff_files) == expected_count, (
        f"Expected {expected_count} diffs in {category}, found {len(diff_files)}"
    )

    for diff_file in diff_files:
        content = diff_file.read_text(encoding="utf-8")
        assert len(content.strip()) > 0, f"Diff file {diff_file.name} is empty"
        chunks = parse_unified_diff(content)
        assert len(chunks) > 0, f"Diff file {diff_file.name} parsed to 0 chunks"
        for chunk in chunks:
            assert chunk.file_path, f"Chunk in {diff_file.name} missing file_path"
            assert chunk.added_lines is not None, f"Chunk in {diff_file.name} missing added_lines"
            assert chunk.removed_lines is not None, f"Chunk in {diff_file.name} missing removed_lines"
