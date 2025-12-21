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
class NewsReport:
    """Represents news from all three sources"""
    trustworthy_source: str  # Empty if news is fake
    sensationalist_source: str  # Always exaggerated
    insider_source: str  # May flip to opposite
    insider_flipped: bool  # Whether insider source flipped


@dataclass
class PendingNewsImpact:
    """Tracks a news story that will affect stock price in the future"""
    company_name: str
    sentiment: NewsSentiment
    impact_magnitude: float  # Percentage change
    weeks_until_impact: int
    is_real: bool  # True if real news, False if hoax
    news_text: str
    news_report: NewsReport  # All three news sources


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

    # Sensationalist positive news templates (exaggerated clickbait)
    SENSATIONALIST_POSITIVE_TEMPLATES = [
        "🚀 {company} ABOUT TO EXPLODE - ANALYSTS PREDICT 500% GAINS! You Won't BELIEVE What Happened!",
        "💰 BREAKING: {company} Stock Set to MOON! Insiders Buying Everything They Can!",
        "🔥 {company} REVOLUTIONIZES {industry} - This Changes EVERYTHING! Stock Price to SKYROCKET!",
        "⚡ URGENT: {company} Discovery Could Make You RICH! Wall Street Going CRAZY!",
        "🎯 {company} Just Destroyed the Competition! Stock About to GO PARABOLIC!",
        "💎 DIAMOND HANDS ALERT: {company} Hidden Gem FINALLY Revealed! TO THE MOON! 🌙",
        "🚨 YOU'RE MISSING OUT: {company} Stock Predicted to 10X by Year End!",
        "⭐ {company} CEO Drops BOMBSHELL Announcement - Market Will Never Be the Same!",
        "🎰 JACKPOT: {company} Strikes GOLD in {industry} Sector! Buy NOW Before It's Too Late!",
        "🏆 {company} CRUSHES Earnings - THIS Is the Trade of the DECADE!",
        "🌟 LEGENDARY Investor Loads Up on {company} - Follow the SMART Money NOW!",
        "💸 {company} Money Printer Goes BRRRR - Unlimited Upside Potential CONFIRMED!",
        "🎉 {company} Just Won the {industry} Lottery! Stock Price Will NEVER Be This Low Again!",
        "⚠️ FOMO ALERT: Everyone's Buying {company} - Don't Get Left Behind!",
        "🔔 BREAKING: {company} Patent Will Mint MILLIONAIRES! Act FAST!",
        "🎊 {company} Announces Deal That Wall Street Calls 'HISTORIC' - Buy Signal FLASHING!",
        "💥 {company} Absolutely DEMOLISHES Competition - Monopoly Status Incoming!",
        "🌊 TSUNAMI of Money Flowing Into {company} - Ride the Wave!",
        "🎺 {company} Blows Past ALL Expectations - Bears Getting DESTROYED!",
        "⚡ FLASH: {company} Innovation Makes Competitors OBSOLETE - Stock to TRIPLE!"
    ]

    # Sensationalist negative news templates (exaggerated disaster)
    SENSATIONALIST_NEGATIVE_TEMPLATES = [
        "💀 {company} COLLAPSING - Get Out NOW Before It's TOO LATE! Total Disaster!",
        "🔥 MARKET BLOODBATH: {company} Stock in FREE FALL! Everything is on FIRE!",
        "⚠️ ALERT: {company} About to GO BANKRUPT?! Insiders Dumping EVERYTHING!",
        "💣 EXPLOSIVE: {company} Scandal Could DESTROY Entire {industry} Industry!",
        "📉 {company} DEATH SPIRAL Confirmed - This Stock is TOXIC! Sell NOW!",
        "🚨 RED ALERT: {company} Crash Imminent! Experts Say 'RUN FOR THE HILLS!'",
        "☠️ {company} DEVASTATED by News - Stock Heading to ZERO?!",
        "⛔ STOP: Do NOT Buy {company}! Absolute DISASTER Unfolding!",
        "💥 {company} IMPLODING - CEO Caught in MASSIVE Scandal! Company DOOMED!",
        "🔴 CATASTROPHIC: {company} Faces EXTINCTION! Shareholders in PANIC MODE!",
        "⚡ BREAKING: {company} Lawsuit Could Wipe Out BILLIONS! Stock PLUMMETING!",
        "🌪️ TORNADO of Bad News Hits {company} - Analysts Scream SELL SELL SELL!",
        "💀 {company} Just Committed Financial SUICIDE - This Stock is DEAD!",
        "🚑 EMERGENCY: {company} Bleeding Cash - Bankruptcy Fears EXPLODE!",
        "⚠️ {company} NIGHTMARE Scenario Unfolding - Investors FLEEING in Terror!",
        "🔥 DUMPSTER FIRE: {company} Management Incompetence EXPOSED! Avoid at ALL Costs!",
        "💣 BOMBSHELL: {company} Hiding DEVASTATING Losses! Cover-up Revealed!",
        "📉 {company} in COMPLETE MELTDOWN - Worst Investment of the Century!",
        "☠️ TOXIC ASSET ALERT: {company} Will DESTROY Your Portfolio! Get Out!",
        "🚨 {company} Regulators Close In - Company Might Not Survive the Week!"
    ]

    def __init__(self):
        self.pending_impacts: List[PendingNewsImpact] = []
        self.news_history: List[Tuple[int, str]] = []  # (week_number, news_text)

    def _generate_news_report(self, company_name: str, industry: str, sentiment: NewsSentiment, is_real: bool) -> NewsReport:
        """Generate news from all three sources"""

        # 1. TRUSTWORTHY SOURCE - Only reports if 100% confirmed (real news)
        if is_real:
            # Use normal templates for trustworthy source
            if sentiment == NewsSentiment.POSITIVE:
                trustworthy_template = random.choice(self.POSITIVE_NEWS_TEMPLATES)
            else:
                trustworthy_template = random.choice(self.NEGATIVE_NEWS_TEMPLATES)
            trustworthy_source = trustworthy_template.format(company=company_name, industry=industry)
        else:
            # Trustworthy source doesn't report fake news
            trustworthy_source = ""

        # 2. SENSATIONALIST SOURCE - Always reports with exaggerated headlines
        if sentiment == NewsSentiment.POSITIVE:
            sensationalist_template = random.choice(self.SENSATIONALIST_POSITIVE_TEMPLATES)
        else:
            sensationalist_template = random.choice(self.SENSATIONALIST_NEGATIVE_TEMPLATES)
        sensationalist_source = sensationalist_template.format(company=company_name, industry=industry)

        # 3. INSIDER SOURCE - 50% chance to flip to opposite
        insider_flipped = random.random() < 0.5

        if insider_flipped:
            # Flip to opposite sentiment
            if sentiment == NewsSentiment.POSITIVE:
                insider_template = random.choice(self.NEGATIVE_NEWS_TEMPLATES)
            else:
                insider_template = random.choice(self.POSITIVE_NEWS_TEMPLATES)
        else:
            # Report same as actual sentiment
            if sentiment == NewsSentiment.POSITIVE:
                insider_template = random.choice(self.POSITIVE_NEWS_TEMPLATES)
            else:
                insider_template = random.choice(self.NEGATIVE_NEWS_TEMPLATES)

        insider_source = insider_template.format(company=company_name, industry=industry)

        return NewsReport(
            trustworthy_source=trustworthy_source,
            sensationalist_source=sensationalist_source,
            insider_source=insider_source,
            insider_flipped=insider_flipped
        )

    def generate_news(self, companies: Dict[str, 'Company'], week_number: int) -> Optional[NewsReport]:
        """Generate market news for a random company"""
        # Select random company
        company_name = random.choice(list(companies.keys()))
        company = companies[company_name]

        # Randomly choose positive or negative sentiment
        sentiment = random.choice([NewsSentiment.POSITIVE, NewsSentiment.NEGATIVE])

        # Determine if news is real or hoax (70% real, 30% hoax)
        is_real = random.random() < 0.7

        # Generate news from all three sources
        news_report = self._generate_news_report(company_name, company.industry, sentiment, is_real)

        # Use trustworthy source text for history (or sensationalist if trustworthy is empty)
        news_text = news_report.trustworthy_source if news_report.trustworthy_source else news_report.sensationalist_source

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
            news_text=news_text,
            news_report=news_report
        )

        self.pending_impacts.append(pending_impact)
        self.news_history.append((week_number, news_text))

        return news_report

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
        # Leverage system
        self.borrowed_amount = 0.0
        self.max_leverage_ratio = 2.0  # Can borrow up to 2x equity
        self.interest_rate_weekly = 0.115  # ~6% annual = 0.115% weekly

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

    def calculate_equity(self, companies: Dict[str, Company], treasury: Treasury) -> float:
        """Calculate equity (net worth minus debt)"""
        return self.calculate_net_worth(companies, treasury) - self.borrowed_amount

    def calculate_total_assets(self, companies: Dict[str, Company], treasury: Treasury) -> float:
        """Calculate total portfolio value (not including cash, only investments)"""
        assets = 0.0

        # Add stock value
        for company_name, shares in self.portfolio.items():
            if company_name in companies:
                assets += companies[company_name].price * shares

        # Add treasury value
        assets += self.treasury_bonds * treasury.price

        return assets

    def borrow_money(self, amount: float, companies: Dict[str, Company], treasury: Treasury) -> Tuple[bool, str]:
        """Borrow money using leverage"""
        if amount <= 0:
            return False, "Invalid amount!"

        equity = self.calculate_equity(companies, treasury)

        # Check if borrowing would exceed max leverage
        new_borrowed = self.borrowed_amount + amount
        if new_borrowed > equity * self.max_leverage_ratio:
            max_can_borrow = max(0, equity * self.max_leverage_ratio - self.borrowed_amount)
            return False, f"Exceeds maximum leverage! You can borrow up to ${max_can_borrow:.2f} more."

        self.borrowed_amount += amount
        self.cash += amount
        return True, f"Successfully borrowed ${amount:.2f}!"

    def repay_loan(self, amount: float) -> Tuple[bool, str]:
        """Repay borrowed money"""
        if amount <= 0:
            return False, "Invalid amount!"

        if amount > self.cash:
            return False, "Insufficient cash!"

        if amount > self.borrowed_amount:
            amount = self.borrowed_amount

        self.borrowed_amount -= amount
        self.cash -= amount
        return True, f"Successfully repaid ${amount:.2f}! Remaining debt: ${self.borrowed_amount:.2f}"

    def apply_interest(self) -> float:
        """Apply weekly interest on borrowed amount"""
        if self.borrowed_amount > 0:
            interest = self.borrowed_amount * (self.interest_rate_weekly / 100)
            self.borrowed_amount += interest
            return interest
        return 0.0

    def check_margin_call(self, companies: Dict[str, Company], treasury: Treasury) -> bool:
        """Check if player is subject to margin call (equity < 30% of total position)"""
        if self.borrowed_amount == 0:
            return False

        equity = self.calculate_equity(companies, treasury)
        total_position = equity + self.borrowed_amount

        # Margin call if equity falls below 30% of total position
        if total_position > 0 and (equity / total_position) < 0.30:
            return True

        return False

    def display_portfolio(self, companies: Dict[str, Company], treasury: Treasury):
        """Display player's portfolio"""
        print(f"\n{'='*60}")
        print(f"{self.name}'s Portfolio")
        print(f"{'='*60}")
        print(f"Cash: ${self.cash:.2f}")

        # Show leverage info
        if self.borrowed_amount > 0:
            print(f"💳 Borrowed (Leverage): ${self.borrowed_amount:.2f}")
            equity = self.calculate_equity(companies, treasury)
            print(f"💰 Equity (Net - Debt): ${equity:.2f}")
            current_leverage = self.borrowed_amount / max(0.01, equity)
            print(f"📊 Leverage Ratio: {current_leverage:.2f}x (Max: {self.max_leverage_ratio:.2f}x)")

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


