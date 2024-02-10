"""
Tests from 6(A) Basic Checks of the DATC
"""

from dipcalc import Adjudicator
from dipcalc.parser import UnitType, Order


def test_A1_non_adjacent_move():
    """
    Check if an illegal move (without convoy) will fail.
    """
    adj = Adjudicator()
    order = adj.str2order("UK F NTH A: PIC")
    assert not adj.validate_order(order)


def test_A2_move_army_to_sea():
    """
    Check if an army could not be moved to open sea.
    """
    adj = Adjudicator()
    order = adj.str2order("UK A LVP A: LVP IRI")
    assert not adj.validate_order(order)


def test_A3_fleet_cannot_move_inland():
    """
    Check whether a fleet can not move to land.
    """
    adj = Adjudicator()
    order = adj.str2order("DE F KIE A: MUN")
    assert not adj.validate_order(order)


def test_A4_cannot_move_to_same_territory():
    """
    Check whether a fleet can not move to land.
    """
    adj = Adjudicator()
    order = adj.str2order("DE F KIE A: KIE")
    assert not adj.validate_order(order)
