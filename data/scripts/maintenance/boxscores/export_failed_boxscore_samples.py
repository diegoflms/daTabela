import csv
import shutil
from pathlib import Path


DATA_DIR = Path("dados")
RAW_DIR = DATA_DIR / "raw" / "boxscores"
DIAG_PATH = DATA_DIR / "diagnostics" / "failed_boxscores_html_analysis.csv"
OUT_DIR = DATA_DIR / "diagnostics" / "failed_boxscore_samples"


def read_csv(path: Path) -> list[dict]:
	with path.open("r", encoding="utf-8-sig", newline="") as file:
		return list(csv.DictReader(file))


def copy_sample(row: dict, label: str, index: int) -> None:
	game_id = row["game_id"]
	src = RAW_DIR / f"game_{game_id}.html"

	if not src.exists():
		return

	dst = OUT_DIR / f"{label}_{index}_game_{game_id}.html"
	shutil.copyfile(src, dst)


def main() -> None:
	OUT_DIR.mkdir(parents=True, exist_ok=True)

	rows = read_csv(DIAG_PATH)

	realtime = [
		row for row in rows
		if int(row.get("realtime_idq0_tables") or 0) >= 2
	]

	unknown = [
		row for row in rows
		if int(row.get("table_count") or 0) > 0
		and int(row.get("realtime_idq0_tables") or 0) < 2
		and int(row.get("classic_general_tables") or 0) < 2
	]

	no_table = [
		row for row in rows
		if int(row.get("table_count") or 0) == 0
		and int(row.get("html_exists") or 0) == 1
	]

	for i, row in enumerate(realtime[:3], start=1):
		copy_sample(row, "realtime_idq0", i)

	for i, row in enumerate(unknown[:3], start=1):
		copy_sample(row, "unknown_table", i)

	for i, row in enumerate(no_table[:2], start=1):
		copy_sample(row, "no_table", i)

	print(f"Amostras exportadas para: {OUT_DIR}")

	print("\nRealtime idq0:")
	for row in realtime[:3]:
		print(row["game_id"], row["boxscore_url"])

	print("\nTabela desconhecida:")
	for row in unknown[:3]:
		print(row["game_id"], row["boxscore_url"])

	print("\nSem tabela:")
	for row in no_table[:2]:
		print(row["game_id"], row["boxscore_url"])


if __name__ == "__main__":
	main()