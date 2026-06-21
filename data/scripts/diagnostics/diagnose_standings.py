import csv
from collections import Counter, defaultdict
from pathlib import Path


DATA_DIR = Path("dados")


def read_csv(path: Path) -> list[dict]:
	if not path.exists():
		return []

	with path.open("r", encoding="utf-8-sig", newline="") as file:
		return list(csv.DictReader(file))


def main() -> None:
	standings = read_csv(DATA_DIR / "standings.csv")

	keys = [
		(
			row.get("season_id"),
			row.get("competition"),
			row.get("team_id"),
		)
		for row in standings
	]

	duplicates = [
		key for key, count in Counter(keys).items()
		if count > 1
	]

	empty_required = [
		row for row in standings
		if not row.get("season_id")
		or not row.get("team_id")
		or not row.get("rank")
	]

	by_season = defaultdict(list)

	for row in standings:
		by_season[(row.get("season_id"), row.get("season_name"))].append(row)

	print("=== STANDINGS ===")
	print(f"Linhas: {len(standings)}")
	print(f"Chaves duplicadas: {len(duplicates)}")
	print(f"Linhas com campos obrigatórios vazios: {len(empty_required)}")

	print("\n=== TEMPORADAS ===")

	for (season_id, season_name), rows in sorted(
		by_season.items(),
		key=lambda item: int(item[0][0] or 0),
	):
		champion = [
			row for row in rows
			if row.get("is_champion") == "1"
		]

		champion_name = champion[0].get("team_name") if champion else ""

		finish_counts = Counter(row.get("finish_stage") for row in rows)

		print(
			f"{season_id} {season_name}: "
			f"{len(rows)} times | campeão: {champion_name or '-'} | "
			f"{dict(finish_counts)}"
		)

	if duplicates[:10]:
		print("\nPrimeiras duplicadas:")
		for key in duplicates[:10]:
			print(key)

	if not duplicates and not empty_required:
		print("\nStatus: OK")


if __name__ == "__main__":
	main()