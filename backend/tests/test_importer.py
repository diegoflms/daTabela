from app.importer import convert_value


def test_convert_empty_values_to_none() -> None:
    assert convert_value("", "INTEGER") is None
    assert convert_value("   ", "REAL") is None
    assert convert_value(None, "TEXT") is None


def test_convert_integer_values() -> None:
    assert convert_value("10", "INTEGER") == 10
    assert convert_value("10.0", "INTEGER") == 10


def test_convert_real_values() -> None:
    assert convert_value("10.5", "REAL") == 10.5
    assert convert_value("10,5", "REAL") == 10.5


def test_keep_text_values() -> None:
    assert convert_value("Franca", "TEXT") == "Franca"