"""Main game engine for blackjack."""

from typing import Optional, List, Tuple
from ..models.deck import Shoe
from ..models.player import Player, Dealer
from ..models.hand import Hand
from ..models.card import Card
from ..rules.payout import PayoutPolicy, PayoutResult
from .game_state import GameState, RoundState


class GameEngine:
    """Main game engine that controls blackjack game flow."""
    
    def __init__(
        self,
        num_decks: int = 6,
        dealer_hits_soft_17: bool = False,
        blackjack_payout: float = 1.5,
        seed: Optional[int] = None
    ):
        """
        Initialize the game engine.
        
        Args:
            num_decks: Number of decks in the shoe
            dealer_hits_soft_17: Whether dealer hits on soft 17
            blackjack_payout: Payout multiplier for blackjack (1.5 = 3:2)
            seed: Optional seed for reproducible games
        """
        self.shoe = Shoe(num_decks=num_decks, seed=seed)
        self.dealer = Dealer(hits_soft_17=dealer_hits_soft_17)
        self.player = Player()
        self.payout_policy = PayoutPolicy(blackjack_payout=blackjack_payout)
        self.state = GameState()
        self.round_results: List[Tuple[Hand, PayoutResult, float]] = []
    
    def start_round(self, bet_amount: float):
        """
        Start a new round with a bet.
        
        Args:
            bet_amount: Amount to bet
            
        Raises:
            ValueError: If not in BETTING state or invalid bet
        """
        if self.state.current_state != RoundState.BETTING:
            raise ValueError(f"Cannot bet in state {self.state.current_state}")
        
        # Clear previous round
        self.player.clear_hands()
        self.dealer.clear_hand()
        self.round_results = []
        
        # Check if shoe needs reshuffling
        if self.shoe.needs_reshuffle():
            self.shoe.shuffle()
        
        # Place bet
        self.player.place_bet(bet_amount)
        
        # Deal initial cards
        self.state.transition_to(RoundState.INITIAL_DEAL)
        self._deal_initial_cards()
        
        # Check for insurance offer
        if self.dealer.upcard.rank.card_value == 1:  # Ace showing
            self.state.transition_to(RoundState.INSURANCE)
        # Check for immediate settlement (both have blackjack)
        elif self.player.hands[0].is_blackjack or self.dealer.hand.is_blackjack:
            self.state.transition_to(RoundState.SETTLEMENT)
            self._settle_round()
        else:
            self.state.transition_to(RoundState.PLAYER_TURN)
    
    def _deal_initial_cards(self):
        """Deal initial two cards to player and dealer."""
        player_hand = self.player.hands[0]
        
        # Deal in proper order: player, dealer, player, dealer
        player_hand.add_card(self.shoe.deal_card())
        self.dealer.hand.add_card(self.shoe.deal_card())
        player_hand.add_card(self.shoe.deal_card())
        self.dealer.hand.add_card(self.shoe.deal_card())
    
    def offer_insurance(self) -> bool:
        """
        Check if insurance can be offered.
        
        Returns:
            True if insurance is available
        """
        return (
            self.state.current_state == RoundState.INSURANCE and
            self.dealer.upcard.is_ace
        )
    
    def take_insurance(self, amount: float):
        """
        Take insurance bet.
        
        Args:
            amount: Insurance bet amount (typically half of main bet)
        """
        if not self.offer_insurance():
            raise ValueError("Insurance not available")
        
        self.player.place_insurance(amount)
        
        # Check for dealer blackjack
        if self.dealer.hand.is_blackjack:
            self.state.transition_to(RoundState.SETTLEMENT)
            self._settle_round()
        else:
            self.state.transition_to(RoundState.PLAYER_TURN)
    
    def decline_insurance(self):
        """Decline insurance and continue to player turn."""
        if self.state.current_state != RoundState.INSURANCE:
            raise ValueError("Not in insurance state")
        
        # Check for dealer blackjack
        if self.dealer.hand.is_blackjack:
            self.state.transition_to(RoundState.SETTLEMENT)
            self._settle_round()
        else:
            self.state.transition_to(RoundState.PLAYER_TURN)
    
    def hit(self, hand_index: int = 0):
        """
        Player takes a card.
        
        Args:
            hand_index: Index of the hand to hit (for splits)
        """
        if self.state.current_state != RoundState.PLAYER_TURN:
            raise ValueError("Cannot hit outside of player turn")
        
        if hand_index >= len(self.player.hands):
            raise ValueError(f"Invalid hand index: {hand_index}")
        
        hand = self.player.hands[hand_index]
        if hand.is_stand or hand.is_bust or hand.is_surrendered:
            raise ValueError("Cannot hit this hand")
        
        card = self.shoe.deal_card()
        hand.add_card(card)
        
        # Check if hand is bust or reached 21
        if hand.is_bust or hand.value == 21:
            hand.is_stand = True
            self._check_player_turn_complete()
    
    def stand(self, hand_index: int = 0):
        """
        Player stands on current hand.
        
        Args:
            hand_index: Index of the hand to stand
        """
        if self.state.current_state != RoundState.PLAYER_TURN:
            raise ValueError("Cannot stand outside of player turn")
        
        if hand_index >= len(self.player.hands):
            raise ValueError(f"Invalid hand index: {hand_index}")
        
        hand = self.player.hands[hand_index]
        if hand.is_stand or hand.is_bust or hand.is_surrendered:
            raise ValueError("Cannot stand on this hand")
        
        hand.is_stand = True
        self._check_player_turn_complete()
    
    def double_down(self, hand_index: int = 0):
        """
        Player doubles down on current hand.
        
        Args:
            hand_index: Index of the hand to double
        """
        if self.state.current_state != RoundState.PLAYER_TURN:
            raise ValueError("Cannot double outside of player turn")
        
        if hand_index >= len(self.player.hands):
            raise ValueError(f"Invalid hand index: {hand_index}")
        
        hand = self.player.hands[hand_index]
        
        if not hand.can_double():
            raise ValueError("Cannot double this hand")
        
        if hand.bet > self.player.bankroll:
            raise ValueError("Insufficient funds to double")
        
        # Double the bet
        self.player.bankroll -= hand.bet
        hand.bet *= 2
        hand.is_doubled = True
        
        # Take exactly one card and stand
        card = self.shoe.deal_card()
        hand.add_card(card)
        hand.is_stand = True
        
        self._check_player_turn_complete()
    
    def split(self, hand_index: int = 0):
        """
        Split a pair into two hands.
        
        Args:
            hand_index: Index of the hand to split
        """
        if self.state.current_state != RoundState.PLAYER_TURN:
            raise ValueError("Cannot split outside of player turn")
        
        if hand_index >= len(self.player.hands):
            raise ValueError(f"Invalid hand index: {hand_index}")
        
        hand = self.player.hands[hand_index]
        
        if not hand.can_split():
            raise ValueError("Cannot split this hand")
        
        if hand.bet > self.player.bankroll:
            raise ValueError("Insufficient funds to split")
        
        # Deduct bet for second hand
        self.player.bankroll -= hand.bet
        
        # Create two new hands
        card1 = hand.cards[0]
        card2 = hand.cards[1]
        
        hand.cards = [card1]
        hand.is_split_hand = True
        
        new_hand = Hand(bet=hand.bet, is_split_hand=True)
        new_hand.cards = [card2]
        
        # Deal one card to each hand
        hand.add_card(self.shoe.deal_card())
        new_hand.add_card(self.shoe.deal_card())
        
        # Insert new hand after current hand
        self.player.hands.insert(hand_index + 1, new_hand)
        
        # If split aces, both hands automatically stand
        if card1.is_ace:
            hand.is_stand = True
            new_hand.is_stand = True
            self._check_player_turn_complete()
    
    def surrender(self, hand_index: int = 0):
        """
        Surrender the hand and get half bet back.
        
        Args:
            hand_index: Index of the hand to surrender
        """
        if self.state.current_state != RoundState.PLAYER_TURN:
            raise ValueError("Cannot surrender outside of player turn")
        
        if hand_index >= len(self.player.hands):
            raise ValueError(f"Invalid hand index: {hand_index}")
        
        hand = self.player.hands[hand_index]
        
        if not hand.can_surrender():
            raise ValueError("Cannot surrender this hand")
        
        hand.is_surrendered = True
        hand.is_stand = True
        
        self._check_player_turn_complete()
    
    def _check_player_turn_complete(self):
        """Check if all player hands are complete and transition to dealer turn."""
        all_complete = all(
            hand.is_stand or hand.is_bust or hand.is_surrendered
            for hand in self.player.hands
        )
        
        if all_complete:
            # Check if dealer needs to play
            all_bust_or_surrender = all(
                hand.is_bust or hand.is_surrendered
                for hand in self.player.hands
            )
            
            if all_bust_or_surrender:
                # Skip dealer turn if all player hands are bust/surrender
                self.state.transition_to(RoundState.SETTLEMENT)
                self._settle_round()
            else:
                self.state.transition_to(RoundState.DEALER_TURN)
                self._play_dealer_turn()
    
    def _play_dealer_turn(self):
        """Play out the dealer's turn automatically."""
        while self.dealer.should_hit():
            card = self.shoe.deal_card()
            self.dealer.hand.add_card(card)
        
        self.state.transition_to(RoundState.SETTLEMENT)
        self._settle_round()
    
    def _settle_round(self):
        """Settle all hands and calculate payouts."""
        self.round_results = []
        
        for hand in self.player.hands:
            result = self.payout_policy.compare_hands(hand, self.dealer.hand)
            payout = self.payout_policy.calculate_payout(
                hand,
                self.dealer.hand,
                self.player.insurance_bet
            )
            
            self.player.win(payout)
            self.round_results.append((hand, result, payout))
            
            # Only count insurance once
            self.player.insurance_bet = 0
        
        self.state.transition_to(RoundState.ROUND_END)
    
    def end_round(self):
        """End the round and prepare for next round."""
        if self.state.current_state != RoundState.ROUND_END:
            raise ValueError("Cannot end round in current state")
        
        self.state.transition_to(RoundState.BETTING)
    
    def get_game_status(self) -> dict:
        """
        Get current game status.
        
        Returns:
            Dictionary with game state information
        """
        return {
            "state": self.state.current_state.value,
            "player_bankroll": self.player.bankroll,
            "player_hands": [
                {
                    "cards": str(hand),
                    "value": hand.value,
                    "bet": hand.bet,
                    "is_blackjack": hand.is_blackjack,
                    "is_bust": hand.is_bust,
                    "is_soft": hand.is_soft,
                    "is_stand": hand.is_stand,
                    "is_surrendered": hand.is_surrendered,
                }
                for hand in self.player.hands
            ],
            "dealer_hand": {
                "cards": str(self.dealer.hand) if self.state.current_state not in [
                    RoundState.BETTING,
                    RoundState.INITIAL_DEAL,
                    RoundState.INSURANCE,
                    RoundState.PLAYER_TURN
                ] else (f"{self.dealer.upcard} ??" if self.dealer.upcard else ""),
                "upcard": str(self.dealer.upcard) if self.dealer.upcard else None,
                "value": self.dealer.hand.value if self.state.current_state in [
                    RoundState.DEALER_TURN,
                    RoundState.SETTLEMENT,
                    RoundState.ROUND_END
                ] else None,
            },
            "shoe_cards_remaining": len(self.shoe),
        }
