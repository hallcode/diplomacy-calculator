import csv
import os
import networkx as nx

from dipcalc.utils import TRUTH_VALUES


class Adjudicator:
    def __init__(self, variant: str = "default"):
        """
        Initialise the app.

        A variant must be a directory containing the following files:
        (1) territories.csv - a list of provinces/seas with the headings:
                name, code, capitalYN, borders, armiesYN, fleetsYN, parent
        (2) factions.csv - a list of factions with the headers:
                code, name, adjectival
        (2) placements.txt - a list of initial placement instructions in the format:
                "FACTION    A/F TERRITORY"

        :param variant: either a path to a variant directory, or a name of a provided variant
        """

        # Set up variant path
        variant_path = variant
        if "/" not in variant:
            variant_path = os.path.join(os.getcwd(), "dipcalc", "variants", variant)

        if not os.path.isdir(variant_path):
            raise Exception("Variant directory does not exist")

        self.variant_path = os.path.abspath(variant_path)

        # Set up other fields (blank at the moment
        self.territories = nx.Graph()
        self.movements = nx.DiGraph()

        self.positions_loaded = False
        self.positions = {}
        self.factions = {}

        # Load the stuffs that needs to be loaded before anything else
        self.load_territories()
        self.load_factions()

    def load_territories(self):
        """
        Load the territories from the variant file
        :return: None
        """

        path = os.path.join(self.variant_path, "territories.csv")
        if not os.path.exists(path):
            raise Exception("Territories file does not exist.")

        with open(path) as territories_csv:
            reader = csv.DictReader(territories_csv)
            territories = list(reader)

            # Add all the territories to the graph
            for t in territories:
                self.territories.add_node(
                    t["code"].lower(),
                    name=t["name"],
                    code=t["code"].lower(),
                    capital=t["capitalYN"] in TRUTH_VALUES,
                    armies=t["armiesYN"] in TRUTH_VALUES,
                    fleets=t["fleetsYN"] in TRUTH_VALUES,
                )

            # Then loop again and add all the edges
            for t in territories:
                for border_territory in t["borders"].lower().split(","):
                    self.territories.add_edge(
                        t["code"].lower(), border_territory, type="border"
                    )

                if t["parent"]:
                    self.territories.add_edge(
                        t["code"], t["parent"].lower(), type="parent"
                    )

    def load_factions(self):
        """
        Load default factions from the variant file
        :return: None
        """
        path = os.path.join(self.variant_path, "factions.csv")
        if not os.path.exists(path):
            raise Exception("Factions file does not exist.")

        with open(path) as factions_file:
            reader = csv.DictReader(factions_file)
            for f in reader:
                code = f["code"].lower()
                self.factions[code] = f

    def place_default(self):
        path = os.path.join(self.variant_path, "placements.txt")
        if not os.path.exists(path):
            raise Exception("Placements file does not exist.")

        with open(path) as placements_file:
            for line in placements_file:
                placement = line.split()
                self.place(*placement)

        self.positions_loaded = True

    def place_all(self, placements: list):
        for placement in placements:
            self.place(*placement)

    def place(self, faction_code: str, unit_type: str, territory_code: str):
        """
        Place a unit on the board. Does not check if the move is legal, only that the placement
        is valid.
        Will overwrite any already placed units.
        :param faction_code: code for the faction
        :param unit_type: A - Army, F - Fleet
        :param territory_code: Code for the territory where the unit is placed
        :return: None
        """

        # Ensure consistency, don't trust the user
        faction_code = faction_code.lower()
        territory_code = territory_code.lower()
        unit_type = unit_type.upper()

        # Check the factions and territories exist
        if faction_code not in self.factions:
            raise Exception(
                f"Cannot place unit; faction '{faction_code.upper()}' does not exist."
            )

        if territory_code not in self.territories:
            raise Exception(
                f"Cannot place unit; territory '{territory_code.upper()}' does not exist."
            )

        # Keep it safe
        territory = self.territories.nodes[territory_code]

        # Check the placement is valid
        if unit_type not in ("A", "F"):
            raise Exception(f"Unit type '{unit_type}' is not valid.")

        if unit_type == "A" and not territory["armies"]:
            raise Exception("Cannot place unit; armies can only be placed on land.")

        if unit_type == "F" and not territory["fleets"]:
            raise Exception(
                "Cannot place unit; fleets can only be placed on seas or coasts."
            )

        position = (faction_code, unit_type)

        self.positions[territory_code] = position

        # Because some territories have a parent (stored as a type of edge)
        # we need to make sure that any parent territory is cleared, and that other children
        # of the same parent are also cleared. Very edge case but needs to be catered for.
        for t in self.territories.adj[territory_code]:
            if self.territories.edges[territory_code, t]["type"] == "parent":
                self.positions[t] = None

                # Now check the other children of the parent
                for b in self.territories.adj[t]:
                    if self.territories.edges[t, b]["type"] == "parent":
                        self.positions[b] = None

    def validate_move(
        self, unit_type: str, initial: str, target: str, faction: str = None
    ) -> bool:
        """
        Determine if a proposed unit move (synonymous with Attack) is valid.
        :param unit_type: A/F for Army or Fleet
        :param initial:  The territory the unit currently occupies
        :param target:  The territory the unit wishes to move to
        :param faction: Optional. The code of the faction the unit belongs to.
                        If included and positions are available, this function will
                        validate the faction.
        :return: bool
        """
        a = initial.lower()
        b = target.lower()
        try:
            edge = self.territories.edges[a, b]
        except KeyError:
            return False

        if edge["type"] != "border":
            return False

        # If there are positions, then check if there is a matching unit on the
        # initial territory. Ditto faction
        if self.positions_loaded:
            try:
                initial_pos = self.positions[a]
                if initial_pos[1].upper() != unit_type.upper():
                    return False

                if faction is not None:
                    if initial_pos[0].lower() != faction.lower():
                        return False

            except KeyError:
                return False

        target_territory = self.territories.nodes[b]
        if unit_type.upper() == "A" and not target_territory["armies"]:
            return False

        if unit_type.upper() == "F" and not target_territory["fleets"]:
            return False

        return True
