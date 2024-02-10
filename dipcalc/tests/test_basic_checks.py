"""
Tests from 6(A) Basic Checks of the DATC
"""

from dipcalc import Adjudicator
from dipcalc.utils import Unit


def test_A1_non_adjacent_move():
    """
    Check if an illegal move (without convoy) will fail.
    """
    adj = Adjudicator()
    assert not adj.validate_move(Unit.FLEET, "nth", "pic")


def test_A2_move_army_to_sea():
    """
    Check if an army could not be moved to open sea.
    """
    adj = Adjudicator()
    assert not adj.validate_move(Unit.ARMY, "liv", "iri")


def test_A3_fleet_cannot_move_inland():
    """
    Check whether a fleet can not move to land.
    """
    adj = Adjudicator()
    assert not adj.validate_move(Unit.FLEET, "kie", "mun")


def test_A4_cannot_move_to_same_territory():
    """
    Check whether a fleet can not move to land.
    """
    adj = Adjudicator()
    assert not adj.validate_move(Unit.FLEET, "kie", "kie")
