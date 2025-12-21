#!/usr/bin/env python3
"""
Competitive Investment Simulation Game
A turn-based stock market simulation for 4 players
"""

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class NewsSentiment(Enum):
    """Sentiment types for news"""
    POSITIVE = "positive"
    NEGATIVE = "negative"


@dataclass
class PendingNewsImpact:
    """Tracks a news story that will affect stock price in the future"""
    company_name: str
    sentiment: NewsSentiment
    impact_magnitude: float  # Percentage change
    weeks_until_impact: int
    is_real: bool  # True if real news, False if hoax
    news_text: str


class MarketNews:
    """Handles market news generation and impacts"""

    # Diverse positive news templates
    POSITIVE_NEWS_TEMPLATES = [
        "{company} reports record-breaking quarterly earnings, surpassing analyst expectations by 15%",
        "{company} announces groundbreaking innovation in {industry} technology that could revolutionize the market",
        "{company} secures massive $2B government contract for next decade",
        "{company} CEO unveils ambitious expansion plan into emerging markets",
        "{company} stock upgraded to 'Strong Buy' by leading Wall Street analysts",
        "{company} reports 40% surge in customer demand for flagship products",
        "{company} announces strategic partnership with Fortune 500 tech giant",
        "{company} successfully completes merger that analysts call 'transformative'",
        "{company} unveils revolutionary product that receives rave reviews from industry experts",
        "{company} reports breakthrough in cost reduction, boosting profit margins significantly",
        "Institutional investors are aggressively accumulating {company} shares",
        "{company} announces share buyback program worth $500M, signaling strong confidence",
        "{company} wins prestigious industry award for innovation and excellence",
        "{company} reports significant reduction in operational costs through AI implementation",
        "{company} secures exclusive rights to game-changing patent in {industry} sector",
        "Market insiders predict {company} will dominate {industry} market within 2 years",
        "{company} announces dividend increase of 25%, rewarding loyal shareholders",
        "{company} opens state-of-the-art facility expected to triple production capacity",
        "Celebrity investor portfolio reveals major stake in {company}",
        "{company} clinical trial results exceed expectations, FDA approval likely"
    ]

    # Diverse negative news templates
    NEGATIVE_NEWS_TEMPLATES = [
        "{company} faces federal investigation over alleged accounting irregularities",
        "{company} CEO abruptly resigns amid internal controversy and board disputes",
        "{company} issues profit warning, citing weak demand in key markets",
        "{company} product recall affects millions of units due to safety concerns",
        "{company} loses major lawsuit, facing potential damages exceeding $800M",
        "Cyber attack on {company} exposes customer data, reputation at risk",
        "{company} factory shutdown due to regulatory violations halts production indefinitely",
        "{company} downgraded to 'Sell' by major investment firms citing declining fundamentals",
        "Whistleblower allegations emerge regarding {company}'s unethical business practices",
        "{company} reports disappointing earnings, missing forecasts by significant margin",
        "Key executives at {company} reportedly selling large portions of their stock holdings",
        "{company} faces class-action lawsuit from shareholders over misleading statements",
        "Supply chain disruptions severely impact {company}'s ability to meet demand",
        "{company} loses exclusive contract to aggressive competitor",
        "Environmental scandal rocks {company}, potentially facing billions in fines",
        "{company} market share erodes as innovative startup disrupts {industry} sector",
        "Labor strikes at {company} facilities threaten to cripple operations",
        "{company} clinical trials show concerning side effects, FDA raises red flags",
        "Major client cancels long-term contract with {company}, citing performance issues",
        "{company} debt levels raise concerns among credit rating agencies"
    ]

    def __init__(self):
        self.pending_impacts: List[PendingNewsImpact] = []
        self.news_history: List[Tuple[int, str]] = []  # (week_number, news_text)

    def generate_news(self, companies: Dict[str, 'Company'], week_number: int) -> Optional[str]:
        """Generate market news for a random company"""
        # Select random company
        company_name = random.choice(list(companies.keys()))
        company = companies[company_name]

        # Randomly choose positive or negative sentiment
        sentiment = random.choice([NewsSentiment.POSITIVE, NewsSentiment.NEGATIVE])

        # Select random news template
        if sentiment == NewsSentiment.POSITIVE:
            template = random.choice(self.POSITIVE_NEWS_TEMPLATES)
        else:
            template = random.choice(self.NEGATIVE_NEWS_TEMPLATES)

        # Format news with company info
        news_text = template.format(company=company_name, industry=company.industry)

        # Determine if news is real or hoax (70% real, 30% hoax)
        is_real = random.random() < 0.7

        # Determine impact magnitude (5% to 15% change)
        base_impact = random.uniform(5.0, 15.0)
        impact_magnitude = base_impact if sentiment == NewsSentiment.POSITIVE else -base_impact

        # Determine when impact will occur (1-4 weeks from now)
        weeks_until_impact = random.randint(1, 4)

        # Create pending impact
        pending_impact = PendingNewsImpact(
            company_name=company_name,
            sentiment=sentiment,
            impact_magnitude=impact_magnitude,
            weeks_until_impact=weeks_until_impact,
            is_real=is_real,
            news_text=news_text
        )

        self.pending_impacts.append(pending_impact)
        self.news_history.append((week_number, news_text))

        return news_text

    def update_pending_impacts(self, companies: Dict[str, 'Company']) -> List[str]:
        """Update countdown for pending impacts and apply them when due"""
        impact_messages = []
        impacts_to_remove = []

        for impact in self.pending_impacts:
            impact.weeks_until_impact -= 1

            if impact.weeks_until_impact <= 0:
                # Time to apply the impact
                company = companies[impact.company_name]

                if impact.is_real:
                    # Apply the actual impact
                    company.price *= (1 + impact.impact_magnitude / 100)
                    company.price = max(0.01, company.price)

                    if impact.sentiment == NewsSentiment.POSITIVE:
                        impact_messages.append(
                            f"📈 MARKET IMPACT: {impact.company_name} surges {abs(impact.impact_magnitude):.1f}% "
                            f"following recent positive news!"
                        )
                    else:
                        impact_messages.append(
                            f"📉 MARKET IMPACT: {impact.company_name} drops {abs(impact.impact_magnitude):.1f}% "
                            f"following recent negative news!"
                        )
                else:
                    # Hoax - news was fake, minimal or opposite effect
                    # Apply small opposite effect (1-3%)
                    opposite_impact = random.uniform(1.0, 3.0)
                    if impact.sentiment == NewsSentiment.POSITIVE:
                        company.price *= (1 - opposite_impact / 100)
                    else:
                        company.price *= (1 + opposite_impact / 100)
                    company.price = max(0.01, company.price)

                    impact_messages.append(
                        f"⚠️  NEWS UPDATE: Earlier reports about {impact.company_name} were exaggerated. "
                        f"Stock adjusts slightly."
                    )

                impacts_to_remove.append(impact)

        # Remove applied impacts
        for impact in impacts_to_remove:
            self.pending_impacts.remove(impact)

        return impact_messages


