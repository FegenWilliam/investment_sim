#!/usr/bin/env python3
"""
Competitive Investment Simulation Game
A turn-based stock market simulation for 1-4 players
"""

import random
import json
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

    def to_dict(self) -> dict:
        """Serialize NewsReport to dictionary"""
        return {
            'trustworthy_source': self.trustworthy_source,
            'sensationalist_source': self.sensationalist_source,
            'insider_source': self.insider_source,
            'insider_flipped': self.insider_flipped
        }

    @staticmethod
    def from_dict(data: dict) -> 'NewsReport':
        """Deserialize NewsReport from dictionary"""
        return NewsReport(
            trustworthy_source=data['trustworthy_source'],
            sensationalist_source=data['sensationalist_source'],
            insider_source=data['insider_source'],
            insider_flipped=data['insider_flipped']
        )


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

    def to_dict(self) -> dict:
        """Serialize PendingNewsImpact to dictionary"""
        return {
            'company_name': self.company_name,
            'sentiment': self.sentiment.value,
            'impact_magnitude': self.impact_magnitude,
            'weeks_until_impact': self.weeks_until_impact,
            'is_real': self.is_real,
            'news_text': self.news_text,
            'news_report': self.news_report.to_dict()
        }

    @staticmethod
    def from_dict(data: dict) -> 'PendingNewsImpact':
        """Deserialize PendingNewsImpact from dictionary"""
        return PendingNewsImpact(
            company_name=data['company_name'],
            sentiment=NewsSentiment(data['sentiment']),
            impact_magnitude=data['impact_magnitude'],
            weeks_until_impact=data['weeks_until_impact'],
            is_real=data['is_real'],
            news_text=data['news_text'],
            news_report=NewsReport.from_dict(data['news_report'])
        )


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

    def to_dict(self) -> dict:
        """Serialize MarketNews to dictionary"""
        return {
            'pending_impacts': [impact.to_dict() for impact in self.pending_impacts],
            'news_history': self.news_history
        }

    @staticmethod
    def from_dict(data: dict) -> 'MarketNews':
        """Deserialize MarketNews from dictionary"""
        market_news = MarketNews()
        market_news.pending_impacts = [
            PendingNewsImpact.from_dict(impact_data)
            for impact_data in data['pending_impacts']
        ]
        market_news.news_history = [tuple(item) for item in data['news_history']]
        return market_news

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

    def generate_news(self, companies: Dict[str, 'Company'], week_number: int, future_prices: Dict[str, List[float]]) -> Optional[NewsReport]:
        """Generate market news for a random company based on future price movements"""
        # Select random company
        company_name = random.choice(list(companies.keys()))
        company = companies[company_name]

        # Determine TRUE sentiment based on future price movement
        # Look at the next 2 weeks average to determine trend
        current_price = company.price
        future_avg = sum(future_prices[company_name]) / len(future_prices[company_name])
        price_change_percent = ((future_avg - current_price) / current_price) * 100

        # TRUE sentiment based on actual future movement
        if price_change_percent > 2.0:  # Stock going up significantly
            true_sentiment = NewsSentiment.POSITIVE
        elif price_change_percent < -2.0:  # Stock going down significantly
            true_sentiment = NewsSentiment.NEGATIVE
        else:
            # Small movement - randomly choose
            true_sentiment = random.choice([NewsSentiment.POSITIVE, NewsSentiment.NEGATIVE])

        # Determine if news is real or hoax (70% real, 30% hoax)
        is_real = random.random() < 0.7

        # If hoax, flip the sentiment (news lies about the future)
        if is_real:
            sentiment = true_sentiment
        else:
            # Hoax - report opposite of truth
            sentiment = NewsSentiment.NEGATIVE if true_sentiment == NewsSentiment.POSITIVE else NewsSentiment.POSITIVE

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


class WeeklyGazette:
    """Handles weekly news outlet that publishes random company news every week"""

    # Weekly gazette news templates - varied company updates
    WEEKLY_NEWS_TEMPLATES = [
        # Product and service updates
        "{company} unveils next-generation product line at {industry} trade show, receiving positive initial feedback from attendees.",
        "{company} announces minor software update addressing customer-requested features in their flagship platform.",
        "Sources report {company} is piloting new service offerings in select markets before potential broader rollout.",
        "{company} quarterly product roadmap hints at upcoming innovations expected to ship later this year.",
        "Industry publication spotlights {company}'s latest patent filings in {industry} technology space.",

        # Business operations
        "{company} opens new regional office to support growing customer base in emerging markets.",
        "Reports indicate {company} is streamlining operations to improve efficiency and reduce overhead costs.",
        "{company} announces expansion of customer support team as user base continues to grow steadily.",
        "Supply chain update: {company} diversifies supplier network to enhance operational resilience.",
        "{company} implements new inventory management system expected to optimize working capital.",

        # Partnerships and collaborations
        "{company} signs distribution agreement with mid-sized retailer expanding market reach.",
        "Trade sources note {company} exploring potential collaboration with {industry} research institutions.",
        "{company} joins industry consortium focused on developing technical standards and best practices.",
        "Local media reports {company} partnering with community organizations on sustainability initiatives.",
        "{company} announces co-marketing arrangement with complementary {industry} service provider.",

        # Corporate updates
        "{company} promotes several senior managers to vice president roles as part of succession planning.",
        "Investor relations team at {company} schedules additional analyst meetings following earnings release.",
        "{company} board of directors approves modest share repurchase authorization signaling stability.",
        "Corporate social responsibility report from {company} highlights progress on environmental commitments.",
        "{company} announces plans to attend upcoming {industry} investor conference circuit.",

        # Market and competitive position
        "Market research firm includes {company} in list of notable {industry} sector players to watch.",
        "{company} gains minor market share in competitive {industry} landscape according to latest data.",
        "Competitive analysis suggests {company} maintaining steady positioning against industry rivals.",
        "Customer satisfaction survey ranks {company} favorably compared to peer group average.",
        "{company} cited in {industry} trend report as company adapting to evolving market dynamics.",

        # Financial and operational metrics
        "{company} reports in-line quarterly metrics meeting baseline street expectations without major surprises.",
        "Operating margin analysis shows {company} maintaining stable profitability levels quarter-over-quarter.",
        "Working capital metrics for {company} remain within normal ranges for {industry} sector companies.",
        "{company} cash position described as adequate to fund ongoing operations and planned investments.",
        "Quarterly update indicates {company} capital expenditures tracking to annual guidance projections.",

        # Research and development
        "{company} R&D team presents findings at {industry} technical symposium garnering peer interest.",
        "Patent office filings show {company} continuing investment in intellectual property development.",
        "Engineering blog from {company} discusses technical challenges and solutions in product development.",
        "{company} announces incremental improvements to manufacturing processes enhancing quality control.",
        "Innovation pipeline at {company} includes several projects in various stages of development.",

        # Personnel and talent
        "{company} announces new employee wellness program aimed at improving workplace satisfaction.",
        "Talent acquisition team at {company} actively recruiting for positions across multiple departments.",
        "{company} implements updated training protocols to enhance employee skill development.",
        "Company culture survey at {company} shows stable employee engagement and retention metrics.",
        "Diversity and inclusion report from {company} outlines ongoing initiatives and progress metrics.",

        # Regulatory and compliance
        "{company} confirms compliance with updated {industry} sector regulatory requirements.",
        "Routine regulatory filing by {company} includes standard disclosures without material changes.",
        "{company} participates in industry working group addressing evolving compliance standards.",
        "Quality assurance processes at {company} pass routine inspection without significant findings.",
        "{company} updates corporate governance policies in line with current best practice recommendations.",

        # Customer and market reach
        "{company} customer testimonial program highlights positive user experiences and use cases.",
        "Geographic expansion update: {company} establishes presence in additional regional markets.",
        "{company} digital marketing campaign launches targeting specific customer segments.",
        "Trade publication features {company} client success story demonstrating product value proposition.",
        "Market penetration analysis shows {company} reaching new customer demographics incrementally.",

        # Technology and infrastructure
        "{company} completes routine infrastructure upgrades improving system reliability and performance.",
        "IT security assessment confirms {company} maintains robust cybersecurity protocols and practices.",
        "{company} announces adoption of cloud technologies to enhance operational scalability.",
        "Data center efficiency improvements at {company} reduce energy consumption and operating costs.",
        "{company} implements enhanced analytics capabilities to support data-driven decision making.",

        # Industry recognition and awards
        "{company} receives industry recognition for customer service excellence from trade association.",
        "Professional organization names {company} to annual list of noteworthy {industry} companies.",
        "{company} executive invited to speak at industry panel discussing {industry} sector trends.",
        "Third-party certification validates {company} adherence to quality and safety standards.",
        "{company} featured in industry case study examining operational best practices and outcomes.",

        # Strategic initiatives
        "{company} announces completion of internal restructuring aimed at organizational efficiency.",
        "Strategic review at {company} identifies opportunities for incremental business optimization.",
        "{company} realigns product portfolio to focus resources on core competency areas.",
        "Long-term planning update from {company} outlines vision for next three to five years.",
        "{company} evaluates potential acquisition targets to complement existing capabilities.",

        # Routine business updates
        "{company} schedules routine maintenance window for systems upgrades during off-peak hours.",
        "Quarterly business review at {company} confirms operations proceeding according to plan.",
        "{company} renews standard contracts with key vendors and service providers.",
        "Seasonal business patterns at {company} tracking consistent with historical trends.",
        "{company} logistics network optimization initiative enters implementation phase.",
    ]

    def __init__(self):
        self.weekly_news_history: List[Tuple[int, str]] = []  # (week_number, news_text)

    def to_dict(self) -> dict:
        """Serialize WeeklyGazette to dictionary"""
        return {
            'weekly_news_history': self.weekly_news_history
        }

    @staticmethod
    def from_dict(data: dict) -> 'WeeklyGazette':
        """Deserialize WeeklyGazette from dictionary"""
        gazette = WeeklyGazette()
        gazette.weekly_news_history = [tuple(item) for item in data['weekly_news_history']]
        return gazette

    def generate_weekly_news(self, companies: Dict[str, 'Company'], week_number: int) -> str:
        """Generate weekly news for a random company"""
        # Select random company
        company_name = random.choice(list(companies.keys()))
        company = companies[company_name]

        # Select random news template
        template = random.choice(self.WEEKLY_NEWS_TEMPLATES)
        news_text = template.format(company=company_name, industry=company.industry)

        # Store in history
        self.weekly_news_history.append((week_number, news_text))

        return news_text


