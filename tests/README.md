# Tests

This folder contains all test files for the investment simulation game.

## Running Tests

To run a specific test from the repository root:
```bash
python3 tests/test_breaking_news.py
```

Or from within the tests directory:
```bash
cd tests
python3 test_breaking_news.py
```

## Test Categories

- **News System Tests**: test_breaking_news.py, test_new_news.py, test_news_*.py
- **Trading Tests**: test_npc_trading.py, test_short_selling.py, test_autosell_availability.py
- **Market Impact Tests**: test_market_impact.py, test_multiple_impacts.py, test_two_stage_impact.py
- **Investment Tests**: test_dollar_investment.py, test_themed_investments.py
- **Save/Load Tests**: test_save_load_themed.py, test_news_save_load.py
- **Feature Tests**: Various other feature-specific tests