class MarketCycleType(Enum):
    """Types of market cycles"""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    RECESSION = "recession"
    INFLATION = "inflation"
    MARKET_CRASH = "market_crash"
    RECOVERY = "recovery"
    TECH_BOOM = "tech_boom"


@dataclass
class ActiveMarketCycle:
    """Represents an active market cycle"""
    cycle_type: MarketCycleType
    weeks_remaining: int
    headline: str
    description: str


class MarketCycle:
    """Handles major market cycles (economic events every 6 months)"""

    def __init__(self):
        self.active_cycle: Optional[ActiveMarketCycle] = None
        self.cycle_history: List[Tuple[int, str]] = []  # (week_number, cycle_name)

    def should_trigger_cycle(self, week_number: int) -> bool:
        """Check if we should trigger a new cycle (every 24 weeks = 6 months)"""
        # Trigger at weeks 24, 48, 72, etc.
        return week_number > 0 and week_number % 24 == 0 and self.active_cycle is None

    def trigger_cycle(self, week_number: int) -> ActiveMarketCycle:
        """Trigger a new market cycle"""
        # Randomly select a cycle type
        cycle_type = random.choice(list(MarketCycleType))
        duration = random.randint(8, 16)  # 2-4 months duration

        # Generate headline and description based on cycle type
        if cycle_type == MarketCycleType.BULL_MARKET:
            headline = "🐂 BULL MARKET SURGE - Economic Expansion Accelerates!"
            description = "Strong GDP growth, rising corporate profits, and investor optimism drive markets higher across all sectors."

        elif cycle_type == MarketCycleType.BEAR_MARKET:
            headline = "🐻 BEAR MARKET BEGINS - Economic Slowdown Hits Markets"
            description = "Weakening economic indicators, declining corporate earnings, and rising uncertainty push markets into sustained decline."

        elif cycle_type == MarketCycleType.RECESSION:
            headline = "📉 RECESSION DECLARED - Economy Contracts for Second Consecutive Quarter"
            description = "Official recession confirmed as unemployment rises, consumer spending falls, and businesses cut investment. Markets tumble."

        elif cycle_type == MarketCycleType.INFLATION:
            headline = "🔥 INFLATION CRISIS - Consumer Prices Soar to Decade Highs"
            description = "Surging inflation erodes purchasing power. Central banks signal aggressive rate hikes. Markets volatile as sectors react differently."

        elif cycle_type == MarketCycleType.MARKET_CRASH:
            headline = "💥 MARKET CRASH - Panic Selling Triggers Circuit Breakers"
            description = "Severe market crash as cascading sell-offs spread panic. All sectors plummet in worst trading day in years."

        elif cycle_type == MarketCycleType.RECOVERY:
            headline = "📈 ECONOMIC RECOVERY - Markets Rally on Strong Rebound Signals"
            description = "Economy shows strong recovery signs. Stimulus measures take effect. Consumer confidence returns. Markets surge broadly."

        else:  # TECH_BOOM
            headline = "🚀 TECHNOLOGY BOOM - Innovation Wave Transforms Markets"
            description = "Revolutionary tech breakthroughs spark investor frenzy. Technology and electronics sectors lead massive market rally."

        self.active_cycle = ActiveMarketCycle(
            cycle_type=cycle_type,
            weeks_remaining=duration,
            headline=headline,
            description=description
        )

        self.cycle_history.append((week_number, headline))
        return self.active_cycle

    def apply_cycle_effects(self, companies: Dict[str, Company]) -> List[str]:
        """Apply market cycle effects to all companies"""
        if not self.active_cycle:
            return []

        messages = []
        cycle = self.active_cycle

        # Apply effects based on cycle type
        if cycle.cycle_type == MarketCycleType.BULL_MARKET:
            # All stocks rise (3-7%)
            for company in companies.values():
                change = random.uniform(3.0, 7.0)
                company.price *= (1 + change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Bull market continues - All stocks trending upward!")

        elif cycle.cycle_type == MarketCycleType.BEAR_MARKET:
            # All stocks fall (2-5%)
            for company in companies.values():
                change = random.uniform(2.0, 5.0)
                company.price *= (1 - change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Bear market persists - Broad market decline continues")

        elif cycle.cycle_type == MarketCycleType.RECESSION:
            # All stocks fall significantly (4-8%)
            for company in companies.values():
                change = random.uniform(4.0, 8.0)
                company.price *= (1 - change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Recession impact - Severe downward pressure on all stocks")

        elif cycle.cycle_type == MarketCycleType.INFLATION:
            # Mixed effects - energy up, others down
            for company in companies.values():
                if company.industry == "Energy":
                    change = random.uniform(4.0, 8.0)
                    company.price *= (1 + change / 100)
                else:
                    change = random.uniform(2.0, 4.0)
                    company.price *= (1 - change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Inflation effects - Energy stocks rise, others pressured by rate hikes")

        elif cycle.cycle_type == MarketCycleType.MARKET_CRASH:
            # Severe crash (8-15%)
            for company in companies.values():
                change = random.uniform(8.0, 15.0)
                company.price *= (1 - change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 MARKET CRASH IMPACT - Extreme selling pressure across all sectors!")

        elif cycle.cycle_type == MarketCycleType.RECOVERY:
            # Strong recovery (5-10%)
            for company in companies.values():
                change = random.uniform(5.0, 10.0)
                company.price *= (1 + change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Economic recovery drives strong gains across all sectors!")

        elif cycle.cycle_type == MarketCycleType.TECH_BOOM:
            # Tech and electronics boom, others moderate gains
            for company in companies.values():
                if company.industry in ["Technology", "Electronics"]:
                    change = random.uniform(7.0, 12.0)
                else:
                    change = random.uniform(2.0, 4.0)
                company.price *= (1 + change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Tech boom continues - Technology and Electronics sectors surge!")

        return messages

    def update_cycle(self, companies: Dict[str, Company]) -> Tuple[List[str], bool]:
        """Update active cycle, return messages and whether cycle ended"""
        if not self.active_cycle:
            return [], False

        self.active_cycle.weeks_remaining -= 1

        # Apply weekly effects
        messages = self.apply_cycle_effects(companies)

        # Check if cycle ended
        if self.active_cycle.weeks_remaining <= 0:
            messages.append(f"\n🔔 MARKET CYCLE ENDED: {self.active_cycle.cycle_type.value.replace('_', ' ').title()} has concluded")
            self.active_cycle = None
            return messages, True

        return messages, False

    def get_current_cycle_display(self) -> Optional[str]:
        """Get display text for current active cycle"""
        if not self.active_cycle:
            return None

        return f"""
{'='*60}
🌍 ACTIVE GLOBAL MARKET CYCLE
{'='*60}
{self.active_cycle.headline}

{self.active_cycle.description}

Duration: {self.active_cycle.weeks_remaining} weeks remaining
{'='*60}
"""


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
        self.market_cycle = MarketCycle()  # Market cycle system (every 6 months)
        self.pending_news_display: Optional[NewsReport] = None  # News to display this week

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

        # Display active market cycle if any
        cycle_display = self.market_cycle.get_current_cycle_display()
        if cycle_display:
            print(cycle_display)

        # Display market news if available
        if self.pending_news_display:
            print("\n" + "📰 " + "="*58)
            print("MARKET NEWS - THIS WEEK'S HEADLINES")
            print("="*60)
            print()

            # Source 1: Financial Times Report
            print("Financial Times Report")
            print("-" * 60)
            if self.pending_news_display.trustworthy_source:
                print(f"  {self.pending_news_display.trustworthy_source}")
            else:
                print("  [No major developments to report at this time]")
            print()

            # Source 2: Market Pulse Daily
            print("Market Pulse Daily")
            print("-" * 60)
            print(f"  {self.pending_news_display.sensationalist_source}")
            print()

            # Source 3: Wall Street Wire
            print("Wall Street Wire")
            print("-" * 60)
            print(f"  {self.pending_news_display.insider_source}")

            print("="*60)

    def update_market(self):
        """Update all stock prices"""
        # Check if we should trigger a new market cycle
        if self.market_cycle.should_trigger_cycle(self.week_number):
            cycle = self.market_cycle.trigger_cycle(self.week_number)
            print("\n" + "🌍" + "="*58)
            print("MAJOR GLOBAL ECONOMIC EVENT")
            print("="*60)
            print(f"\n{cycle.headline}")
            print(f"\n{cycle.description}")
            print(f"\nThis cycle will affect markets for {cycle.weeks_remaining} weeks.")
            print("="*60)
            input("\nPress Enter to continue...")

        # Update active market cycle
        cycle_messages, cycle_ended = self.market_cycle.update_cycle(self.companies)

        # Apply any pending news impacts
        impact_messages = self.market_news.update_pending_impacts(self.companies)

        # Display all market movements
        all_messages = cycle_messages + impact_messages
        if all_messages:
            print("\n" + "⚡" + "="*58)
            print("BREAKING NEWS - MARKET MOVEMENTS")
            print("="*60)
            for message in all_messages:
                print(f"  {message}")
            print("="*60)
            input("\nPress Enter to continue...")

        # Regular price updates for all companies (only if no cycle is active)
        if not self.market_cycle.active_cycle:
            for company in self.companies.values():
                company.update_price()

    def player_turn(self, player: Player):
        """Execute a single player's turn"""
        print(f"\n\n{'#'*60}")
        print(f"Round {self.round_number} - Week {self.week_number} - {player.name}'s Turn")
        print(f"{'#'*60}")

        # Apply weekly interest on borrowed amount
        interest = player.apply_interest()
        if interest > 0:
            print(f"\n💳 Weekly interest charged on loan: ${interest:.2f}")

        # Check for margin call
        if player.check_margin_call(self.companies, self.treasury):
            print("\n" + "⚠️ " + "="*58)
            print("MARGIN CALL ALERT!")
            print("="*60)
            print("Your equity has fallen below 30% of your total position!")
            print("You must either deposit cash or sell assets to reduce leverage.")
            equity = player.calculate_equity(self.companies, self.treasury)
            print(f"Current Equity: ${equity:.2f}")
            print(f"Borrowed Amount: ${player.borrowed_amount:.2f}")
            print(f"Required Action: Increase equity or repay loan immediately!")
            print("="*60)
            input("\nPress Enter to continue...")

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
            print("6. Borrow Money (Leverage)")
            print("7. Repay Loan")
            print("8. End Turn")
            print("-"*60)

            choice = input("Enter choice (1-8): ").strip()

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
                self._borrow_money_menu(player)

            elif choice == "7":
                self._repay_loan_menu(player)

            elif choice == "8":
                print(f"\n{player.name} has ended their turn.")
                break

            else:
                print("Invalid choice! Please enter a number between 1 and 8.")

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

    def _borrow_money_menu(self, player: Player):
        """Menu for borrowing money using leverage"""
        print("\n" + "="*60)
        print("BORROW MONEY (LEVERAGE)")
        print("="*60)

        equity = player.calculate_equity(self.companies, self.treasury)
        max_can_borrow = max(0, equity * player.max_leverage_ratio - player.borrowed_amount)

        print(f"Your Equity: ${equity:.2f}")
        print(f"Already Borrowed: ${player.borrowed_amount:.2f}")
        print(f"Max Leverage Ratio: {player.max_leverage_ratio:.2f}x")
        print(f"Maximum You Can Borrow: ${max_can_borrow:.2f}")
        print(f"Interest Rate: {player.interest_rate_weekly:.3f}% per week (~6% annually)")
        print()

        if max_can_borrow <= 0:
            print("You've reached your maximum leverage limit!")
            return

        try:
            amount = float(input("How much to borrow? $"))

            if amount <= 0:
                print("Invalid amount!")
                return

            success, message = player.borrow_money(amount, self.companies, self.treasury)
            print(f"\n{message}")

        except ValueError:
            print("Invalid input!")

    def _repay_loan_menu(self, player: Player):
        """Menu for repaying borrowed money"""
        print("\n" + "="*60)
        print("REPAY LOAN")
        print("="*60)

        if player.borrowed_amount <= 0:
            print("You don't have any outstanding loans!")
            return

        print(f"Outstanding Loan: ${player.borrowed_amount:.2f}")
        print(f"Available Cash: ${player.cash:.2f}")
        print()

        try:
            amount = float(input("How much to repay? $"))

            if amount <= 0:
                print("Invalid amount!")
                return

            success, message = player.repay_loan(amount)
            print(f"\n{message}")

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