class LiquidityLevel(Enum):
    """Liquidity levels for stocks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Company:
    """Represents a publicly traded company"""

    def __init__(self, name: str, industry: str, initial_price: float, volatility: float, liquidity: LiquidityLevel = LiquidityLevel.MEDIUM):
        self.name = name
        self.industry = industry
        self.price = initial_price
        self.base_volatility = volatility
        self.price_history = [initial_price]
        self.liquidity = liquidity
        # Hidden fundamentals for research hints (not directly visible to players)
        self.true_strength = random.uniform(0.3, 0.9)  # 0-1 scale, affects hint accuracy
        self.hidden_sentiment = random.choice([-1, 0, 1])  # -1: bearish, 0: neutral, 1: bullish

    def update_price(self):
        """Update stock price based on volatility (random walk)"""
        # Random price change based on volatility
        change_percent = random.uniform(-self.base_volatility, self.base_volatility)
        self.price *= (1 + change_percent / 100)
        self.price = max(0.01, self.price)  # Prevent negative prices
        self.price_history.append(self.price)

    def calculate_slippage(self, shares: int, is_buy: bool) -> float:
        """Calculate price slippage based on liquidity and trade size"""
        # Base slippage percentages by liquidity level
        if self.liquidity == LiquidityLevel.HIGH:
            base_slippage = 0.0005  # 0.05% per 100 shares
        elif self.liquidity == LiquidityLevel.MEDIUM:
            base_slippage = 0.002  # 0.2% per 100 shares
        else:  # LOW
            base_slippage = 0.005  # 0.5% per 100 shares

        # Calculate slippage based on trade size
        slippage_multiplier = shares / 100.0
        total_slippage = base_slippage * slippage_multiplier

        # Slippage goes against the trader (increases buy price, decreases sell price)
        if is_buy:
            return 1 + total_slippage
        else:
            return 1 - total_slippage

    def get_liquidity_indicator(self) -> str:
        """Get visual indicator for liquidity"""
        if self.liquidity == LiquidityLevel.HIGH:
            return "💧💧💧"
        elif self.liquidity == LiquidityLevel.MEDIUM:
            return "💧💧"
        else:
            return "💧"

    def to_dict(self) -> dict:
        """Serialize company to dictionary"""
        return {
            'name': self.name,
            'industry': self.industry,
            'price': self.price,
            'base_volatility': self.base_volatility,
            'price_history': self.price_history,
            'liquidity': self.liquidity.value,
            'true_strength': self.true_strength,
            'hidden_sentiment': self.hidden_sentiment
        }

    @staticmethod
    def from_dict(data: dict) -> 'Company':
        """Deserialize company from dictionary"""
        company = Company(
            name=data['name'],
            industry=data['industry'],
            initial_price=data['price'],
            volatility=data['base_volatility'],
            liquidity=LiquidityLevel(data['liquidity'])
        )
        company.price = data['price']
        company.price_history = data['price_history']
        company.true_strength = data['true_strength']
        company.hidden_sentiment = data['hidden_sentiment']
        return company

    def __str__(self):
        return f"{self.name} ({self.industry}) - ${self.price:.2f} {self.get_liquidity_indicator()}"


class Treasury:
    """Represents treasury bonds"""

    def __init__(self):
        self.name = "US Treasury Bonds"
        self.interest_rate = 3.5  # 3.5% annual return
        self.price = 100.0  # $100 per bond

    def to_dict(self) -> dict:
        """Serialize treasury to dictionary"""
        return {
            'interest_rate': self.interest_rate,
            'price': self.price
        }

    @staticmethod
    def from_dict(data: dict) -> 'Treasury':
        """Deserialize treasury from dictionary"""
        treasury = Treasury()
        treasury.interest_rate = data['interest_rate']
        treasury.price = data['price']
        return treasury

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
        self.max_leverage_ratio = 5.0  # Can borrow up to 5x equity
        self.interest_rate_weekly = 0.115  # ~6% annual = 0.115% weekly
        # Research tracking
        self.researched_this_week = False
        self.research_history: Dict[str, List[str]] = {}  # company_name -> list of hints received

    def buy_stock(self, company: Company, shares: int) -> Tuple[bool, str]:
        """Buy shares of a company with liquidity slippage"""
        # Calculate effective price with slippage
        slippage_factor = company.calculate_slippage(shares, is_buy=True)
        effective_price = company.price * slippage_factor
        total_cost = effective_price * shares

        if total_cost > self.cash:
            return False, "Insufficient funds!"

        self.cash -= total_cost
        if company.name in self.portfolio:
            self.portfolio[company.name] += shares
        else:
            self.portfolio[company.name] = shares

        # Calculate and show slippage impact
        slippage_cost = (effective_price - company.price) * shares
        if slippage_cost > 0.01:
            message = f"Purchase successful! (Price slippage: ${slippage_cost:.2f} due to {company.liquidity.value} liquidity)"
        else:
            message = "Purchase successful!"

        return True, message

    def sell_stock(self, company: Company, shares: int) -> Tuple[bool, str]:
        """Sell shares of a company with liquidity slippage"""
        if company.name not in self.portfolio or self.portfolio[company.name] < shares:
            return False, "You don't own that many shares!"

        # Calculate effective price with slippage
        slippage_factor = company.calculate_slippage(shares, is_buy=False)
        effective_price = company.price * slippage_factor
        total_value = effective_price * shares

        self.cash += total_value
        self.portfolio[company.name] -= shares
        if self.portfolio[company.name] == 0:
            del self.portfolio[company.name]

        # Calculate and show slippage impact
        slippage_loss = (company.price - effective_price) * shares
        if slippage_loss > 0.01:
            message = f"Sale successful! (Price slippage: -${slippage_loss:.2f} due to {company.liquidity.value} liquidity)"
        else:
            message = "Sale successful!"

        return True, message

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

    def force_liquidate_margin_call(self, companies: Dict[str, Company], treasury: Treasury) -> List[str]:
        """
        Automatically liquidate positions to meet margin requirements.
        Returns a list of actions taken.
        """
        actions = []

        if not self.check_margin_call(companies, treasury):
            return actions  # No margin call, nothing to do

        actions.append(f"🚨 FORCED LIQUIDATION for {self.name} - Margin call not resolved")

        # Liquidate stocks first
        # Sort by value (sell largest positions first to minimize transactions)
        stock_positions = [(name, shares, companies[name].price * shares)
                          for name, shares in self.portfolio.items()]
        stock_positions.sort(key=lambda x: x[2], reverse=True)

        for company_name, shares, value in stock_positions:
            if not self.check_margin_call(companies, treasury):
                break  # Margin call resolved

            company = companies[company_name]
            proceeds = shares * company.price
            self.cash += proceeds
            self.portfolio[company_name] = 0
            actions.append(f"   Sold {shares} shares of {company_name} for ${proceeds:.2f}")

            # Use proceeds to repay loan
            repayment = min(self.cash, self.borrowed_amount)
            if repayment > 0:
                self.borrowed_amount -= repayment
                self.cash -= repayment
                actions.append(f"   Repaid ${repayment:.2f} of loan")

        # Clean up empty positions
        self.portfolio = {k: v for k, v in self.portfolio.items() if v > 0}

        # If still in margin call, liquidate treasury bonds
        if self.check_margin_call(companies, treasury) and self.treasury_bonds > 0:
            proceeds = self.treasury_bonds * treasury.price
            self.cash += proceeds
            actions.append(f"   Sold {self.treasury_bonds} treasury bonds for ${proceeds:.2f}")
            self.treasury_bonds = 0

            # Use proceeds to repay loan
            repayment = min(self.cash, self.borrowed_amount)
            if repayment > 0:
                self.borrowed_amount -= repayment
                self.cash -= repayment
                actions.append(f"   Repaid ${repayment:.2f} of loan")

        # Final status
        equity = self.calculate_equity(companies, treasury)
        if self.check_margin_call(companies, treasury):
            actions.append(f"   ⚠️ WARNING: Still in margin call after full liquidation!")
            actions.append(f"   Final Equity: ${equity:.2f}, Debt: ${self.borrowed_amount:.2f}")
        else:
            actions.append(f"   ✓ Margin call resolved. Equity: ${equity:.2f}, Debt: ${self.borrowed_amount:.2f}")

        return actions

    def research_company(self, company: Company, future_price: float = None) -> str:
        """Research a company to get a hint (once per week)"""
        if self.researched_this_week:
            return "You've already researched a company this week!"

        # Generate a hint based on company fundamentals AND future price movements
        # Hints are "mostly true" - 85% accuracy
        is_accurate = random.random() < 0.85

        hint_templates = [
            # Volatility and risk hints
            ("Technical analysis reveals {company} exhibits {level} beta coefficient, suggesting price movements could be {magnitude} compared to broader market trends.",
             lambda c: {"level": "an elevated" if c.base_volatility > 7.5 else "a moderate" if c.base_volatility > 6 else "a relatively low",
                       "magnitude": "substantially amplified" if c.base_volatility > 7.5 else "moderately volatile" if c.base_volatility > 6 else "relatively stable"}),

            ("Quantitative risk models indicate {company} displays {pattern} variance patterns with {description} in the {industry} sector.",
             lambda c: {"pattern": "high-frequency" if c.base_volatility > 8 else "medium-frequency" if c.base_volatility > 6 else "low-frequency",
                       "description": "significant outlier characteristics" if c.base_volatility > 8 else "typical behavior" if c.base_volatility > 6 else "defensive qualities",
                       "industry": c.industry}),

            # Industry and sector sentiment
            ("Industry analysts from leading {industry} research firms are {sentiment} about sector tailwinds, citing {factors}.",
             lambda c: {"industry": c.industry,
                       "sentiment": "increasingly bullish" if c.hidden_sentiment > 0 else "growing pessimistic" if c.hidden_sentiment < 0 else "cautiously neutral",
                       "factors": "favorable regulatory environment and strong demand" if c.hidden_sentiment > 0 else "headwinds from competition and margin pressure" if c.hidden_sentiment < 0 else "mixed macroeconomic signals"}),

            ("Sector rotation analysis suggests {industry} stocks like {company} may be {position} institutional portfolio allocations over the next quarter.",
             lambda c: {"industry": c.industry,
                       "position": "entering" if c.hidden_sentiment > 0 else "exiting" if c.hidden_sentiment < 0 else "maintaining stable presence in"}),

            # Fundamental strength and valuation
            ("Deep dive fundamental analysis of {company} reveals {strength} balance sheet metrics, with debt-to-equity ratios {ratio_desc} and cash flow generation {cash_desc}.",
             lambda c: {"strength": "robust" if c.true_strength > 0.65 else "concerning" if c.true_strength < 0.5 else "adequate",
                       "ratio_desc": "well below industry averages" if c.true_strength > 0.65 else "elevated compared to peers" if c.true_strength < 0.5 else "in line with sector norms",
                       "cash_desc": "exceeding expectations" if c.true_strength > 0.65 else "underperforming forecasts" if c.true_strength < 0.5 else "meeting baseline requirements"}),

            ("Proprietary valuation models comparing {company} to peer group suggest shares are currently trading at {valuation} relative to intrinsic value estimates.",
             lambda c: {"valuation": "a discount" if c.true_strength > 0.65 else "a premium" if c.true_strength < 0.5 else "fair value"}),

            ("Management quality assessment for {company} indicates {quality} corporate governance and {execution} track record of strategic execution.",
             lambda c: {"quality": "exemplary" if c.true_strength > 0.65 else "questionable" if c.true_strength < 0.5 else "acceptable",
                       "execution": "a strong" if c.true_strength > 0.65 else "a weak" if c.true_strength < 0.5 else "a mixed"}),

            # Liquidity and market microstructure
            ("Market microstructure analysis of {company} shows {liquidity} order book depth with bid-ask spreads {spread} and daily trading volumes {volume}.",
             lambda c: {"liquidity": "exceptional" if c.liquidity == LiquidityLevel.HIGH else "constrained" if c.liquidity == LiquidityLevel.LOW else "moderate",
                       "spread": "remaining tight" if c.liquidity == LiquidityLevel.HIGH else "widening significantly" if c.liquidity == LiquidityLevel.LOW else "within normal ranges",
                       "volume": "consistently robust" if c.liquidity == LiquidityLevel.HIGH else "disappointingly thin" if c.liquidity == LiquidityLevel.LOW else "adequate for most positions"}),

            ("Trading desk liquidity report flags {company} as {classification} for large block trades, with estimated market impact costs {impact}.",
             lambda c: {"classification": "highly favorable" if c.liquidity == LiquidityLevel.HIGH else "challenging" if c.liquidity == LiquidityLevel.LOW else "manageable",
                       "impact": "minimal even for substantial positions" if c.liquidity == LiquidityLevel.HIGH else "potentially significant for moderate-sized orders" if c.liquidity == LiquidityLevel.LOW else "reasonable for typical retail trades"}),

            # Price momentum and technical analysis
            ("{company}'s recent price action demonstrates {trend} momentum with {pattern} chart patterns suggesting {direction} pressure.",
             lambda c: {"trend": "strong bullish" if len(c.price_history) >= 2 and c.price > c.price_history[-2] else "bearish" if len(c.price_history) >= 2 and c.price < c.price_history[-2] else "sideways consolidation",
                       "pattern": "continuation" if len(c.price_history) >= 2 and c.price > c.price_history[-2] else "reversal" if len(c.price_history) >= 2 and c.price < c.price_history[-2] else "indecisive",
                       "direction": "continued upward" if len(c.price_history) >= 2 and c.price > c.price_history[-2] else "downward" if len(c.price_history) >= 2 and c.price < c.price_history[-2] else "range-bound"}),

            ("Moving average convergence analysis for {company} indicates {signal} crossover patterns with RSI readings {rsi} and MACD trends {macd}.",
             lambda c: {"signal": "bullish golden cross" if len(c.price_history) >= 2 and c.price > c.price_history[-2] else "bearish death cross" if len(c.price_history) >= 2 and c.price < c.price_history[-2] else "neutral",
                       "rsi": "approaching overbought territory" if len(c.price_history) >= 2 and c.price > c.price_history[-2] else "drifting into oversold zones" if len(c.price_history) >= 2 and c.price < c.price_history[-2] else "hovering near midpoint",
                       "macd": "strengthening upward" if len(c.price_history) >= 2 and c.price > c.price_history[-2] else "weakening considerably" if len(c.price_history) >= 2 and c.price < c.price_history[-2] else "showing no clear direction"}),

            # Comprehensive outlook and forecasting
            ("Comprehensive research synthesis on {company} yields {outlook} outlook, with analyst price targets {targets} and institutional sentiment {sentiment}.",
             lambda c: {"outlook": "a constructive" if c.hidden_sentiment >= 0 and c.true_strength > 0.6 else "a cautious" if c.hidden_sentiment < 0 or c.true_strength < 0.45 else "a neutral",
                       "targets": "skewed to the upside" if c.hidden_sentiment >= 0 and c.true_strength > 0.6 else "pointing toward downside risk" if c.hidden_sentiment < 0 or c.true_strength < 0.45 else "clustered around current levels",
                       "sentiment": "building conviction" if c.hidden_sentiment >= 0 and c.true_strength > 0.6 else "exhibiting caution" if c.hidden_sentiment < 0 or c.true_strength < 0.45 else "remaining on the sidelines"}),

            ("Multi-factor quantitative scoring places {company} in the {percentile} percentile of our {industry} coverage universe, with {rating} recommendations.",
             lambda c: {"percentile": "upper" if c.true_strength > 0.65 else "lower" if c.true_strength < 0.5 else "middle",
                       "industry": c.industry,
                       "rating": "predominantly buy-side" if c.true_strength > 0.65 else "mostly sell-side" if c.true_strength < 0.5 else "mixed hold and neutral"}),

            # Institutional and insider activity
            ("Recent SEC filings reveal {activity} institutional ownership changes in {company}, with hedge funds {action} and insider transactions {insider}.",
             lambda c: {"activity": "notable" if c.liquidity == LiquidityLevel.HIGH else "limited" if c.liquidity == LiquidityLevel.LOW else "moderate",
                       "action": "accumulating significant positions" if c.liquidity == LiquidityLevel.HIGH else "reducing exposure" if c.liquidity == LiquidityLevel.LOW else "maintaining current stakes",
                       "insider": "showing confidence through purchases" if c.true_strength > 0.6 else "raising concerns via sales" if c.true_strength < 0.5 else "remaining neutral"}),

            ("Smart money tracker algorithms detect {flow} capital flows into {company}, suggesting {implication} from sophisticated investors.",
             lambda c: {"flow": "aggressive" if c.liquidity == LiquidityLevel.HIGH and c.true_strength > 0.6 else "weak" if c.liquidity == LiquidityLevel.LOW or c.true_strength < 0.5 else "steady",
                       "implication": "strong conviction and positive positioning" if c.liquidity == LiquidityLevel.HIGH and c.true_strength > 0.6 else "lack of interest or distributional activity" if c.liquidity == LiquidityLevel.LOW or c.true_strength < 0.5 else "wait-and-see approach"}),

            # Risk-specific insights
            ("Stress testing scenarios for {company} indicate {resilience} to market shocks, with downside protection {protection} and volatility buffers {buffer}.",
             lambda c: {"resilience": "strong resilience" if c.base_volatility < 6.5 and c.true_strength > 0.6 else "vulnerability" if c.base_volatility > 8 or c.true_strength < 0.45 else "moderate stability",
                       "protection": "well-established" if c.base_volatility < 6.5 else "minimal" if c.base_volatility > 8 else "present but limited",
                       "buffer": "providing substantial cushion" if c.true_strength > 0.6 else "offering little safety margin" if c.true_strength < 0.5 else "adequate for normal conditions"}),

            ("Value-at-risk calculations for {company} suggest {risk} portfolio impact under adverse scenarios, with tail risk exposures {tail}.",
             lambda c: {"risk": "contained" if c.base_volatility < 7 else "elevated" if c.base_volatility > 8 else "moderate",
                       "tail": "largely mitigated" if c.base_volatility < 7 else "requiring careful monitoring" if c.base_volatility > 8 else "within acceptable parameters"}),

            # Growth and earnings insights
            ("Forward earnings projections for {company} show {growth} trajectory with revenue growth {revenue} and margin expansion {margin}.",
             lambda c: {"growth": "an accelerating" if c.hidden_sentiment > 0 and c.true_strength > 0.6 else "a decelerating" if c.hidden_sentiment < 0 or c.true_strength < 0.5 else "a stable",
                       "revenue": "outpacing sector averages" if c.hidden_sentiment > 0 else "lagging competitors" if c.hidden_sentiment < 0 else "matching industry benchmarks",
                       "margin": "expected to improve materially" if c.true_strength > 0.65 else "likely to contract" if c.true_strength < 0.5 else "forecasted to remain steady"}),

            ("Competitive positioning analysis suggests {company} maintains {position} market share with {moat} competitive advantages.",
             lambda c: {"position": "expanding" if c.true_strength > 0.65 and c.hidden_sentiment > 0 else "eroding" if c.true_strength < 0.5 or c.hidden_sentiment < 0 else "stable",
                       "moat": "durable and widening" if c.true_strength > 0.65 else "questionable or narrowing" if c.true_strength < 0.5 else "moderate"}),
        ]

        # Add future price-based hints if future_price is provided
        if future_price is not None:
            price_change_pct = ((future_price - company.price) / company.price) * 100

            # Create a lambda that captures the future price movement
            def future_momentum_data(c):
                return {
                    "trend": "accelerating upward" if price_change_pct > 3 else "declining" if price_change_pct < -3 else "consolidating",
                    "direction": "positive" if price_change_pct > 1 else "negative" if price_change_pct < -1 else "neutral",
                    "strength": "strong" if abs(price_change_pct) > 5 else "moderate" if abs(price_change_pct) > 2 else "weak"
                }

            hint_templates.extend([
                ("Our proprietary momentum indicators suggest {company} is showing {trend} momentum with {strength} directional signals in the near term.",
                 future_momentum_data),

                ("Algorithmic trading models detect {direction} flow patterns for {company}, with institutional positioning suggesting {trend} price action ahead.",
                 future_momentum_data),

                ("Short-term predictive analytics for {company} indicate {trend} momentum, with our quant models flagging {strength} probability of continuation.",
                 future_momentum_data),
            ])

        # Select random hint template
        template, data_func = random.choice(hint_templates)

        # Get data for this company
        data = data_func(company)
        data["company"] = company.name

        # If inaccurate, flip the sentiment/direction
        if not is_accurate:
            # Flip certain descriptors to make hint misleading
            flips = {
                "optimistic": "pessimistic", "pessimistic": "optimistic",
                "solid": "questionable", "questionable": "solid",
                "excellent": "limited", "limited": "excellent",
                "bullish": "bearish", "bearish": "bullish",
                "favorable": "concerning", "concerning": "favorable",
                "strong": "weak", "weak": "strong",
                "significant": "mild", "mild": "significant"
            }
            for key, value in data.items():
                if value in flips:
                    data[key] = flips[value]

        hint = template.format(**data)

        # Mark research as used
        self.researched_this_week = True

        # Store hint in history
        if company.name not in self.research_history:
            self.research_history[company.name] = []
        self.research_history[company.name].append(hint)

        return hint

    def reset_weekly_research(self):
        """Reset research availability for new week"""
        self.researched_this_week = False

    def to_dict(self) -> dict:
        """Serialize player to dictionary"""
        return {
            'name': self.name,
            'cash': self.cash,
            'portfolio': self.portfolio,
            'treasury_bonds': self.treasury_bonds,
            'borrowed_amount': self.borrowed_amount,
            'max_leverage_ratio': self.max_leverage_ratio,
            'interest_rate_weekly': self.interest_rate_weekly,
            'researched_this_week': self.researched_this_week,
            'research_history': self.research_history
        }

    @staticmethod
    def from_dict(data: dict) -> 'Player':
        """Deserialize player from dictionary"""
        player = Player(data['name'], data['cash'])
        player.portfolio = data['portfolio']
        player.treasury_bonds = data['treasury_bonds']
        player.borrowed_amount = data['borrowed_amount']
        player.max_leverage_ratio = data['max_leverage_ratio']
        player.interest_rate_weekly = data['interest_rate_weekly']
        player.researched_this_week = data['researched_this_week']
        player.research_history = data['research_history']
        return player

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

    def to_dict(self) -> dict:
        """Serialize ActiveMarketCycle to dictionary"""
        return {
            'cycle_type': self.cycle_type.value,
            'weeks_remaining': self.weeks_remaining,
            'headline': self.headline,
            'description': self.description
        }

    @staticmethod
    def from_dict(data: dict) -> 'ActiveMarketCycle':
        """Deserialize ActiveMarketCycle from dictionary"""
        return ActiveMarketCycle(
            cycle_type=MarketCycleType(data['cycle_type']),
            weeks_remaining=data['weeks_remaining'],
            headline=data['headline'],
            description=data['description']
        )


class MarketCycle:
    """Handles major market cycles (economic events every 6 months)"""

    def __init__(self):
        self.active_cycle: Optional[ActiveMarketCycle] = None
        self.cycle_history: List[Tuple[int, str]] = []  # (week_number, cycle_name)

    def to_dict(self) -> dict:
        """Serialize MarketCycle to dictionary"""
        return {
            'active_cycle': self.active_cycle.to_dict() if self.active_cycle else None,
            'cycle_history': self.cycle_history
        }

    @staticmethod
    def from_dict(data: dict) -> 'MarketCycle':
        """Deserialize MarketCycle from dictionary"""
        market_cycle = MarketCycle()
        if data['active_cycle']:
            market_cycle.active_cycle = ActiveMarketCycle.from_dict(data['active_cycle'])
        market_cycle.cycle_history = [tuple(item) for item in data['cycle_history']]
        return market_cycle

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


class HedgeFund(Player):
    """Represents an AI-controlled hedge fund NPC"""

    def __init__(self, name: str, strategy: str, starting_cash: float = 10000.0):
        super().__init__(name, starting_cash)
        self.strategy = strategy  # "aggressive", "value", "contrarian"
        self.is_npc = True

    def to_dict(self) -> dict:
        """Serialize hedge fund to dictionary"""
        data = super().to_dict()
        data['strategy'] = self.strategy
        data['is_npc'] = self.is_npc
        return data

    @staticmethod
    def from_dict(data: dict) -> 'HedgeFund':
        """Deserialize hedge fund from dictionary"""
        hedge_fund = HedgeFund(data['name'], data['strategy'], data['cash'])
        hedge_fund.portfolio = data['portfolio']
        hedge_fund.treasury_bonds = data['treasury_bonds']
        hedge_fund.borrowed_amount = data['borrowed_amount']
        hedge_fund.max_leverage_ratio = data['max_leverage_ratio']
        hedge_fund.interest_rate_weekly = data['interest_rate_weekly']
        hedge_fund.researched_this_week = data['researched_this_week']
        hedge_fund.research_history = data['research_history']
        return hedge_fund

    def make_automated_trade(self, companies: Dict[str, Company], treasury: Treasury,
                           market_cycle: 'MarketCycle', week_number: int) -> List[str]:
        """Execute automated trading based on strategy"""
        actions = []

        # Aggressive Growth Fund Strategy
        if self.strategy == "aggressive":
            actions.extend(self._aggressive_strategy(companies, treasury, market_cycle))

        # Value Fund Strategy
        elif self.strategy == "value":
            actions.extend(self._value_strategy(companies, treasury, market_cycle))

        # Contrarian Fund Strategy
        elif self.strategy == "contrarian":
            actions.extend(self._contrarian_strategy(companies, treasury, market_cycle))

        return actions

    def _aggressive_strategy(self, companies: Dict[str, Company], treasury: Treasury,
                           market_cycle: 'MarketCycle') -> List[str]:
        """Aggressive: High volatility stocks, uses leverage, momentum trading"""
        actions = []

        # Use leverage aggressively if not already maxed out
        equity = self.calculate_equity(companies, treasury)
        if equity > 0 and self.borrowed_amount < equity * 1.5:
            borrow_amount = min(2000, equity * 1.5 - self.borrowed_amount)
            if borrow_amount > 100:
                success, msg = self.borrow_money(borrow_amount, companies, treasury)
                if success:
                    actions.append(f"🏦 {self.name} borrowed ${borrow_amount:.2f} for aggressive plays")

        # Target high volatility stocks during bull markets or recovery
        if market_cycle.active_cycle and market_cycle.active_cycle.cycle_type in [
            MarketCycleType.BULL_MARKET, MarketCycleType.RECOVERY, MarketCycleType.TECH_BOOM
        ]:
            # Buy high volatility stocks
            high_vol_companies = sorted(companies.values(), key=lambda c: c.base_volatility, reverse=True)[:2]
            for company in high_vol_companies:
                if self.cash > 1000:
                    shares_to_buy = int(min(self.cash * 0.3, 3000) / company.price)
                    if shares_to_buy > 0:
                        success, msg = self.buy_stock(company, shares_to_buy)
                        if success:
                            actions.append(f"📈 {self.name} aggressively bought {shares_to_buy} shares of {company.name}")

        # Sell during bear markets or crashes
        elif market_cycle.active_cycle and market_cycle.active_cycle.cycle_type in [
            MarketCycleType.BEAR_MARKET, MarketCycleType.MARKET_CRASH, MarketCycleType.RECESSION
        ]:
            # Sell positions to cut losses
            for company_name, shares in list(self.portfolio.items()):
                sell_shares = int(shares * 0.4)  # Sell 40% of position
                if sell_shares > 0:
                    company = companies[company_name]
                    success, msg = self.sell_stock(company, sell_shares)
                    if success:
                        actions.append(f"📉 {self.name} cut position, sold {sell_shares} shares of {company_name}")

        # Baseline buying: always try to buy high volatility stocks if we have cash
        else:
            if self.cash > 1000:
                high_vol_companies = sorted(companies.values(), key=lambda c: c.base_volatility, reverse=True)[:2]
                for company in high_vol_companies:
                    if self.cash > 1000:
                        shares_to_buy = int(min(self.cash * 0.2, 2000) / company.price)
                        if shares_to_buy > 0:
                            success, msg = self.buy_stock(company, shares_to_buy)
                            if success:
                                actions.append(f"📊 {self.name} bought {shares_to_buy} shares of {company.name}")
                                break  # Buy one company at a time during neutral markets

        return actions

    def _value_strategy(self, companies: Dict[str, Company], treasury: Treasury,
                       market_cycle: 'MarketCycle') -> List[str]:
        """Value: Conservative, low volatility stocks, diversified"""
        actions = []

        # Conservative leverage (only up to 1x equity)
        equity = self.calculate_equity(companies, treasury)
        if equity > 0 and self.borrowed_amount < equity * 0.8:
            borrow_amount = min(1000, equity * 0.8 - self.borrowed_amount)
            if borrow_amount > 100:
                success, msg = self.borrow_money(borrow_amount, companies, treasury)
                if success:
                    actions.append(f"🏦 {self.name} conservatively borrowed ${borrow_amount:.2f}")

        # Focus on low volatility, high liquidity stocks
        stable_companies = [c for c in companies.values()
                          if c.base_volatility < 7.0 and c.liquidity == LiquidityLevel.HIGH]

        # Fallback to medium liquidity if no high liquidity stocks available
        if not stable_companies:
            stable_companies = [c for c in companies.values()
                              if c.base_volatility < 8.0 and c.liquidity in [LiquidityLevel.HIGH, LiquidityLevel.MEDIUM]]

        if stable_companies and self.cash > 1000:
            company = random.choice(stable_companies)
            shares_to_buy = int(min(self.cash * 0.2, 2000) / company.price)
            if shares_to_buy > 0:
                success, msg = self.buy_stock(company, shares_to_buy)
                if success:
                    actions.append(f"💎 {self.name} added {shares_to_buy} shares of {company.name} (value play)")

        # Buy treasury bonds for safety during volatile times
        if market_cycle.active_cycle and market_cycle.active_cycle.cycle_type in [
            MarketCycleType.MARKET_CRASH, MarketCycleType.RECESSION
        ]:
            if self.cash > 500:
                bonds_to_buy = int(self.cash * 0.3 / treasury.price)
                if bonds_to_buy > 0:
                    success = self.buy_treasury(treasury, bonds_to_buy)
                    if success:
                        actions.append(f"🛡️ {self.name} bought {bonds_to_buy} treasury bonds for safety")

        return actions

    def _contrarian_strategy(self, companies: Dict[str, Company], treasury: Treasury,
                           market_cycle: 'MarketCycle') -> List[str]:
        """Contrarian: Buy fear, sell greed - opposite of market sentiment"""
        actions = []

        # Moderate leverage usage
        equity = self.calculate_equity(companies, treasury)
        if equity > 0 and self.borrowed_amount < equity * 1.2:
            borrow_amount = min(1500, equity * 1.2 - self.borrowed_amount)
            if borrow_amount > 100:
                success, msg = self.borrow_money(borrow_amount, companies, treasury)
                if success:
                    actions.append(f"🏦 {self.name} borrowed ${borrow_amount:.2f} for contrarian positions")

        # BUY during crashes/recessions (buy fear)
        if market_cycle.active_cycle and market_cycle.active_cycle.cycle_type in [
            MarketCycleType.MARKET_CRASH, MarketCycleType.RECESSION, MarketCycleType.BEAR_MARKET
        ]:
            # Buy the most beaten down stocks
            if self.cash > 1000:
                companies_list = list(companies.values())
                company = random.choice(companies_list)
                shares_to_buy = int(min(self.cash * 0.4, 3500) / company.price)
                if shares_to_buy > 0:
                    success, msg = self.buy_stock(company, shares_to_buy)
                    if success:
                        actions.append(f"🎯 {self.name} bought the dip! {shares_to_buy} shares of {company.name}")

        # SELL during bull markets/recovery (sell greed)
        elif market_cycle.active_cycle and market_cycle.active_cycle.cycle_type in [
            MarketCycleType.BULL_MARKET, MarketCycleType.RECOVERY
        ]:
            # Sell profitable positions
            for company_name, shares in list(self.portfolio.items()):
                if shares > 10:
                    sell_shares = int(shares * 0.5)  # Sell 50% when market is euphoric
                    company = companies[company_name]
                    success, msg = self.sell_stock(company, sell_shares)
                    if success:
                        actions.append(f"💰 {self.name} took profits, sold {sell_shares} shares of {company_name}")

        # Baseline buying: buy random stocks during neutral markets
        else:
            if self.cash > 1000:
                companies_list = list(companies.values())
                company = random.choice(companies_list)
                shares_to_buy = int(min(self.cash * 0.25, 2500) / company.price)
                if shares_to_buy > 0:
                    success, msg = self.buy_stock(company, shares_to_buy)
                    if success:
                        actions.append(f"🎲 {self.name} bought {shares_to_buy} shares of {company.name}")

        return actions


class InvestmentGame:
    """Main game class"""

    def __init__(self):
        self.companies: Dict[str, Company] = {}
        self.treasury = Treasury()
        self.players: List[Player] = []
        self.hedge_funds: List[HedgeFund] = []  # NPC hedge funds
        self.current_turn = 0
        self.round_number = 1
        self.week_number = 1  # Track weeks (each player turn = 1 week)
        self.market_news = MarketNews()  # Market news system
        self.market_cycle = MarketCycle()  # Market cycle system (every 6 months)
        self.pending_news_display: Optional[NewsReport] = None  # News to display this week
        self.weekly_gazette = WeeklyGazette()  # Weekly news outlet
        self.pending_weekly_news: Optional[str] = None  # Weekly news to display

        # Future price pre-calculation (hidden from players)
        # Stores next 2 weeks of calculated prices: {company_name: [week+1 price, week+2 price]}
        self.future_prices: Dict[str, List[float]] = {}

        self._initialize_companies()
        self._initialize_players()
        self._initialize_hedge_funds()

        # Pre-calculate initial future prices
        self._precalculate_future_prices()

    def _initialize_companies(self):
        """Initialize the 5 companies with different industries and liquidity levels"""
        company_data = [
            ("TechCorp", "Technology", 150.0, 8.0, LiquidityLevel.HIGH),
            ("ElectroMax", "Electronics", 85.0, 6.5, LiquidityLevel.MEDIUM),
            ("PharmaCare", "Pharmaceuticals", 220.0, 5.0, LiquidityLevel.LOW),
            ("AutoDrive", "Automotive", 95.0, 7.0, LiquidityLevel.MEDIUM),
            ("EnergyPlus", "Energy", 110.0, 9.0, LiquidityLevel.LOW),
        ]

        for name, industry, price, volatility, liquidity in company_data:
            company = Company(name, industry, price, volatility, liquidity)
            self.companies[name] = company

    def _initialize_players(self):
        """Initialize 1-4 players"""
        print("\n" + "="*60)
        print("Welcome to Investment Simulation!")
        print("="*60)

        # Ask for number of players
        while True:
            try:
                num_players = int(input("\nHow many players? (1-4): ").strip())
                if 1 <= num_players <= 4:
                    break
                else:
                    print("Please enter a number between 1 and 4!")
            except ValueError:
                print("Invalid input! Please enter a number.")

        print(f"\nEnter names for {num_players} player(s):")

        for i in range(num_players):
            while True:
                name = input(f"Player {i+1} name: ").strip()
                if name:
                    self.players.append(Player(name))
                    break
                else:
                    print("Name cannot be empty!")

    def _initialize_hedge_funds(self):
        """Initialize 3 NPC hedge funds with different strategies"""
        self.hedge_funds = [
            HedgeFund("Apex Capital (NPC)", "aggressive", 10000.0),
            HedgeFund("Steadfast Value (NPC)", "value", 10000.0),
            HedgeFund("Contrarian Partners (NPC)", "contrarian", 10000.0)
        ]
        print("\n" + "="*60)
        print("3 AI Hedge Funds have entered the market:")
        print("  - Apex Capital: Aggressive growth strategy")
        print("  - Steadfast Value: Conservative value investing")
        print("  - Contrarian Partners: Contrarian trading")
        print("These NPCs will compete with you in the market!")
        print("="*60)

    def display_market(self):
        """Display current market prices"""
        print("\n" + "="*60)
        print(f"MARKET PRICES - Week {self.week_number}")
        print("="*60)
        for company in self.companies.values():
            print(f"  {company}")
        print()
        print(f"  {self.treasury}")
        print()
        print("  Liquidity: 💧 = Low | 💧💧 = Medium | 💧💧💧 = High")
        print("  (Lower liquidity = higher price impact on large trades)")
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

        # Display weekly gazette news if available
        if self.pending_weekly_news:
            print("\n" + "📰 " + "="*58)
            print("THE BUSINESS GAZETTE - WEEKLY EDITION")
            print("="*60)
            print()
            print("This Week in Business:")
            print("-" * 60)
            print(f"  {self.pending_weekly_news}")
            print("="*60)

    def execute_hedge_fund_trades(self):
        """Execute automated trades for all hedge funds"""
        all_actions = []

        for hedge_fund in self.hedge_funds:
            # Apply interest on borrowed amounts
            interest = hedge_fund.apply_interest()

            # Make automated trades based on strategy
            actions = hedge_fund.make_automated_trade(
                self.companies, self.treasury, self.market_cycle, self.week_number
            )
            all_actions.extend(actions)

        # Display hedge fund actions if any
        if all_actions:
            print("\n" + "🤖" + "="*58)
            print("HEDGE FUND ACTIVITY")
            print("="*60)
            for action in all_actions:
                print(f"  {action}")
            print("="*60)
            input("\nPress Enter to continue...")

    def update_market(self):
        """Update all stock prices"""
        # Execute hedge fund trades first (NPCs react to market conditions)
        self.execute_hedge_fund_trades()

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

        # Recalculate future prices after market update
        self._precalculate_future_prices()

    def _precalculate_future_prices(self):
        """
        Pre-calculate the next 2 weeks of prices for all companies.
        This data is NEVER shown to players, but used for news/research generation.
        """
        import copy

        # Clear existing future prices
        self.future_prices = {}

        # For each company, calculate future prices
        for company_name, company in self.companies.items():
            future_company_prices = []

            # Create a deep copy of game state for simulation
            for week_ahead in range(1, 3):  # Calculate week+1 and week+2
                future_week = self.week_number + week_ahead

                # Start with current price
                if week_ahead == 1:
                    simulated_price = company.price
                else:
                    # Use the previously calculated week+1 price
                    simulated_price = future_company_prices[0]

                # Apply market cycle effects if active or triggering
                cycle_effect = 0.0
                if self.market_cycle.active_cycle:
                    # Check if cycle will still be active
                    weeks_left = self.market_cycle.active_cycle.weeks_remaining - (week_ahead - 1)
                    if weeks_left > 0:
                        cycle_type = self.market_cycle.active_cycle.cycle_type
                        cycle_effect = self._get_cycle_effect(cycle_type, company.industry)

                # Check if a new cycle will trigger at this future week
                elif future_week > 0 and future_week % 24 == 0:
                    # A new cycle would trigger - we don't know which type, so use average effect
                    cycle_effect = 0.0  # Neutral assumption for future cycle triggers

                # Apply cycle effect
                if cycle_effect != 0:
                    simulated_price *= (1 + cycle_effect / 100)
                else:
                    # Random walk if no cycle
                    change_percent = random.uniform(-company.base_volatility, company.base_volatility)
                    simulated_price *= (1 + change_percent / 100)

                # Apply pending news impacts that will occur in this future week
                for impact in self.market_news.pending_impacts:
                    if impact.company_name == company_name:
                        weeks_until = impact.weeks_until_impact - (week_ahead - 1)
                        if weeks_until == 0:
                            # This impact will apply in this future week
                            if impact.is_real:
                                simulated_price *= (1 + impact.impact_magnitude / 100)

                # Ensure price stays positive
                simulated_price = max(0.01, simulated_price)
                future_company_prices.append(simulated_price)

            self.future_prices[company_name] = future_company_prices

    def _get_cycle_effect(self, cycle_type: 'MarketCycleType', industry: str) -> float:
        """Get the average price change effect for a cycle type"""
        if cycle_type == MarketCycleType.BULL_MARKET:
            return random.uniform(3.0, 7.0)
        elif cycle_type == MarketCycleType.BEAR_MARKET:
            return -random.uniform(2.0, 5.0)
        elif cycle_type == MarketCycleType.RECESSION:
            return -random.uniform(4.0, 8.0)
        elif cycle_type == MarketCycleType.INFLATION:
            if industry == "Energy":
                return random.uniform(4.0, 8.0)
            else:
                return -random.uniform(2.0, 4.0)
        elif cycle_type == MarketCycleType.MARKET_CRASH:
            return -random.uniform(8.0, 15.0)
        elif cycle_type == MarketCycleType.RECOVERY:
            return random.uniform(5.0, 10.0)
        elif cycle_type == MarketCycleType.TECH_BOOM:
            if industry in ["Technology", "Electronics"]:
                return random.uniform(7.0, 12.0)
            else:
                return random.uniform(2.0, 4.0)
        return 0.0

    def player_turn(self, player: Player):
        """Execute a single player's turn"""
        print(f"\n\n{'#'*60}")
        print(f"Round {self.round_number} - Week {self.week_number} - {player.name}'s Turn")
        print(f"{'#'*60}")

        # Reset weekly research at start of turn
        player.reset_weekly_research()

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
            self.pending_news_display = self.market_news.generate_news(self.companies, self.week_number, self.future_prices)
        else:
            self.pending_news_display = None

        # Generate weekly gazette news (every week)
        self.pending_weekly_news = self.weekly_gazette.generate_weekly_news(self.companies, self.week_number)

        while True:
            print("\n" + "-"*60)
            print("What would you like to do?")
            print("-"*60)
            print("1. View Market Prices")
            print("2. View My Portfolio")
            print("3. Buy Stocks")
            print("4. Sell Stocks")
            print("5. Buy Treasury Bonds")
            print("6. Research Company (once per week)")
            print("7. Borrow Money (Leverage)")
            print("8. Repay Loan")
            print("9. Save Game")
            print("10. End Turn")
            print("-"*60)

            choice = input("Enter choice (1-10): ").strip()

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
                self._research_company_menu(player)

            elif choice == "7":
                self._borrow_money_menu(player)

            elif choice == "8":
                self._repay_loan_menu(player)

            elif choice == "9":
                filename = input("Enter save filename (default: savegame.json): ").strip()
                if not filename:
                    filename = "savegame.json"
                self.save_game(filename)

            elif choice == "10":
                print(f"\n{player.name} has ended their turn.")
                break

            else:
                print("Invalid choice! Please enter a number between 1 and 10.")

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

                # Calculate effective price with slippage
                slippage_factor = company.calculate_slippage(shares, is_buy=True)
                effective_price = company.price * slippage_factor
                total_cost = effective_price * shares

                print(f"\nQuoted price: ${company.price:.2f} per share")
                print(f"Effective price (with slippage): ${effective_price:.2f} per share")
                print(f"Total cost: ${total_cost:.2f}")

                success, message = player.buy_stock(company, shares)
                print(f"\n{message}")
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

                # Calculate effective price with slippage
                slippage_factor = company.calculate_slippage(shares, is_buy=False)
                effective_price = company.price * slippage_factor
                total_value = effective_price * shares

                print(f"\nQuoted price: ${company.price:.2f} per share")
                print(f"Effective price (with slippage): ${effective_price:.2f} per share")
                print(f"Total value: ${total_value:.2f}")

                success, message = player.sell_stock(company, shares)
                print(f"\n{message}")
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

    def _research_company_menu(self, player: Player):
        """Menu for researching a company to get hints"""
        print("\n" + "="*60)
        print("RESEARCH COMPANY")
        print("="*60)

        if player.researched_this_week:
            print("You've already researched a company this week!")
            print("You can research one company per week.")
            return

        print("Select a company to research (you'll receive a strategic hint):")
        print()

        companies_list = list(self.companies.values())
        for i, company in enumerate(companies_list, 1):
            # Show if player has researched this company before
            research_count = len(player.research_history.get(company.name, []))
            history_marker = f" [Researched {research_count}x]" if research_count > 0 else ""
            print(f"{i}. {company.name} ({company.industry}){history_marker}")
        print("0. Cancel")

        try:
            choice = int(input("\nSelect company to research (0 to cancel): "))
            if choice == 0:
                return

            if 1 <= choice <= len(companies_list):
                company = companies_list[choice - 1]

                print("\n" + "="*60)
                print(f"RESEARCH REPORT: {company.name}")
                print("="*60)

                # Get future price for next week (hidden from player, used for hint generation)
                future_price = self.future_prices.get(company.name, [None])[0]
                hint = player.research_company(company, future_price)
                print(f"\n🔍 {hint}")

                print("\n" + "="*60)
                print("Note: Research insights are usually reliable but not guaranteed.")
                print("="*60)

                # Show previous research if any
                if len(player.research_history[company.name]) > 1:
                    print(f"\nPrevious research on {company.name}:")
                    for i, old_hint in enumerate(player.research_history[company.name][:-1], 1):
                        print(f"  {i}. {old_hint}")

                input("\nPress Enter to continue...")
            else:
                print("Invalid choice!")

        except ValueError:
            print("Invalid input!")

    def save_game(self, filename: str = "savegame.json") -> bool:
        """Save game state to JSON file"""
        try:
            game_state = {
                'current_turn': self.current_turn,
                'round_number': self.round_number,
                'week_number': self.week_number,
                'companies': {name: company.to_dict() for name, company in self.companies.items()},
                'treasury': self.treasury.to_dict(),
                'players': [player.to_dict() for player in self.players],
                'hedge_funds': [hf.to_dict() for hf in self.hedge_funds],
                'market_news': self.market_news.to_dict(),
                'market_cycle': self.market_cycle.to_dict(),
                'pending_news_display': self.pending_news_display.to_dict() if self.pending_news_display else None,
                'weekly_gazette': self.weekly_gazette.to_dict(),
                'pending_weekly_news': self.pending_weekly_news,
                'future_prices': self.future_prices
            }

            with open(filename, 'w') as f:
                json.dump(game_state, f, indent=2)

            print(f"\n✅ Game saved successfully to {filename}!")
            return True

        except Exception as e:
            print(f"\n❌ Error saving game: {e}")
            return False

    @staticmethod
    def load_game(filename: str = "savegame.json") -> Optional['InvestmentGame']:
        """Load game state from JSON file"""
        try:
            with open(filename, 'r') as f:
                game_state = json.load(f)

            # Create new game instance
            game = InvestmentGame.__new__(InvestmentGame)

            # Restore basic game state
            game.current_turn = game_state['current_turn']
            game.round_number = game_state['round_number']
            game.week_number = game_state['week_number']

            # Restore companies
            game.companies = {
                name: Company.from_dict(data)
                for name, data in game_state['companies'].items()
            }

            # Restore treasury
            game.treasury = Treasury.from_dict(game_state['treasury'])

            # Restore players
            game.players = [Player.from_dict(data) for data in game_state['players']]

            # Restore hedge funds
            game.hedge_funds = [HedgeFund.from_dict(data) for data in game_state['hedge_funds']]

            # Restore market news
            game.market_news = MarketNews.from_dict(game_state['market_news'])

            # Restore market cycle
            game.market_cycle = MarketCycle.from_dict(game_state['market_cycle'])

            # Restore pending news display
            if game_state['pending_news_display']:
                game.pending_news_display = NewsReport.from_dict(game_state['pending_news_display'])
            else:
                game.pending_news_display = None

            # Restore weekly gazette
            game.weekly_gazette = WeeklyGazette.from_dict(game_state.get('weekly_gazette', {'weekly_news_history': []}))
            game.pending_weekly_news = game_state.get('pending_weekly_news', None)

            # Restore future prices (or recalculate if not present in save file)
            if 'future_prices' in game_state:
                game.future_prices = game_state['future_prices']
            else:
                # Old save file - recalculate future prices
                game.future_prices = {}
                game._precalculate_future_prices()

            print(f"\n✅ Game loaded successfully from {filename}!")
            return game

        except FileNotFoundError:
            print(f"\n❌ Save file '{filename}' not found!")
            return None
        except Exception as e:
            print(f"\n❌ Error loading game: {e}")
            return None

    def display_leaderboard(self):
        """Display current standings"""
        print("\n" + "="*60)
        print("LEADERBOARD")
        print("="*60)

        # Calculate net worth for all players and hedge funds
        standings = []
        for player in self.players:
            net_worth = player.calculate_net_worth(self.companies, self.treasury)
            standings.append((player.name, net_worth, False))

        for hedge_fund in self.hedge_funds:
            net_worth = hedge_fund.calculate_net_worth(self.companies, self.treasury)
            standings.append((hedge_fund.name, net_worth, True))

        # Sort by net worth descending
        standings.sort(key=lambda x: x[1], reverse=True)

        for rank, (name, net_worth, is_npc) in enumerate(standings, 1):
            npc_marker = " 🤖" if is_npc else ""
            print(f"{rank}. {name}{npc_marker}: ${net_worth:.2f}")

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

            # Increment week after all players have taken their turn
            self.week_number += 1

            # End of round
            print("\n" + "="*60)
            print(f"End of Round {self.round_number}")
            print("="*60)

            # Enforce margin calls BEFORE market prices change
            print("\nProcessing margin calls...")
            margin_call_actions = []
            for player in self.players:
                if player.check_margin_call(self.companies, self.treasury):
                    actions = player.force_liquidate_margin_call(self.companies, self.treasury)
                    margin_call_actions.extend(actions)

            if margin_call_actions:
                print("\n" + "⚠️ "*30)
                print("AUTOMATIC MARGIN CALL LIQUIDATIONS")
                print("⚠️ "*30)
                for action in margin_call_actions:
                    print(action)
                print("="*60)
                input("\nPress Enter to continue...")

            # Update market prices
            print("\nUpdating market prices...")
            self.update_market()

            # Show leaderboard
            self.display_leaderboard()

            # Automatically continue to next round
            self.round_number += 1
            input("\nPress Enter to continue to next round...")


        # Final standings
        print("\n" + "="*60)
        print("GAME OVER - Final Standings")
        print("="*60)
        self.display_leaderboard()
        print("\nThanks for playing!")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("Investment Simulation Game")
    print("="*60)
    print("\n1. Start New Game")
    print("2. Load Saved Game")
    print("3. Exit")
    print()

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        game = InvestmentGame()
        game.play()
    elif choice == "2":
        filename = input("Enter save filename (default: savegame.json): ").strip()
        if not filename:
            filename = "savegame.json"
        game = InvestmentGame.load_game(filename)
        if game:
            game.play()
    elif choice == "3":
        print("Goodbye!")
        return
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
