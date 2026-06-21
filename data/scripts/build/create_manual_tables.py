from pathlib import Path

from src.utils.csv_io import ensure_csv


DATA_DIR = Path("dados")


AWARDS_FIELDS = [
	"id",
	"season_id",
	"season_name",
	"competition",
	"award_name",
	"award_category",
	"award_scope",
	"rank_position",
	"player_id",
	"player_name_raw",
	"team_id",
	"team_name_raw",
	"position",
	"notes",
	"source_url",
]


TEAM_TITLES_FIELDS = [
	"id",
	"season_id",
	"season_name",
	"competition",
	"title_name",
	"team_id",
	"team_name_raw",
	"opponent_team_id",
	"opponent_team_name_raw",
	"final_wins",
	"final_losses",
	"notes",
	"source_url",
]


def main() -> None:
	ensure_csv(DATA_DIR / "awards.csv", AWARDS_FIELDS)
	ensure_csv(DATA_DIR / "team_titles.csv", TEAM_TITLES_FIELDS)

	print("Tabelas manuais criadas/verificadas:")
	print(DATA_DIR / "awards.csv")
	print(DATA_DIR / "team_titles.csv")


if __name__ == "__main__":
	main()