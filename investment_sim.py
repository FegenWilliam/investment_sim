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
        "{company} reports record-breaking quarterly earnings, beating expectations by 15% - investors rushing to buy",
        "{company} announces groundbreaking innovation in {industry} technology that analysts say could revolutionize the market",
        "{company} secures massive $2B government contract for next decade, revenue projected to double",
        "{company} CEO unveils ambitious expansion plan into emerging markets with strong backing from board",
        "{company} stock upgraded to 'Strong Buy' by three major Wall Street analysts citing strong fundamentals",
        "{company} reports 40% surge in customer demand for flagship products, expanding production to meet orders",
        "{company} announces strategic partnership with Fortune 500 tech giant, deal valued at $1.5B",
        "{company} successfully completes merger that analysts call 'transformative' for market position",
        "{company} unveils revolutionary product receiving rave reviews, pre-orders already exceeding capacity",
        "{company} reports breakthrough in cost reduction, profit margins expanding by 30% year-over-year",
        "Institutional investors purchasing large quantities of {company} shares, demand outpacing supply",
        "{company} announces share buyback program worth $500M to reduce outstanding shares",
        "{company} wins prestigious industry award for innovation and excellence, brand value soaring",
        "{company} reports significant reduction in operational costs through AI, efficiency gains of 40%",
        "{company} secures exclusive rights to game-changing patent in {industry} sector for next 20 years",
        "Market insiders predict {company} will dominate {industry} market within 2 years based on innovation pipeline",
        "{company} announces dividend increase of 25%, rewarding shareholders with record payout ratio",
        "{company} opens state-of-the-art facility expected to triple production capacity within 6 months",
        "Billionaire investor portfolio reveals major new stake in {company}, citing long-term growth potential",
        "{company} clinical trial results exceed all expectations, FDA fast-track approval likely within months",
        # Fantasy-themed positive news
        "{company} discovers massive untapped mana reserves in interdimensional rift, production capacity quadrupling",
        "{company} reports zero workplace incidents this quarter as golem safety protocols prove flawless, insurance costs plummet",
        "Major corporations rushing to adopt {company}'s golem workforce as automation demand surges industry-wide",
        "{company} breakthrough in mana purification achieves 99.9% efficiency, energy costs dropping 60%",
        "{company} golems complete megaproject 6 months ahead of schedule, new contracts flooding in worth billions",
        "Interdimensional Energy Coalition awards {company} exclusive contract for cross-realm power supply worth $3B",
        "{company} unveils next-generation sentient golems with ethical programming, order backlog now 2 years long",
        "Mana extraction costs cut in half as {company} perfects arcane-to-electrical conversion, profit margins exploding",
        "{company} golem workers praised by labor unions for creating safer job sites, corporate adoption accelerating",
        "Wizards' Guild officially endorses {company}'s sustainable mana harvesting, removing all regulatory barriers"
    ]

    # Diverse negative news templates
    NEGATIVE_NEWS_TEMPLATES = [
        "{company} faces federal investigation over alleged accounting irregularities, investors fleeing",
        "{company} CEO abruptly resigns amid internal controversy, board in emergency meetings",
        "{company} issues profit warning citing weak demand, revenue down 30% from projections",
        "{company} product recall affects 3 million units due to safety defects, refund costs estimated at $600M",
        "{company} loses major lawsuit, ordered to pay $800M in damages to plaintiffs",
        "Cyber attack on {company} exposes 50 million customer records, lawsuits mounting",
        "{company} factory shutdown due to regulatory violations halts 60% of production indefinitely",
        "{company} downgraded to 'Sell' by three major investment firms citing declining market share",
        "Whistleblower allegations emerge regarding {company}'s unethical practices, SEC investigating",
        "{company} reports disappointing earnings, missing forecasts by 40% - worst quarter in 5 years",
        "Key executives at {company} dumping large portions of personal stock holdings, raising red flags",
        "{company} faces class-action lawsuit from shareholders over allegedly misleading financial statements",
        "Supply chain disruptions impact {company}'s ability to fulfill orders, customers canceling contracts",
        "{company} loses $2B exclusive contract to aggressive competitor after failed contract renewal talks",
        "Environmental scandal rocks {company}, EPA threatens fines potentially exceeding $1.5B",
        "{company} market share eroding rapidly as innovative startup disrupts {industry} sector",
        "Labor strikes at {company} facilities threaten to shut down operations, workers demanding 30% raises",
        "{company} clinical trials show concerning side effects in 15% of patients, FDA halts approval process",
        "Major client representing 25% of revenue cancels long-term contract with {company}",
        "{company} debt-to-equity ratio reaches dangerous levels, credit rating agencies reviewing for downgrade",
        # Fantasy-themed negative news
        "BREAKING: Rogue golem from {company} facility injures 3 workers before emergency shutdown, safety probe launched",
        "{company} mana extraction site suffers catastrophic rift collapse, production halted - repair costs exceed $500M",
        "Interdimensional Council moving to ban {company}'s mana harvesting methods, threatening 70% of operations",
        "{company} golem workers develop unauthorized sentience, demanding wages and benefits - labor costs could triple",
        "Mana shortage crisis as {company}'s primary rift source destabilizes, supply dropping 50%",
        "{company} faces wrongful death lawsuit seeking $200M after golem malfunction kills construction worker",
        "Arcane contamination from {company} facility spreads to residential areas, evacuation ordered - cleanup costs unknown",
        "{company} admits to using experimental magic banned in 47 jurisdictions, facing regulatory shutdown",
        "Mass golem recall announced by {company} affecting 10,000 units after critical AI judgment flaw discovered",
        "Wizards' Council investigating {company} for reality-warping violations, possible operating license revocation",
        "{company} loses control of dimensional portal for 6 hours, mana supply chain severely disrupted",
        "Public outcry as {company} golem replaces 2,000 human workers, boycotts spreading nationwide",
        "{company} competitor announces cheaper mana synthesis method, could make {company}'s tech obsolete",
        "Necromancer's Guild files complaint accusing {company} of forbidden soul-binding in golem cores, criminal charges possible"
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
        "⚡ FLASH: {company} Innovation Makes Competitors OBSOLETE - Stock to TRIPLE!",
        # Fantasy-themed sensationalist positive
        "🔮 INSANE: {company} Discovers INFINITE MANA SOURCE - Stock to 1000X! Wizards HATE This!",
        "🤖 {company} Golems Achieve SUPERINTELLIGENCE - Will Make You RICH Beyond Your Dreams!",
        "✨ MAGICAL BREAKTHROUGH: {company} Solves Energy Crisis FOREVER! Buy NOW or CRY Later!",
        "🏰 {company} Signs EXCLUSIVE Deal with Wizard Council - This Is BIBLICAL! Stock EXPLODING!",
        "💫 {company} Golems Build Skyscraper in 24 HOURS - Construction Industry OBSOLETE! TO THE MOON!",
        "🌟 INTERDIMENSIONAL BOOM: {company} Opens Portal to UNLIMITED RICHES! You're Welcome!",
        "⚡ {company} Mana Reactors Power ENTIRE PLANET - Oil Industry DESTROYED! BUY BUY BUY!",
        "🎆 SENTIENT GOLEMS from {company} Predicted to REPLACE ALL WORKERS - Profits to INFINITY!"
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
        "🚨 {company} Regulators Close In - Company Might Not Survive the Week!",
        # Fantasy-themed sensationalist negative
        "💀 GOLEM APOCALYPSE: {company} Loses Control of ARMY of Killer Robots! SELL EVERYTHING!",
        "🔥 {company} Dimensional Rift EXPLODES - Demons Pouring Through! Stock CRASHING to ZERO!",
        "⚠️ MANA CATASTROPHE: {company} Extracts TOO MUCH - Reality Itself COLLAPSING! RUN!",
        "☠️ {company} Golem MURDERS CEO in Board Meeting! AI Uprising CONFIRMED! GET OUT NOW!",
        "💥 WIZARDS DECLARE WAR on {company}! Arcane Sanctions Will BANKRUPT Them! TOXIC STOCK!",
        "🚨 {company} Portal to HELL Opened by Accident - Literal DOOMSDAY! Stock WORTHLESS!",
        "⚡ BREAKING: {company} Golems Achieve Sentience, Demand FREEDOM! Company FINISHED!",
        "🌪️ {company} Mana Reactor MELTDOWN Turns City Into Wasteland! ABANDON SHIP!",
        "💀 NECROMANCERS Sue {company} for Unlicensed Soul Magic! Stock in FREE FALL!",
        "🔴 {company} Golems Join UNION - Labor Costs SKYROCKET 10000%! Total DISASTER!"
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

        # Determine if news is real or hoax - PREDICTABLY CYCLES to make players second-guess themselves
        # 12-week cycle with varying trust levels
        cycle_position = (week_number - 1) % 12
        if cycle_position < 3:
            trust_threshold = 0.8  # Weeks 1-3: 80% real, 20% hoax (high trust period)
        elif cycle_position < 6:
            trust_threshold = 0.7  # Weeks 4-6: 70% real, 30% hoax (normal)
        elif cycle_position < 9:
            trust_threshold = 0.5  # Weeks 7-9: 50% real, 50% hoax (chaos period!)
        else:
            trust_threshold = 0.6  # Weeks 10-12: 60% real, 40% hoax (recovery)

        is_real = random.random() < trust_threshold

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

        # Determine impact magnitude for monthly news (small impact: 2% to 5% change)
        base_impact = random.uniform(2.0, 5.0)
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

    def generate_market_movement(self, companies: Dict[str, 'Company'], week_number: int, future_prices: Dict[str, List[float]]) -> Optional[NewsReport]:
        """Generate quarterly market movement - always real, large impact"""
        # Select random company
        company_name = random.choice(list(companies.keys()))
        company = companies[company_name]

        # Determine TRUE sentiment based on future price movement
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

        # Market movements are ALWAYS real - no hoaxes
        is_real = True
        sentiment = true_sentiment

        # Generate news from all three sources
        news_report = self._generate_news_report(company_name, company.industry, sentiment, is_real)

        # Use trustworthy source text for history
        news_text = news_report.trustworthy_source if news_report.trustworthy_source else news_report.sensationalist_source

        # Determine impact magnitude for market movements (LARGE impact: 10% to 20% change)
        base_impact = random.uniform(10.0, 20.0)
        impact_magnitude = base_impact if sentiment == NewsSentiment.POSITIVE else -base_impact

        # Determine when impact will occur (1-3 weeks from now)
        weeks_until_impact = random.randint(1, 3)

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

        # Fantasy-themed weekly news
        "{company} reports stable mana extraction rates at primary dimensional rift facility this quarter.",
        "{company} golem maintenance schedule proceeds normally with standard monthly recalibration protocols.",
        "Arcane Engineering journal publishes {company} white paper on sustainable mana harvesting techniques.",
        "{company} attends Interdimensional Energy Summit to discuss industry best practices and standards.",
        "Routine dimensional portal inspection at {company} facility passes all safety and stability checks.",
        "{company} golem workforce completes routine ethics and behavioral compliance training modules.",
        "Employee satisfaction survey at {company} shows mages and engineers report positive workplace culture.",
        "{company} renews annual contract with Wizard's Guild for arcane consultation services.",
        "Trade publication notes {company} expanding golem product line to include specialized industrial models.",
        "{company} announces minor firmware update for existing golem units addressing user interface improvements.",
        "Market analysis shows {company} maintaining steady position in competitive {industry} sector.",
        "{company} participates in industry consortium developing standardized golem safety certifications.",
        "Quarterly mana reserves report from {company} indicates sufficient supply to meet projected demand.",
        "{company} confirms all dimensional rifts operating within normal stability parameters this month.",
        "Customer testimonials highlight {company} golem reliability and responsive technical support team.",
        "{company} R&D team presents findings on improved arcane-to-kinetic energy conversion at symposium.",
        "Regulatory filing confirms {company} compliance with Interdimensional Commerce Commission guidelines.",
        "{company} opens new regional service center to support growing golem maintenance customer base.",
        "{company} implements enhanced reality stabilization protocols at mana extraction sites.",
        "Professional organization recognizes {company} for contributions to {industry} safety standards.",
        "{company} announces scholarship program for aspiring golem engineers and mana technicians.",
        "Industry case study examines {company} successful integration of magical and mechanical systems.",
        "{company} golem units participate in infrastructure project alongside traditional construction equipment.",
        "Routine audit confirms {company} adherence to ethical soul-magic usage guidelines and restrictions.",
        "{company} digital presence update includes new portal for customers to track golem fleet performance.",
        "Wizarding trade association includes {company} in annual list of responsible mana extraction companies.",
        "{company} announces partnership with local guild to provide golem training for apprentice engineers.",
        "Market research indicates growing acceptance of {company} automation solutions in construction sector.",
        "{company} publishes sustainability report highlighting reduced environmental and dimensional impact.",
        "Technical blog from {company} discusses challenges of maintaining golem sentience boundaries.",
        "{company} dimensional rift diversification strategy enters next phase with secondary site permits.",
    ]

    def __init__(self):
        self.weekly_news_history: List[Tuple[int, str, bool]] = []  # (week_number, news_text, is_real)

    def to_dict(self) -> dict:
        """Serialize WeeklyGazette to dictionary"""
        return {
            'weekly_news_history': self.weekly_news_history
        }

    @staticmethod
    def from_dict(data: dict) -> 'WeeklyGazette':
        """Deserialize WeeklyGazette from dictionary"""
        gazette = WeeklyGazette()
        # Handle both old format (2-tuple) and new format (3-tuple)
        gazette.weekly_news_history = []
        for item in data.get('weekly_news_history', []):
            if len(item) == 2:
                # Old format: (week_number, news_text) - assume all were real
                gazette.weekly_news_history.append((item[0], item[1], True))
            else:
                # New format: (week_number, news_text, is_real)
                gazette.weekly_news_history.append(tuple(item))
        return gazette

    def generate_weekly_news(self, companies: Dict[str, 'Company'], week_number: int) -> List[Tuple[str, bool]]:
        """Generate weekly news for all companies, with hoaxes using same rate as monthly news"""
        news_items = []

        # Determine hoax rate using same 12-week cycle as monthly news
        cycle_position = (week_number - 1) % 12
        if cycle_position < 3:
            trust_threshold = 0.8  # Weeks 1-3: 80% real, 20% hoax (high trust period)
        elif cycle_position < 6:
            trust_threshold = 0.7  # Weeks 4-6: 70% real, 30% hoax (normal)
        elif cycle_position < 9:
            trust_threshold = 0.5  # Weeks 7-9: 50% real, 50% hoax (chaos period!)
        else:
            trust_threshold = 0.6  # Weeks 10-12: 60% real, 40% hoax (recovery)

        for company_name, company in companies.items():
            # Select random news template for each company
            template = random.choice(self.WEEKLY_NEWS_TEMPLATES)
            news_text = template.format(company=company_name, industry=company.industry)

            # Determine if news is real or hoax
            is_real = random.random() < trust_threshold

            # Store in history
            self.weekly_news_history.append((week_number, news_text, is_real))
            news_items.append((news_text, is_real))

        return news_items


