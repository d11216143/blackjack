"""Hand model for blackjack game."""

from typing import List, Tuple
from .card import Card


class Hand:
    """Represents a blackjack hand."""
    
    def __init__(self, bet: float = 0, is_split_hand: bool = False):
        """
        Initialize a hand.
        
        Args:
            bet: Amount bet on this hand
            is_split_hand: Whether this hand was created from a split
        """
        self.cards: List[Card] = []
        self.bet = bet
        self.is_split_hand = is_split_hand
        self.is_doubled = False
        self.is_surrendered = False
        self.is_stand = False
    
    def add_card(self, card: Card):
        """Add a card to the hand."""
        self.cards.append(card)
    
    def can_split(self) -> bool:
        """Check if the hand can be split (two cards of same rank)."""
        return (
            len(self.cards) == 2 and
            self.cards[0].rank == self.cards[1].rank and
            not self.is_split_hand
        )
    
    def can_double(self) -> bool:
        """Check if the hand can be doubled (exactly two cards)."""
        return len(self.cards) == 2 and not self.is_doubled
    
    def can_surrender(self) -> bool:
        """Check if the hand can surrender (exactly two cards)."""
        return len(self.cards) == 2 and not self.is_split_hand
    
    def get_value(self) -> Tuple[int, bool]:
        """
        Calculate the value of the hand.
        
        Returns:
            Tuple of (value, is_soft) where is_soft indicates if an Ace is counted as 11
        """
        total = 0
        aces = 0
        
        # Count non-ace cards
        for card in self.cards:
            if card.is_ace:
                aces += 1
            else:
                total += card.value
        
        # Add aces
        if aces == 0:
            return (total, False)
        
        # Try to use one ace as 11
        if total + 11 + (aces - 1) <= 21:
            return (total + 11 + (aces - 1), True)
        
        # All aces count as 1
        return (total + aces, False)
    
    @property
    def value(self) -> int:
        """Get the best value for the hand."""
        return self.get_value()[0]
    
    @property
    def is_soft(self) -> bool:
        """Check if the hand is soft (has an Ace counted as 11)."""
        return self.get_value()[1]
    
    @property
    def is_bust(self) -> bool:
        """Check if the hand is bust (over 21)."""
        return self.value > 21
    
    @property
    def is_blackjack(self) -> bool:
        """Check if the hand is a natural blackjack (21 with first two cards)."""
        return (
            len(self.cards) == 2 and
            self.value == 21 and
            not self.is_split_hand
        )
    
    def __str__(self) -> str:
        """String representation of the hand."""
        cards_str = " ".join(str(card) for card in self.cards)
        value, is_soft = self.get_value()
        soft_str = " (soft)" if is_soft else ""
        return f"{cards_str} = {value}{soft_str}"
    
    def __repr__(self) -> str:
        """Developer representation of the hand."""
        return f"Hand(cards={len(self.cards)}, value={self.value}, bet={self.bet})"
