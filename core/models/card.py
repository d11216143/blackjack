"""Card model for blackjack game."""

from enum import Enum
from typing import List


class Suit(Enum):
    """Card suits."""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    """Card ranks with their blackjack values."""
    ACE = (1, "A")
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "10")
    JACK = (10, "J")
    QUEEN = (10, "Q")
    KING = (10, "K")
    
    def __init__(self, card_value: int, display: str):
        self._value_ = card_value
        self.card_value = card_value
        self.display = display


class Card:
    """Represents a playing card."""
    
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
    
    @property
    def value(self) -> int:
        """Get the blackjack value of the card."""
        return self.rank.card_value
    
    @property
    def is_ace(self) -> bool:
        """Check if the card is an Ace."""
        return self.rank == Rank.ACE
    
    def __str__(self) -> str:
        """String representation of the card."""
        return f"{self.rank.display}{self.suit.value}"
    
    def __repr__(self) -> str:
        """Developer representation of the card."""
        return f"Card({self.suit.name}, {self.rank.name})"
    
    def __eq__(self, other) -> bool:
        """Check equality between cards."""
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
