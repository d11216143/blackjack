"""Command-line interface for blackjack game."""

from typing import Optional
from core.engine.game_engine import GameEngine
from core.engine.game_state import RoundState


class BlackjackCLI:
    """Command-line interface for playing blackjack."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the CLI.
        
        Args:
            seed: Optional seed for reproducible games
        """
        self.engine = GameEngine(seed=seed)
    
    def print_game_status(self, show_dealer_hole: bool = False):
        """
        Print current game status.
        
        Args:
            show_dealer_hole: Whether to show dealer's hole card
        """
        status = self.engine.get_game_status()
        
        print("\n" + "=" * 50)
        print(f"Bankroll: ${status['player_bankroll']:.2f}")
        print(f"Cards remaining in shoe: {status['shoe_cards_remaining']}")
        print("=" * 50)
        
        # Show dealer's hand
        if self.engine.dealer.upcard:
            if show_dealer_hole or status['state'] in ['dealer_turn', 'settlement', 'round_end']:
                dealer_info = status['dealer_hand']
                print(f"\nDealer's hand: {dealer_info['cards']}")
                if dealer_info['value'] is not None:
                    print(f"Dealer's value: {dealer_info['value']}")
            else:
                print(f"\nDealer's hand: {self.engine.dealer.upcard} ??")
        
        # Show player's hands
        if self.engine.player.hands:
            print("\nYour hands:")
            for i, hand_info in enumerate(status['player_hands']):
                prefix = f"Hand {i + 1}:" if len(status['player_hands']) > 1 else "Your hand:"
                print(f"{prefix} {hand_info['cards']}")
                print(f"  Value: {hand_info['value']}, Bet: ${hand_info['bet']:.2f}")
                
                if hand_info['is_blackjack']:
                    print("  *** BLACKJACK! ***")
                elif hand_info['is_bust']:
                    print("  *** BUST! ***")
                elif hand_info['is_surrendered']:
                    print("  *** SURRENDERED ***")
        
        print()
    
    def play_round(self):
        """Play a single round of blackjack."""
        # Betting phase
        print("\n" + "=" * 50)
        print("NEW ROUND")
        print("=" * 50)
        print(f"Your bankroll: ${self.engine.player.bankroll:.2f}")
        
        while True:
            try:
                bet_input = input("Enter bet amount (or 'q' to quit): ")
                if bet_input.lower() == 'q':
                    return False
                
                bet_amount = float(bet_input)
                self.engine.start_round(bet_amount)
                break
            except ValueError as e:
                print(f"Invalid bet: {e}")
        
        self.print_game_status()
        
        # Insurance phase
        if self.engine.state.current_state == RoundState.INSURANCE:
            insurance_input = input("Dealer shows Ace. Take insurance? (y/n): ")
            if insurance_input.lower() == 'y':
                max_insurance = self.engine.player.hands[0].bet / 2
                try:
                    insurance_amount = min(max_insurance, self.engine.player.bankroll)
                    self.engine.take_insurance(insurance_amount)
                    print(f"Insurance bet: ${insurance_amount:.2f}")
                except ValueError as e:
                    print(f"Insurance declined: {e}")
                    self.engine.decline_insurance()
            else:
                self.engine.decline_insurance()
            
            self.print_game_status()
        
        # Player turn
        if self.engine.state.current_state == RoundState.PLAYER_TURN:
            for hand_index in range(len(self.engine.player.hands)):
                hand = self.engine.player.hands[hand_index]
                
                # Skip if hand is already complete
                if hand.is_stand or hand.is_bust or hand.is_surrendered:
                    continue
                
                print(f"\n--- Playing hand {hand_index + 1} of {len(self.engine.player.hands)} ---")
                
                while not hand.is_stand and not hand.is_bust:
                    # Show available actions
                    actions = []
                    actions.append("(h)it")
                    actions.append("(s)tand")
                    
                    if hand.can_double() and hand.bet <= self.engine.player.bankroll:
                        actions.append("(d)ouble")
                    
                    if hand.can_split() and hand.bet <= self.engine.player.bankroll:
                        actions.append("s(p)lit")
                    
                    if hand.can_surrender():
                        actions.append("s(u)rrender")
                    
                    action = input(f"Choose action {', '.join(actions)}: ").lower()
                    
                    try:
                        if action == 'h':
                            self.engine.hit(hand_index)
                        elif action == 's':
                            self.engine.stand(hand_index)
                        elif action == 'd' and hand.can_double():
                            self.engine.double_down(hand_index)
                        elif action == 'p' and hand.can_split():
                            self.engine.split(hand_index)
                            print("Hand split!")
                        elif action == 'u' and hand.can_surrender():
                            self.engine.surrender(hand_index)
                        else:
                            print("Invalid action")
                            continue
                        
                        self.print_game_status()
                        
                        # Check if hand changed due to split
                        if action == 'p':
                            break
                        
                    except ValueError as e:
                        print(f"Error: {e}")
        
        # Show final results
        if self.engine.state.current_state == RoundState.ROUND_END:
            self.print_game_status(show_dealer_hole=True)
            
            print("\n" + "=" * 50)
            print("ROUND RESULTS")
            print("=" * 50)
            
            for i, (hand, result, payout) in enumerate(self.engine.round_results):
                prefix = f"Hand {i + 1}:" if len(self.engine.round_results) > 1 else "Result:"
                print(f"{prefix} {self.engine.payout_policy.get_result_description(result)}")
                
                if payout > 0:
                    profit = payout - hand.bet
                    print(f"  Payout: ${payout:.2f} (profit: ${profit:.2f})")
                else:
                    print(f"  Lost: ${hand.bet:.2f}")
            
            print(f"\nNew bankroll: ${self.engine.player.bankroll:.2f}")
            
            self.engine.end_round()
        
        return True
    
    def run(self):
        """Run the main game loop."""
        print("\n" + "=" * 50)
        print("WELCOME TO BLACKJACK")
        print("=" * 50)
        print(f"Starting bankroll: ${self.engine.player.bankroll:.2f}")
        print("\nRules:")
        print("- Blackjack pays 3:2")
        print("- Dealer stands on soft 17" if not self.engine.dealer.hits_soft_17 else "- Dealer hits on soft 17")
        print("- You can Hit, Stand, Double, Split, or Surrender")
        print()
        
        while self.engine.player.bankroll > 0:
            continue_playing = self.play_round()
            
            if not continue_playing:
                break
            
            if self.engine.player.bankroll <= 0:
                print("\n" + "=" * 50)
                print("You're out of money! Game over.")
                print("=" * 50)
                break
            
            play_again = input("\nPlay another round? (y/n): ")
            if play_again.lower() != 'y':
                break
        
        print("\n" + "=" * 50)
        print("THANK YOU FOR PLAYING")
        print(f"Final bankroll: ${self.engine.player.bankroll:.2f}")
        print("=" * 50)


def main():
    """Main entry point for CLI."""
    import sys
    
    seed = None
    if len(sys.argv) > 1:
        try:
            seed = int(sys.argv[1])
            print(f"Using seed: {seed}")
        except ValueError:
            print("Invalid seed, using random")
    
    cli = BlackjackCLI(seed=seed)
    cli.run()


if __name__ == "__main__":
    main()