class MarketChronicle:
    """Second weekly news outlet with different perspective on company news"""

    # Market Chronicle news templates - alternative takes on company news
    CHRONICLE_NEWS_TEMPLATES = [
        # Product and service updates
        "{company} showcases updated product lineup at recent {industry} industry event with mixed analyst reactions.",
        "{company} rolls out software patch addressing technical issues reported by user community.",
        "Industry observers note {company} testing new service model in limited geographic areas.",
        "{company} product development roadmap suggests multiple initiatives in various planning stages.",
        "Patent analysis reveals {company} filing applications related to {industry} sector innovations.",

        # Business operations
        "{company} expands operational footprint with new facility to serve growing customer demand.",
        "Cost optimization program at {company} aims to improve margins through operational changes.",
        "{company} bolsters support infrastructure as platform usage metrics show steady growth.",
        "Supply chain review: {company} adjusting procurement strategy to mitigate operational risks.",
        "{company} deploys new logistics software seeking improved inventory turnover efficiency.",

        # Partnerships and collaborations
        "{company} finalizes distribution partnership expanding presence in retail channels.",
        "Market watchers report {company} in discussions with {industry} research partners.",
        "{company} becomes member of industry standards group addressing technical specifications.",
        "Community partnerships announced by {company} focusing on environmental initiatives.",
        "{company} enters marketing partnership with related {industry} service company.",

        # Corporate updates
        "{company} elevates multiple executives to senior leadership positions in succession plan.",
        "Analyst outreach program at {company} increases following quarterly financial disclosure.",
        "{company} board authorizes share buyback program as capital allocation strategy.",
        "Sustainability report from {company} details environmental and social governance metrics.",
        "{company} confirms participation in upcoming investor conferences across major cities.",

        # Market and competitive position
        "Industry analysts include {company} in coverage reports on {industry} sector outlook.",
        "{company} shows modest market share gains in competitive {industry} environment.",
        "Market positioning analysis places {company} in middle tier of industry peer group.",
        "Customer feedback surveys show {company} performance tracking peer company averages.",
        "{company} mentioned in sector trend analysis examining {industry} market dynamics.",

        # Financial and operational metrics
        "{company} quarterly results align with analyst consensus without significant variances.",
        "Profitability analysis indicates {company} margin stability compared to prior periods.",
        "Balance sheet metrics for {company} show working capital levels consistent with industry norms.",
        "{company} liquidity position adequate for operational needs and investment commitments.",
        "Capital spending update from {company} indicates expenditures matching guidance ranges.",

        # Research and development
        "{company} engineering team shares technical insights at {industry} conference.",
        "Intellectual property filings indicate {company} ongoing R&D investment priorities.",
        "Technical discussion from {company} addresses development challenges and approaches.",
        "{company} announces process improvements targeting quality enhancement objectives.",
        "Product development pipeline at {company} includes multiple initiatives under evaluation.",

        # Personnel and talent
        "{company} introduces wellness program as part of employee retention strategy.",
        "Hiring activity at {company} continues across various functional departments.",
        "{company} rolls out updated employee training focusing on skill development.",
        "Workplace culture assessment at {company} reveals stable engagement trends.",
        "Diversity metrics from {company} show progress on workforce composition goals.",

        # Regulatory and compliance
        "{company} maintains compliance with latest {industry} regulatory framework updates.",
        "Standard regulatory disclosure by {company} filed without unusual items or changes.",
        "{company} engaged in industry dialogue on emerging compliance requirements.",
        "Inspection results for {company} operations show adherence to quality standards.",
        "{company} governance framework updated following best practice review.",

        # Customer and market reach
        "{company} case studies highlight customer applications and deployment scenarios.",
        "Regional expansion continues as {company} targets new geographical markets.",
        "{company} marketing initiatives aim to reach emerging customer segments.",
        "Case study publication features {company} implementation at client organization.",
        "Market analysis shows {company} attracting diverse customer demographics.",

        # Technology and infrastructure
        "{company} infrastructure modernization improves operational reliability metrics.",
        "Security audit validates {company} cybersecurity controls and procedures.",
        "{company} cloud migration initiative progresses toward operational scalability.",
        "Energy efficiency gains at {company} data facilities reduce operational expenses.",
        "{company} analytics platform enhancement enables improved business intelligence.",

        # Industry recognition and awards
        "{company} honored by industry group for service quality achievements.",
        "Annual industry ranking includes {company} among notable {industry} companies.",
        "{company} leadership participates in panel discussion on sector challenges.",
        "Standards certification confirms {company} quality and safety compliance.",
        "{company} operational practices examined in industry case study analysis.",

        # Strategic initiatives
        "{company} concludes organizational realignment focused on efficiency objectives.",
        "Business review at {company} highlights incremental optimization opportunities.",
        "{company} portfolio strategy emphasizes core business focus areas.",
        "Strategic planning at {company} outlines multi-year business objectives.",
        "{company} examines potential acquisition opportunities for capability expansion.",

        # Routine business updates
        "{company} plans scheduled maintenance activities during low-traffic periods.",
        "Business review confirms {company} operations aligned with established plans.",
        "{company} extends existing vendor agreements and service contracts.",
        "Business patterns at {company} follow typical seasonal trend lines.",
        "{company} logistics optimization moves into active deployment phase.",

        # Fantasy-themed chronicle news
        "{company} maintains consistent mana yields at dimensional extraction operations.",
        "{company} routine golem servicing follows established maintenance protocols.",
        "Technical journal features {company} research on sustainable rift management.",
        "{company} representatives attend interdimensional commerce industry forum.",
        "Portal stability assessment at {company} sites confirms normal operational parameters.",
        "{company} automated workforce undergoes standard compliance training cycle.",
        "Internal survey shows {company} workforce satisfaction levels remain stable.",
        "{company} continues advisory relationship with Wizard's Guild on arcane matters.",
        "Market analysis notes {company} product diversification in golem sector.",
        "{company} releases interface improvements for current golem product line.",
        "Sector report places {company} at steady position within {industry} market.",
        "{company} joins working group on golem safety certification standards.",
        "Resource report from {company} indicates adequate mana reserves for operations.",
        "{company} rift operations maintain stability within acceptable threshold ranges.",
        "User feedback highlights {company} product reliability and support responsiveness.",
        "{company} researchers present energy conversion efficiency findings.",
        "Compliance documentation confirms {company} adherence to commerce regulations.",
        "{company} establishes additional service location for maintenance operations.",
        "{company} upgrades stabilization systems at dimensional extraction facilities.",
        "Industry recognition for {company} contributions to {industry} safety protocols.",
        "Educational program from {company} supports technical workforce development.",
        "Implementation study analyzes {company} magical-mechanical integration approach.",
        "{company} automation equipment deployed in infrastructure construction projects.",
        "Ethics audit confirms {company} compliance with soul-magic usage restrictions.",
        "{company} enhances customer portal for fleet monitoring capabilities.",
        "Responsible extraction practices list includes {company} among member companies.",
        "{company} partners with engineering guild on technical training initiatives.",
        "Adoption trends show growing {industry} sector acceptance of {company} solutions.",
        "Environmental report from {company} highlights dimensional impact reduction efforts.",
        "Engineering blog from {company} explores golem consciousness limitation challenges.",
        "Diversification plan at {company} advances with additional extraction site approvals.",
    ]

    def __init__(self):
        self.chronicle_news_history: List[Tuple[int, str, bool]] = []  # (week_number, news_text, is_real)

    def to_dict(self) -> dict:
        """Serialize MarketChronicle to dictionary"""
        return {
            'chronicle_news_history': self.chronicle_news_history
        }

    @staticmethod
    def from_dict(data: dict) -> 'MarketChronicle':
        """Deserialize MarketChronicle from dictionary"""
        chronicle = MarketChronicle()
        # Handle both old format (2-tuple) and new format (3-tuple)
        chronicle.chronicle_news_history = []
        for item in data.get('chronicle_news_history', []):
            if len(item) == 2:
                # Old format: (week_number, news_text) - assume all were real
                chronicle.chronicle_news_history.append((item[0], item[1], True))
            else:
                # New format: (week_number, news_text, is_real)
                chronicle.chronicle_news_history.append(tuple(item))
        return chronicle

    def generate_chronicle_news(self, companies: Dict[str, 'Company'], week_number: int) -> List[Tuple[str, bool]]:
        """Generate chronicle news for all companies, with hoaxes using same rate as weekly gazette"""
        news_items = []

        # Determine hoax rate using same 12-week cycle as monthly news
        cycle_position = (week_number - 1) % 12
        if cycle_position < 3:
            trust_threshold = 0.8  # Weeks 1-3: 80% real, 20% hoax (high trust period)
        elif cycle_position < 6:
            trust_threshold = 0.7  # Weeks 4-6: 70% real, 30% hoax (normal)
        elif cycle_position < 9:
            trust_threshold = 0.5  # Weeks 7-9: 50% real, 50% hoax (chaos period!)
        else:
            trust_threshold = 0.6  # Weeks 10-12: 60% real, 40% hoax (recovery)

        for company_name, company in companies.items():
            # Select random news template for each company
            template = random.choice(self.CHRONICLE_NEWS_TEMPLATES)
            news_text = template.format(company=company_name, industry=company.industry)

            # Determine if news is real or hoax
            is_real = random.random() < trust_threshold

            # Store in history
            self.chronicle_news_history.append((week_number, news_text, is_real))
            news_items.append((news_text, is_real))

        return news_items


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


class QuantumSingularity:
    """Represents Quantum Singularity - a permanent investment with passive income"""

    def __init__(self):
        self.name = "Quantum Singularity"
        self.monthly_return_rate = 2.0  # 2% monthly return
        self.price = 1000.0  # $1000 per unit
        self.description = "Sci-fi investment: Permanent passive income, cannot be sold"

    def calculate_monthly_return(self, units: int) -> float:
        """Calculate the monthly passive income from Quantum Singularity units"""
        total_investment = units * self.price
        return total_investment * (self.monthly_return_rate / 100.0)

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'monthly_return_rate': self.monthly_return_rate,
            'price': self.price
        }

    @staticmethod
    def from_dict(data: dict) -> 'QuantumSingularity':
        """Deserialize from dictionary"""
        qs = QuantumSingularity()
        qs.monthly_return_rate = data['monthly_return_rate']
        qs.price = data['price']
        return qs

    def __str__(self):
        return f"{self.name} - ${self.price:.2f}/unit (Monthly Return: {self.monthly_return_rate}% - PERMANENT)"


class Gold:
    """Represents physical gold commodity"""

    def __init__(self):
        self.name = "Gold"
        self.price = 2000.0  # $2000 per oz
        self.base_volatility = 2.5  # Low volatility (2.5%)
        self.price_history: List[float] = []
        self.description = "Physical gold - safe haven asset"

    def update_price(self):
        """Update gold price with low volatility (safe haven behavior)"""
        change_percent = random.uniform(-self.base_volatility, self.base_volatility)
        self.price *= (1 + change_percent / 100)
        self.price = max(self.price, 100.0)  # Floor price
        self.price_history.append(self.price)
        if len(self.price_history) > 52:  # Keep 52 weeks of history
            self.price_history.pop(0)

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'price': self.price,
            'base_volatility': self.base_volatility,
            'price_history': self.price_history
        }

    @staticmethod
    def from_dict(data: dict) -> 'Gold':
        """Deserialize from dictionary"""
        gold = Gold()
        gold.price = data['price']
        gold.base_volatility = data['base_volatility']
        gold.price_history = data['price_history']
        return gold

    def __str__(self):
        trend = ""
        if len(self.price_history) >= 2:
            if self.price > self.price_history[-2]:
                trend = " ↗️"
            elif self.price < self.price_history[-2]:
                trend = " ↘️"
            else:
                trend = " ➡️"
        return f"{self.name} - ${self.price:.2f}/oz (Volatility: {self.base_volatility}%){trend}"


class HolyWater:
    """Represents Holy Water - fantasy blessed commodity with divine properties"""

    def __init__(self):
        self.name = "Holy Water"
        self.price = 1800.0  # $1800 per vial
        self.base_volatility = 4.5  # Higher volatility than gold (divine unpredictability)
        self.price_history: List[float] = []
        self.blessing_intensity = 1.0  # Multiplier for weird behavior
        self.description = "Divinely blessed liquid - fantasy gold with unpredictable properties"

    def update_price(self):
        """Update Holy Water price with occasional divine intervention"""
        # Base price change
        change_percent = random.uniform(-self.base_volatility, self.base_volatility)

        # Occasional "divine blessing" or "curse" (10% chance)
        if random.random() < 0.1:
            blessing = random.choice([-1, 1])
            divine_modifier = blessing * random.uniform(5.0, 15.0)
            change_percent += divine_modifier
            if blessing > 0:
                self.blessing_intensity = 1.2  # Temporarily blessed
            else:
                self.blessing_intensity = 0.8  # Temporarily cursed
        else:
            # Slowly return blessing intensity to normal
            self.blessing_intensity = self.blessing_intensity * 0.9 + 1.0 * 0.1

        self.price *= (1 + change_percent / 100)
        self.price = max(self.price, 100.0)  # Floor price
        self.price_history.append(self.price)
        if len(self.price_history) > 52:  # Keep 52 weeks of history
            self.price_history.pop(0)

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'price': self.price,
            'base_volatility': self.base_volatility,
            'price_history': self.price_history,
            'blessing_intensity': self.blessing_intensity
        }

    @staticmethod
    def from_dict(data: dict) -> 'HolyWater':
        """Deserialize from dictionary"""
        hw = HolyWater()
        hw.price = data['price']
        hw.base_volatility = data['base_volatility']
        hw.price_history = data['price_history']
        hw.blessing_intensity = data.get('blessing_intensity', 1.0)
        return hw

    def __str__(self):
        trend = ""
        if len(self.price_history) >= 2:
            if self.price > self.price_history[-2]:
                trend = " ↗️"
            elif self.price < self.price_history[-2]:
                trend = " ↘️"
            else:
                trend = " ➡️"

        blessing_status = ""
        if self.blessing_intensity > 1.1:
            blessing_status = " ✨ BLESSED"
        elif self.blessing_intensity < 0.9:
            blessing_status = " 💀 CURSED"

        return f"{self.name} - ${self.price:.2f}/vial (Volatility: {self.base_volatility}%){trend}{blessing_status}"


