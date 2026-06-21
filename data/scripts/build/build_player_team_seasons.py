from src.transformations.player_team_seasons_builder import build_player_team_seasons


def main() -> None:
	result = build_player_team_seasons()

	print("Tabela player_team_seasons gerada.")
	print(f"Arquivo: {result['output_path']}")
	print(f"Linhas de player_game_stats lidas: {result['input_rows']}")
	print(f"Linhas geradas em player_team_seasons: {result['output_rows']}")

	print("\nLinhas ignoradas:")

	skipped = result["skipped"]

	if not skipped:
		print("nenhuma")
	else:
		for reason, count in skipped.items():
			print(f"{reason}: {count}")


if __name__ == "__main__":
	main()