"""Payout policy for blackjack game."""

from enum import Enum
from typing import Optional
from ..models.hand import Hand


class PayoutResult(Enum):
    """Result of a hand comparison."""
    PLAYER_BLACKJACK = "player_blackjack"
    PLAYER_WIN = "player_win"
    PUSH = "push"
    DEALER_WIN = "dealer_win"
    PLAYER_BUST = "player_bust"
    DEALER_BUST = "dealer_bust"
    PLAYER_SURRENDER = "player_surrender"


class PayoutPolicy:
    """Handles payout calculation for blackjack hands."""
    
    def __init__(self, blackjack_payout: float = 1.5, insurance_payout: float = 2.0):
        """
        Initialize payout policy.
        
        Args:
            blackjack_payout: Multiplier for blackjack (1.5 = 3:2, 1.2 = 6:5)
            insurance_payout: Multiplier for insurance (2.0 = 2:1)
        """
        self.blackjack_payout = blackjack_payout
        self.insurance_payout = insurance_payout
    
    def compare_hands(self, player_hand: Hand, dealer_hand: Hand) -> PayoutResult:
        """
        Compare player and dealer hands to determine result.
        
        Args:
            player_hand: Player's hand
            dealer_hand: Dealer's hand
            
        Returns:
            PayoutResult indicating the outcome
        """
        # Check for surrender
        if player_hand.is_surrendered:
            return PayoutResult.PLAYER_SURRENDER
        
        # Check for player bust
        if player_hand.is_bust:
            return PayoutResult.PLAYER_BUST
        
        # Check for dealer bust
        if dealer_hand.is_bust:
            return PayoutResult.DEALER_BUST
        
        player_value = player_hand.value
        dealer_value = dealer_hand.value
        
        # Check for player blackjack
        if player_hand.is_blackjack and not dealer_hand.is_blackjack:
            return PayoutResult.PLAYER_BLACKJACK
        
        # Both have blackjack or same value
        if player_value == dealer_value:
            return PayoutResult.PUSH
        
        # Compare values
        if player_value > dealer_value:
            return PayoutResult.PLAYER_WIN
        else:
            return PayoutResult.DEALER_WIN
    
    def calculate_payout(
        self,
        player_hand: Hand,
        dealer_hand: Hand,
        insurance_bet: float = 0
    ) -> float:
        """
        Calculate the total payout for a hand.
        
        Args:
            player_hand: Player's hand
            dealer_hand: Dealer's hand
            insurance_bet: Amount bet on insurance
            
        Returns:
            Total payout amount (including original bet if won)
        """
        result = self.compare_hands(player_hand, dealer_hand)
        payout = 0
        
        # Handle insurance
        if insurance_bet > 0 and dealer_hand.is_blackjack:
            payout += insurance_bet * (1 + self.insurance_payout)
        
        # Handle main hand
        if result == PayoutResult.PLAYER_BLACKJACK:
            payout += player_hand.bet * (1 + self.blackjack_payout)
        elif result == PayoutResult.PLAYER_WIN or result == PayoutResult.DEALER_BUST:
            payout += player_hand.bet * 2
        elif result == PayoutResult.PUSH:
            payout += player_hand.bet
        elif result == PayoutResult.PLAYER_SURRENDER:
            payout += player_hand.bet * 0.5
        # PLAYER_BUST and DEALER_WIN: payout is 0
        
        return payout
    
    def get_result_description(self, result: PayoutResult) -> str:
        """Get a human-readable description of the result."""
        descriptions = {
            PayoutResult.PLAYER_BLACKJACK: "Blackjack! Player wins",
            PayoutResult.PLAYER_WIN: "Player wins",
            PayoutResult.PUSH: "Push (tie)",
            PayoutResult.DEALER_WIN: "Dealer wins",
            PayoutResult.PLAYER_BUST: "Player busts - Dealer wins",
            PayoutResult.DEALER_BUST: "Dealer busts - Player wins",
            PayoutResult.PLAYER_SURRENDER: "Player surrenders",
        }
        return descriptions.get(result, "Unknown result")
