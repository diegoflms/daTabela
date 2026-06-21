from src.transformations.player_career_totals_builder import build_player_career_totals


def main() -> None:
	result = build_player_career_totals()

	print("Tabela player_career_totals gerada.")
	print(f"Arquivo: {result['output_path']}")
	print(f"Linhas lidas de player_team_seasons: {result['input_rows']}")
	print(f"Linhas geradas: {result['output_rows']}")


if __name__ == "__main__":
	main()