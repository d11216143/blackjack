# Blackjack (21點) Game

A complete implementation of the classic Blackjack card game with comprehensive system analysis and design.

## Features

- **Complete Blackjack Rules**
  - Natural Blackjack pays 3:2
  - Dealer stands on soft 17 (configurable to H17)
  - Player actions: Hit, Stand, Double Down, Split, Surrender
  - Insurance available when dealer shows Ace
  - Proper hand value calculation with Ace as 1 or 11

- **Game Features**
  - Multiple deck shoe (default 6 decks)
  - Automatic reshuffling when shoe is low
  - Bankroll management
  - Reproducible games with seed support (for testing)

- **Edge Cases Handled**
  - Both player and dealer have Blackjack (Push)
  - Split Aces (receive one card and stand)
  - Player bust
  - Dealer bust
  - Multiple hands from splitting

## Project Structure

```
blackjack/
├── core/                   # Core game logic
│   ├── models/            # Data models
│   │   ├── card.py       # Card, Suit, Rank classes
│   │   ├── deck.py       # Deck and Shoe classes
│   │   ├── hand.py       # Hand class with value calculation
│   │   └── player.py     # Player and Dealer classes
│   ├── rules/            # Game rules
│   │   └── payout.py     # Payout policy and result comparison
│   └── engine/           # Game engine
│       ├── game_state.py # State machine (RoundState)
│       └── game_engine.py # Main game controller
├── ui/                    # User interfaces
│   └── cli.py            # Command-line interface
├── tests/                 # Test suite
│   ├── test_hand.py      # Hand value calculation tests
│   ├── test_payout.py    # Payout policy tests
│   └── test_game_engine.py # Integration tests
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/d11216143/blackjack.git
cd blackjack
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Running the Game

**Basic usage:**
```bash
python main.py
```

**With reproducible seed (for testing):**
```bash
python main.py 42
```

### How to Play

1. **Betting:** Enter your bet amount at the start of each round
2. **Insurance:** If dealer shows an Ace, you can take insurance (up to half your bet)
3. **Player Actions:**
   - `h` - Hit: Take another card
   - `s` - Stand: Keep current hand
   - `d` - Double: Double your bet and take one final card
   - `p` - Split: Split a pair into two hands
   - `u` - Surrender: Give up half your bet and end the hand

4. **Winning:**
   - Blackjack (Ace + 10-value card) pays 3:2
   - Regular win pays 1:1
   - Insurance pays 2:1
   - Surrender returns half your bet
   - Push (tie) returns your bet

## Game Rules

### Card Values
- Number cards (2-10): Face value
- Face cards (J, Q, K): 10 points
- Ace: 1 or 11 points (whichever is better)

### Hand Values
- **Soft hand:** Contains an Ace counted as 11 (e.g., A-6 = soft 17)
- **Hard hand:** No Ace or Ace counted as 1 (e.g., 10-7 = hard 17)
- **Blackjack:** Ace + 10-value card as first two cards (beats regular 21)
- **Bust:** Hand value exceeds 21 (automatic loss)

### Dealer Rules
- Must hit on 16 or less
- Must stand on 17 or more (S17 rule)
- Dealer plays after all players complete their hands

### Player Actions
- **Hit:** Available anytime (except after stand/bust)
- **Stand:** Available anytime
- **Double Down:** Only on first two cards, doubles bet and takes exactly one card
- **Split:** Only on matching rank pairs (e.g., 8-8, K-K), creates two hands
  - Split Aces receive one card each and automatically stand
  - Cannot split after taking additional cards
- **Surrender:** Only on first two cards (not available on split hands), returns half the bet
- **Insurance:** Only when dealer shows Ace, bets up to half main bet, pays 2:1 if dealer has Blackjack

### Payouts
- **Blackjack:** 3:2 (bet $10, win $15)
- **Regular Win:** 1:1 (bet $10, win $10)
- **Push:** Return bet (no profit)
- **Loss:** Lose bet
- **Surrender:** Return half bet
- **Insurance:** 2:1 when dealer has Blackjack

## Testing

Run the test suite:
```bash
pytest tests/
```

Run with verbose output:
```bash
pytest -v tests/
```

Run specific test file:
```bash
pytest tests/test_hand.py
```

### Test Coverage

- **Unit Tests:**
  - Hand value calculation (including multiple Aces)
  - Payout calculations for all scenarios
  - Action eligibility (split, double, surrender)

- **Integration Tests:**
  - Complete game flow
  - Edge cases (both Blackjack, bust, etc.)
  - State machine transitions
  - Validation and error handling

- **Reproducible Tests:**
  - All tests use seeds for consistent results
  - Enables reliable testing of random gameplay

## System Design

### State Machine
The game follows a state machine pattern:
```
BETTING → INITIAL_DEAL → [INSURANCE] → PLAYER_TURN → DEALER_TURN → SETTLEMENT → ROUND_END → BETTING
```

**State Descriptions:**
- `BETTING`: Player places bet
- `INITIAL_DEAL`: Deal 2 cards to player and dealer
- `INSURANCE`: Optional insurance if dealer shows Ace
- `PLAYER_TURN`: Player makes decisions (hit, stand, etc.)
- `DEALER_TURN`: Dealer plays according to rules
- `SETTLEMENT`: Calculate results and payouts
- `ROUND_END`: Round complete, ready for next round

### Data Models

**Card:** Represents a playing card with suit and rank

**Deck/Shoe:** Manages multiple decks with shuffling
- Supports configurable number of decks
- Seedable random number generator for testing
- Automatic reshuffle when cards run low

**Hand:** Represents a blackjack hand
- Calculates optimal value (soft/hard)
- Tracks split, double, surrender status
- Validates available actions

**Player:** Manages bankroll and hands
- Supports multiple hands (for splits)
- Tracks bets and insurance

**Dealer:** Follows house rules
- Configurable H17/S17 rule
- Automatic play according to rules

**GameEngine:** Orchestrates game flow
- State management
- Action validation
- Payout calculation
- Error handling

### Design Principles

1. **Separation of Concerns:**
   - Models: Data structures
   - Rules: Game logic and payouts
   - Engine: Flow control
   - UI: User interaction

2. **Testability:**
   - Seedable RNG for reproducible tests
   - Clear state machine for predictable behavior
   - Isolated components for unit testing

3. **Extensibility:**
   - Easy to add new UI (web, GUI)
   - Configurable rules (H17/S17, payout ratios)
   - Modular design for adding features

4. **Validation:**
   - Comprehensive input validation
   - State-based action checking
   - Clear error messages

## System Analysis Summary

### Project Goals
- Implement a complete, playable Blackjack game
- Follow standard casino rules
- Provide clean, maintainable code architecture
- Support testing and reproducibility

### Requirements Met

**Functional Requirements:**
- ✅ FR-01: Game initialization (shoe, bankroll, betting)
- ✅ FR-02: Card dealing
- ✅ FR-03: Player actions (Hit, Stand, Double, Split, Surrender, Insurance)
- ✅ FR-04: Dealer actions (following rules)
- ✅ FR-05: Settlement and payout calculation
- ✅ FR-06: Game status display
- ✅ FR-07: Round restart capability

**Non-Functional Requirements:**
- ✅ Performance: Instant response for all actions
- ✅ Usability: Clear CLI interface with action prompts
- ✅ Maintainability: Modular architecture with clear separation
- ✅ Testability: Comprehensive test suite with seedable RNG
- ✅ Extensibility: Easy to add new features and interfaces

### Edge Cases Handled
- Both player and dealer have Blackjack (Push)
- Splitting pairs (including Aces)
- Player bust (immediate loss)
- Dealer bust (player wins)
- Push scenarios (same value)
- Surrender (half bet return)
- Insurance with dealer Blackjack
- Multiple Aces in hand
- Soft/hard hand transitions

## Future Enhancements (Roadmap)

- [ ] **Basic Strategy Advisor:** Suggest optimal plays
- [ ] **Multi-player Mode:** Support multiple players at table
- [ ] **Web UI:** Browser-based interface
- [ ] **Game History:** Save and replay hands
- [ ] **Statistics:** Track win rates, profits over time
- [ ] **Card Counting Practice:** Educational mode
- [ ] **Variations:** Add side bets, different rule sets
- [ ] **Mobile App:** Native mobile interface

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Author

Created as a demonstration of comprehensive system analysis and design for a classic card game.