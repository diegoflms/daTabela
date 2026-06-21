from src.transformations.player_seasons_builder import build_player_seasons


def main() -> None:
    result = build_player_seasons()

    print("Tabela player_seasons gerada.")
    print(f"Arquivo: {result.get('output_path', 'dados/player_seasons.csv')}")

    for key, value in result.items():
        if key != "output_path":
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
