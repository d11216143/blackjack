#!/usr/bin/env python3
"""Main entry point for Blackjack game."""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.cli import main

if __name__ == "__main__":
    main()
