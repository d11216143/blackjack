"""Deck and Shoe models for blackjack game."""

import random
from typing import List, Optional
from .card import Card, Suit, Rank


class Deck:
    """Represents a standard 52-card deck."""
    
    def __init__(self):
        self.cards: List[Card] = []
        self._initialize_deck()
    
    def _initialize_deck(self):
        """Initialize a standard 52-card deck."""
        self.cards = [
            Card(suit, rank)
            for suit in Suit
            for rank in Rank
        ]
    
    def __len__(self) -> int:
        """Return the number of cards in the deck."""
        return len(self.cards)


class Shoe:
    """Represents a shoe containing multiple decks with shuffling support."""
    
    def __init__(self, num_decks: int = 6, seed: Optional[int] = None):
        """
        Initialize a shoe with multiple decks.
        
        Args:
            num_decks: Number of 52-card decks to include
            seed: Optional seed for reproducible shuffling (for testing)
        """
        if num_decks < 1:
            raise ValueError("Number of decks must be at least 1")
        
        self.num_decks = num_decks
        self.cards: List[Card] = []
        self.discarded: List[Card] = []
        self._rng = random.Random(seed) if seed is not None else random.Random()
        self._initialize_shoe()
        self.shuffle()
    
    def _initialize_shoe(self):
        """Initialize the shoe with the specified number of decks."""
        self.cards = []
        for _ in range(self.num_decks):
            deck = Deck()
            self.cards.extend(deck.cards)
    
    def shuffle(self):
        """Shuffle all cards (including discarded) back into the shoe."""
        self.cards.extend(self.discarded)
        self.discarded = []
        self._rng.shuffle(self.cards)
    
    def deal_card(self) -> Card:
        """
        Deal a card from the shoe.
        
        Returns:
            Card from the top of the shoe
            
        Raises:
            ValueError: If the shoe is empty
        """
        if len(self.cards) == 0:
            raise ValueError("Shoe is empty, must reshuffle")
        return self.cards.pop()
    
    def discard(self, card: Card):
        """Add a card to the discard pile."""
        self.discarded.append(card)
    
    def needs_reshuffle(self, threshold: float = 0.25) -> bool:
        """
        Check if the shoe needs reshuffling.
        
        Args:
            threshold: Fraction of cards remaining that triggers reshuffle
            
        Returns:
            True if cards remaining is below threshold
        """
        total_cards = self.num_decks * 52
        remaining_ratio = len(self.cards) / total_cards
        return remaining_ratio < threshold
    
    def __len__(self) -> int:
        """Return the number of cards remaining in the shoe."""
        return len(self.cards)
