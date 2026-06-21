import csv
from collections import Counter
from pathlib import Path


DATA_DIR = Path("dados")


def read_csv(path: Path) -> list[dict]:
	if not path.exists():
		return []

	with path.open("r", encoding="utf-8-sig", newline="") as file:
		return list(csv.DictReader(file))


def main() -> None:
	pgs = read_csv(DATA_DIR / "player_game_stats.csv")
	pts = read_csv(DATA_DIR / "player_team_seasons.csv")

	resolved_pgs = [
		row for row in pgs
		if row.get("player_id") and row.get("team_id") and row.get("season_id")
	]

	expected_keys = {
		(
			row.get("season_id"),
			row.get("team_id"),
			row.get("player_id"),
		)
		for row in resolved_pgs
	}

	actual_keys = [
		(
			row.get("season_id"),
			row.get("team_id"),
			row.get("player_id"),
		)
		for row in pts
	]

	actual_key_set = set(actual_keys)

	duplicated_keys = [
		key for key, count in Counter(actual_keys).items()
		if count > 1
	]

	missing_keys = expected_keys - actual_key_set
	extra_keys = actual_key_set - expected_keys

	empty_required = [
		row for row in pts
		if not row.get("season_id")
		or not row.get("team_id")
		or not row.get("player_id")
	]

	print("=== PLAYER TEAM SEASONS ===")
	print(f"Linhas resolvidas em player_game_stats: {len(resolved_pgs)}")
	print(f"Grupos esperados: {len(expected_keys)}")
	print(f"Linhas em player_team_seasons: {len(pts)}")
	print(f"Chaves duplicadas: {len(duplicated_keys)}")
	print(f"Chaves faltando: {len(missing_keys)}")
	print(f"Chaves extras: {len(extra_keys)}")
	print(f"Linhas com ID obrigatório vazio: {len(empty_required)}")

	if duplicated_keys[:10]:
		print("\nPrimeiras duplicadas:")
		for key in duplicated_keys[:10]:
			print(key)

	if missing_keys:
		print("\nPrimeiras faltando:")
		for key in list(missing_keys)[:10]:
			print(key)

	if extra_keys:
		print("\nPrimeiras extras:")
		for key in list(extra_keys)[:10]:
			print(key)

	if (
		len(expected_keys) == len(pts)
		and not duplicated_keys
		and not missing_keys
		and not extra_keys
		and not empty_required
	):
		print("\nStatus: OK")


if __name__ == "__main__":
	main()