from pokerkit import Automation, Mode, NoLimitTexasHoldem
import subprocess

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

    def calculateHandStrength(self, gameState, player_index):

        hand = gameState.hole_cards[player_index]
        board = gameState.board_cards
        num_active_players = len([s for s in gameState.statuses if s])

        print("Calculating strength for hand: ", hand, "and board: ", board)
        hand_str = "".join([f"{card.rank.lower()}{card.suit.lower()}" for card in hand])

        board_str = ""
        if board:
            board_str = "".join([f"{card[0].rank.lower()}{card[0].suit.lower()}" for card in board])
        
        # Build command
        cmd = ["./dependencies/holdem-eval/holdem-eval"]
        if board_str:
            cmd.extend(["-b", board_str])
        cmd.extend([hand_str]+["random"]*num_active_players)  # Compare against random hands

        cmd.extend(["-t", "0.01", "--mc"])  # Monte Carlo simulation with 0.01s timeout
        try:
            # Run holdem-eval and capture output
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout
            
            # Parse equity from output
            for line in output.split('\n'):
                if hand_str in line:
                    equity = float(line.split(':')[1].strip().rstrip('%')) / 100
                    print(f"Equity for {hand_str}: {equity*100}%")
                    return equity
                    
        except Exception as e:
            print(f"Error: {e}")
            # return 0.5  # Default to 0.5 on error
        raise Exception("Error running holdem-eval")

    def getPlay(self, gameState, player_index):
        # Simple strategy: check/call with medium-strong hands, bet with strong hands, fold weak hands
        is_raised = gameState.checking_or_calling_amount > 0
        strength = self.calculateHandStrength(gameState, player_index)
        print(f"Strength: {strength}")
        if is_raised and strength > .8:
            return "r"
        elif not is_raised and strength > 0.5:
            return "r"
        elif strength > 0.3:
            return "c"
        else:
            return "f"


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
            action = input("Your action (c=call, r=raise, f=fold): ")
        else:
            action = input("Your action (c=check, r=bet, f=fold): ")

        while action not in ['c', 'r', 'f']:
            action = input("Invalid input. Try again (c, r, f): ")

        return action
