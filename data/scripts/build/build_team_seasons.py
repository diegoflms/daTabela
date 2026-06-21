from src.transformations.team_seasons_builder import build_team_seasons


def main() -> None:
	result = build_team_seasons()

	print("Tabela team_seasons gerada.")
	print(f"Arquivo: {result['output_path']}")
	print(f"Linhas lidas de team_game_stats: {result['input_rows']}")
	print(f"Linhas geradas: {result['output_rows']}")


if __name__ == "__main__":
	main()