# -*- coding: utf-8 -*-

"""Generate an OBO Foundry-wide graph."""

import gzip
import json
import json.decoder
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

import bioregistry
import click
from bioontologies import get_obograph_by_prefix
from more_click import verbose_option
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

__all__ = [
    "main",
]

HERE = Path(__file__).parent.resolve()
PATH = HERE.joinpath("graph.tsv.gz")
SAMPLE = HERE.joinpath("graph_sample.tsv")
RELATION_SUMMARY_DETAILED = HERE.joinpath("relation_summary_detailed.json")
RELATION_SUMMARY = HERE.joinpath("relation_summary.tsv")

SKIP_PREFIXES = {
    # Decommissioned
    "gaz",
    # Overwhelming amount of trash
    "txpo",
    "apollosv",
    "aero",
    "aeo",
    # Tons of non-RO relations
    "cido",
}


def secho(s: str, fg=None) -> None:
    """Write text in tqdm with :func:`click.style`."""
    tqdm.write(click.style(s, fg=fg))


@click.command()
@click.option("--minimum")
@verbose_option
def main(minimum: Optional[str]):
    """Run large-scale ontology analysis."""
    with logging_redirect_tqdm():
        _main(minimum=minimum)


def _main(minimum: Optional[str]):
    prefixes = sorted(
        prefix
        for prefix, resource in bioregistry.read_registry().items()
        if bioregistry.get_obofoundry_uri_prefix(prefix)
        and prefix not in SKIP_PREFIXES
        and (not minimum or minimum <= prefix)
        and not bioregistry.is_deprecated(prefix)
    )
    it = tqdm(prefixes, unit="prefix", desc="Parsing")

    dd = defaultdict(list)
    counters = defaultdict(Counter)
    for prefix in it:
        it.set_postfix(prefix=prefix)
        try:
            # TODO get only base ontologies, no imports
            results = get_obograph_by_prefix(prefix)
        except (IOError, json.decoder.JSONDecodeError):
            secho(f"[{prefix}] JSON decode error", fg="red")
            continue
        if not results.graph_document:
            secho(f"[{prefix}] no graphs", fg="red")
            continue
        for graph in results.graph_document.graphs:
            for edge in graph.standardize(use_tqdm=False).edges:
                dd[edge.sub, edge.pred, edge.obj].append(prefix)
                counters[edge.pred][prefix] += 1

    secho(f"writing {len(dd):,} triples to {PATH}", fg="green")
    out_it = tqdm(sorted(dd.items()), desc="Writing", unit_scale=True, unit="row")
    with gzip.open(PATH, "wt") as file:
        with SAMPLE.open("w") as sample_file:
            for _, (triple, sources) in zip(range(10), out_it):
                for _file in [file, sample_file]:
                    print(*triple, "|".join(sources), sep="\t", file=_file)
        for triple, sources in out_it:
            print(*triple, "|".join(sources), sep="\t", file=file)

    secho(f"writing detailed summary to {RELATION_SUMMARY_DETAILED}", fg="green")
    RELATION_SUMMARY_DETAILED.write_text(json.dumps(counters, sort_keys=True, indent=2))

    secho(f"writing detailed summary to {RELATION_SUMMARY}", fg="green")
    with RELATION_SUMMARY.open("w") as file:
        for pred, c in sorted(counters.items()):
            print(
                pred,
                bool(bioregistry.normalize_curie(pred)),
                sum(c.values()),
                "|".join(sorted(c)),
                sep="\t",
                file=file,
            )


if __name__ == "__main__":
    main()
