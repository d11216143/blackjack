#!/usr/bin/env python3
"""Example game scenarios demonstrating various features."""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.engine.game_engine import GameEngine
from core.engine.game_state import RoundState


def demo_split():
    """Demonstrate split functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Split Pairs")
    print("=" * 60)
    
    engine = GameEngine(seed=19)
    engine.start_round(100)
    
    print(f"Player hand: {engine.player.hands[0]}")
    print(f"Dealer upcard: {engine.dealer.upcard}")
    print(f"Player can split: {engine.player.hands[0].can_split()}")
    
    if engine.player.hands[0].can_split():
        print("\nSplitting the pair...")
        engine.split(0)
        
        print(f"Now player has {len(engine.player.hands)} hands:")
        for i, hand in enumerate(engine.player.hands):
            print(f"  Hand {i+1}: {hand}")
        
        # Auto-play both hands
        for i in range(len(engine.player.hands)):
            if not engine.player.hands[i].is_stand:
                engine.stand(i)
        
        print(f"\nDealer hand: {engine.dealer.hand}")
        print(f"Final bankroll: ${engine.player.bankroll:.2f}")


def demo_blackjack():
    """Find and demonstrate a blackjack."""
    print("\n" + "=" * 60)
    print("DEMO: Player Blackjack")
    print("=" * 60)
    
    for seed in range(200):
        engine = GameEngine(seed=seed)
        engine.start_round(100)
        
        if engine.state.current_state == RoundState.INSURANCE:
            engine.decline_insurance()
        
        if engine.player.hands[0].is_blackjack and not engine.dealer.hand.is_blackjack:
            print(f"Found blackjack with seed {seed}!")
            print(f"Player hand: {engine.player.hands[0]}")
            print(f"Dealer upcard: {engine.dealer.upcard}")
            print(f"Dealer hand: {engine.dealer.hand}")
            
            if engine.round_results:
                result, payout_result, payout = engine.round_results[0]
                print(f"Result: {engine.payout_policy.get_result_description(payout_result)}")
                print(f"Payout: ${payout:.2f} (profit: ${payout - 100:.2f})")
            print(f"Final bankroll: ${engine.player.bankroll:.2f}")
            break


def demo_insurance():
    """Demonstrate insurance scenario."""
    print("\n" + "=" * 60)
    print("DEMO: Insurance Offer")
    print("=" * 60)
    
    for seed in range(100):
        engine = GameEngine(seed=seed)
        engine.start_round(100)
        
        if engine.state.current_state == RoundState.INSURANCE:
            print(f"Found insurance scenario with seed {seed}!")
            print(f"Player hand: {engine.player.hands[0]}")
            print(f"Dealer upcard: {engine.dealer.upcard} (Ace)")
            
            # Take insurance
            print("\nTaking insurance for $50...")
            engine.take_insurance(50)
            
            print(f"Dealer hand: {engine.dealer.hand}")
            print(f"Dealer has blackjack: {engine.dealer.hand.is_blackjack}")
            
            if engine.round_results:
                result, payout_result, payout = engine.round_results[0]
                print(f"Result: {engine.payout_policy.get_result_description(payout_result)}")
                print(f"Payout: ${payout:.2f}")
            print(f"Final bankroll: ${engine.player.bankroll:.2f}")
            break


def demo_hand_values():
    """Demonstrate various hand value calculations."""
    print("\n" + "=" * 60)
    print("DEMO: Hand Value Calculations")
    print("=" * 60)
    
    from core.models.hand import Hand
    from core.models.card import Card, Suit, Rank
    
    examples = [
        ("Simple hand", [Rank.FIVE, Rank.TEN]),
        ("Soft 17", [Rank.ACE, Rank.SIX]),
        ("Hard 17", [Rank.TEN, Rank.SEVEN]),
        ("Blackjack", [Rank.ACE, Rank.KING]),
        ("Multiple Aces (A+A+9)", [Rank.ACE, Rank.ACE, Rank.NINE]),
        ("Three Aces (A+A+A)", [Rank.ACE, Rank.ACE, Rank.ACE]),
        ("Bust (10+K+5)", [Rank.TEN, Rank.KING, Rank.FIVE]),
    ]
    
    for description, ranks in examples:
        hand = Hand()
        for i, rank in enumerate(ranks):
            hand.add_card(Card(Suit.HEARTS if i % 2 == 0 else Suit.DIAMONDS, rank))
        
        value, is_soft = hand.get_value()
        print(f"\n{description}:")
        print(f"  Cards: {hand}")
        print(f"  Value: {value} ({'soft' if is_soft else 'hard'})")
        if hand.is_blackjack:
            print("  *** BLACKJACK! ***")
        elif hand.is_bust:
            print("  *** BUST! ***")


def demo_all_actions():
    """Show all available player actions."""
    print("\n" + "=" * 60)
    print("DEMO: All Player Actions")
    print("=" * 60)
    
    actions = {
        "Hit": "Take another card from the shoe",
        "Stand": "Keep current hand and end turn",
        "Double Down": "Double bet, take one card, and stand (2 cards only)",
        "Split": "Split matching pairs into two hands (2 cards only)",
        "Surrender": "Give up and get half bet back (2 cards only)",
        "Insurance": "Side bet when dealer shows Ace, pays 2:1"
    }
    
    for action, description in actions.items():
        print(f"\n{action}:")
        print(f"  {description}")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("BLACKJACK GAME EXAMPLES AND DEMONSTRATIONS")
    print("=" * 60)
    
    demo_hand_values()
    demo_all_actions()
    demo_blackjack()
    demo_split()
    demo_insurance()
    
    print("\n" + "=" * 60)
    print("To play the game interactively, run: python main.py")
    print("To run with a specific seed, run: python main.py <seed>")
    print("To run tests, run: pytest tests/ -v")
    print("=" * 60)


if __name__ == "__main__":
    main()
