"""Player and Dealer models for blackjack game."""

from typing import List
from .hand import Hand


class Player:
    """Represents a blackjack player."""
    
    def __init__(self, bankroll: float = 1000):
        """
        Initialize a player.
        
        Args:
            bankroll: Starting amount of money
        """
        self.bankroll = bankroll
        self.hands: List[Hand] = []
        self.insurance_bet: float = 0
    
    def place_bet(self, amount: float) -> Hand:
        """
        Place a bet and create a new hand.
        
        Args:
            amount: Amount to bet
            
        Returns:
            New Hand with the bet amount
            
        Raises:
            ValueError: If bet exceeds bankroll
        """
        if amount > self.bankroll:
            raise ValueError(f"Insufficient funds: bet {amount} > bankroll {self.bankroll}")
        if amount <= 0:
            raise ValueError("Bet must be positive")
        
        self.bankroll -= amount
        hand = Hand(bet=amount)
        self.hands = [hand]
        return hand
    
    def place_insurance(self, amount: float):
        """
        Place an insurance bet.
        
        Args:
            amount: Amount to bet on insurance
            
        Raises:
            ValueError: If insurance bet exceeds bankroll
        """
        if amount > self.bankroll:
            raise ValueError(f"Insufficient funds for insurance: {amount} > {self.bankroll}")
        
        self.bankroll -= amount
        self.insurance_bet = amount
    
    def win(self, amount: float):
        """Add winnings to bankroll."""
        self.bankroll += amount
    
    def clear_hands(self):
        """Clear all hands and insurance for a new round."""
        self.hands = []
        self.insurance_bet = 0
    
    def __str__(self) -> str:
        """String representation of the player."""
        return f"Player(bankroll=${self.bankroll:.2f}, hands={len(self.hands)})"


class Dealer:
    """Represents the blackjack dealer."""
    
    def __init__(self, hits_soft_17: bool = False):
        """
        Initialize a dealer.
        
        Args:
            hits_soft_17: Whether dealer hits on soft 17 (H17) or stands (S17)
        """
        self.hand = Hand()
        self.hits_soft_17 = hits_soft_17
    
    def should_hit(self) -> bool:
        """
        Determine if dealer should hit based on rules.
        
        Returns:
            True if dealer should hit
        """
        value = self.hand.value
        
        if value < 17:
            return True
        
        if value == 17 and self.hand.is_soft and self.hits_soft_17:
            return True
        
        return False
    
    def clear_hand(self):
        """Clear the dealer's hand for a new round."""
        self.hand = Hand()
    
    @property
    def upcard(self) -> 'Card':
        """Get the dealer's visible card (first card)."""
        if len(self.hand.cards) == 0:
            return None
        return self.hand.cards[0]
    
    @property
    def hole_card(self) -> 'Card':
        """Get the dealer's hole card (second card)."""
        if len(self.hand.cards) < 2:
            return None
        return self.hand.cards[1]
    
    def __str__(self) -> str:
        """String representation of the dealer."""
        return f"Dealer({self.hand})"
