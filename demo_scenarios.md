# Blackjack Game Demo Scenarios

This document demonstrates various scenarios and features of the Blackjack game.

## Scenario 1: Player Gets Blackjack
**Seed: 42**
- Player: 6♥ J♣ (16)
- Dealer: K♥ 9♦ (19)
- Player hits and busts (demonstrated in main test)

## Scenario 2: Double Down
**Seed: 456**
Run: `python main.py 456`
- Allows testing double down functionality

## Scenario 3: Split Pairs
**Seed: 789**
Run: `python main.py 789`
- Test splitting pairs

## Scenario 4: Surrender
**Seed: 111**
Run: `python main.py 111`
- Test surrender option

## Scenario 5: Insurance
**Seed: (varies)**
Run: `python main.py`
- When dealer shows Ace, insurance is offered

## Game Actions Available

### Hit (h)
- Take another card
- Available anytime during player turn
- Auto-stand if reach 21 or bust

### Stand (s)
- Keep current hand
- Ends your turn

### Double (d)
- Double your bet
- Take exactly one more card
- Only available on initial two cards
- Requires sufficient bankroll

### Split (p)
- Split matching pairs into two hands
- Each hand gets its own bet
- Split Aces receive one card each
- Only available on initial two cards

### Surrender (u)
- Give up and get half bet back
- Only available on initial two cards
- Not available on split hands

### Insurance
- Offered when dealer shows Ace
- Bet up to half your main bet
- Pays 2:1 if dealer has Blackjack

## Edge Cases Demonstrated

### Both Blackjack (Push)
When both player and dealer have Blackjack:
- If dealer shows Ace, insurance offered first
- Result: Push (tie) - bet returned

### Split Aces
When splitting Aces:
- Each hand receives one card
- Both hands automatically stand
- Cannot hit split Aces

### Multiple Aces
Hand value calculation handles multiple Aces:
- A + A = 12 (soft)
- A + A + 9 = 21 (soft)
- A + A + A = 13 (soft)
- Always counts one Ace as 11 if possible without busting

### Dealer Rules
- Must hit on 16 or less
- Must stand on 17 or more (S17 rule by default)
- Configurable to H17 (hit soft 17)

## Test Coverage

Run tests with:
```bash
pytest tests/ -v
```

45 comprehensive tests covering:
- Hand value calculation with various Ace combinations
- Action eligibility checks
- Payout calculations for all outcomes
- Complete game flow scenarios
- Edge case handling
- Input validation
- State machine transitions
