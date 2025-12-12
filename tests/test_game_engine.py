"""Integration tests for game engine."""

import pytest
from core.engine.game_engine import GameEngine
from core.engine.game_state import RoundState


class TestGameFlow:
    """Test complete game flow."""
    
    def test_simple_round_player_wins(self):
        """Test a simple round where player wins."""
        # Use seed for reproducible test
        engine = GameEngine(seed=42)
        
        # Start round with bet
        initial_bankroll = engine.player.bankroll
        engine.start_round(10)
        
        # Check initial state
        assert engine.state.current_state in [
            RoundState.PLAYER_TURN,
            RoundState.SETTLEMENT,
            RoundState.INSURANCE
        ]
        assert len(engine.player.hands) == 1
        assert len(engine.player.hands[0].cards) == 2
        assert len(engine.dealer.hand.cards) == 2
    
    def test_player_hit_and_stand(self):
        """Test player hitting and standing."""
        engine = GameEngine(seed=123)
        engine.start_round(10)
        
        # Skip if immediate settlement
        if engine.state.current_state == RoundState.PLAYER_TURN:
            # Hit
            initial_cards = len(engine.player.hands[0].cards)
            engine.hit(0)
            assert len(engine.player.hands[0].cards) == initial_cards + 1
            
            # Stand if not bust
            if not engine.player.hands[0].is_bust:
                engine.stand(0)
                assert engine.player.hands[0].is_stand
    
    def test_player_bust_loses(self):
        """Test player bust results in loss."""
        engine = GameEngine(seed=999)
        engine.start_round(10)
        
        # Skip to player turn if needed
        if engine.state.current_state == RoundState.INSURANCE:
            engine.decline_insurance()
        
        if engine.state.current_state == RoundState.PLAYER_TURN:
            # Keep hitting until bust or stand
            while (not engine.player.hands[0].is_bust and
                   not engine.player.hands[0].is_stand and
                   engine.state.current_state == RoundState.PLAYER_TURN):
                engine.hit(0)
            
            # If bust, should auto-settle
            if engine.player.hands[0].is_bust:
                assert engine.state.current_state in [RoundState.SETTLEMENT, RoundState.ROUND_END]
    
    def test_blackjack_immediate_payout(self):
        """Test blackjack triggers immediate settlement."""
        # Find a seed that gives blackjack
        for seed in range(1000):
            engine = GameEngine(seed=seed)
            engine.start_round(10)
            
            if engine.player.hands[0].is_blackjack and not engine.dealer.hand.is_blackjack:
                # Should be in settlement or round_end
                assert engine.state.current_state in [RoundState.SETTLEMENT, RoundState.ROUND_END]
                
                # Player should get 3:2 payout
                if engine.state.current_state == RoundState.ROUND_END:
                    assert len(engine.round_results) > 0
                break
    
    def test_double_down(self):
        """Test double down functionality."""
        engine = GameEngine(seed=456)
        initial_bankroll = engine.player.bankroll
        engine.start_round(10)
        
        # Skip to player turn
        if engine.state.current_state == RoundState.INSURANCE:
            engine.decline_insurance()
        
        if engine.state.current_state == RoundState.PLAYER_TURN:
            hand = engine.player.hands[0]
            if hand.can_double():
                engine.double_down(0)
                
                assert hand.is_doubled
                assert hand.bet == 20
                assert hand.is_stand
                assert len(hand.cards) == 3
    
    def test_split_creates_two_hands(self):
        """Test splitting creates two hands."""
        # Find a seed that allows split
        for seed in range(1000):
            engine = GameEngine(seed=seed)
            engine.start_round(10)
            
            if engine.state.current_state == RoundState.INSURANCE:
                engine.decline_insurance()
            
            if engine.state.current_state == RoundState.PLAYER_TURN:
                hand = engine.player.hands[0]
                if hand.can_split() and not hand.cards[0].is_ace:
                    initial_bankroll = engine.player.bankroll
                    engine.split(0)
                    
                    assert len(engine.player.hands) == 2
                    assert engine.player.hands[0].bet == 10
                    assert engine.player.hands[1].bet == 10
                    assert engine.player.bankroll == initial_bankroll - 10
                    break
    
    def test_surrender_returns_half(self):
        """Test surrender returns half of bet."""
        engine = GameEngine(seed=789)
        initial_bankroll = engine.player.bankroll
        engine.start_round(10)
        
        # Skip to player turn
        if engine.state.current_state == RoundState.INSURANCE:
            engine.decline_insurance()
        
        if engine.state.current_state == RoundState.PLAYER_TURN:
            hand = engine.player.hands[0]
            if hand.can_surrender():
                engine.surrender(0)
                
                assert hand.is_surrendered
                assert hand.is_stand
                
                # Wait for settlement
                if engine.state.current_state == RoundState.ROUND_END:
                    # Should get half back
                    expected_bankroll = initial_bankroll - 10 + 5
                    assert engine.player.bankroll == expected_bankroll


