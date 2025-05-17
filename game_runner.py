from pokerkit import Automation, Mode, NoLimitTexasHoldem

class GameRunner:
    def __init__(self, player_list):
        self.players = player_list
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
            mode=Mode.CASH_GAME,
        )
        self.state = self.game((100,) * len(self.players), len(self.players))

    def handle_player_action(self, player_index):
        # TODO: Check if we have enough stacks for bet or calling off
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
        elif action == 'r':
            # Bet 50% of pot or min-raise
            min_bet = self.state.min_completion_betting_or_raising_to_amount
            if not min_bet:
                min_bet = 0
            if self.state.checking_or_calling_amount > 0:
                # Raising
                amount = max(
                    min_bet,
                    self.state.checking_or_calling_amount + self.state.total_pot_amount // 2
                )
            else:
                # Betting
                amount = max(
                    min_bet,
                    self.state.total_pot_amount // 2 or self.state.min_bet
                )
            if amount > self.state.stacks[player_index]:
                amount = self.state.stacks[player_index]
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
        # List of betting rounds
        rounds = ['PREFLOP', 'FLOP', 'TURN', 'RIVER']
        
        # Run each betting round
        for round_name in rounds:
            print(f"\n--- {round_name} ---")
            self.run_betting_round()
            
            # Check if only one player remains
            if len([s for s in self.state.statuses if s]) <= 1:
                return

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
