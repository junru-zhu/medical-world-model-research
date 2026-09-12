#!/usr/bin/env python3
"""Build a stable BibTeX bibliography from the canonical included corpus."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from reference_overrides import apply_reference_override


METHOD_ENTRIES = r"""
@article{tricco2018prisma_scr,
  title   = {PRISMA Extension for Scoping Reviews (PRISMA-ScR): Checklist and Explanation},
  author  = {Tricco, Andrea C. and Lillie, Erin and Zarin, Wasifa and O'Brien, Kelly K. and Colquhoun, Heather and Levac, Danielle and Moher, David and Peters, Micah D. J. and Horsley, Tanya and Weeks, Laura and Hempel, Susanne and Akl, Elie A. and Chang, Christine and McGowan, Jessie and Stewart, Lesley and Hartling, Lisa and Aldcroft, Adrian and Wilson, Michael G. and Garritty, Chantelle and Lewin, Simon and Godfrey, Christina M. and Macdonald, Marilyn T. and Langlois, Etienne V. and Soares-Weiser, Karla and Moriarty, Jo and Clifford, Tammy and Tunçalp, Özge and Straus, Sharon E.},
  journal = {Annals of Internal Medicine},
  year    = {2018},
  volume  = {169},
  number  = {7},
  pages   = {467--473},
  doi     = {10.7326/M18-0850}
}

@article{rethlefsen2021prisma_s,
  title   = {PRISMA-S: an extension to the PRISMA Statement for Reporting Literature Searches in Systematic Reviews},
  author  = {Rethlefsen, Melissa L. and Kirtley, Shona and Waffenschmidt, Siw and Ayala, Ana Patricia and Moher, David and Page, Matthew J. and Koffel, Jonathan B. and {PRISMA-S Group}},
  journal = {Systematic Reviews},
  year    = {2021},
  volume  = {10},
  number  = {1},
  pages   = {39},
  doi     = {10.1186/s13643-020-01542-z}
}

@article{collins2024tripod_ai,
  title   = {TRIPOD+AI Statement: Updated Guidance for Reporting Clinical Prediction Models That Use Regression or Machine Learning Methods},
  author  = {Collins, Gary S. and Moons, Karel G. M. and Dhiman, Paula and Riley, Richard D. and Beam, Andrew L. and Van Calster, Ben and Ghassemi, Marzyeh and Liu, Xiaoxuan and Reitsma, Johannes B. and van Smeden, Maarten and Boulesteix, Anne-Laure and Camaradou, Jennifer Catherine and Celi, Leo Anthony and Denaxas, Spiros and Denniston, Alastair K. and Glocker, Ben and Golub, Robert M. and Harvey, Hugh and Heinze, Georg and Hoffman, Michael M. and Kengne, André Pascal and Lam, Emily and Lee, Naomi and Loder, Elizabeth W. and Maier-Hein, Lena and Mateen, Bilal A. and McCradden, Melissa D. and Oakden-Rayner, Lauren and Ordish, Johan and Parnell, Richard and Rose, Sherri and Singh, Karandeep and Wynants, Laure and Logullo, Patricia},
  journal = {BMJ},
  year    = {2024},
  volume  = {385},
  pages   = {e078378},
  doi     = {10.1136/bmj-2023-078378}
}

@article{vasey2022decide_ai,
  title   = {Reporting Guideline for the Early-Stage Clinical Evaluation of Decision Support Systems Driven by Artificial Intelligence: DECIDE-AI},
  author  = {Vasey, Baptiste and Nagendran, Myura and Campbell, Bruce and Clifton, David A. and Collins, Gary S. and Denaxas, Spiros and Denniston, Alastair K. and Faes, Livia and Geerts, Bart and Ibrahim, Mudathir and Liu, Xiaoxuan and Mateen, Bilal A. and Mathur, Piyush and McCradden, Melissa D. and Morgan, Lauren and Ordish, Johan and Rogers, Campbell and Saria, Suchi and Ting, Daniel S. W. and Watkinson, Peter and Weber, Wim and Wheatstone, Peter and McCulloch, Peter and {DECIDE-AI expert group}},
  journal = {Nature Medicine},
  year    = {2022},
  volume  = {28},
  number  = {5},
  pages   = {924--933},
  doi     = {10.1038/s41591-022-01772-9}
}

@article{hernan2016target_trial,
  title   = {Using Big Data to Emulate a Target Trial When a Randomized Trial Is Not Available},
  author  = {Hernán, Miguel A. and Robins, James M.},
  journal = {American Journal of Epidemiology},
  year    = {2016},
  volume  = {183},
  number  = {8},
  pages   = {758--764},
  doi     = {10.1093/aje/kwv254}
}

@misc{reyna2019physionet_sepsis,
  title  = {Early Prediction of Sepsis from Clinical Data: The PhysioNet/Computing in Cardiology Challenge 2019},
  author = {Reyna, Matthew and Josef, Chris and Jeter, Russell and Shashikumar, Supreeth and Moody, Benjamin and Westover, M. Brandon and Sharma, Ashish and Nemati, Shamim and Clifford, Gari D.},
  year   = {2019},
  doi    = {10.13026/v64v-d857},
  note   = {PhysioNet, version 1.0.0}
}
""".strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def escape(value: str) -> str:
    return (
        value.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("_", r"\_")
        .replace("#", r"\#")
    )


def authors(value: str) -> str:
    value = value.strip()
    if not value:
        return "Unknown"
    if ";" in value:
        names = [name.strip() for name in value.split(";") if name.strip()]
    else:
        names = [name.strip() for name in value.split(",") if name.strip()]
    return " and ".join(escape(name) for name in names)


def key(candidate_id: str) -> str:
    return "mwm_" + re.sub(r"[^a-z0-9]+", "_", candidate_id.casefold()).strip("_")


def entry(row: dict[str, str]) -> str:
    row = apply_reference_override(row)
    fields = [
        ("title", escape(row["title"])),
        ("author", authors(row["authors"])),
        ("year", row["year"] or "2026"),
    ]
    venue = row.get("venue", "").strip()
    booktitle = row.get("booktitle", "").strip()
    doi = row.get("doi", "").strip()
    arxiv_id = row.get("arxiv_id", "").strip()
    url = row.get("url", "").strip()
    record_type = row.get("record_type", "").casefold()
    entry_type = row.get("entry_type", "").strip()
    if not entry_type:
        if "conference" in record_type or "proceedings" in record_type:
            entry_type = "inproceedings"
        elif "article" in record_type and venue:
            entry_type = "article"
        else:
            entry_type = "misc"
    if entry_type == "article" and venue:
        fields.append(("journal", escape(venue)))
    elif entry_type == "inproceedings" and (booktitle or venue):
        fields.append(("booktitle", escape(booktitle or venue)))
    elif venue:
        fields.append(("howpublished", escape(venue)))
    for source, target in (
        ("series", "series"),
        ("volume", "volume"),
        ("issue", "number"),
        ("pages", "pages"),
    ):
        value = row.get(source, "").strip()
        if value:
            fields.append((target, escape(value)))
    article_number = row.get("article_number", "").strip()
    if article_number:
        fields.append(("pages", escape(article_number)))
    publisher = row.get("publisher", "").strip()
    if publisher:
        fields.append(("publisher", escape(publisher)))
    if doi:
        fields.append(("doi", doi))
    if arxiv_id:
        fields.extend(
            [
                ("eprint", arxiv_id),
                ("archivePrefix", "arXiv"),
            ]
        )
    if url:
        fields.append(("url", url))
    note = row.get("note", "").strip()
    if note:
        fields.append(("note", escape(note)))

    lines = [f"@{entry_type}{{{key(row['candidate_id'])},"]
    for index, (name, value) in enumerate(fields):
        comma = "," if index < len(fields) - 1 else ""
        lines.append(f"  {name:<13} = {{{value}}}{comma}")
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--included", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = read_csv(args.included)
    if len(rows) != 93:
        raise ValueError(f"Expected 93 included publications, found {len(rows)}")
    entries = [entry(row) for row in rows]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n\n".join(entries + [METHOD_ENTRIES]) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(entries) + 6} BibTeX entries to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