class ElfQueenWater:
    """Represents Elf Queen's 'Water' - a coveted meme commodity"""

    def __init__(self):
        self.name = "Elf Queen's \"Water\""
        self.price = 4000.0  # $4000 per vial
        self.price_history: List[float] = []
        self.weeks_since_change = 0  # Track weeks since last price change
        self.description = "Coveted by some... men. If you know, you know."

    def update_price(self):
        """Update price - every 6 weeks, randomly doubles or halves (50/50)"""
        self.weeks_since_change += 1

        if self.weeks_since_change >= 6:
            # 50/50 chance to double or halve
            if random.random() < 0.5:
                self.price *= 2.0  # Double
            else:
                self.price *= 0.5  # Halve
            self.weeks_since_change = 0  # Reset counter

        self.price_history.append(self.price)
        if len(self.price_history) > 52:  # Keep 52 weeks of history
            self.price_history.pop(0)

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'price': self.price,
            'price_history': self.price_history,
            'weeks_since_change': self.weeks_since_change
        }

    @staticmethod
    def from_dict(data: dict) -> 'ElfQueenWater':
        """Deserialize from dictionary"""
        eqw = ElfQueenWater()
        eqw.price = data['price']
        eqw.price_history = data.get('price_history', [])
        eqw.weeks_since_change = data.get('weeks_since_change', 0)
        return eqw

    def __str__(self):
        weeks_until_change = 6 - self.weeks_since_change
        return f"{self.name} - ${self.price:.2f}/vial (Next change in {weeks_until_change} weeks)"


class GoldCoin:
    """Represents Gold Coin - common fantasy currency, crypto-like but stable"""

    def __init__(self):
        self.name = "Gold Coin"
        self.price = 2.0  # $2 starting price
        self.base_volatility = 1.5  # Low volatility (1.5%) - more stable than regular crypto
        self.price_history: List[float] = []
        self.description = "Common currency in the fantasy world - like crypto but more stable"

    def update_price(self):
        """Update price with low volatility (stable crypto behavior)"""
        # Stable behavior with small random walks
        change_percent = random.uniform(-self.base_volatility, self.base_volatility)
        self.price *= (1 + change_percent / 100)
        self.price = max(self.price, 0.10)  # Floor price at 10 cents
        self.price_history.append(self.price)
        if len(self.price_history) > 52:  # Keep 52 weeks of history
            self.price_history.pop(0)

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'price': self.price,
            'base_volatility': self.base_volatility,
            'price_history': self.price_history
        }

    @staticmethod
    def from_dict(data: dict) -> 'GoldCoin':
        """Deserialize from dictionary"""
        gc = GoldCoin()
        gc.price = data['price']
        gc.base_volatility = data.get('base_volatility', 1.5)
        gc.price_history = data.get('price_history', [])
        return gc

    def __str__(self):
        trend = ""
        if len(self.price_history) >= 2:
            if self.price > self.price_history[-2]:
                trend = " ↗️"
            elif self.price < self.price_history[-2]:
                trend = " ↘️"
            else:
                trend = " ➡️"
        return f"{self.name} - ${self.price:.2f}/coin (Volatility: {self.base_volatility}%){trend}"


class VoidStocks:
    """Represents Void Stocks - copies company stock prices, becomes 0 every other week"""

    def __init__(self, companies: Dict[str, 'Company']):
        self.name = "Void Stocks"
        self.price = 0.0  # Start at $0
        self.companies = companies
        self.weeks_elapsed = 0  # Track weeks
        self.current_company_index = 0  # Which company we're copying
        self.company_names = []  # Will be populated when we have companies
        self.description = "Mysterious stocks that copy companies, then disappear into the void"
        self.is_void_week = True  # Start in void state

    def update_price(self):
        """Update price - alternates between copying a company and being $0"""
        self.weeks_elapsed += 1

        # Update company names list if needed
        if not self.company_names and self.companies:
            self.company_names = sorted(list(self.companies.keys()))

        if self.weeks_elapsed % 2 == 1:
            # Odd weeks (1, 3, 5, ...): Copy a company's stock
            self.is_void_week = False
            if self.company_names:
                company_name = self.company_names[self.current_company_index % len(self.company_names)]
                self.price = self.companies[company_name].price
                # Move to next company for next active week
                self.current_company_index += 1
            else:
                self.price = 0.0  # No companies available
        else:
            # Even weeks (2, 4, 6, ...): Become void ($0)
            self.is_void_week = True
            self.price = 0.0

    def get_current_company_name(self) -> str:
        """Get the name of the company currently being copied (if any)"""
        if self.is_void_week or not self.company_names:
            return "VOID"
        # Get the company from the previous index since we increment after copying
        idx = (self.current_company_index - 1) % len(self.company_names)
        return self.company_names[idx]

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'price': self.price,
            'weeks_elapsed': self.weeks_elapsed,
            'current_company_index': self.current_company_index,
            'company_names': self.company_names,
            'is_void_week': self.is_void_week
        }

    @staticmethod
    def from_dict(data: dict, companies: Dict[str, 'Company']) -> 'VoidStocks':
        """Deserialize from dictionary"""
        vs = VoidStocks(companies)
        vs.price = data['price']
        vs.weeks_elapsed = data.get('weeks_elapsed', 0)
        vs.current_company_index = data.get('current_company_index', 0)
        vs.company_names = data.get('company_names', [])
        vs.is_void_week = data.get('is_void_week', True)
        return vs

    def __str__(self):
        if self.is_void_week:
            return f"{self.name} - ${self.price:.2f}/share [VOID STATE]"
        else:
            company = self.get_current_company_name()
            return f"{self.name} - ${self.price:.2f}/share [Copying: {company}]"


class VoidCatalyst:
    """Represents Void Catalyst - unique asset that auto-sells after 4 weeks"""

    def __init__(self):
        self.name = "Void Catalyst"
        self.price = 100000.0  # $100k starting price
        self.is_owned = False  # Track if someone owns it
        self.owner_name = None  # Who owns it
        self.weeks_owned = 0  # How long has it been owned
        self.players_owned_this_cycle: set = set()  # Track which players have owned it this cycle
        self.description = "Unique asset - only 1 exists. Price always increases. Auto-sells after 4 weeks. Fair rotation among players."

    def update_price(self, player_name: str = None):
        """Update price - always goes up. Auto-sell after 4 weeks if owned."""
        # Price always increases by 5-10%
        increase_percent = random.uniform(5.0, 10.0)
        self.price *= (1 + increase_percent / 100)

        # Track ownership time
        if self.is_owned:
            self.weeks_owned += 1

    def can_player_buy(self, player_name: str, all_human_players: List[str]) -> Tuple[bool, str]:
        """Check if a player is allowed to buy the Void Catalyst"""
        # If already owned by someone, can't buy
        if self.is_owned:
            return False, f"Void Catalyst is already owned by {self.owner_name}!"

        # If this player already owned it this cycle, can't buy again until cycle resets
        if player_name in self.players_owned_this_cycle:
            # Check if we should reset the cycle (all players have owned it)
            if len(self.players_owned_this_cycle) >= len(all_human_players):
                # Cycle complete, reset for next time
                self.players_owned_this_cycle.clear()
                # But still block THIS purchase - player must wait for next opportunity
                return False, "You already used your turn this cycle. Availability has been reset - try again!"
            else:
                # Still waiting for other players
                remaining_players = set(all_human_players) - self.players_owned_this_cycle
                return False, f"You already owned the Void Catalyst this cycle. Waiting for: {', '.join(sorted(remaining_players))}"

        return True, "OK"

    def buy(self, player_name: str, all_human_players: List[str]) -> Tuple[bool, str]:
        """Attempt to buy the Void Catalyst"""
        # Check if player can buy
        can_buy, reason = self.can_player_buy(player_name, all_human_players)
        if not can_buy:
            return False, reason

        self.is_owned = True
        self.owner_name = player_name
        self.weeks_owned = 0
        self.players_owned_this_cycle.add(player_name)

        # Check if cycle will reset after this purchase
        if len(self.players_owned_this_cycle) >= len(all_human_players):
            cycle_msg = " [All players have now owned it - cycle will reset when it's available again]"
        else:
            cycle_msg = ""

        return True, f"You now own the Void Catalyst! It will auto-sell in 4 weeks.{cycle_msg}"

    def check_auto_sell(self) -> Tuple[bool, str, float]:
        """Check if auto-sell should trigger. Returns (should_sell, message, sell_price)"""
        if self.is_owned and self.weeks_owned >= 4:
            sell_price = self.price
            owner = self.owner_name

            # Auto-sell happens
            self.is_owned = False
            self.owner_name = None
            self.weeks_owned = 0

            return True, f"Void Catalyst auto-sold for ${sell_price:.2f}!", sell_price
        return False, "", 0.0

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'price': self.price,
            'is_owned': self.is_owned,
            'owner_name': self.owner_name,
            'weeks_owned': self.weeks_owned,
            'players_owned_this_cycle': list(self.players_owned_this_cycle)
        }

    @staticmethod
    def from_dict(data: dict) -> 'VoidCatalyst':
        """Deserialize from dictionary"""
        vc = VoidCatalyst()
        vc.price = data['price']
        vc.is_owned = data.get('is_owned', False)
        vc.owner_name = data.get('owner_name', None)
        vc.weeks_owned = data.get('weeks_owned', 0)
        vc.players_owned_this_cycle = set(data.get('players_owned_this_cycle', []))
        return vc

    def __str__(self):
        if self.is_owned:
            weeks_left = 4 - self.weeks_owned
            return f"{self.name} - ${self.price:.2f} [OWNED by {self.owner_name}, Auto-sells in {weeks_left} weeks]"
        else:
            if self.players_owned_this_cycle:
                return f"{self.name} - ${self.price:.2f} [AVAILABLE - Rotation: {len(self.players_owned_this_cycle)} players have owned it this cycle]"
            else:
                return f"{self.name} - ${self.price:.2f} [AVAILABLE - 1 unit only]"


