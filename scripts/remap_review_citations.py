#!/usr/bin/env python3
"""Remap numbered manuscript citations after a corpus eligibility correction."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CITATION_PATTERN = re.compile(r"\[([0-9,\-– ]+)\]")


def expand_numbers(text: str) -> list[int]:
    numbers: list[int] = []
    for item in text.replace("–", "-").split(","):
        item = item.strip()
        if not item:
            continue
        if "-" in item:
            start_text, end_text = item.split("-", 1)
            start, end = int(start_text), int(end_text)
            if end < start:
                raise ValueError(f"Invalid citation range: {item}")
            numbers.extend(range(start, end + 1))
        else:
            numbers.append(int(item))
    return numbers


def compress_numbers(numbers: list[int]) -> str:
    ordered = sorted(set(numbers))
    if not ordered:
        return ""
    parts: list[str] = []
    start = previous = ordered[0]
    for number in ordered[1:]:
        if number == previous + 1:
            previous = number
            continue
        parts.append(
            str(start) if start == previous else f"{start}-{previous}"
        )
        start = previous = number
    parts.append(str(start) if start == previous else f"{start}-{previous}")
    return ",".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manuscript", type=Path, required=True)
    parser.add_argument("--old-map", type=Path, required=True)
    parser.add_argument("--new-map", type=Path, required=True)
    parser.add_argument("--method-count", type=int, default=6)
    args = parser.parse_args()

    old_map = json.loads(args.old_map.read_text(encoding="utf-8"))
    new_map = json.loads(args.new_map.read_text(encoding="utf-8"))
    old_by_number = {
        item["number"]: candidate_id for candidate_id, item in old_map.items()
    }
    old_study_count = len(old_by_number)
    new_study_count = len(new_map)
    number_map: dict[int, int | None] = {}
    for old_number, candidate_id in old_by_number.items():
        new_item = new_map.get(candidate_id)
        number_map[old_number] = (
            int(new_item["number"]) if new_item is not None else None
        )
    for offset in range(1, args.method_count + 1):
        number_map[old_study_count + offset] = new_study_count + offset

    manuscript = args.manuscript.read_text(encoding="utf-8")
    marker = "## References"
    if marker not in manuscript:
        raise ValueError("Manuscript has no References heading.")
    body = manuscript.split(marker, 1)[0].rstrip()

    def replace(match: re.Match[str]) -> str:
        old_numbers = expand_numbers(match.group(1))
        unknown = [number for number in old_numbers if number not in number_map]
        if unknown:
            raise ValueError(f"Unknown citation numbers: {unknown}")
        new_numbers = [
            number_map[number]
            for number in old_numbers
            if number_map[number] is not None
        ]
        compressed = compress_numbers(
            [int(number) for number in new_numbers if number is not None]
        )
        if not compressed:
            raise ValueError(
                f"Citation {match.group(0)} contains only removed records; "
                "edit its prose before remapping."
            )
        return f"[{compressed}]"

    remapped = CITATION_PATTERN.sub(replace, body)
    args.manuscript.write_text(
        remapped + "\n\n## References\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "old_study_references": old_study_count,
                "new_study_references": new_study_count,
                "method_references": args.method_count,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
