import pytest
from app.tools.calculator import safe_calculate, RestrictedASTEvaluator


def test_basic_arithmetic():
    res = safe_calculate("149 * 2 - 149")
    assert res["success"] is True
    assert res["result"] == 149.0
    assert res["formatted"] == "149.00"


def test_complex_expressions():
    res = safe_calculate("(100.5 + 49.5) / 2")
    assert res["success"] is True
    assert res["result"] == 75.0


def test_modulo_and_power():
    res_mod = safe_calculate("10 % 3")
    assert res_mod["success"] is True
    assert res_mod["result"] == 1.0

    res_pow = safe_calculate("2 ** 8")
    assert res_pow["success"] is True
    assert res_pow["result"] == 256.0


def test_unary_operators():
    res = safe_calculate("-149 + 200")
    assert res["success"] is True
    assert res["result"] == 51.0

    res2 = safe_calculate("+50 - (+25)")
    assert res2["success"] is True
    assert res2["result"] == 25.0


def test_currency_stripping():
    res = safe_calculate("$149.00 * 2 - $149.00")
    assert res["success"] is True
    assert res["result"] == 149.0


def test_zero_division():
    res = safe_calculate("100 / 0")
    assert res["success"] is False
    assert "zero" in res["error"].lower()


def test_security_rejection_names():
    res = safe_calculate("x + 10")
    assert res["success"] is False
    assert "Disallowed security-sensitive syntax" in res["error"]


def test_security_rejection_calls():
    res = safe_calculate("__import__('os').system('ls')")
    assert res["success"] is False


def test_security_rejection_attributes():
    res = safe_calculate("str.__class__")
    assert res["success"] is False


def test_dos_prevention_excessive_power():
    res = safe_calculate("9 ** 999999")
    assert res["success"] is False
    assert "Exponent must be between" in res["error"]


def test_dos_prevention_length_limit():
    long_expr = "1 + " * 60 + "1"
    res = safe_calculate(long_expr)
    assert res["success"] is False
    assert "exceeds maximum length" in res["error"]