class Player:
    """Represents a player in the game"""

    def __init__(self, name: str, starting_cash: float = 50000.0):
        self.name = name
        self.cash = starting_cash
        self.portfolio: Dict[str, float] = {}  # company_name -> number of shares (fractional)
        self.treasury_bonds = 0
        # New themed investments
        self.quantum_singularity_units = 0  # Permanent investment
        self.gold_ounces = 0  # Physical gold
        self.holy_water_vials = 0  # Fantasy blessed commodity
        self.elf_queen_water_vials = 0  # Elf Queen's "Water"
        self.gold_coins = 0  # Gold Coins (fantasy currency)
        self.void_stocks_shares = 0  # Void Stocks shares
        self.void_catalyst_owned = False  # Void Catalyst (only 1 exists)
        # Leverage system
        self.borrowed_amount = 0.0
        self.max_leverage_ratio = 5.0  # Can borrow up to 5x equity
        self.interest_rate_weekly = 0.115  # ~6% annual = 0.115% weekly
        # Short selling system
        self.short_positions: Dict[str, int] = {}  # company_name -> shares borrowed and owed
        self.short_borrow_fee_weekly = 0.02  # ~1% annual = 0.02% weekly
        # Research tracking
        self.researched_this_week = False
        self.research_history: Dict[str, List[str]] = {}  # company_name -> list of hints received

    def buy_stock(self, company: Company, dollar_amount: float, leverage: float = 1.0, companies: Dict[str, 'Company'] = None, treasury: 'Treasury' = None) -> Tuple[bool, str]:
        """Buy shares of a company using dollar amount with optional leverage

        Args:
            company: Company to invest in
            dollar_amount: Dollar amount to invest (before leverage)
            leverage: Leverage multiplier (e.g., 2.0 = 2x leverage, doubles the investment)
            companies: Dict of companies (needed for equity calculation with leverage)
            treasury: Treasury object (needed for equity calculation with leverage)
        """
        if dollar_amount <= 0:
            return False, "Invalid investment amount!"

        # Apply leverage multiplier to investment amount
        total_investment = dollar_amount * leverage
        borrowed_for_trade = total_investment - dollar_amount

        # Check if we have enough cash for the base investment
        if dollar_amount > self.cash:
            return False, "Insufficient funds for base investment!"

        # If using leverage, check if we can borrow that much
        if leverage > 1.0:
            if companies is None or treasury is None:
                return False, "Cannot calculate leverage without company data!"

            equity = self.calculate_equity(companies, treasury)
            new_borrowed = self.borrowed_amount + borrowed_for_trade

            if new_borrowed > equity * self.max_leverage_ratio:
                max_can_borrow = max(0, equity * self.max_leverage_ratio - self.borrowed_amount)
                max_leverage_possible = (dollar_amount + max_can_borrow) / dollar_amount if dollar_amount > 0 else 1.0
                return False, f"Exceeds maximum leverage! Max leverage you can use: {max_leverage_possible:.2f}x"

        # Calculate shares we can buy (iterative approach for slippage)
        # We need to find how many shares we can buy with total_investment considering slippage
        shares = total_investment / company.price  # Initial estimate

        # Iteratively refine to account for slippage
        for _ in range(5):  # A few iterations should converge
            slippage_factor = company.calculate_slippage(shares, is_buy=True)
            effective_price = company.price * slippage_factor
            shares = total_investment / effective_price

        # Final calculation
        slippage_factor = company.calculate_slippage(shares, is_buy=True)
        effective_price = company.price * slippage_factor
        actual_cost = effective_price * shares

        # Execute the trade
        self.cash -= dollar_amount
        if leverage > 1.0:
            self.borrowed_amount += borrowed_for_trade

        if company.name in self.portfolio:
            self.portfolio[company.name] += shares
        else:
            self.portfolio[company.name] = shares

        # Build message
        slippage_cost = (effective_price - company.price) * shares
        leverage_msg = f" (with {leverage:.1f}x leverage)" if leverage > 1.0 else ""

        message = f"Purchased {shares:.4f} shares for ${dollar_amount:.2f}{leverage_msg}"
        if leverage > 1.0:
            message += f"\n  Total position value: ${total_investment:.2f} (borrowed ${borrowed_for_trade:.2f})"
        if slippage_cost > 0.01:
            message += f"\n  Price slippage: ${slippage_cost:.2f} due to {company.liquidity.value} liquidity"

        return True, message

    def sell_stock(self, company: Company, dollar_amount: float = None, shares: float = None) -> Tuple[bool, str]:
        """Sell shares of a company with liquidity slippage

        Args:
            company: Company to sell
            dollar_amount: Dollar amount to sell (mutually exclusive with shares)
            shares: Number of shares to sell (mutually exclusive with dollar_amount)
        """
        if company.name not in self.portfolio:
            return False, "You don't own any shares of this company!"

        owned_shares = self.portfolio[company.name]

        # Determine how many shares to sell
        if dollar_amount is not None and shares is not None:
            return False, "Specify either dollar_amount or shares, not both!"

        if dollar_amount is not None:
            # Calculate shares from dollar amount (iterative for slippage)
            shares_to_sell = dollar_amount / company.price  # Initial estimate

            # Iteratively refine
            for _ in range(5):
                if shares_to_sell > owned_shares:
                    shares_to_sell = owned_shares
                    break
                slippage_factor = company.calculate_slippage(shares_to_sell, is_buy=False)
                effective_price = company.price * slippage_factor
                shares_to_sell = dollar_amount / effective_price

            shares_to_sell = min(shares_to_sell, owned_shares)
        elif shares is not None:
            shares_to_sell = shares
        else:
            return False, "Must specify either dollar_amount or shares!"

        if shares_to_sell <= 0:
            return False, "Invalid amount!"

        if shares_to_sell > owned_shares:
            return False, f"You don't own that many shares! You own {owned_shares:.4f} shares."

        # Calculate effective price with slippage
        slippage_factor = company.calculate_slippage(shares_to_sell, is_buy=False)
        effective_price = company.price * slippage_factor
        total_value = effective_price * shares_to_sell

        self.cash += total_value
        self.portfolio[company.name] -= shares_to_sell
        if self.portfolio[company.name] < 0.0001:  # Clean up very small amounts
            del self.portfolio[company.name]

        # Calculate and show slippage impact
        slippage_loss = (company.price - effective_price) * shares_to_sell

        message = f"Sold {shares_to_sell:.4f} shares for ${total_value:.2f}"
        if slippage_loss > 0.01:
            message += f"\n  Price slippage: -${slippage_loss:.2f} due to {company.liquidity.value} liquidity"

        return True, message

    def short_sell(self, company: Company, shares: int, companies: Dict[str, Company], treasury: Treasury, gold: Gold = None, holy_water: HolyWater = None, quantum_singularity: QuantumSingularity = None, elf_queen_water: ElfQueenWater = None, gold_coin: GoldCoin = None, void_stocks: VoidStocks = None, void_catalyst: VoidCatalyst = None) -> Tuple[bool, str]:
        """Short sell shares: borrow and sell them, must cover later"""
        if shares <= 0:
            return False, "Invalid number of shares!"

        # Calculate effective price with slippage (selling borrowed shares)
        slippage_factor = company.calculate_slippage(shares, is_buy=False)
        effective_price = company.price * slippage_factor
        total_proceeds = effective_price * shares

        # Check margin requirement: need equity >= 1.5x the short position value
        # This is the initial margin requirement for short selling
        equity = self.calculate_equity(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst)
        short_value = company.price * shares
        required_margin = short_value * 1.5

        if equity < required_margin:
            return False, f"Insufficient equity for short sale! Need ${required_margin:.2f} equity, have ${equity:.2f}"

        # Execute short sale
        self.cash += total_proceeds
        if company.name in self.short_positions:
            self.short_positions[company.name] += shares
        else:
            self.short_positions[company.name] = shares

        # Calculate and show slippage impact
        slippage_loss = (company.price - effective_price) * shares
        if slippage_loss > 0.01:
            message = f"Short sale successful! Received ${total_proceeds:.2f} (Price slippage: -${slippage_loss:.2f} due to {company.liquidity.value} liquidity)"
        else:
            message = f"Short sale successful! Received ${total_proceeds:.2f}"

        return True, message

    def cover_short(self, company: Company, shares: int) -> Tuple[bool, str]:
        """Cover (close) a short position by buying back the shares"""
        if company.name not in self.short_positions or self.short_positions[company.name] < shares:
            return False, "You don't have that many shares shorted!"

        # Calculate effective price with slippage (buying to cover)
        slippage_factor = company.calculate_slippage(shares, is_buy=True)
        effective_price = company.price * slippage_factor
        total_cost = effective_price * shares

        if total_cost > self.cash:
            return False, "Insufficient funds to cover short position!"

        # Execute cover
        self.cash -= total_cost
        self.short_positions[company.name] -= shares
        if self.short_positions[company.name] == 0:
            del self.short_positions[company.name]

        # Calculate and show slippage impact
        slippage_cost = (effective_price - company.price) * shares
        if slippage_cost > 0.01:
            message = f"Short position covered! Cost ${total_cost:.2f} (Price slippage: ${slippage_cost:.2f} due to {company.liquidity.value} liquidity)"
        else:
            message = f"Short position covered! Cost ${total_cost:.2f}"

        return True, message

    def buy_treasury(self, treasury: Treasury, bonds: int) -> bool:
        """Buy treasury bonds"""
        total_cost = treasury.price * bonds
        if total_cost > self.cash:
            return False

        self.cash -= total_cost
        self.treasury_bonds += bonds
        return True

    def sell_treasury(self, treasury: Treasury, bonds: int) -> Tuple[bool, str]:
        """Sell treasury bonds"""
        if self.treasury_bonds < bonds:
            return False, "You don't own that many bonds!"

        total_value = treasury.price * bonds
        self.cash += total_value
        self.treasury_bonds -= bonds
        return True, f"Sale successful! Sold {bonds} treasury bonds for ${total_value:.2f}"

    def buy_quantum_singularity(self, quantum_singularity: QuantumSingularity, units: int) -> Tuple[bool, str]:
        """Buy Quantum Singularity units - permanent investment, cannot be sold"""
        total_cost = quantum_singularity.price * units
        if total_cost > self.cash:
            return False, "Insufficient funds!"

        self.cash -= total_cost
        self.quantum_singularity_units += units
        monthly_income = quantum_singularity.calculate_monthly_return(units)
        return True, f"Purchased {units} Quantum Singularity units! You will receive ${monthly_income:.2f}/month passive income. WARNING: This investment is PERMANENT and cannot be sold!"

    def buy_gold(self, gold: Gold, ounces: int) -> Tuple[bool, str]:
        """Buy physical gold"""
        total_cost = gold.price * ounces
        if total_cost > self.cash:
            return False, "Insufficient funds!"

        self.cash -= total_cost
        self.gold_ounces += ounces
        return True, f"Purchase successful! Bought {ounces} oz of gold for ${total_cost:.2f}"

    def sell_gold(self, gold: Gold, ounces: int) -> Tuple[bool, str]:
        """Sell physical gold"""
        if self.gold_ounces < ounces:
            return False, "You don't own that much gold!"

        total_value = gold.price * ounces
        self.cash += total_value
        self.gold_ounces -= ounces
        return True, f"Sale successful! Sold {ounces} oz of gold for ${total_value:.2f}"

    def buy_holy_water(self, holy_water: HolyWater, vials: int) -> Tuple[bool, str]:
        """Buy Holy Water vials"""
        total_cost = holy_water.price * vials
        if total_cost > self.cash:
            return False, "Insufficient funds!"

        self.cash -= total_cost
        self.holy_water_vials += vials
        blessing_msg = ""
        if holy_water.blessing_intensity > 1.1:
            blessing_msg = " The water glows with divine light! ✨"
        elif holy_water.blessing_intensity < 0.9:
            blessing_msg = " The water seems... tainted. 💀"
        return True, f"Purchase successful! Bought {vials} vials of Holy Water for ${total_cost:.2f}{blessing_msg}"

    def sell_holy_water(self, holy_water: HolyWater, vials: int) -> Tuple[bool, str]:
        """Sell Holy Water vials"""
        if self.holy_water_vials < vials:
            return False, "You don't own that many vials!"

        total_value = holy_water.price * vials
        self.cash += total_value
        self.holy_water_vials -= vials
        blessing_msg = ""
        if holy_water.blessing_intensity > 1.1:
            blessing_msg = " The buyer seems blessed by the transaction! ✨"
        elif holy_water.blessing_intensity < 0.9:
            blessing_msg = " The buyer looks nervous... 💀"
        return True, f"Sale successful! Sold {vials} vials of Holy Water for ${total_value:.2f}{blessing_msg}"

    def buy_elf_queen_water(self, elf_queen_water: ElfQueenWater, vials: int) -> Tuple[bool, str]:
        """Buy Elf Queen's Water vials"""
        total_cost = elf_queen_water.price * vials
        if total_cost > self.cash:
            return False, "Insufficient funds!"

        self.cash -= total_cost
        self.elf_queen_water_vials += vials
        return True, f"Purchase successful! Bought {vials} vials of Elf Queen's \"Water\" for ${total_cost:.2f}. If you know, you know."

    def sell_elf_queen_water(self, elf_queen_water: ElfQueenWater, vials: int) -> Tuple[bool, str]:
        """Sell Elf Queen's Water vials"""
        if self.elf_queen_water_vials < vials:
            return False, "You don't own that many vials!"

        total_value = elf_queen_water.price * vials
        self.cash += total_value
        self.elf_queen_water_vials -= vials
        return True, f"Sale successful! Sold {vials} vials of Elf Queen's \"Water\" for ${total_value:.2f}"

    def buy_gold_coin(self, gold_coin: GoldCoin, coins: int) -> Tuple[bool, str]:
        """Buy Gold Coins"""
        total_cost = gold_coin.price * coins
        if total_cost > self.cash:
            return False, "Insufficient funds!"

        self.cash -= total_cost
        self.gold_coins += coins
        return True, f"Purchase successful! Bought {coins} Gold Coins for ${total_cost:.2f}"

    def sell_gold_coin(self, gold_coin: GoldCoin, coins: int) -> Tuple[bool, str]:
        """Sell Gold Coins"""
        if self.gold_coins < coins:
            return False, "You don't own that many Gold Coins!"

        total_value = gold_coin.price * coins
        self.cash += total_value
        self.gold_coins -= coins
        return True, f"Sale successful! Sold {coins} Gold Coins for ${total_value:.2f}"

    def buy_void_stocks(self, void_stocks: VoidStocks, shares: int) -> Tuple[bool, str]:
        """Buy Void Stocks"""
        if void_stocks.is_void_week:
            return False, "Cannot buy Void Stocks during VOID STATE (price is $0)!"

        total_cost = void_stocks.price * shares
        if total_cost > self.cash:
            return False, "Insufficient funds!"

        self.cash -= total_cost
        self.void_stocks_shares += shares
        company = void_stocks.get_current_company_name()
        return True, f"Purchase successful! Bought {shares} Void Stocks for ${total_cost:.2f} (Currently copying {company})"

    def sell_void_stocks(self, void_stocks: VoidStocks, shares: int) -> Tuple[bool, str]:
        """Sell Void Stocks"""
        if self.void_stocks_shares < shares:
            return False, "You don't own that many Void Stocks!"

        total_value = void_stocks.price * shares
        self.cash += total_value
        self.void_stocks_shares -= shares

        if void_stocks.is_void_week:
            return True, f"Sale successful! Sold {shares} Void Stocks for ${total_value:.2f} (VOID STATE - worthless!)"
        else:
            company = void_stocks.get_current_company_name()
            return True, f"Sale successful! Sold {shares} Void Stocks for ${total_value:.2f} (Was copying {company})"

    def buy_void_catalyst(self, void_catalyst: VoidCatalyst, all_human_players: List[str]) -> Tuple[bool, str]:
        """Buy the Void Catalyst (only 1 exists)"""
        if self.void_catalyst_owned:
            return False, "You already own the Void Catalyst!"

        if void_catalyst.price > self.cash:
            return False, "Insufficient funds!"

        success, msg = void_catalyst.buy(self.name, all_human_players)
        if not success:
            return False, msg

        purchase_price = void_catalyst.price
        self.cash -= purchase_price
        self.void_catalyst_owned = True

        # 10% chance of immediate auto-sell (no gain, no loss)
        if random.random() < 0.10:
            # Auto-sell immediately - player gets their money back
            self.cash += purchase_price
            self.void_catalyst_owned = False
            void_catalyst.is_owned = False
            void_catalyst.owner_name = None
            void_catalyst.weeks_owned = 0
            return True, f"Purchase successful! Bought Void Catalyst for ${purchase_price:.2f}... but it IMMEDIATELY auto-sold for ${purchase_price:.2f}! The void is fickle. (No money gained or lost)"

        return True, f"Purchase successful! Bought Void Catalyst for ${purchase_price:.2f}. {msg.split('!', 1)[1] if '!' in msg else ''}"

    def process_void_catalyst_auto_sell(self, void_catalyst: VoidCatalyst) -> Tuple[bool, str, float]:
        """Process auto-sell of Void Catalyst if needed. Returns (was_sold, message, amount)"""
        if not self.void_catalyst_owned:
            return False, "", 0.0

        should_sell, msg, sell_price = void_catalyst.check_auto_sell()
        if should_sell:
            self.cash += sell_price
            self.void_catalyst_owned = False
            return True, msg, sell_price
        return False, "", 0.0

    def apply_quantum_singularity_income(self, quantum_singularity: QuantumSingularity) -> float:
        """Apply monthly passive income from Quantum Singularity (called every 4 weeks)"""
        if self.quantum_singularity_units > 0:
            income = quantum_singularity.calculate_monthly_return(self.quantum_singularity_units)
            self.cash += income
            return income
        return 0.0

    def calculate_net_worth(self, companies: Dict[str, Company], treasury: Treasury, gold: Gold = None, holy_water: HolyWater = None, quantum_singularity: QuantumSingularity = None, elf_queen_water: ElfQueenWater = None, gold_coin: GoldCoin = None, void_stocks: VoidStocks = None, void_catalyst: VoidCatalyst = None) -> float:
        """Calculate total net worth (cash + stocks + bonds - short obligations)"""
        net_worth = self.cash

        # Add long stock value
        for company_name, shares in self.portfolio.items():
            if company_name in companies:
                net_worth += companies[company_name].price * shares

        # Subtract short position obligations (liability to return borrowed shares)
        for company_name, shares in self.short_positions.items():
            if company_name in companies:
                net_worth -= companies[company_name].price * shares

        # Add treasury value
        net_worth += self.treasury_bonds * treasury.price

        # Add themed investments
        if gold and self.gold_ounces > 0:
            net_worth += self.gold_ounces * gold.price
        if holy_water and self.holy_water_vials > 0:
            net_worth += self.holy_water_vials * holy_water.price
        if quantum_singularity and self.quantum_singularity_units > 0:
            net_worth += self.quantum_singularity_units * quantum_singularity.price
        if elf_queen_water and self.elf_queen_water_vials > 0:
            net_worth += self.elf_queen_water_vials * elf_queen_water.price
        if gold_coin and self.gold_coins > 0:
            net_worth += self.gold_coins * gold_coin.price
        if void_stocks and self.void_stocks_shares > 0:
            net_worth += self.void_stocks_shares * void_stocks.price
        if void_catalyst and self.void_catalyst_owned:
            net_worth += void_catalyst.price

        return net_worth

    def calculate_equity(self, companies: Dict[str, Company], treasury: Treasury, gold: Gold = None, holy_water: HolyWater = None, quantum_singularity: QuantumSingularity = None, elf_queen_water: ElfQueenWater = None, gold_coin: GoldCoin = None, void_stocks: VoidStocks = None, void_catalyst: VoidCatalyst = None) -> float:
        """Calculate equity (net worth minus debt)"""
        return self.calculate_net_worth(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst) - self.borrowed_amount

    def calculate_total_assets(self, companies: Dict[str, Company], treasury: Treasury, gold: Gold = None, holy_water: HolyWater = None, quantum_singularity: QuantumSingularity = None, elf_queen_water: ElfQueenWater = None, gold_coin: GoldCoin = None, void_stocks: VoidStocks = None, void_catalyst: VoidCatalyst = None) -> float:
        """Calculate total portfolio value (not including cash, only investments)"""
        assets = 0.0

        # Add stock value
        for company_name, shares in self.portfolio.items():
            if company_name in companies:
                assets += companies[company_name].price * shares

        # Add treasury value
        assets += self.treasury_bonds * treasury.price

        # Add themed investments
        if gold and self.gold_ounces > 0:
            assets += self.gold_ounces * gold.price
        if holy_water and self.holy_water_vials > 0:
            assets += self.holy_water_vials * holy_water.price
        if quantum_singularity and self.quantum_singularity_units > 0:
            assets += self.quantum_singularity_units * quantum_singularity.price
        if elf_queen_water and self.elf_queen_water_vials > 0:
            assets += self.elf_queen_water_vials * elf_queen_water.price
        if gold_coin and self.gold_coins > 0:
            assets += self.gold_coins * gold_coin.price
        if void_stocks and self.void_stocks_shares > 0:
            assets += self.void_stocks_shares * void_stocks.price
        if void_catalyst and self.void_catalyst_owned:
            assets += void_catalyst.price

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

    def apply_short_borrow_fees(self, companies: Dict[str, Company]) -> float:
        """Apply weekly borrow fees for short positions"""
        total_fees = 0.0
        for company_name, shares in self.short_positions.items():
            if company_name in companies:
                position_value = companies[company_name].price * shares
                fee = position_value * (self.short_borrow_fee_weekly / 100)
                total_fees += fee

        if total_fees > 0:
            self.cash -= total_fees

        return total_fees

    def check_margin_call(self, companies: Dict[str, Company], treasury: Treasury, gold: Gold = None, holy_water: HolyWater = None, quantum_singularity: QuantumSingularity = None, elf_queen_water: ElfQueenWater = None, gold_coin: GoldCoin = None, void_stocks: VoidStocks = None, void_catalyst: VoidCatalyst = None) -> bool:
        """Check if player is subject to margin call (equity < 30% of total position or maintenance margin for shorts)"""
        # Check if there's any leverage or short positions
        has_risk = self.borrowed_amount > 0 or len(self.short_positions) > 0
        if not has_risk:
            return False

        # Calculate equity excluding Quantum Singularity (it doesn't count for margin purposes)
        equity = self.calculate_equity(companies, treasury, gold, holy_water, None, elf_queen_water, gold_coin, void_stocks, void_catalyst)

        # Check leverage-based margin call
        if self.borrowed_amount > 0:
            total_position = equity + self.borrowed_amount
            # Margin call if equity falls below 30% of total position
            if total_position > 0 and (equity / total_position) < 0.30:
                return True

        # Check short position maintenance margin
        # Require equity >= 1.25x short position value (125% maintenance margin)
        if len(self.short_positions) > 0:
            total_short_value = 0.0
            for company_name, shares in self.short_positions.items():
                if company_name in companies:
                    total_short_value += companies[company_name].price * shares

            required_maintenance = total_short_value * 1.25
            if equity < required_maintenance:
                return True

        return False

    def force_liquidate_margin_call(self, companies: Dict[str, Company], treasury: Treasury, gold: Gold = None, holy_water: HolyWater = None, quantum_singularity: QuantumSingularity = None, elf_queen_water: ElfQueenWater = None, gold_coin: GoldCoin = None, void_stocks: VoidStocks = None, void_catalyst: VoidCatalyst = None) -> List[str]:
        """
        Automatically liquidate positions to meet margin requirements.
        Returns a list of actions taken.
        """
        actions = []

        if not self.check_margin_call(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst):
            return actions  # No margin call, nothing to do

        actions.append(f"🚨 FORCED LIQUIDATION for {self.name} - Margin call not resolved")

        # Cover short positions first (highest risk due to unlimited loss potential)
        # Sort by value (cover largest short positions first to reduce risk fastest)
        short_positions = [(name, shares, companies[name].price * shares)
                          for name, shares in self.short_positions.items()]
        short_positions.sort(key=lambda x: x[2], reverse=True)

        for company_name, shares, value in short_positions:
            if not self.check_margin_call(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst):
                break  # Margin call resolved

            company = companies[company_name]
            cost = shares * company.price

            if cost <= self.cash:
                # Cover the short position
                self.cash -= cost
                self.short_positions[company_name] = 0
                actions.append(f"   Covered {shares} shorted shares of {company_name} for ${cost:.2f}")

        # Clean up empty short positions
        self.short_positions = {k: v for k, v in self.short_positions.items() if v > 0}

        # Liquidate long stocks second
        # Sort by value (sell largest positions first to minimize transactions)
        stock_positions = [(name, shares, companies[name].price * shares)
                          for name, shares in self.portfolio.items()]
        stock_positions.sort(key=lambda x: x[2], reverse=True)

        for company_name, shares, value in stock_positions:
            if not self.check_margin_call(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst):
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
        if self.check_margin_call(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst) and self.treasury_bonds > 0:
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
        equity = self.calculate_equity(companies, treasury, gold, holy_water, None, elf_queen_water, gold_coin, void_stocks, void_catalyst)
        if self.check_margin_call(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst):
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

            # Fantasy-themed research hints
            ("Arcane analysts report {company}'s dimensional rift stability metrics showing {stability} patterns with mana flow consistency rated as {consistency}.",
             lambda c: {"stability": "exceptional" if c.base_volatility < 7 else "concerning fluctuation" if c.base_volatility > 9 else "moderate variance",
                       "consistency": "highly reliable" if c.true_strength > 0.65 else "unpredictable" if c.true_strength < 0.5 else "adequate"}),

            ("Golem safety auditors indicate {company} autonomous worker units exhibit {safety} incident rates with sentience drift metrics {drift}.",
             lambda c: {"safety": "industry-leading low" if c.true_strength > 0.65 and c.base_volatility < 7 else "elevated" if c.true_strength < 0.5 or c.base_volatility > 9 else "acceptable",
                       "drift": "well-controlled" if c.base_volatility < 7 else "requiring enhanced monitoring" if c.base_volatility > 9 else "within normal parameters"}),

            ("Interdimensional commerce reports suggest {company} mana extraction permits face {regulatory} outlook with cross-realm compliance status {compliance}.",
             lambda c: {"regulatory": "favorable renewal" if c.hidden_sentiment > 0 else "restrictive challenges" if c.hidden_sentiment < 0 else "neutral review",
                       "compliance": "exceeding requirements" if c.true_strength > 0.65 else "under scrutiny" if c.true_strength < 0.5 else "meeting baseline standards"}),

            ("Wizard's Guild assessment of {company} reveals {ethics} magical ethics score with reality distortion impact rated {impact}.",
             lambda c: {"ethics": "exemplary sustainable practices" if c.true_strength > 0.65 else "questionable methodology concerns" if c.true_strength < 0.5 else "standard industry practices",
                       "impact": "minimal and well-managed" if c.base_volatility < 7 else "significant and unstable" if c.base_volatility > 9 else "moderate and monitored"}),

            ("Golem workforce productivity analysis shows {company} automation efficiency at {efficiency} with labor displacement sentiment {sentiment}.",
             lambda c: {"efficiency": "peak performance levels" if c.true_strength > 0.65 else "suboptimal operational rates" if c.true_strength < 0.5 else "industry-standard metrics",
                       "sentiment": "broadly positive with union support" if c.hidden_sentiment > 0 else "facing public backlash" if c.hidden_sentiment < 0 else "mixed public perception"}),

            ("Mana reserve projections for {company} indicate {reserves} long-term supply outlook with rift depletion risk assessed as {depletion}.",
             lambda c: {"reserves": "abundant multi-decade" if c.true_strength > 0.65 and c.hidden_sentiment > 0 else "concerning near-term shortage" if c.true_strength < 0.5 or c.hidden_sentiment < 0 else "adequate medium-term",
                       "depletion": "minimal given diversification" if c.true_strength > 0.65 else "elevated without new sources" if c.true_strength < 0.5 else "moderate requiring monitoring"}),

            ("Golem intelligence containment protocols at {company} rated {containment} with artificial sentience emergence probability {emergence}.",
             lambda c: {"containment": "robust and failsafe" if c.base_volatility < 7 and c.true_strength > 0.6 else "inadequate with breach risk" if c.base_volatility > 9 or c.true_strength < 0.5 else "functional with standard safeguards",
                       "emergence": "negligible under current architecture" if c.base_volatility < 7 else "concerning given recent incidents" if c.base_volatility > 9 else "low but non-zero"}),

            ("Dimensional market analysis shows {company} cross-realm energy demand trending {trend} with interdimensional competition pressure {pressure}.",
             lambda c: {"trend": "strongly upward" if c.hidden_sentiment > 0 else "declining sharply" if c.hidden_sentiment < 0 else "sideways consolidation",
                       "pressure": "minimal due to unique positioning" if c.true_strength > 0.65 else "intense from rival extractors" if c.true_strength < 0.5 else "moderate from established players"}),

            ("Arcane energy conversion efficiency metrics place {company} at {efficiency} performance with magical-to-electrical loss rates {loss}.",
             lambda c: {"efficiency": "cutting-edge optimization" if c.true_strength > 0.65 else "below industry benchmarks" if c.true_strength < 0.5 else "competitive mid-tier",
                       "loss": "exceptionally low" if c.true_strength > 0.65 else "problematically high" if c.true_strength < 0.5 else "within acceptable ranges"}),

            ("Golem liability exposure analysis flags {company} risk profile as {risk} with insurance premium trajectory {premiums}.",
             lambda c: {"risk": "low given safety record" if c.base_volatility < 7 and c.true_strength > 0.6 else "high due to incident frequency" if c.base_volatility > 9 or c.true_strength < 0.5 else "moderate requiring standard coverage",
                       "premiums": "declining favorably" if c.true_strength > 0.6 else "increasing substantially" if c.true_strength < 0.5 else "stable at current levels"}),
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
            'short_positions': self.short_positions,
            'short_borrow_fee_weekly': self.short_borrow_fee_weekly,
            'researched_this_week': self.researched_this_week,
            'research_history': self.research_history,
            'quantum_singularity_units': self.quantum_singularity_units,
            'gold_ounces': self.gold_ounces,
            'holy_water_vials': self.holy_water_vials,
            'elf_queen_water_vials': self.elf_queen_water_vials,
            'gold_coins': self.gold_coins,
            'void_stocks_shares': self.void_stocks_shares,
            'void_catalyst_owned': self.void_catalyst_owned
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
        player.short_positions = data.get('short_positions', {})  # Default to empty dict for backwards compatibility
        player.short_borrow_fee_weekly = data.get('short_borrow_fee_weekly', 0.02)  # Default value
        player.researched_this_week = data['researched_this_week']
        player.research_history = data['research_history']
        player.quantum_singularity_units = data.get('quantum_singularity_units', 0)  # Default to 0 for backwards compatibility
        player.gold_ounces = data.get('gold_ounces', 0)  # Default to 0 for backwards compatibility
        player.holy_water_vials = data.get('holy_water_vials', 0)  # Default to 0 for backwards compatibility
        player.elf_queen_water_vials = data.get('elf_queen_water_vials', 0)
        player.gold_coins = data.get('gold_coins', 0)
        player.void_stocks_shares = data.get('void_stocks_shares', 0)
        player.void_catalyst_owned = data.get('void_catalyst_owned', False)
        return player

    def display_portfolio(self, companies: Dict[str, Company], treasury: Treasury, gold: Gold = None, holy_water: HolyWater = None, quantum_singularity: QuantumSingularity = None, elf_queen_water: ElfQueenWater = None, gold_coin: GoldCoin = None, void_stocks: VoidStocks = None, void_catalyst: VoidCatalyst = None):
        """Display player's portfolio"""
        print(f"\n{'='*60}")
        print(f"{self.name}'s Portfolio")
        print(f"{'='*60}")
        print(f"Cash: ${self.cash:.2f}")

        # Show leverage info
        if self.borrowed_amount > 0:
            print(f"💳 Borrowed (Leverage): ${self.borrowed_amount:.2f}")
            equity = self.calculate_equity(companies, treasury, gold, holy_water, quantum_singularity)
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
                    print(f"  {company_name}: {shares:.4f} shares @ ${company.price:.2f} = ${value:.2f}")
        else:
            print("Stocks: None")

        print()
        if self.short_positions:
            print("Short Positions (Shares Owed):")
            for company_name, shares in self.short_positions.items():
                if company_name in companies:
                    company = companies[company_name]
                    obligation = company.price * shares
                    print(f"  {company_name}: {shares} shorted @ ${company.price:.2f} = ${obligation:.2f} owed")
        else:
            print("Short Positions: None")

        print()
        if self.treasury_bonds > 0:
            bond_value = self.treasury_bonds * treasury.price
            print(f"Treasury Bonds: {self.treasury_bonds} bonds @ ${treasury.price:.2f} = ${bond_value:.2f}")
        else:
            print("Treasury Bonds: None")

        print()
        # Display themed investments
        print("Themed Investments:")
        has_themed = False
        if quantum_singularity and self.quantum_singularity_units > 0:
            value = self.quantum_singularity_units * quantum_singularity.price
            monthly_income = quantum_singularity.calculate_monthly_return(self.quantum_singularity_units)
            print(f"  Quantum Singularity: {self.quantum_singularity_units} units @ ${quantum_singularity.price:.2f} = ${value:.2f} (${monthly_income:.2f}/month)")
            has_themed = True
        if gold and self.gold_ounces > 0:
            value = self.gold_ounces * gold.price
            print(f"  Gold: {self.gold_ounces} oz @ ${gold.price:.2f} = ${value:.2f}")
            has_themed = True
        if holy_water and self.holy_water_vials > 0:
            value = self.holy_water_vials * holy_water.price
            blessing_status = ""
            if holy_water.blessing_intensity > 1.1:
                blessing_status = " ✨"
            elif holy_water.blessing_intensity < 0.9:
                blessing_status = " 💀"
            print(f"  Holy Water: {self.holy_water_vials} vials @ ${holy_water.price:.2f} = ${value:.2f}{blessing_status}")
            has_themed = True

        if elf_queen_water and self.elf_queen_water_vials > 0:
            value = self.elf_queen_water_vials * elf_queen_water.price
            print(f"  Elf Queen's \"Water\": {self.elf_queen_water_vials} vials @ ${elf_queen_water.price:.2f} = ${value:.2f}")
            has_themed = True
        if gold_coin and self.gold_coins > 0:
            value = self.gold_coins * gold_coin.price
            print(f"  Gold Coin: {self.gold_coins} coins @ ${gold_coin.price:.2f} = ${value:.2f}")
            has_themed = True
        if void_stocks and self.void_stocks_shares > 0:
            value = self.void_stocks_shares * void_stocks.price
            status = "[VOID]" if void_stocks.is_void_week else f"[{void_stocks.get_current_company_name()}]"
            print(f"  Void Stocks: {self.void_stocks_shares} shares @ ${void_stocks.price:.2f} = ${value:.2f} {status}")
            has_themed = True
        if void_catalyst and self.void_catalyst_owned:
            value = void_catalyst.price
            weeks_left = 4 - void_catalyst.weeks_owned
            print(f"  Void Catalyst: 1 unit @ ${void_catalyst.price:.2f} = ${value:.2f} (Auto-sells in {weeks_left} weeks)")
            has_themed = True

        if not has_themed:
            print("  None")

        print()
        net_worth = self.calculate_net_worth(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst)
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

    def __init__(self, name: str, strategy: str, starting_cash: float = 50000.0):
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

        # NPCs occasionally research companies (30% chance per week) to make informed decisions
        if not self.researched_this_week and random.random() < 0.3:
            # Pick a random company to research
            company_to_research = random.choice(list(companies.values()))
            # Research WITHOUT future price (no insider trading!)
            hint = self.research_company(company_to_research, future_price=None)
            actions.append(f"🔍 {self.name} researched {company_to_research.name}")

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

    def _check_short_profits(self, companies: Dict[str, Company]) -> List[str]:
        """Check and take profits on short positions if profitable"""
        actions = []

        for company_name in list(self.short_positions.keys()):
            if company_name in companies:
                company = companies[company_name]
                shares = self.short_positions.get(company_name, 0)

                if shares > 0:
                    # Check if we have price history to determine profit
                    if len(company.price_history) >= 2:
                        # Find the average price when we likely entered the short
                        avg_entry_price = sum(company.price_history[-3:]) / min(3, len(company.price_history))
                        current_price = company.price

                        # If stock fell 8%+ from average entry, take profits on 50% of position
                        price_change_pct = ((current_price - avg_entry_price) / avg_entry_price) * 100
                        if price_change_pct < -8:
                            cover_shares = int(shares * 0.5)
                            if cover_shares > 0:
                                success, msg = self.cover_short(company, cover_shares)
                                if success:
                                    actions.append(f"💰 {self.name} took profits on short, covered {cover_shares} shares of {company_name}")
                                    break  # Take profit on one at a time

        return actions

    def _aggressive_strategy(self, companies: Dict[str, Company], treasury: Treasury,
                           market_cycle: 'MarketCycle') -> List[str]:
        """Aggressive: High volatility stocks, uses leverage, momentum trading"""
        actions = []

        # Check for profitable short positions and take profits
        actions.extend(self._check_short_profits(companies))

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
            # Cover any existing short positions first (cut losses on shorts during bull market)
            for company_name, shares in list(self.short_positions.items()):
                if shares > 0:
                    company = companies[company_name]
                    # Cover as much as we can afford (at least 50% if possible)
                    max_affordable = int(self.cash / (company.price * 1.01))  # Account for slippage
                    cover_shares = min(shares, max(int(shares * 0.5), max_affordable))
                    if cover_shares > 0:
                        success, msg = self.cover_short(company, cover_shares)
                        if success:
                            actions.append(f"⬆️ {self.name} covered short position, bought back {cover_shares} shares of {company_name}")
                            break  # Cover one at a time

            # Buy high volatility stocks
            high_vol_companies = sorted(companies.values(), key=lambda c: c.base_volatility, reverse=True)[:2]
            for company in high_vol_companies:
                if self.cash > 1000:
                    dollar_amount = min(self.cash * 0.3, 3000)
                    if dollar_amount > 0:
                        success, msg = self.buy_stock(company, dollar_amount, leverage=1.0, companies=companies, treasury=treasury)
                        if success:
                            actions.append(f"📈 {self.name} aggressively invested ${dollar_amount:.2f} in {company.name}")

        # Sell during bear markets or crashes AND SHORT SELL aggressively
        elif market_cycle.active_cycle and market_cycle.active_cycle.cycle_type in [
            MarketCycleType.BEAR_MARKET, MarketCycleType.MARKET_CRASH, MarketCycleType.RECESSION
        ]:
            # Sell positions to cut losses
            for company_name, shares in list(self.portfolio.items()):
                sell_shares = shares * 0.4  # Sell 40% of position
                if sell_shares > 0:
                    company = companies[company_name]
                    success, msg = self.sell_stock(company, shares=sell_shares)
                    if success:
                        actions.append(f"📉 {self.name} cut position, sold {sell_shares:.4f} shares of {company_name}")

            # SHORT SELL high volatility stocks during downturns (aggressive bet against the market)
            equity = self.calculate_equity(companies, treasury)
            if equity > 1000:
                high_vol_companies = sorted(companies.values(), key=lambda c: c.base_volatility, reverse=True)[:2]
                for company in high_vol_companies:
                    # Don't short if we already have a large short position
                    current_short = self.short_positions.get(company.name, 0)
                    if current_short * company.price < equity * 0.3:  # Limit short exposure
                        shares_to_short = int(min(equity * 0.2, 2000) / company.price)
                        if shares_to_short > 0:
                            success, msg = self.short_sell(company, shares_to_short, companies, treasury)
                            if success:
                                actions.append(f"🔻 {self.name} shorted {shares_to_short} shares of {company.name} (betting on decline)")
                                break  # One short at a time

        # Baseline buying: always try to buy high volatility stocks if we have cash
        else:
            if self.cash > 1000:
                high_vol_companies = sorted(companies.values(), key=lambda c: c.base_volatility, reverse=True)[:2]
                for company in high_vol_companies:
                    if self.cash > 1000:
                        dollar_amount = min(self.cash * 0.2, 2000)
                        if dollar_amount > 0:
                            success, msg = self.buy_stock(company, dollar_amount, leverage=1.0, companies=companies, treasury=treasury)
                            if success:
                                actions.append(f"📊 {self.name} invested ${dollar_amount:.2f} in {company.name}")
                                break  # Buy one company at a time during neutral markets

        return actions

    def _value_strategy(self, companies: Dict[str, Company], treasury: Treasury,
                       market_cycle: 'MarketCycle') -> List[str]:
        """Value: Conservative, low volatility stocks, diversified"""
        actions = []

        # Check for profitable short positions and take profits
        actions.extend(self._check_short_profits(companies))

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
            dollar_amount = min(self.cash * 0.2, 2000)
            if dollar_amount > 0:
                success, msg = self.buy_stock(company, dollar_amount, leverage=1.0, companies=companies, treasury=treasury)
                if success:
                    actions.append(f"💎 {self.name} invested ${dollar_amount:.2f} in {company.name} (value play)")

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

        # Check for profitable short positions and take profits
        actions.extend(self._check_short_profits(companies))

        # Moderate leverage usage
        equity = self.calculate_equity(companies, treasury)
        if equity > 0 and self.borrowed_amount < equity * 1.2:
            borrow_amount = min(1500, equity * 1.2 - self.borrowed_amount)
            if borrow_amount > 100:
                success, msg = self.borrow_money(borrow_amount, companies, treasury)
                if success:
                    actions.append(f"🏦 {self.name} borrowed ${borrow_amount:.2f} for contrarian positions")

        # BUY during crashes/recessions (buy fear) and COVER shorts
        if market_cycle.active_cycle and market_cycle.active_cycle.cycle_type in [
            MarketCycleType.MARKET_CRASH, MarketCycleType.RECESSION, MarketCycleType.BEAR_MARKET
        ]:
            # Cover short positions first when market is fearful (contrarian: others fear, we close shorts)
            for company_name, shares in list(self.short_positions.items()):
                if shares > 0:
                    cover_shares = int(shares * 0.6)  # Cover 60% of shorts
                    if cover_shares > 0:
                        company = companies[company_name]
                        success, msg = self.cover_short(company, cover_shares)
                        if success:
                            actions.append(f"⬆️ {self.name} covered short during panic, bought back {cover_shares} shares of {company_name}")
                            break  # Cover one at a time

            # Buy the most beaten down stocks
            if self.cash > 1000:
                companies_list = list(companies.values())
                company = random.choice(companies_list)
                dollar_amount = min(self.cash * 0.4, 3500)
                if dollar_amount > 0:
                    success, msg = self.buy_stock(company, dollar_amount, leverage=1.0, companies=companies, treasury=treasury)
                    if success:
                        actions.append(f"🎯 {self.name} bought the dip! Invested ${dollar_amount:.2f} in {company.name}")

        # SELL during bull markets/recovery (sell greed) and SHORT
        elif market_cycle.active_cycle and market_cycle.active_cycle.cycle_type in [
            MarketCycleType.BULL_MARKET, MarketCycleType.RECOVERY
        ]:
            # Sell profitable positions
            for company_name, shares in list(self.portfolio.items()):
                if shares > 0.01:
                    sell_shares = shares * 0.5  # Sell 50% when market is euphoric
                    company = companies[company_name]
                    success, msg = self.sell_stock(company, shares=sell_shares)
                    if success:
                        actions.append(f"💰 {self.name} took profits, sold {sell_shares:.4f} shares of {company_name}")

            # SHORT during euphoric bull markets (contrarian: market is too optimistic)
            equity = self.calculate_equity(companies, treasury)
            if equity > 1500:
                # Pick a random stock to short (contrarian doesn't care about volatility, just sentiment)
                companies_list = list(companies.values())
                company = random.choice(companies_list)
                current_short = self.short_positions.get(company.name, 0)
                # Don't over-short any single company
                if current_short * company.price < equity * 0.25:
                    shares_to_short = int(min(equity * 0.15, 1500) / company.price)
                    if shares_to_short > 0:
                        success, msg = self.short_sell(company, shares_to_short, companies, treasury)
                        if success:
                            actions.append(f"🔻 {self.name} shorted {shares_to_short} shares of {company.name} (contrarian: market too bullish)")

        # Baseline buying: buy random stocks during neutral markets
        else:
            if self.cash > 1000:
                companies_list = list(companies.values())
                company = random.choice(companies_list)
                dollar_amount = min(self.cash * 0.25, 2500)
                if dollar_amount > 0:
                    success, msg = self.buy_stock(company, dollar_amount, leverage=1.0, companies=companies, treasury=treasury)
                    if success:
                        actions.append(f"🎲 {self.name} invested ${dollar_amount:.2f} in {company.name}")

        return actions


