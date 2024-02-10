import os
import csv

import networkx as nx
from dipcalc.utils import TRUTH_VALUES
from dipcalc.parser import UnitType, Territory, Faction, Order


def load_territories(variant_path: str) -> nx.Graph:
    territories_graph = nx.Graph()

    path = os.path.join(variant_path, "territories.csv")
    if not os.path.exists(path):
        raise Exception("Territories file does not exist.")

    with open(path) as territories_csv:
        reader = csv.DictReader(territories_csv)
        territories = list(reader)

        # Add all the territories to the graph
        for t in territories:
            territories_graph.add_node(
                t["code"].lower(),
                data=Territory(
                    name=t["name"],
                    code=t["code"].lower(),
                    capital=t["capitalYN"] in TRUTH_VALUES,
                    armies=t["armiesYN"] in TRUTH_VALUES,
                    fleets=t["fleetsYN"] in TRUTH_VALUES,
                ),
            )

        # Then loop again and add all the edges
        for t in territories:
            for border_territory in t["borders"].lower().split(","):
                territories_graph.add_edge(
                    t["code"].lower(), border_territory, type="border"
                )

            if t["parent"]:
                territories_graph.add_edge(
                    t["code"], t["parent"].lower(), type="parent"
                )

    return territories_graph


def load_factions(variant_path: str) -> dict[str, Faction]:
    """
    Load factions from file
    :param variant_path:
    :return:
    """
    factions = {}

    path = os.path.join(variant_path, "factions.csv")
    if not os.path.exists(path):
        raise Exception("Factions file does not exist.")

    with open(path) as factions_file:
        reader = csv.DictReader(factions_file)
        for f in reader:
            code = f["code"].lower()
            factions[code] = Faction(code=code, name=f["name"])

    return factions
