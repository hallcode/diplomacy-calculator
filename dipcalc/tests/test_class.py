"""
Test the Adjudicator class
"""

import os

from pytest import raises
from dipcalc import Adjudicator
from dipcalc.parser import UnitType


def test_variant_not_exists_raises_error():
    with raises(Exception):
        Adjudicator(variant="fake-variant")


def test_loading_test_variant():
    adj = Adjudicator(variant="basictest")

    assert adj.territories.number_of_nodes() == 8
    assert adj.territories.number_of_edges() == 13
    assert len(adj.factions) == 3


def test_loading_variant_from_path():
    path = os.path.join(os.getcwd(), "dipcalc", "variants", "basictest")
    adj = Adjudicator(variant=path)

    assert adj.territories.number_of_nodes() == 8
    assert adj.territories.number_of_edges() == 13
    assert len(adj.factions) == 3


def test_place_default_units():
    adj = Adjudicator()
    # No positions should be loaded at this point
    assert len(adj.positions) == 0
    assert not adj.positions_loaded

    adj.place_default()

    assert len(adj.positions) > 0
    assert adj.positions["vie"][0].code == "ah"
    assert adj.positions["vie"][1] is UnitType.ARMY
    assert adj.positions_loaded
