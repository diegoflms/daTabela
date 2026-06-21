import pytest

from app.models.table_specs import FINAL_TABLE_SPECS
from tests.helpers import row_count


@pytest.mark.database
def test_core_tables_exist_and_are_queryable() -> None:
    for spec in FINAL_TABLE_SPECS:
        count = row_count(spec.table_name)

        assert count is not None, f"Tabela ausente ou inválida: {spec.table_name}"
        assert count >= 0, f"Contagem inválida em: {spec.table_name}"


@pytest.mark.database
@pytest.mark.parametrize(
    "table_name",
    [
        "seasons",
        "teams",
        "players",
        "games",
        "player_game_stats",
        "team_game_stats",
    ],
)
def test_core_imported_tables_are_not_empty(table_name: str) -> None:
    count = row_count(table_name)

    assert count is not None, f"Tabela ausente: {table_name}"
    assert count > 0, f"Tabela principal vazia: {table_name}"


@pytest.mark.database
def test_expected_table_catalog_size() -> None:
    table_names = [spec.table_name for spec in FINAL_TABLE_SPECS]

    assert len(table_names) >= 16
    assert len(table_names) == len(set(table_names))