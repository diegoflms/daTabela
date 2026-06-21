import argparse
import asyncio
import csv
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from tqdm import tqdm


DATA_DIR = Path("dados")
RAW_DIR = DATA_DIR / "raw" / "boxscores"
OUT_PATH = DATA_DIR / "diagnostics" / "render_failed_boxscores_report.csv"


DEFAULT_ERROR_TYPES = {
	"empty_boxscore_template",
	"cache_missing",
}


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


def count_player_rows(html: str) -> int:
	soup = BeautifulSoup(html, "lxml")
	count = 0

	for table in soup.select("table.real_time_table_stats[idq='0']"):
		for row in table.select("tbody tr"):
			cells = [
				cell.get_text(" ", strip=True)
				for cell in row.find_all(["td", "th"])
			]

			if len(cells) < 5:
				continue

			first = cells[0].replace(" ", "")
			stats_part = " ".join(cells[2:])

			if first.startswith("#") and any(char.isdigit() for char in stats_part):
				count += 1

	return count


async def render_one(context, row: dict, wait_ms: int) -> dict:
	game_id = row["game_id"]
	url = row["boxscore_url"]
	html_path = RAW_DIR / f"game_{game_id}.html"

	page = await context.new_page()

	try:
		await page.goto(url, wait_until="domcontentloaded", timeout=60000)

		try:
			await page.wait_for_load_state("networkidle", timeout=15000)
		except Exception:
			pass

		try:
			await page.wait_for_function(
				"""
				() => {
					const tables = Array.from(
						document.querySelectorAll("table.real_time_table_stats[idq='0']")
					);

					if (tables.length < 2) {
						return false;
					}

					return tables.some(table => {
						const rows = Array.from(table.querySelectorAll("tbody tr"));

						return rows.some(row => {
							const text = row.innerText || "";
							return /^#\\s*\\d+/m.test(text) && (/\\d+:\\d+|\\d+\\/\\d+/.test(text));
						});
					});
				}
				""",
				timeout=wait_ms,
			)

			status = "rendered_with_player_rows"

		except Exception:
			status = "rendered_but_no_player_rows"

		# Pequena folga para tablesorter/DOM terminar de estabilizar.
		await page.wait_for_timeout(1000)

		html = await page.content()
		RAW_DIR.mkdir(parents=True, exist_ok=True)
		html_path.write_text(html, encoding="utf-8")

		player_rows = count_player_rows(html)

		return {
			"game_id": game_id,
			"season_id": row.get("season_id", ""),
			"previous_error_type": row.get("error_type", ""),
			"render_status": status,
			"player_rows": player_rows,
			"html_size": len(html),
			"boxscore_url": url,
			"local_html": str(html_path).replace("\\", "/"),
			"error_message": "",
		}

	except Exception as exc:
		return {
			"game_id": game_id,
			"season_id": row.get("season_id", ""),
			"previous_error_type": row.get("error_type", ""),
			"render_status": "render_failed",
			"player_rows": 0,
			"html_size": 0,
			"boxscore_url": url,
			"local_html": str(html_path).replace("\\", "/"),
			"error_message": str(exc),
		}

	finally:
		await page.close()


async def run(limit: int | None, wait_ms: int, error_types: set[str]) -> None:
	failed = read_csv(DATA_DIR / "_runtime" / "failed_boxscores.csv")

	rows = [
		row for row in failed
		if row.get("error_type", "") in error_types
	]

	if limit:
		rows = rows[:limit]

	if not rows:
		print("Nenhum boxscore para renderizar.")
		return

	results = []

	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True)

		context = await browser.new_context(
			locale="pt-BR",
			user_agent=(
				"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
				"AppleWebKit/537.36 (KHTML, like Gecko) "
				"Chrome/120.0 Safari/537.36"
			),
		)

		for row in tqdm(rows, desc="Renderizando boxscores"):
			result = await render_one(context, row, wait_ms)
			results.append(result)

		await context.close()
		await browser.close()

	fieldnames = [
		"game_id",
		"season_id",
		"previous_error_type",
		"render_status",
		"player_rows",
		"html_size",
		"boxscore_url",
		"local_html",
		"error_message",
	]

	write_csv(OUT_PATH, results, fieldnames)

	print(f"\nRelatório gerado em: {OUT_PATH}")
	print(f"Renderizados: {len(results)}")
	print(f"Com linhas de jogadores: {sum(1 for row in results if int(row['player_rows']) > 0)}")
	print(f"Sem linhas de jogadores: {sum(1 for row in results if int(row['player_rows']) == 0)}")


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Renderiza boxscores falhos com Playwright e salva o HTML pós-JS."
	)

	parser.add_argument(
		"--limit",
		type=int,
		default=None,
		help="Limita quantidade de páginas renderizadas para teste.",
	)

	parser.add_argument(
		"--wait-ms",
		type=int,
		default=25000,
		help="Tempo máximo esperando as linhas de jogadores aparecerem.",
	)

	parser.add_argument(
		"--types",
		default="empty_boxscore_template,cache_missing",
		help="Tipos de erro a renderizar, separados por vírgula.",
	)

	args = parser.parse_args()

	error_types = {
		item.strip()
		for item in args.types.split(",")
		if item.strip()
	}

	asyncio.run(
		run(
			limit=args.limit,
			wait_ms=args.wait_ms,
			error_types=error_types,
		)
	)


if __name__ == "__main__":
	main()
