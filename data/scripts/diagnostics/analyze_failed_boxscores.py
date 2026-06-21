import csv
from pathlib import Path

from bs4 import BeautifulSoup


DATA_DIR = Path("dados")
RAW_DIR = DATA_DIR / "raw" / "boxscores"
OUT_PATH = DATA_DIR / "diagnostics" / "failed_boxscores_html_analysis.csv"


def read_csv(path: Path) -> list[dict]:
	if not path.exists():
		return []

	with path.open("r", encoding="utf-8-sig", newline="") as file:
		return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)

	with path.open("w", encoding="utf-8", newline="") as file:
		writer = csv.DictWriter(file, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(rows)


def has_text(html: str, text: str) -> int:
	return int(text.lower() in html.lower())


def main() -> None:
	failed = read_csv(DATA_DIR / "_runtime" / "failed_boxscores.csv")
	rows = []

	for item in failed:
		game_id = item.get("game_id", "")
		html_path = RAW_DIR / f"game_{game_id}.html"

		if not html_path.exists():
			rows.append(
				{
					"game_id": game_id,
					"season_id": item.get("season_id", ""),
					"error_type": item.get("error_type", ""),
					"html_exists": 0,
					"html_size": 0,
					"table_count": 0,
					"realtime_tables": 0,
					"realtime_idq0_tables": 0,
					"classic_general_tables": 0,
					"has_team_home_stats": 0,
					"has_team_away_stats": 0,
					"has_total": 0,
					"has_acoes_coletivas": 0,
					"has_pts_header": 0,
					"boxscore_url": item.get("boxscore_url", ""),
				}
			)
			continue

		html = html_path.read_text(encoding="utf-8", errors="replace")
		soup = BeautifulSoup(html, "lxml")

		rows.append(
			{
				"game_id": game_id,
				"season_id": item.get("season_id", ""),
				"error_type": item.get("error_type", ""),
				"html_exists": 1,
				"html_size": len(html),
				"table_count": len(soup.select("table")),
				"realtime_tables": len(soup.select("table.real_time_table_stats")),
				"realtime_idq0_tables": len(soup.select("table.real_time_table_stats[idq='0']")),
				"classic_general_tables": len(soup.select("table.team_general_table[idx='general'], table[idx='general']")),
				"has_team_home_stats": int(soup.select_one("#team_home_stats") is not None),
				"has_team_away_stats": int(soup.select_one("#team_away_stats") is not None),
				"has_total": has_text(html, "Total"),
				"has_acoes_coletivas": has_text(html, "Ações coletivas") or has_text(html, "Acoes coletivas"),
				"has_pts_header": has_text(html, "Pts C/T") or has_text(html, "PTS"),
				"boxscore_url": item.get("boxscore_url", ""),
			}
		)

	fieldnames = [
		"game_id",
		"season_id",
		"error_type",
		"html_exists",
		"html_size",
		"table_count",
		"realtime_tables",
		"realtime_idq0_tables",
		"classic_general_tables",
		"has_team_home_stats",
		"has_team_away_stats",
		"has_total",
		"has_acoes_coletivas",
		"has_pts_header",
		"boxscore_url",
	]

	write_csv(OUT_PATH, rows, fieldnames)

	print(f"Análise gerada em: {OUT_PATH}")
	print(f"Linhas analisadas: {len(rows)}")

	print("\nResumo rápido:")
	print(f"HTML ausente: {sum(1 for r in rows if r['html_exists'] == 0)}")
	print(f"Com realtime idq=0: {sum(1 for r in rows if r['realtime_idq0_tables'] >= 2)}")
	print(f"Com classic general: {sum(1 for r in rows if r['classic_general_tables'] >= 2)}")
	print(f"Sem nenhuma tabela: {sum(1 for r in rows if r['table_count'] == 0)}")
	print(f"Com tabela mas sem modelo conhecido: {sum(1 for r in rows if r['table_count'] > 0 and r['realtime_idq0_tables'] < 2 and r['classic_general_tables'] < 2)}")


if __name__ == "__main__":
	main()