class Company:
    """Represents a publicly traded company"""

    def __init__(self, name: str, industry: str, initial_price: float, volatility: float):
        self.name = name
        self.industry = industry
        self.price = initial_price
        self.base_volatility = volatility
        self.price_history = [initial_price]

    def update_price(self):
        """Update stock price based on volatility (random walk)"""
        # Random price change based on volatility
        change_percent = random.uniform(-self.base_volatility, self.base_volatility)
        self.price *= (1 + change_percent / 100)
        self.price = max(0.01, self.price)  # Prevent negative prices
        self.price_history.append(self.price)

    def __str__(self):
        return f"{self.name} ({self.industry}) - ${self.price:.2f}"


class Treasury:
    """Represents treasury bonds"""

    def __init__(self):
        self.name = "US Treasury Bonds"
        self.interest_rate = 3.5  # 3.5% annual return
        self.price = 100.0  # $100 per bond

    def __str__(self):
        return f"{self.name} - ${self.price:.2f} (Annual Return: {self.interest_rate}%)"


class Player:
    """Represents a player in the game"""

    def __init__(self, name: str, starting_cash: float = 10000.0):
        self.name = name
        self.cash = starting_cash
        self.portfolio: Dict[str, int] = {}  # company_name -> number of shares
        self.treasury_bonds = 0

    def buy_stock(self, company: Company, shares: int) -> bool:
        """Buy shares of a company"""
        total_cost = company.price * shares
        if total_cost > self.cash:
            return False

        self.cash -= total_cost
        if company.name in self.portfolio:
            self.portfolio[company.name] += shares
        else:
            self.portfolio[company.name] = shares
        return True

    def sell_stock(self, company: Company, shares: int) -> bool:
        """Sell shares of a company"""
        if company.name not in self.portfolio or self.portfolio[company.name] < shares:
            return False

        self.cash += company.price * shares
        self.portfolio[company.name] -= shares
        if self.portfolio[company.name] == 0:
            del self.portfolio[company.name]
        return True

    def buy_treasury(self, treasury: Treasury, bonds: int) -> bool:
        """Buy treasury bonds"""
        total_cost = treasury.price * bonds
        if total_cost > self.cash:
            return False

        self.cash -= total_cost
        self.treasury_bonds += bonds
        return True

    def calculate_net_worth(self, companies: Dict[str, Company], treasury: Treasury) -> float:
        """Calculate total net worth (cash + stocks + bonds)"""
        net_worth = self.cash

        # Add stock value
        for company_name, shares in self.portfolio.items():
            if company_name in companies:
                net_worth += companies[company_name].price * shares

        # Add treasury value
        net_worth += self.treasury_bonds * treasury.price

        return net_worth

    def display_portfolio(self, companies: Dict[str, Company], treasury: Treasury):
        """Display player's portfolio"""
        print(f"\n{'='*60}")
        print(f"{self.name}'s Portfolio")
        print(f"{'='*60}")
        print(f"Cash: ${self.cash:.2f}")
        print()

        if self.portfolio:
            print("Stocks:")
            for company_name, shares in self.portfolio.items():
                if company_name in companies:
                    company = companies[company_name]
                    value = company.price * shares
                    print(f"  {company_name}: {shares} shares @ ${company.price:.2f} = ${value:.2f}")
        else:
            print("Stocks: None")

        print()
        if self.treasury_bonds > 0:
            bond_value = self.treasury_bonds * treasury.price
            print(f"Treasury Bonds: {self.treasury_bonds} bonds @ ${treasury.price:.2f} = ${bond_value:.2f}")
        else:
            print("Treasury Bonds: None")

        print()
        net_worth = self.calculate_net_worth(companies, treasury)
        print(f"Total Net Worth: ${net_worth:.2f}")
        print(f"{'='*60}")


