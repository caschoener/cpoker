from pokerkit import Automation, Mode, NoLimitTexasHoldem

"""
A simple AI. No bluffing, just bets/calls/folds depending on hand strength.

Human can play against it by typing c, b, f. bet is always 50% pot.
"""

NUM_PLAYERS = 2


def prettyprint_cards(cards):
    if cards is None:
        return ""
    suit_to_emoji = {
        'h': '♥️',
        'd': '♦️',
        'c': '♣️',
        's': '♠️'
    }
    return [f"{card.rank}{suit_to_emoji[card.suit.lower()]:3}" for card in cards]


class HandStrengthAI:
    def __init__(self):
        pass

    def calculateHandStrength(self, hand, board):
        # Placeholder for hand strength calculation
        # In a real implementation, you'd evaluate the strength of the hand
         return 0.5  # Return a value between 0 and 1

    def getPlay(self, gameState, player_index):
        # Simple strategy: check/call with medium-strong hands, bet with strong hands, fold weak hands
        hand = gameState.hole_cards[player_index]
        board = gameState.board_cards

        strength = self.calculateHandStrength(hand, board)

        if strength > 0.7:
            return "b"  # Bet/raise
        elif strength > 0.3:
            return "c"  # Check/call
        else:
            return "f"  # Fold


class HumanPlayer:
    def __init__(self):
        pass

    def getPlay(self, gameState, player_index):
        # Display game state to human
        print(f"\nYour cards: {prettyprint_cards(gameState.hole_cards[player_index])}")
        print(f"Board: {prettyprint_cards(x[0] for x in gameState.board_cards)}")
        print(f"Pot: {gameState.total_pot_amount}")

        if gameState.checking_or_calling_amount > 0:
            print(f"To call: {gameState.checking_or_calling_amount}")
            action = input("Your action (c=call, b=raise, f=fold): ")
        else:
            action = input("Your action (c=check, b=bet, f=fold): ")

        while action not in ['c', 'b', 'f']:
            action = input("Invalid input. Try again (c, b, f): ")

        return action


class GameRunner:
    def __init__(self, num_players):
        self.players = [HandStrengthAI() for _ in range(num_players-1)]
        self.players.append(HumanPlayer())
        self.game = NoLimitTexasHoldem(
            automations=(
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.CARD_BURNING,
                Automation.HOLE_DEALING,  # Automate dealing cards
                Automation.BOARD_DEALING,  # Automate dealing the board
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            ante_trimming_status=True,
            raw_antes=0,
            raw_blinds_or_straddles=(1, 2),  # Small blind, big blind
            min_bet=2,

        )
        self.state = self.game((100,) * num_players, num_players)

    def handle_player_action(self, player_index):
        player = self.players[player_index]
        action = player.getPlay(self.state, player_index)

        if action == 'f':
            print(f"Player {player_index} folds")
            self.state.fold()
        elif action == 'c':
            amount = self.state.checking_or_calling_amount
            if amount > 0:
                print(f"Player {player_index} calls {amount}")
            else:
                print(f"Player {player_index} checks")
            self.state.check_or_call()
        elif action == 'b':
            # Bet 50% of pot or min-raise
            if self.state.checking_or_calling_amount > 0:
                # Raising
                amount = max(
                    self.state.min_completion_betting_or_raising_to_amount,
                    self.state.checking_or_calling_amount + self.state.total_pot_amount // 2
                )
            else:
                # Betting
                amount = max(
                    self.state.min_completion_betting_or_raising_to_amount,
                    self.state.total_pot_amount // 2 or self.state.min_bet
                )
            print(f"Player {player_index} bets/raises to {amount}")
            self.state.complete_bet_or_raise_to(amount)

    def run_betting_round(self):
        # Run a complete betting round
        while True:
            if len(self.state.actor_indices) == 0:
                # Betting round is complete
                break

            player_index = self.state.actor_index
            print(f"\nPlayer {player_index}'s turn to act")
            self.handle_player_action(player_index)

    def run_hand(self):
        # Deal hole cards and run preflop
        print("--- PREFLOP ---")
        self.run_betting_round()

        if len([s for s in self.state.statuses if s]) <= 1:
            # Only one player left
            return

        # Deal flop and run flop betting
        print("\n--- FLOP ---")
        self.run_betting_round()

        if len([s for s in self.state.statuses if s]) <= 1:
            return

        # Deal turn and run turn betting
        print("\n--- TURN ---")
        self.run_betting_round()

        if len([s for s in self.state.statuses if s]) <= 1:
            return

        # Deal river and run river betting
        print("\n--- RIVER ---")
        self.run_betting_round()

        # Handle showdown if needed
        if len([s for s in self.state.statuses if s]) > 1:
            print("\n--- SHOWDOWN ---")
            while self.state.can_show_or_muck_hole_cards():
                player_index = self.state.showdown_index
                print(f"Player {player_index} shows {self.state.hole_cards[player_index]}")
                self.state.show_or_muck_hole_cards()

    def run(self):
        print("Starting Texas Hold'em game...")
        self.state = self.game((100,) * len(self.players), len(self.players))

        while True:
            print("\n==== NEW HAND ====")
            # Reset the state for a new hand

            self.run_hand()

            # Show results
            print("\nHand complete!")
            print("Player {} wins {}".format(self.state.payoffs.index(max(self.state.payoffs)), max(self.state.payoffs)))
            print("Payoffs:", self.state.payoffs)
            print("Stacks:", self.state.stacks)

            play_again = input("\nPlay another hand? (y/n): ")
            if play_again.lower() != 'y':
                break
            self.state = self.game(self.state.stacks, len(self.players))


if __name__ == "__main__":  # Fixed from "main"
    game = GameRunner(NUM_PLAYERS)  # 3 AI players + 1 human
    game.run()
