"""Game state management for blackjack."""

from enum import Enum


class RoundState(Enum):
    """States in a blackjack round."""
    BETTING = "betting"
    INITIAL_DEAL = "initial_deal"
    INSURANCE = "insurance"
    PLAYER_TURN = "player_turn"
    DEALER_TURN = "dealer_turn"
    SETTLEMENT = "settlement"
    ROUND_END = "round_end"


class GameState:
    """Manages the state machine for a blackjack game."""
    
    def __init__(self):
        self.current_state = RoundState.BETTING
        self.current_hand_index = 0
    
    def transition_to(self, new_state: RoundState):
        """
        Transition to a new state.
        
        Args:
            new_state: The state to transition to
        """
        self.current_state = new_state
    
    def can_transition_to(self, new_state: RoundState) -> bool:
        """
        Check if transition to new state is valid.
        
        Args:
            new_state: The state to check
            
        Returns:
            True if transition is valid
        """
        valid_transitions = {
            RoundState.BETTING: [RoundState.INITIAL_DEAL],
            RoundState.INITIAL_DEAL: [RoundState.INSURANCE, RoundState.PLAYER_TURN, RoundState.SETTLEMENT],
            RoundState.INSURANCE: [RoundState.PLAYER_TURN, RoundState.SETTLEMENT],
            RoundState.PLAYER_TURN: [RoundState.DEALER_TURN, RoundState.SETTLEMENT],
            RoundState.DEALER_TURN: [RoundState.SETTLEMENT],
            RoundState.SETTLEMENT: [RoundState.ROUND_END],
            RoundState.ROUND_END: [RoundState.BETTING],
        }
        
        return new_state in valid_transitions.get(self.current_state, [])
    
    def reset(self):
        """Reset to initial state."""
        self.current_state = RoundState.BETTING
        self.current_hand_index = 0