class InvestmentGame:
    """Main game class"""

    def __init__(self):
        self.companies: Dict[str, Company] = {}
        self.treasury = Treasury()
        self.players: List[Player] = []
        self.current_turn = 0
        self.round_number = 1
        self.week_number = 1  # Track weeks (each player turn = 1 week)
        self.market_news = MarketNews()  # Market news system
        self.pending_news_display: Optional[str] = None  # News to display this week

        self._initialize_companies()
        self._initialize_players()

    def _initialize_companies(self):
        """Initialize the 5 companies with different industries"""
        company_data = [
            ("TechCorp", "Technology", 150.0, 8.0),
            ("ElectroMax", "Electronics", 85.0, 6.5),
            ("PharmaCare", "Pharmaceuticals", 220.0, 5.0),
            ("AutoDrive", "Automotive", 95.0, 7.0),
            ("EnergyPlus", "Energy", 110.0, 9.0),
        ]

        for name, industry, price, volatility in company_data:
            company = Company(name, industry, price, volatility)
            self.companies[name] = company

    def _initialize_players(self):
        """Initialize 4 players"""
        print("\n" + "="*60)
        print("Welcome to Investment Simulation!")
        print("="*60)
        print("\nEnter names for 4 players:")

        for i in range(4):
            while True:
                name = input(f"Player {i+1} name: ").strip()
                if name:
                    self.players.append(Player(name))
                    break
                else:
                    print("Name cannot be empty!")

    def display_market(self):
        """Display current market prices"""
        print("\n" + "="*60)
        print(f"MARKET PRICES - Week {self.week_number}")
        print("="*60)
        for company in self.companies.values():
            print(f"  {company}")
        print()
        print(f"  {self.treasury}")
        print("="*60)

        # Display market news if available
        if self.pending_news_display:
            print("\n" + "📰 " + "="*58)
            print("MARKET NEWS")
            print("="*60)
            print(f"  {self.pending_news_display}")
            print("="*60)

    def update_market(self):
        """Update all stock prices"""
        # Apply any pending news impacts
        impact_messages = self.market_news.update_pending_impacts(self.companies)

        if impact_messages:
            print("\n" + "⚡" + "="*58)
            print("BREAKING NEWS - MARKET MOVEMENTS")
            print("="*60)
            for message in impact_messages:
                print(f"  {message}")
            print("="*60)
            input("\nPress Enter to continue...")

        # Regular price updates for all companies
        for company in self.companies.values():
            company.update_price()

    def player_turn(self, player: Player):
        """Execute a single player's turn"""
        print(f"\n\n{'#'*60}")
        print(f"Round {self.round_number} - Week {self.week_number} - {player.name}'s Turn")
        print(f"{'#'*60}")

        # Generate news every 4 weeks (monthly)
        if self.week_number % 4 == 0:
            self.pending_news_display = self.market_news.generate_news(self.companies, self.week_number)
        else:
            self.pending_news_display = None

        while True:
            print("\n" + "-"*60)
            print("What would you like to do?")
            print("-"*60)
            print("1. View Market Prices")
            print("2. View My Portfolio")
            print("3. Buy Stocks")
            print("4. Sell Stocks")
            print("5. Buy Treasury Bonds")
            print("6. End Turn")
            print("-"*60)

            choice = input("Enter choice (1-6): ").strip()

            if choice == "1":
                self.display_market()

            elif choice == "2":
                player.display_portfolio(self.companies, self.treasury)

            elif choice == "3":
                self._buy_stocks_menu(player)

            elif choice == "4":
                self._sell_stocks_menu(player)

            elif choice == "5":
                self._buy_treasury_menu(player)

            elif choice == "6":
                print(f"\n{player.name} has ended their turn.")
                break

            else:
                print("Invalid choice! Please enter a number between 1 and 6.")

    def _buy_stocks_menu(self, player: Player):
        """Menu for buying stocks"""
        print("\n" + "="*60)
        print("BUY STOCKS")
        print("="*60)
        print(f"Available Cash: ${player.cash:.2f}")
        print()

        companies_list = list(self.companies.values())
        for i, company in enumerate(companies_list, 1):
            print(f"{i}. {company}")
        print("0. Cancel")

        try:
            choice = int(input("\nSelect company (0 to cancel): "))
            if choice == 0:
                return

            if 1 <= choice <= len(companies_list):
                company = companies_list[choice - 1]
                shares = int(input(f"How many shares of {company.name}? "))

                if shares <= 0:
                    print("Invalid number of shares!")
                    return

                total_cost = company.price * shares
                print(f"\nTotal cost: ${total_cost:.2f}")

                if player.buy_stock(company, shares):
                    print(f"Successfully purchased {shares} shares of {company.name}!")
                else:
                    print("Insufficient funds!")
            else:
                print("Invalid choice!")

        except ValueError:
            print("Invalid input!")

    def _sell_stocks_menu(self, player: Player):
        """Menu for selling stocks"""
        print("\n" + "="*60)
        print("SELL STOCKS")
        print("="*60)

        if not player.portfolio:
            print("You don't own any stocks!")
            return

        portfolio_items = list(player.portfolio.items())
        for i, (company_name, shares) in enumerate(portfolio_items, 1):
            company = self.companies[company_name]
            print(f"{i}. {company_name}: {shares} shares @ ${company.price:.2f}")
        print("0. Cancel")

        try:
            choice = int(input("\nSelect stock to sell (0 to cancel): "))
            if choice == 0:
                return

            if 1 <= choice <= len(portfolio_items):
                company_name, owned_shares = portfolio_items[choice - 1]
                company = self.companies[company_name]

                shares = int(input(f"How many shares to sell (you own {owned_shares})? "))

                if shares <= 0:
                    print("Invalid number of shares!")
                    return

                total_value = company.price * shares
                print(f"\nTotal value: ${total_value:.2f}")

                if player.sell_stock(company, shares):
                    print(f"Successfully sold {shares} shares of {company.name}!")
                else:
                    print("You don't own that many shares!")
            else:
                print("Invalid choice!")

        except ValueError:
            print("Invalid input!")

    def _buy_treasury_menu(self, player: Player):
        """Menu for buying treasury bonds"""
        print("\n" + "="*60)
        print("BUY TREASURY BONDS")
        print("="*60)
        print(f"Available Cash: ${player.cash:.2f}")
        print(f"{self.treasury}")
        print()

        try:
            bonds = int(input("How many bonds to purchase? "))

            if bonds <= 0:
                print("Invalid number of bonds!")
                return

            total_cost = self.treasury.price * bonds
            print(f"\nTotal cost: ${total_cost:.2f}")

            if player.buy_treasury(self.treasury, bonds):
                print(f"Successfully purchased {bonds} treasury bonds!")
            else:
                print("Insufficient funds!")

        except ValueError:
            print("Invalid input!")

    def display_leaderboard(self):
        """Display current standings"""
        print("\n" + "="*60)
        print("LEADERBOARD")
        print("="*60)

        # Calculate net worth for all players
        standings = []
        for player in self.players:
            net_worth = player.calculate_net_worth(self.companies, self.treasury)
            standings.append((player.name, net_worth))

        # Sort by net worth descending
        standings.sort(key=lambda x: x[1], reverse=True)

        for rank, (name, net_worth) in enumerate(standings, 1):
            print(f"{rank}. {name}: ${net_worth:.2f}")

        print("="*60)

    def play(self):
        """Main game loop"""
        print("\n" + "="*60)
        print("Game Start! Each player begins with $10,000")
        print("="*60)

        # Show initial market
        self.display_market()

        input("\nPress Enter to begin the game...")

        # Game loop
        while True:
            # Each player takes their turn
            for player in self.players:
                self.player_turn(player)
                self.week_number += 1  # Increment week after each player's turn

            # End of round
            print("\n" + "="*60)
            print(f"End of Round {self.round_number}")
            print("="*60)

            # Update market prices
            print("\nUpdating market prices...")
            self.update_market()

            # Show leaderboard
            self.display_leaderboard()

            # Continue to next round
            continue_game = input("\nContinue to next round? (y/n): ").strip().lower()
            if continue_game != 'y':
                break

            self.round_number += 1

        # Final standings
        print("\n" + "="*60)
        print("GAME OVER - Final Standings")
        print("="*60)
        self.display_leaderboard()
        print("\nThanks for playing!")


def main():
    """Main entry point"""
    game = InvestmentGame()
    game.play()


if __name__ == "__main__":
    main()