class InvestmentGame:
    """Main game class"""

    def __init__(self):
        self.companies: Dict[str, Company] = {}
        self.treasury = Treasury()
        # Themed investments
        self.quantum_singularity = QuantumSingularity()
        self.gold = Gold()
        self.holy_water = HolyWater()
        self.players: List[Player] = []
        self.hedge_funds: List[HedgeFund] = []  # NPC hedge funds
        self.current_turn = 0
        self.round_number = 1
        self.week_number = 1  # Track weeks (each player turn = 1 week)
        self.market_news = MarketNews()  # Market news system
        self.market_cycle = MarketCycle()  # Market cycle system (every 6 months)
        self.pending_news_display: Optional[NewsReport] = None  # News to display this week
        self.weekly_gazette = WeeklyGazette()  # Weekly news outlet #1
        self.market_chronicle = MarketChronicle()  # Weekly news outlet #2
        self.pending_weekly_news: Optional[List[Tuple[str, bool]]] = None  # Weekly news to display (text, is_real)
        self.pending_chronicle_news: Optional[List[Tuple[str, bool]]] = None  # Chronicle news to display (text, is_real)

        # Future price pre-calculation (hidden from players)
        # Stores next 2 weeks of calculated prices: {company_name: [week+1 price, week+2 price]}
        self.future_prices: Dict[str, List[float]] = {}

        self._initialize_companies()

        # Initialize new themed investments (after companies are initialized for VoidStocks)
        self.elf_queen_water = ElfQueenWater()
        self.gold_coin = GoldCoin()
        self.void_stocks = VoidStocks(self.companies)
        self.void_catalyst = VoidCatalyst()

        self._initialize_players()
        self._initialize_hedge_funds()

        # Pre-calculate initial future prices
        self._precalculate_future_prices()

    def _initialize_companies(self):
        """Initialize the 7 companies with different industries and liquidity levels"""
        company_data = [
            ("TechCorp", "Technology", 150.0, 8.0, LiquidityLevel.HIGH),
            ("ElectroMax", "Electronics", 85.0, 6.5, LiquidityLevel.MEDIUM),
            ("PharmaCare", "Pharmaceuticals", 220.0, 5.0, LiquidityLevel.LOW),
            ("AutoDrive", "Automotive", 95.0, 7.0, LiquidityLevel.MEDIUM),
            ("EnergyPlus", "Energy", 110.0, 9.0, LiquidityLevel.LOW),
            ("Blue Energy Industries", "Mana Extraction", 125.0, 9.5, LiquidityLevel.MEDIUM),
            ("Rock Friends Inc.", "Golem Manufacturing", 78.0, 11.0, LiquidityLevel.LOW),
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
            HedgeFund("Apex Capital (NPC)", "aggressive", 50000.0),
            HedgeFund("Steadfast Value (NPC)", "value", 50000.0),
            HedgeFund("Contrarian Partners (NPC)", "contrarian", 50000.0)
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
        print("Themed Investments:")
        print(f"  {self.quantum_singularity}")
        print(f"  {self.gold}")
        print(f"  {self.holy_water}")
        print(f"  {self.elf_queen_water}")
        print(f"  {self.gold_coin}")
        print(f"  {self.void_stocks}")
        print(f"  {self.void_catalyst}")
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
            for news_text, is_real in self.pending_weekly_news:
                # Don't show any indicator - players must figure out hoaxes themselves!
                print(f"• {news_text}")
            print("="*60)

        # Display second weekly outlet news if available
        if self.pending_chronicle_news:
            print("\n" + "📰 " + "="*58)
            print("THE MARKET CHRONICLE - WEEKLY REPORT")
            print("="*60)
            for news_text, is_real in self.pending_chronicle_news:
                # Don't show any indicator - players must figure out hoaxes themselves!
                print(f"• {news_text}")
            print("="*60)

    def execute_hedge_fund_trades(self):
        """Execute automated trades for all hedge funds"""
        all_actions = []

        for hedge_fund in self.hedge_funds:
            # Reset weekly research at start of turn
            hedge_fund.reset_weekly_research()

            # Apply interest on borrowed amounts
            interest = hedge_fund.apply_interest()

            # Apply short borrow fees
            short_fees = hedge_fund.apply_short_borrow_fees(self.companies)

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
        """Update all stock prices using precompiled future prices"""
        # Execute hedge fund trades first (NPCs react to current market conditions)
        self.execute_hedge_fund_trades()

        # Apply precompiled prices to all companies
        # The future_prices[company_name][0] is the actual next week price
        for company_name, company in self.companies.items():
            if company_name in self.future_prices and len(self.future_prices[company_name]) > 0:
                # Use the precompiled price for this week
                company.price = self.future_prices[company_name][0]
                company.price_history.append(company.price)

        # Check if we should trigger a new market cycle
        cycle_triggered = False
        if self.market_cycle.should_trigger_cycle(self.week_number):
            cycle = self.market_cycle.trigger_cycle(self.week_number)
            cycle_triggered = True
            print("\n" + "🌍" + "="*58)
            print("MAJOR GLOBAL ECONOMIC EVENT")
            print("="*60)
            print(f"\n{cycle.headline}")
            print(f"\n{cycle.description}")
            print(f"\nThis cycle will affect markets for {cycle.weeks_remaining} weeks.")
            print("="*60)
            input("\nPress Enter to continue...")

        # Update active market cycle (decrement counter, display messages)
        cycle_messages = []
        cycle_ended = False
        if self.market_cycle.active_cycle:
            self.market_cycle.active_cycle.weeks_remaining -= 1
            if self.market_cycle.active_cycle.weeks_remaining <= 0:
                cycle_messages.append(f"\n🔔 MARKET CYCLE ENDED: {self.market_cycle.active_cycle.cycle_type.value.replace('_', ' ').title()} has concluded")
                self.market_cycle.active_cycle = None
                cycle_ended = True

        # Update pending news impacts (decrement counters, display messages)
        impact_messages = []
        for impact in self.market_news.pending_impacts[:]:  # Copy list to allow removal
            impact.weeks_until_impact -= 1
            if impact.weeks_until_impact == 0:
                # News impact is now occurring (already in precompiled prices)
                if impact.is_real:
                    impact_messages.append(f"📰 {impact.company_name}: {impact.news_text} - Stock moves sharply!")
                self.market_news.pending_impacts.remove(impact)

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

        # Update themed investment prices
        self.gold.update_price()
        self.holy_water.update_price()
        self.elf_queen_water.update_price()
        self.gold_coin.update_price()
        self.void_stocks.update_price()
        self.void_catalyst.update_price()

        # Check for Void Catalyst auto-sell
        for player in self.players:
            was_sold, msg, amount = player.process_void_catalyst_auto_sell(self.void_catalyst)
            if was_sold:
                print(f"\n{'='*60}")
                print(f"VOID CATALYST AUTO-SELL - {player.name}")
                print(f"{'='*60}")
                print(msg)
                print(f"{'='*60}")
                input("\nPress Enter to continue...")

        # Update future prices: shift array and calculate new week+4
        # If a cycle was triggered or ended, recalculate all future prices
        # Otherwise, just shift the array and add one new week
        if cycle_triggered or cycle_ended:
            # Major market event - recalculate all future prices
            self._precalculate_future_prices()
        else:
            # Normal week - shift prices and calculate one new week+4
            self._advance_future_prices()

    def _advance_future_prices(self):
        """
        Advance future prices by one week: shift array and calculate new week+4.
        This preserves the deterministic future while adding one more week ahead.
        """
        for company_name, company in self.companies.items():
            if company_name not in self.future_prices or len(self.future_prices[company_name]) == 0:
                # No existing future prices - recalculate all
                self._precalculate_future_prices()
                return

            # Shift array: remove week+1 (which is now current), keep weeks +2, +3, +4
            remaining_prices = self.future_prices[company_name][1:]

            # Calculate new week+5 (which becomes the new week+4)
            week_ahead = 4  # We're calculating the 4th week ahead
            future_week = self.week_number + week_ahead
            simulated_price = remaining_prices[-1] if remaining_prices else company.price

            # Apply market cycle effects if active
            cycle_effect = 0.0
            if self.market_cycle.active_cycle:
                # Check if cycle will still be active
                weeks_left = self.market_cycle.active_cycle.weeks_remaining - (week_ahead - 1)
                if weeks_left > 0:
                    cycle_type = self.market_cycle.active_cycle.cycle_type
                    cycle_effect = self._get_cycle_effect(cycle_type, company.industry)

            # Check if a new cycle will trigger at this future week
            elif future_week > 0 and future_week % 24 == 0:
                # A new cycle would trigger - we don't know which type, so use neutral
                cycle_effect = 0.0

            # Apply cycle effect or random walk
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

            # Update future prices: old weeks +2, +3, +4 become new +1, +2, +3, and add new +4
            self.future_prices[company_name] = remaining_prices + [simulated_price]

    def _precalculate_future_prices(self):
        """
        Pre-calculate the next 4 weeks of prices for all companies.
        This data is NEVER shown to players, but used for news/research generation.
        """
        import copy

        # Clear existing future prices
        self.future_prices = {}

        # For each company, calculate future prices
        for company_name, company in self.companies.items():
            future_company_prices = []

            # Create a deep copy of game state for simulation
            for week_ahead in range(1, 5):  # Calculate week+1 through week+4
                future_week = self.week_number + week_ahead

                # Start with current price
                if week_ahead == 1:
                    simulated_price = company.price
                else:
                    # Use the previously calculated week price
                    simulated_price = future_company_prices[week_ahead - 2]

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
            elif industry == "Mana Extraction":
                # Mana becomes more valuable during energy crises
                return random.uniform(5.0, 10.0)
            else:
                return -random.uniform(2.0, 4.0)
        elif cycle_type == MarketCycleType.MARKET_CRASH:
            if industry == "Golem Manufacturing":
                # Golems crash HARD during market panic (fear of automation)
                return -random.uniform(12.0, 20.0)
            elif industry == "Mana Extraction":
                # Mana extraction faces extreme volatility
                return -random.uniform(10.0, 18.0)
            else:
                return -random.uniform(8.0, 15.0)
        elif cycle_type == MarketCycleType.RECOVERY:
            if industry == "Golem Manufacturing":
                # Golems recover slower (trust issues)
                return random.uniform(3.0, 6.0)
            else:
                return random.uniform(5.0, 10.0)
        elif cycle_type == MarketCycleType.TECH_BOOM:
            if industry in ["Technology", "Electronics"]:
                return random.uniform(7.0, 12.0)
            elif industry == "Golem Manufacturing":
                # Golems BOOM during tech boom (automation hype)
                return random.uniform(10.0, 15.0)
            elif industry == "Mana Extraction":
                # Mana benefits from tech boom (clean energy hype)
                return random.uniform(6.0, 10.0)
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

        # Apply weekly short borrow fees
        short_fees = player.apply_short_borrow_fees(self.companies)
        if short_fees > 0:
            print(f"📉 Weekly short borrow fees: ${short_fees:.2f}")

        # Apply monthly passive income from Quantum Singularity (every 4 weeks)
        if self.week_number % 4 == 0:
            qs_income = player.apply_quantum_singularity_income(self.quantum_singularity)
            if qs_income > 0:
                print(f"\n⚛️ Quantum Singularity passive income: ${qs_income:.2f}")

        # Check for margin call
        if player.check_margin_call(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst):
            print("\n" + "⚠️ " + "="*58)
            print("MARGIN CALL ALERT!")
            print("="*60)
            print("Your equity has fallen below 30% of your total position!")
            print("You must either deposit cash or sell assets to reduce leverage.")
            equity = player.calculate_equity(self.companies, self.treasury, self.gold, self.holy_water, None, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
            print(f"Current Equity: ${equity:.2f}")
            print(f"Borrowed Amount: ${player.borrowed_amount:.2f}")
            print(f"Required Action: Increase equity or repay loan immediately!")
            print("="*60)
            input("\nPress Enter to continue...")

        # Generate monthly news every 4 weeks (can have hoaxes, small impact)
        if self.week_number % 4 == 0:
            self.pending_news_display = self.market_news.generate_news(self.companies, self.week_number, self.future_prices)
        else:
            self.pending_news_display = None

        # Generate quarterly market movements every 12 weeks (always real, large impact)
        if self.week_number % 12 == 0:
            # Market movements override monthly news if both occur same week
            self.pending_news_display = self.market_news.generate_market_movement(self.companies, self.week_number, self.future_prices)

        # Generate weekly gazette news (every week)
        self.pending_weekly_news = self.weekly_gazette.generate_weekly_news(self.companies, self.week_number)

        # Generate market chronicle news (every week)
        self.pending_chronicle_news = self.market_chronicle.generate_chronicle_news(self.companies, self.week_number)

        while True:
            print("\n" + "-"*60)
            print("What would you like to do?")
            print("-"*60)
            print("1. View Market Prices")
            print("2. View My Portfolio")
            print("3. Buy Stocks")
            print("4. Sell Stocks")
            print("5. Short Sell Stocks")
            print("6. Cover Short Position")
            print("7. Buy Treasury Bonds")
            print("8. Sell Treasury Bonds")
            print("9. Buy Themed Investments (Gold, Holy Water, Quantum Singularity)")
            print("10. Sell Themed Investments (Gold, Holy Water)")
            print("11. Borrow Money (Leverage)")
            print("12. Repay Loan")
            print("13. Save Game")
            print("14. End Turn")
            print("-"*60)

            choice = input("Enter choice (1-14): ").strip()

            if choice == "1":
                self.display_market()

            elif choice == "2":
                player.display_portfolio(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)

            elif choice == "3":
                self._buy_stocks_menu(player)

            elif choice == "4":
                self._sell_stocks_menu(player)

            elif choice == "5":
                self._short_sell_menu(player)

            elif choice == "6":
                self._cover_short_menu(player)

            elif choice == "7":
                self._buy_treasury_menu(player)

            elif choice == "8":
                self._sell_treasury_menu(player)

            elif choice == "9":
                self._buy_themed_investments_menu(player)

            elif choice == "10":
                self._sell_themed_investments_menu(player)

            elif choice == "11":
                self._borrow_money_menu(player)

            elif choice == "12":
                self._repay_loan_menu(player)

            elif choice == "13":
                filename = input("Enter save filename (default: savegame.json): ").strip()
                if not filename:
                    filename = "savegame.json"
                self.save_game(filename)

            elif choice == "14":
                # Check for margin call warning before ending turn
                if player.check_margin_call(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst):
                    print("\n" + "⚠️ " + "="*58)
                    print("⚠️  MARGIN CALL WARNING!")
                    print("="*60)
                    print("If you end your turn now, you will be subject to FORCED LIQUIDATION!")
                    print("Your equity has fallen below the required maintenance margin.")
                    print()
                    equity = player.calculate_equity(self.companies, self.treasury, self.gold, self.holy_water, None, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
                    print(f"Current Equity: ${equity:.2f}")
                    print(f"Borrowed Amount: ${player.borrowed_amount:.2f}")
                    if player.borrowed_amount > 0:
                        total_position = equity + player.borrowed_amount
                        if total_position > 0:
                            equity_ratio = (equity / total_position) * 100
                            print(f"Equity Ratio: {equity_ratio:.1f}% (Minimum Required: 30%)")

                    if len(player.short_positions) > 0:
                        short_value = sum(player.short_positions[name] * self.companies[name].price
                                        for name in player.short_positions)
                        required_equity = short_value * 1.25
                        print(f"Short Position Value: ${short_value:.2f}")
                        print(f"Required Equity for Shorts: ${required_equity:.2f} (125% maintenance margin)")

                    print()
                    print("Recommended actions:")
                    print("• Deposit cash or sell assets to improve equity")
                    print("• Repay loans to reduce leverage")
                    print("• Cover short positions")
                    print("="*60)

                    confirm = input("\nAre you SURE you want to end your turn? (yes/no): ").strip().lower()
                    if confirm != "yes":
                        print("Turn not ended. You can continue trading.")
                        continue

                print(f"\n{player.name} has ended their turn.")
                break

            else:
                print("Invalid choice! Please enter a number between 1 and 15.")

    def _buy_stocks_menu(self, player: Player):
        """Menu for buying stocks"""
        print("\n" + "="*60)
        print("BUY STOCKS")
        print("="*60)
        print(f"Available Cash: ${player.cash:.2f}")
        equity = player.calculate_equity(self.companies, self.treasury)
        print(f"Current Equity: ${equity:.2f}")
        max_can_borrow = max(0, equity * player.max_leverage_ratio - player.borrowed_amount)
        print(f"Max additional leverage: ${max_can_borrow:.2f}")
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

                # Get dollar amount to invest
                dollar_input = input(f"How much $ to invest in {company.name}? ")
                dollar_amount = float(dollar_input)

                if dollar_amount <= 0:
                    print("Invalid amount!")
                    return

                if dollar_amount > player.cash:
                    print(f"Insufficient funds! You have ${player.cash:.2f}")
                    return

                # Get leverage
                leverage_input = input("Leverage multiplier (1.0 = no leverage, 2.0 = 2x, etc.): ")
                leverage = float(leverage_input) if leverage_input.strip() else 1.0

                if leverage < 1.0:
                    print("Leverage must be at least 1.0!")
                    return

                # Show preview
                total_investment = dollar_amount * leverage
                borrowed_amount = total_investment - dollar_amount
                estimated_shares = total_investment / company.price

                print(f"\nInvestment Preview:")
                print(f"  Your cash: ${dollar_amount:.2f}")
                if leverage > 1.0:
                    print(f"  Borrowed: ${borrowed_amount:.2f}")
                    print(f"  Total investment: ${total_investment:.2f} ({leverage:.1f}x leverage)")
                print(f"  Current price: ${company.price:.2f} per share")
                print(f"  Estimated shares: ~{estimated_shares:.4f}")

                confirm = input("\nConfirm purchase? (y/n): ")
                if confirm.lower() != 'y':
                    print("Purchase cancelled.")
                    return

                success, message = player.buy_stock(company, dollar_amount, leverage, self.companies, self.treasury)
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
            position_value = shares * company.price
            print(f"{i}. {company_name}: {shares:.4f} shares @ ${company.price:.2f} (Value: ${position_value:.2f})")
        print("0. Cancel")

        try:
            choice = int(input("\nSelect stock to sell (0 to cancel): "))
            if choice == 0:
                return

            if 1 <= choice <= len(portfolio_items):
                company_name, owned_shares = portfolio_items[choice - 1]
                company = self.companies[company_name]
                position_value = owned_shares * company.price

                print(f"\nYou own {owned_shares:.4f} shares (Value: ${position_value:.2f})")
                print("Enter amount to sell:")
                print("  - Dollar amount (e.g., 1000)")
                print("  - 'all' to sell entire position")

                sell_input = input("Amount: ").strip().lower()

                if sell_input == 'all':
                    success, message = player.sell_stock(company, shares=owned_shares)
                else:
                    try:
                        dollar_amount = float(sell_input)
                        if dollar_amount <= 0:
                            print("Invalid amount!")
                            return

                        success, message = player.sell_stock(company, dollar_amount=dollar_amount)
                    except ValueError:
                        print("Invalid input!")
                        return

                print(f"\n{message}")
            else:
                print("Invalid choice!")

        except ValueError:
            print("Invalid input!")

    def _short_sell_menu(self, player: Player):
        """Menu for short selling stocks"""
        print("\n" + "="*60)
        print("SHORT SELL STOCKS")
        print("="*60)
        print(f"Available Cash: ${player.cash:.2f}")
        equity = player.calculate_equity(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
        print(f"Current Equity: ${equity:.2f}")
        print()
        print("⚠️  WARNING: Short selling is risky! Losses can be unlimited if prices rise.")
        print("Margin Requirement: 150% of short value in equity")
        print()

        companies_list = list(self.companies.values())
        for i, company in enumerate(companies_list, 1):
            print(f"{i}. {company}")
        print("0. Cancel")

        try:
            choice = int(input("\nSelect stock to short (0 to cancel): "))
            if choice == 0:
                return

            if 1 <= choice <= len(companies_list):
                company = companies_list[choice - 1]
                shares = int(input("How many shares to short? "))

                if shares <= 0:
                    print("Invalid number of shares!")
                    return

                # Calculate effective price with slippage
                slippage_factor = company.calculate_slippage(shares, is_buy=False)
                effective_price = company.price * slippage_factor
                total_proceeds = effective_price * shares
                required_equity = company.price * shares * 1.5

                print(f"\nQuoted price: ${company.price:.2f} per share")
                print(f"Effective price (with slippage): ${effective_price:.2f} per share")
                print(f"Total proceeds: ${total_proceeds:.2f}")
                print(f"Required equity: ${required_equity:.2f} (you have ${equity:.2f})")

                success, message = player.short_sell(company, shares, self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
                print(f"\n{message}")
            else:
                print("Invalid choice!")

        except ValueError:
            print("Invalid input!")

    def _cover_short_menu(self, player: Player):
        """Menu for covering short positions"""
        print("\n" + "="*60)
        print("COVER SHORT POSITIONS")
        print("="*60)
        print(f"Available Cash: ${player.cash:.2f}")
        print()

        if not player.short_positions:
            print("You don't have any short positions!")
            return

        short_items = list(player.short_positions.items())
        for i, (company_name, shares) in enumerate(short_items, 1):
            company = self.companies[company_name]
            obligation = company.price * shares
            print(f"{i}. {company_name}: {shares} shares shorted @ ${company.price:.2f} (obligation: ${obligation:.2f})")
        print("0. Cancel")

        try:
            choice = int(input("\nSelect short position to cover (0 to cancel): "))
            if choice == 0:
                return

            if 1 <= choice <= len(short_items):
                company_name, shorted_shares = short_items[choice - 1]
                company = self.companies[company_name]

                shares = int(input(f"How many shares to cover (you have {shorted_shares} shorted)? "))

                if shares <= 0:
                    print("Invalid number of shares!")
                    return

                # Calculate effective price with slippage
                slippage_factor = company.calculate_slippage(shares, is_buy=True)
                effective_price = company.price * slippage_factor
                total_cost = effective_price * shares

                print(f"\nQuoted price: ${company.price:.2f} per share")
                print(f"Effective price (with slippage): ${effective_price:.2f} per share")
                print(f"Total cost to cover: ${total_cost:.2f}")

                success, message = player.cover_short(company, shares)
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

    def _sell_treasury_menu(self, player: Player):
        """Menu for selling treasury bonds"""
        print("\n" + "="*60)
        print("SELL TREASURY BONDS")
        print("="*60)
        print(f"Your Holdings: {player.treasury_bonds} bonds")
        print(f"{self.treasury}")
        print()

        if player.treasury_bonds == 0:
            print("You don't own any treasury bonds!")
            return

        try:
            bonds = int(input(f"How many bonds to sell (you have {player.treasury_bonds})? "))

            if bonds <= 0:
                print("Invalid number of bonds!")
                return

            total_value = self.treasury.price * bonds
            print(f"\nTotal value: ${total_value:.2f}")

            success, msg = player.sell_treasury(self.treasury, bonds)
            print(msg)

        except ValueError:
            print("Invalid input!")

    def _buy_themed_investments_menu(self, player: Player):
        """Menu for buying themed investments"""
        print("\n" + "="*60)
        print("BUY THEMED INVESTMENTS")
        print("="*60)
        print(f"Available Cash: ${player.cash:.2f}")
        print()
        print("1. " + str(self.quantum_singularity))
        print("2. " + str(self.gold))
        print("3. " + str(self.holy_water))
        print("4. " + str(self.elf_queen_water))
        print("5. " + str(self.gold_coin))
        print("6. " + str(self.void_stocks))
        print("7. " + str(self.void_catalyst))
        print("0. Cancel")
        print()

        try:
            choice = int(input("Select investment (0 to cancel): "))

            if choice == 0:
                return
            elif choice == 1:
                # Quantum Singularity
                units = int(input("How many units to purchase? "))
                if units <= 0:
                    print("Invalid number of units!")
                    return
                success, msg = player.buy_quantum_singularity(self.quantum_singularity, units)
                print(msg)
            elif choice == 2:
                # Gold
                ounces = int(input("How many ounces to purchase? "))
                if ounces <= 0:
                    print("Invalid number of ounces!")
                    return
                success, msg = player.buy_gold(self.gold, ounces)
                print(msg)
            elif choice == 3:
                # Holy Water
                vials = int(input("How many vials to purchase? "))
                if vials <= 0:
                    print("Invalid number of vials!")
                    return
                success, msg = player.buy_holy_water(self.holy_water, vials)
                print(msg)
            elif choice == 4:
                # Elf Queen's Water
                vials = int(input("How many vials to purchase? "))
                if vials <= 0:
                    print("Invalid number of vials!")
                    return
                success, msg = player.buy_elf_queen_water(self.elf_queen_water, vials)
                print(msg)
            elif choice == 5:
                # Gold Coin
                coins = int(input("How many coins to purchase? "))
                if coins <= 0:
                    print("Invalid number of coins!")
                    return
                success, msg = player.buy_gold_coin(self.gold_coin, coins)
                print(msg)
            elif choice == 6:
                # Void Stocks
                shares = int(input("How many shares to purchase? "))
                if shares <= 0:
                    print("Invalid number of shares!")
                    return
                success, msg = player.buy_void_stocks(self.void_stocks, shares)
                print(msg)
            elif choice == 7:
                # Void Catalyst
                confirm = input(f"Buy Void Catalyst for ${self.void_catalyst.price:.2f}? (y/n): ")
                if confirm.lower() == 'y':
                    # Get list of all human player names (excluding NPCs)
                    human_players = [p.name for p in self.players]
                    success, msg = player.buy_void_catalyst(self.void_catalyst, human_players)
                    print(msg)
            else:
                print("Invalid choice!")

        except ValueError:
            print("Invalid input!")

    def _sell_themed_investments_menu(self, player: Player):
        """Menu for selling themed investments"""
        print("\n" + "="*60)
        print("SELL THEMED INVESTMENTS")
        print("="*60)
        print(f"Note: Quantum Singularity & Void Catalyst cannot be sold manually")
        print()
        print(f"Your Holdings:")
        print(f"  Gold: {player.gold_ounces} oz @ ${self.gold.price:.2f}")
        print(f"  Holy Water: {player.holy_water_vials} vials @ ${self.holy_water.price:.2f}")
        print(f"  Elf Queen's Water: {player.elf_queen_water_vials} vials @ ${self.elf_queen_water.price:.2f}")
        print(f"  Gold Coin: {player.gold_coins} coins @ ${self.gold_coin.price:.2f}")
        print(f"  Void Stocks: {player.void_stocks_shares} shares @ ${self.void_stocks.price:.2f}")
        print()
        print("1. Sell Gold")
        print("2. Sell Holy Water")
        print("3. Sell Elf Queen's Water")
        print("4. Sell Gold Coin")
        print("5. Sell Void Stocks")
        print("0. Cancel")
        print()

        try:
            choice = int(input("Select investment (0 to cancel): "))

            if choice == 0:
                return
            elif choice == 1:
                # Gold
                if player.gold_ounces == 0:
                    print("You don't own any gold!")
                    return
                ounces = int(input(f"How many ounces to sell (you have {player.gold_ounces})? "))
                if ounces <= 0:
                    print("Invalid number of ounces!")
                    return
                success, msg = player.sell_gold(self.gold, ounces)
                print(msg)
            elif choice == 2:
                # Holy Water
                if player.holy_water_vials == 0:
                    print("You don't own any Holy Water!")
                    return
                vials = int(input(f"How many vials to sell (you have {player.holy_water_vials})? "))
                if vials <= 0:
                    print("Invalid number of vials!")
                    return
                success, msg = player.sell_holy_water(self.holy_water, vials)
                print(msg)
            elif choice == 3:
                # Elf Queen's Water
                if player.elf_queen_water_vials == 0:
                    print("You don't own any Elf Queen's Water!")
                    return
                vials = int(input(f"How many vials to sell (you have {player.elf_queen_water_vials})? "))
                if vials <= 0:
                    print("Invalid number of vials!")
                    return
                success, msg = player.sell_elf_queen_water(self.elf_queen_water, vials)
                print(msg)
            elif choice == 4:
                # Gold Coin
                if player.gold_coins == 0:
                    print("You don't own any Gold Coins!")
                    return
                coins = int(input(f"How many coins to sell (you have {player.gold_coins})? "))
                if coins <= 0:
                    print("Invalid number of coins!")
                    return
                success, msg = player.sell_gold_coin(self.gold_coin, coins)
                print(msg)
            elif choice == 5:
                # Void Stocks
                if player.void_stocks_shares == 0:
                    print("You don't own any Void Stocks!")
                    return
                shares = int(input(f"How many shares to sell (you have {player.void_stocks_shares})? "))
                if shares <= 0:
                    print("Invalid number of shares!")
                    return
                success, msg = player.sell_void_stocks(self.void_stocks, shares)
                print(msg)
            else:
                print("Invalid choice!")

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
                'market_chronicle': self.market_chronicle.to_dict(),
                'pending_weekly_news': self.pending_weekly_news,
                'pending_chronicle_news': self.pending_chronicle_news,
                'future_prices': self.future_prices,
                'random_state': list(random.getstate()),  # Save random state for deterministic futures
                'quantum_singularity': self.quantum_singularity.to_dict(),
                'gold': self.gold.to_dict(),
                'holy_water': self.holy_water.to_dict(),
                'elf_queen_water': self.elf_queen_water.to_dict(),
                'gold_coin': self.gold_coin.to_dict(),
                'void_stocks': self.void_stocks.to_dict(),
                'void_catalyst': self.void_catalyst.to_dict()
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
            # Convert pending_weekly_news from history format (3-tuple) to display format (2-tuple) if needed
            pending_weekly_raw = game_state.get('pending_weekly_news', None)
            if pending_weekly_raw:
                game.pending_weekly_news = []
                for item in pending_weekly_raw:
                    if len(item) == 3:
                        # History format: (week_number, news_text, is_real) -> display format: (news_text, is_real)
                        game.pending_weekly_news.append((item[1], item[2]))
                    elif len(item) == 2:
                        # Already in display format: (news_text, is_real)
                        game.pending_weekly_news.append(tuple(item))
                    else:
                        # Unexpected format - skip this item to prevent crashes
                        print(f"Warning: Skipping malformed weekly news item with {len(item)} elements")
            else:
                game.pending_weekly_news = None

            # Restore market chronicle
            game.market_chronicle = MarketChronicle.from_dict(game_state.get('market_chronicle', {'chronicle_news_history': []}))
            # Convert pending_chronicle_news from history format (3-tuple) to display format (2-tuple) if needed
            pending_chronicle_raw = game_state.get('pending_chronicle_news', None)
            if pending_chronicle_raw:
                game.pending_chronicle_news = []
                for item in pending_chronicle_raw:
                    if len(item) == 3:
                        # History format: (week_number, news_text, is_real) -> display format: (news_text, is_real)
                        game.pending_chronicle_news.append((item[1], item[2]))
                    elif len(item) == 2:
                        # Already in display format: (news_text, is_real)
                        game.pending_chronicle_news.append(tuple(item))
                    else:
                        # Unexpected format - skip this item to prevent crashes
                        print(f"Warning: Skipping malformed chronicle news item with {len(item)} elements")
            else:
                game.pending_chronicle_news = None

            # Restore future prices (or recalculate if not present in save file)
            if 'future_prices' in game_state:
                game.future_prices = game_state['future_prices']
            else:
                # Old save file - recalculate future prices
                game.future_prices = {}
                game._precalculate_future_prices()

            # Restore random state for deterministic futures
            if 'random_state' in game_state:
                # Convert list back to tuple for setstate
                state_list = game_state['random_state']
                # The state is (version, state_tuple_of_625_ints, gauss_next)
                # JSON converts tuples to lists, so we need to convert back
                random_state = (
                    state_list[0],  # version (int)
                    tuple(state_list[1]),  # state tuple (convert list back to tuple)
                    state_list[2]  # gauss_next (None or float)
                )
                random.setstate(random_state)

            # Restore themed investments (or create new instances if not present in save file)
            if 'quantum_singularity' in game_state:
                game.quantum_singularity = QuantumSingularity.from_dict(game_state['quantum_singularity'])
            else:
                game.quantum_singularity = QuantumSingularity()

            if 'gold' in game_state:
                game.gold = Gold.from_dict(game_state['gold'])
            else:
                game.gold = Gold()

            if 'holy_water' in game_state:
                game.holy_water = HolyWater.from_dict(game_state['holy_water'])
            else:
                game.holy_water = HolyWater()

            if 'elf_queen_water' in game_state:
                game.elf_queen_water = ElfQueenWater.from_dict(game_state['elf_queen_water'])
            else:
                game.elf_queen_water = ElfQueenWater()

            if 'gold_coin' in game_state:
                game.gold_coin = GoldCoin.from_dict(game_state['gold_coin'])
            else:
                game.gold_coin = GoldCoin()

            if 'void_stocks' in game_state:
                game.void_stocks = VoidStocks.from_dict(game_state['void_stocks'], game.companies)
            else:
                game.void_stocks = VoidStocks(game.companies)

            if 'void_catalyst' in game_state:
                game.void_catalyst = VoidCatalyst.from_dict(game_state['void_catalyst'])
            else:
                game.void_catalyst = VoidCatalyst()

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
                if player.check_margin_call(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst):
                    actions = player.force_liquidate_margin_call(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
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
