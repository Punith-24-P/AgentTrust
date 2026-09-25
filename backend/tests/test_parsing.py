import pytest
from app.utils.parsing import extract_sections, extract_numbers_and_units, check_exact_fact


def test_extract_sections():
    text = "According to §4 of the directive, with reference to Section 12 and sec 18."
    sections = extract_sections(text)
    assert "§4" in sections
    assert "§12" in sections
    assert "§18" in sections


def test_check_exact_fact_section():
    status, reason = check_exact_fact("§4", "section", "Applications are governed by §4 of Civic Permits.")
    assert status == "PASS"

    status, reason = check_exact_fact("§4", "section", "Applications are governed by §18.")
    assert status == "FAIL"

    status, reason = check_exact_fact("§4", "section", "No section mentioned here.")
    assert status == "MISSING"


def test_check_exact_fact_deadline():
    status, reason = check_exact_fact("30 calendar days", "deadline", "Filing required within 30 calendar days.")
    assert status == "PASS"

    status, reason = check_exact_fact("30 calendar days", "deadline", "Filing required within 60 calendar days.")
    assert status == "FAIL"

    status, reason = check_exact_fact("30 calendar days", "deadline", "Filing required within 30 business days.")
    assert status == "FAIL"  # unit mismatch


def test_check_exact_fact_authority():
    status, reason = check_exact_fact("Department of Urban Administration", "authority", "Submitted to the Department of Urban Administration.")
    assert status == "PASS"

    status, reason = check_exact_fact("Environmental Hazard Response Unit", "authority", "Submitted to Police.")
    assert status == "MISSING"
