from src.transformations.player_records_builder import build_player_records


def main() -> None:
	result = build_player_records()

	print("Tabela player_records gerada.")
	print(f"Arquivo: {result['output_path']}")
	print(f"Linhas lidas de player_game_stats: {result['input_rows']}")
	print(f"Linhas válidas com player_id: {result['valid_rows']}")
	print(f"Linhas geradas: {result['output_rows']}")


if __name__ == "__main__":
	main()