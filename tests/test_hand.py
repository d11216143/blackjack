"""Unit tests for Hand model."""

import pytest
from core.models.card import Card, Suit, Rank
from core.models.hand import Hand


class TestHandValue:
    """Test hand value calculation."""
    
    def test_simple_hand(self):
        """Test simple hand without aces."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.FIVE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.TEN))
        
        assert hand.value == 15
        assert not hand.is_soft
        assert not hand.is_bust
    
    def test_ace_as_11(self):
        """Test ace counted as 11."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        
        assert hand.value == 17
        assert hand.is_soft
    
    def test_ace_as_1(self):
        """Test ace counted as 1 when 11 would bust."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.TEN))
        hand.add_card(Card(Suit.CLUBS, Rank.NINE))
        
        assert hand.value == 20
        assert not hand.is_soft
    
    def test_multiple_aces(self):
        """Test multiple aces in hand."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.ACE))
        hand.add_card(Card(Suit.CLUBS, Rank.NINE))
        
        # A + A + 9 = 1 + 1 + 9 = 11 or 1 + 11 + 9 = 21
        assert hand.value == 21
        assert hand.is_soft
    
    def test_three_aces(self):
        """Test three aces in hand."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.ACE))
        hand.add_card(Card(Suit.CLUBS, Rank.ACE))
        
        # A + A + A = 1 + 1 + 11 = 13 (soft)
        assert hand.value == 13
        assert hand.is_soft
    
    def test_four_aces(self):
        """Test four aces in hand."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.ACE))
        hand.add_card(Card(Suit.CLUBS, Rank.ACE))
        hand.add_card(Card(Suit.SPADES, Rank.ACE))
        
        # A + A + A + A = 1 + 1 + 1 + 11 = 14 (soft)
        assert hand.value == 14
        assert hand.is_soft
    
    def test_blackjack(self):
        """Test natural blackjack."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.KING))
        
        assert hand.value == 21
        assert hand.is_blackjack
        assert hand.is_soft
    
    def test_21_not_blackjack(self):
        """Test 21 with more than two cards is not blackjack."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.SEVEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SEVEN))
        hand.add_card(Card(Suit.CLUBS, Rank.SEVEN))
        
        assert hand.value == 21
        assert not hand.is_blackjack
    
    def test_bust(self):
        """Test busted hand."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.KING))
        hand.add_card(Card(Suit.CLUBS, Rank.FIVE))
        
        assert hand.value == 25
        assert hand.is_bust


class TestHandActions:
    """Test hand action eligibility."""
    
    def test_can_split_same_rank(self):
        """Test can split with same rank cards."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.EIGHT))
        hand.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
        
        assert hand.can_split()
    
    def test_can_split_same_value(self):
        """Test can split with same value but different rank."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.KING))
        
        # Can only split same rank, not same value
        assert not hand.can_split()
    
    def test_cannot_split_after_hit(self):
        """Test cannot split after taking more cards."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.EIGHT))
        hand.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
        hand.add_card(Card(Suit.CLUBS, Rank.FIVE))
        
        assert not hand.can_split()
    
    def test_can_double(self):
        """Test can double with two cards."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.FIVE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        
        assert hand.can_double()
    
    def test_cannot_double_after_hit(self):
        """Test cannot double after taking more cards."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.FIVE))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        hand.add_card(Card(Suit.CLUBS, Rank.TWO))
        
        assert not hand.can_double()
    
    def test_can_surrender(self):
        """Test can surrender with two cards."""
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        
        assert hand.can_surrender()
    
    def test_cannot_surrender_split_hand(self):
        """Test cannot surrender on split hand."""
        hand = Hand(is_split_hand=True)
        hand.add_card(Card(Suit.HEARTS, Rank.EIGHT))
        hand.add_card(Card(Suit.DIAMONDS, Rank.THREE))
        
        assert not hand.can_surrender()
