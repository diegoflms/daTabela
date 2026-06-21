from src.transformations.standings_builder import build_standings


def main() -> None:
	result = build_standings()

	print("Tabela standings gerada.")
	print(f"Arquivo: {result['output_path']}")
	print(f"Jogos lidos: {result['games_read']}")
	print(f"Jogos de temporada regular usados: {result['regular_games']}")
	print(f"Jogos de playoffs detectados: {result['postseason_games']}")
	print(f"Linhas geradas em standings: {result['standings_rows']}")


if __name__ == "__main__":
	main()