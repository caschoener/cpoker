from handstrength_ai import HandStrengthAI, HumanPlayer
from game_runner import GameRunner
import argparse


def main():
    parser = argparse.ArgumentParser(description='Play poker against AI opponents')
    parser.add_argument('--num_players', type=int, default=2,
                        help='Number of players (default: 2)')
    args = parser.parse_args()

    player_list = [HumanPlayer()] + [HandStrengthAI() for _ in range(args.num_players-1)]

    game_runner = GameRunner(player_list)
    game_runner.run()


if __name__ == "__main__":
    main()
