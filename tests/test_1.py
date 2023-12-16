import pytest
import procenty.rrso


def test_rr_wieksza_zero():
    """Check if column names in header are uppercase"""
    r = procenty.rrso.rata_rowna(10,1,1)
    assert r > 0

