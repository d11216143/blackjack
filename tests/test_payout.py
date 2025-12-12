"""Unit tests for payout policy."""

import pytest
from core.models.card import Card, Suit, Rank
from core.models.hand import Hand
from core.rules.payout import PayoutPolicy, PayoutResult


class TestPayoutComparison:
    """Test hand comparison logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.policy = PayoutPolicy()
    
    def test_player_blackjack_wins(self):
        """Test player blackjack beats dealer 21."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.KING))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.SEVEN))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.SEVEN))
        dealer_hand.add_card(Card(Suit.HEARTS, Rank.SEVEN))
        
        result = self.policy.compare_hands(player_hand, dealer_hand)
        assert result == PayoutResult.PLAYER_BLACKJACK
    
    def test_both_blackjack_push(self):
        """Test both having blackjack results in push."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.KING))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.ACE))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.QUEEN))
        
        result = self.policy.compare_hands(player_hand, dealer_hand)
        assert result == PayoutResult.PUSH
    
    def test_player_bust_loses(self):
        """Test player bust always loses."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.KING))
        player_hand.add_card(Card(Suit.CLUBS, Rank.FIVE))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.SPADES, Rank.TEN))
        dealer_hand.add_card(Card(Suit.HEARTS, Rank.SEVEN))
        
        result = self.policy.compare_hands(player_hand, dealer_hand)
        assert result == PayoutResult.PLAYER_BUST
    
    def test_dealer_bust_player_wins(self):
        """Test dealer bust means player wins."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.NINE))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.TEN))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.KING))
        dealer_hand.add_card(Card(Suit.HEARTS, Rank.FIVE))
        
        result = self.policy.compare_hands(player_hand, dealer_hand)
        assert result == PayoutResult.DEALER_BUST
    
    def test_same_value_push(self):
        """Test same value results in push."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.NINE))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.NINE))
        
        result = self.policy.compare_hands(player_hand, dealer_hand)
        assert result == PayoutResult.PUSH
    
    def test_player_higher_wins(self):
        """Test player higher value wins."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.NINE))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.TEN))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.SEVEN))
        
        result = self.policy.compare_hands(player_hand, dealer_hand)
        assert result == PayoutResult.PLAYER_WIN
    
    def test_dealer_higher_wins(self):
        """Test dealer higher value wins."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.SEVEN))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.TEN))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.NINE))
        
        result = self.policy.compare_hands(player_hand, dealer_hand)
        assert result == PayoutResult.DEALER_WIN
    
    def test_surrender(self):
        """Test surrender result."""
        player_hand = Hand(bet=10)
        player_hand.is_surrendered = True
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.TEN))
        
        result = self.policy.compare_hands(player_hand, dealer_hand)
        assert result == PayoutResult.PLAYER_SURRENDER


class TestPayoutCalculation:
    """Test payout calculation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.policy = PayoutPolicy(blackjack_payout=1.5)
    
    def test_blackjack_payout_3_to_2(self):
        """Test blackjack pays 3:2."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.KING))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.TEN))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.SEVEN))
        
        payout = self.policy.calculate_payout(player_hand, dealer_hand)
        # Bet (10) + Win (10 * 1.5) = 25
        assert payout == 25
    
    def test_regular_win_payout(self):
        """Test regular win pays 1:1."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.NINE))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.TEN))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.SEVEN))
        
        payout = self.policy.calculate_payout(player_hand, dealer_hand)
        # Bet (10) + Win (10) = 20
        assert payout == 20
    
    def test_push_returns_bet(self):
        """Test push returns original bet."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.NINE))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.NINE))
        
        payout = self.policy.calculate_payout(player_hand, dealer_hand)
        assert payout == 10
    
    def test_loss_no_payout(self):
        """Test loss returns nothing."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.SEVEN))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.TEN))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.NINE))
        
        payout = self.policy.calculate_payout(player_hand, dealer_hand)
        assert payout == 0
    
    def test_surrender_returns_half(self):
        """Test surrender returns half of bet."""
        player_hand = Hand(bet=10)
        player_hand.is_surrendered = True
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.SIX))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.TEN))
        
        payout = self.policy.calculate_payout(player_hand, dealer_hand)
        assert payout == 5
    
    def test_insurance_win(self):
        """Test insurance pays 2:1 when dealer has blackjack."""
        player_hand = Hand(bet=10)
        player_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
        player_hand.add_card(Card(Suit.DIAMONDS, Rank.NINE))
        
        dealer_hand = Hand()
        dealer_hand.add_card(Card(Suit.CLUBS, Rank.ACE))
        dealer_hand.add_card(Card(Suit.SPADES, Rank.KING))
        
        insurance_bet = 5
        payout = self.policy.calculate_payout(player_hand, dealer_hand, insurance_bet)
        # Lost main bet (0) + Insurance bet (5) + Insurance win (5 * 2) = 15
        assert payout == 15
