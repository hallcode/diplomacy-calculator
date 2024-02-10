import csv
import os
import networkx as nx

from dipcalc.parser import UnitType, Order, OrderType
from dipcalc.loaders import load_territories, load_factions


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

        self.territories = load_territories(variant_path)
        self.factions = load_factions(variant_path)

        self.movements = nx.DiGraph()

        self.positions_loaded = False
        self.positions = {}

    def place_default(self):
        path = os.path.join(self.variant_path, "placements.txt")
        if not os.path.exists(path):
            raise Exception("Placements file does not exist.")

        with open(path) as placements_file:
            for line in placements_file:
                placement = line.split()
                unit = UnitType(placement[1].upper())
                self.place(placement[0], unit, placement[2])

        self.positions_loaded = True

    def place_all(self, placements: list):
        for placement in placements:
            if isinstance(placement[1], str):
                placement[1] = UnitType(placement[1])
            self.place(*placement)

    def place(self, faction_code: str, unit_type: UnitType, territory_code: str):
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
        territory = self.territories.nodes[territory_code]["data"]
        faction = self.factions[faction_code]

        # Check the placement is valid
        if not isinstance(unit_type, UnitType):
            raise Exception(f"UnitType type '{unit_type}' is not valid.")

        if unit_type is UnitType.ARMY and not territory.armies:
            raise Exception("Cannot place unit; armies can only be placed on land.")

        if unit_type is UnitType.FLEET and not territory.fleets:
            raise Exception(
                "Cannot place unit; fleets can only be placed on seas or coasts."
            )

        position = (faction, unit_type)

        self.positions[territory.code] = position

        # Because some territories have a parent (stored as a type of edge)
        # we need to make sure that any parent territory is cleared, and that other children
        # of the same parent are also cleared. Very edge case but needs to be catered for.
        for t in self.territories.adj[territory.code]:
            if self.territories.edges[territory.code, t]["type"] == "parent":
                del self.positions[t]

                # Now check the other children of the parent
                for b in self.territories.adj[t]:
                    if self.territories.edges[t, b]["type"] == "parent":
                        del self.positions[b]

    def validate_order(self, order: Order, check_placements: bool = False) -> bool:
        """
        Check the basic validity of an order and return True if the order is valid
        :param order:
        :param check_placements:
        :return:
        """

        if order.type is OrderType.HOLD:
            return self.validate_position(order)

        # Check the territories are in the graph, and that they're adjacent
        unit_territory = order.territory
        from_territory = order.target[0]
        to_territory = order.target[1]
        try:
            edge = self.territories.edges[unit_territory.code, to_territory.code]

            if edge["type"] != "border":
                return False

            # If this is a support order, then also check that (1) it's not supporting itself and
            # (2) it is also bordering the territory it wishes to help
            if order.type is OrderType.SUPPORT:
                support_edge = self.territories.edges[
                    unit_territory.code, from_territory.code
                ]
                attack_edge = self.territories.edges[
                    unit_territory.code, to_territory.code
                ]

                if support_edge["type"] != "border" or attack_edge["type"] != "border":
                    return False

        except KeyError:
            return False

        if check_placements:
            return self.validate_position(order)

        # In any case, check the proposed move makes sense
        if order.unit is UnitType.ARMY and not to_territory.armies:
            return False

        if order.unit is UnitType.FLEET and not to_territory.fleets:
            return False

        return True

    def validate_position(self, order: Order):
        if not self.positions_loaded:
            return True

        try:
            initial_pos = self.positions[order.territory.code]
            if initial_pos[1] is not order.unit:
                return False

            if order.faction is not None:
                if initial_pos[0].code != order.faction.code:
                    return False

        except KeyError:
            return False

        return True
