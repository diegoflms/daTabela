import csv
import os
import tempfile
from pathlib import Path


def ensure_parent(path: Path) -> None:
	"""Garante que a pasta pai exista."""
	path.parent.mkdir(parents=True, exist_ok=True)


def ensure_csv(path: Path, fieldnames: list[str]) -> None:
	"""Cria CSV com cabeçalho caso não exista."""
	ensure_parent(path)

	if path.exists():
		return

	with path.open("w", newline="", encoding="utf-8") as file:
		writer = csv.DictWriter(file, fieldnames=fieldnames)
		writer.writeheader()


def read_csv_dicts(path: Path) -> list[dict]:
	"""Lê CSV como lista de dicionários."""
	if not path.exists():
		return []

	with path.open("r", newline="", encoding="utf-8-sig") as file:
		return list(csv.DictReader(file))


def write_csv_dicts(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
	"""Escreve CSV de forma atômica."""
	ensure_parent(path)

	with tempfile.NamedTemporaryFile(
		"w",
		delete=False,
		newline="",
		encoding="utf-8",
		dir=str(path.parent),
	) as tmp:
		writer = csv.DictWriter(tmp, fieldnames=fieldnames, extrasaction="ignore")
		writer.writeheader()
		writer.writerows(rows)
		temp_name = tmp.name

	os.replace(temp_name, path)


def next_id(rows: list[dict]) -> int:
	"""Retorna próximo id inteiro."""
	ids = []

	for row in rows:
		try:
			ids.append(int(row.get("id", 0)))
		except ValueError:
			continue

	return max(ids, default=0) + 1