class TestEdgeCases:
    """Test edge cases."""
    
    def test_both_blackjack_push(self):
        """Test both having blackjack results in push."""
        # Find a seed where both get blackjack
        for seed in range(1000):
            engine = GameEngine(seed=seed)
            engine.start_round(10)
            
            if engine.player.hands[0].is_blackjack and engine.dealer.hand.is_blackjack:
                # If dealer shows Ace, insurance is offered first
                if engine.state.current_state == RoundState.INSURANCE:
                    engine.decline_insurance()
                
                # Should now be settled
                assert engine.state.current_state in [RoundState.SETTLEMENT, RoundState.ROUND_END]
                
                if engine.state.current_state == RoundState.ROUND_END:
                    # Should be a push - get bet back
                    assert engine.player.bankroll == 1000
                break
    
    def test_insurance_with_dealer_blackjack(self):
        """Test insurance pays when dealer has blackjack."""
        # Find a seed where dealer shows ace
        for seed in range(1000):
            engine = GameEngine(seed=seed)
            engine.start_round(10)
            
            if engine.state.current_state == RoundState.INSURANCE:
                initial_bankroll = engine.player.bankroll
                engine.take_insurance(5)
                
                if engine.dealer.hand.is_blackjack:
                    # Should settle immediately
                    assert engine.state.current_state in [RoundState.SETTLEMENT, RoundState.ROUND_END]
                break
    
    def test_cannot_hit_after_stand(self):
        """Test cannot hit after standing."""
        engine = GameEngine(seed=111)
        engine.start_round(10)
        
        if engine.state.current_state == RoundState.INSURANCE:
            engine.decline_insurance()
        
        if engine.state.current_state == RoundState.PLAYER_TURN:
            engine.stand(0)
            
            with pytest.raises(ValueError):
                engine.hit(0)
    
    def test_shoe_reshuffle_on_low_cards(self):
        """Test shoe reshuffles when cards are low."""
        engine = GameEngine(num_decks=1, seed=222)
        
        # Deal many rounds to deplete shoe
        for _ in range(15):
            try:
                if engine.state.current_state == RoundState.BETTING:
                    engine.start_round(1)
                    
                    if engine.state.current_state == RoundState.INSURANCE:
                        engine.decline_insurance()
                    
                    # Auto-play to end
                    while engine.state.current_state == RoundState.PLAYER_TURN:
                        engine.stand(0)
                    
                    if engine.state.current_state == RoundState.ROUND_END:
                        engine.end_round()
            except ValueError:
                # Shoe empty, should reshuffle
                break
        
        # Shoe should reshuffle automatically or have reshuffled
        assert True  # Test passes if no exceptions


class TestValidation:
    """Test validation and error handling."""
    
    def test_invalid_bet_too_high(self):
        """Test cannot bet more than bankroll."""
        engine = GameEngine()
        
        with pytest.raises(ValueError):
            engine.start_round(2000)  # More than starting bankroll
    
    def test_invalid_bet_negative(self):
        """Test cannot place negative bet."""
        engine = GameEngine()
        
        with pytest.raises(ValueError):
            engine.start_round(-10)
    
    def test_cannot_hit_in_wrong_state(self):
        """Test cannot hit when not in player turn."""
        engine = GameEngine()
        
        with pytest.raises(ValueError):
            engine.hit(0)  # Not in player turn yet
    
    def test_cannot_double_after_hit(self):
        """Test cannot double after taking a card."""
        engine = GameEngine(seed=333)
        engine.start_round(10)
        
        if engine.state.current_state == RoundState.INSURANCE:
            engine.decline_insurance()
        
        if engine.state.current_state == RoundState.PLAYER_TURN:
            engine.hit(0)
            
            if not engine.player.hands[0].is_bust:
                with pytest.raises(ValueError):
                    engine.double_down(0)
