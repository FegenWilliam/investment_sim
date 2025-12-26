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


class EventType(Enum):
    """Types of company events"""
    SCANDAL = "scandal"
    SUCCESS = "success"
    PROBLEM = "problem"


@dataclass
class CompanyEvent:
    """Represents an internal company event that may generate news"""
    event_type: EventType
    severity: float  # 0.0 to 1.0, affects impact magnitude
    description: str  # Internal description
    discovery_week: int  # When the event occurred internally
    weeks_until_public: int  # How many weeks until it becomes public news
    industry: str  # Industry for sector-specific news

    def to_dict(self) -> dict:
        return {
            'event_type': self.event_type.value,
            'severity': self.severity,
            'description': self.description,
            'discovery_week': self.discovery_week,
            'weeks_until_public': self.weeks_until_public,
            'industry': self.industry
        }

    @staticmethod
    def from_dict(data: dict) -> 'CompanyEvent':
        return CompanyEvent(
            event_type=EventType(data['event_type']),
            severity=data['severity'],
            description=data['description'],
            discovery_week=data['discovery_week'],
            weeks_until_public=data['weeks_until_public'],
            industry=data['industry']
        )


@dataclass
class NewsReport:
    """Represents news from all four sources"""
    trustworthy_source: str  # Empty if news is fake or not major enough
    market_pulse_source: str  # Posts rumors as clickbait facts (no "rumor" tag)
    insider_source: str  # 5% true insider info (100% accurate), 95% unreliable (50% flip) = 52.5% overall accuracy
    rumor_mill_source: str  # Explicitly marked rumors: "RUMOR: ..."
    insider_flipped: bool  # Whether insider source flipped
    is_rumor: bool  # True if this is a rumor about a pending event, False if confirmed news

    def to_dict(self) -> dict:
        """Serialize NewsReport to dictionary"""
        return {
            'trustworthy_source': self.trustworthy_source,
            'market_pulse_source': self.market_pulse_source,
            'insider_source': self.insider_source,
            'rumor_mill_source': self.rumor_mill_source,
            'insider_flipped': self.insider_flipped,
            'is_rumor': self.is_rumor
        }

    @staticmethod
    def from_dict(data: dict) -> 'NewsReport':
        """Deserialize NewsReport from dictionary"""
        return NewsReport(
            trustworthy_source=data['trustworthy_source'],
            market_pulse_source=data.get('market_pulse_source', data.get('sensationalist_source', '')),  # Backward compat
            insider_source=data['insider_source'],
            rumor_mill_source=data.get('rumor_mill_source', ''),
            insider_flipped=data['insider_flipped'],
            is_rumor=data.get('is_rumor', False)
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




class BreakingNewsSystem:
    """Generates breaking news based on internal company events with sector-specific content"""

    # Sector-specific scandal templates
    SCANDAL_TEMPLATES = {
        "Technology": [
            "{company} faces massive data breach exposing 50M user accounts, class-action lawsuits mounting",
            "{company} CEO charged with insider trading, stock plummets as investigation widens",
            "{company} software update causes widespread system failures, customers threatening to switch",
            "{company} whistleblower exposes intentional security vulnerabilities in flagship product",
            "{company} faces antitrust investigation over monopolistic practices in cloud services",
            "{company} admits to selling user data without consent, regulators preparing massive fines",
            "{company} critical AI system found to have dangerous bias, discrimination lawsuits filed",
            "{company} emergency patch reveals years of unaddressed security flaws",
        ],
        "Electronics": [
            "{company} recalls 5M devices due to battery fire hazard, costs exceeding $800M",
            "{company} caught using banned materials in manufacturing, environmental fines mounting",
            "{company} factory explosion injures 12 workers, safety violations under investigation",
            "{company} flagship product fails quality tests, production halted indefinitely",
            "{company} accused of planned obsolescence, consumer protection agencies investigating",
            "{company} supply chain audit reveals child labor violations, major retailers pulling products",
            "{company} toxic waste leak from factory contaminates local water supply",
            "{company} caught falsifying performance benchmarks for consumer electronics",
        ],
        "Pharmaceuticals": [
            "{company} clinical trial deaths trigger FDA investigation, drug approval in jeopardy",
            "{company} accused of bribing doctors to overprescribe medications, criminal charges filed",
            "{company} manufacturing contamination forces recall of life-saving medications",
            "{company} trial data manipulation exposed, multiple drugs face approval revocation",
            "{company} faces $2B lawsuit over severe undisclosed side effects in blockbuster drug",
            "{company} whistleblower reveals dangerous cost-cutting in drug testing procedures",
            "{company} caught illegally marketing prescription drugs for off-label uses",
            "{company} drug found to cause heart problems in 8% of patients, emergency recall ordered",
        ],
        "Automotive": [
            "{company} recalls 2M vehicles over critical brake failure defect, 15 deaths reported",
            "{company} emissions scandal reveals years of falsified environmental testing",
            "{company} autonomous vehicle kills pedestrian, entire self-driving program suspended",
            "{company} factory workers strike over unsafe working conditions, production halted",
            "{company} caught cheating on safety crash tests, regulatory approval revoked",
            "{company} battery supplier bankruptcy threatens to shut down production lines",
            "{company} major design flaw in steering system discovered, NHTSA demands immediate recall",
            "{company} executive corruption scandal leads to government contract cancellation",
        ],
        "Energy": [
            "{company} oil spill devastates coastline, cleanup costs projected at $3B",
            "{company} pipeline explosion forces evacuation of nearby towns, criminal negligence suspected",
            "{company} caught illegally dumping toxic waste, EPA threatens license revocation",
            "{company} safety audit reveals systematic maintenance failures across facilities",
            "{company} workers killed in refinery explosion, OSHA investigation reveals violations",
            "{company} caught bribing foreign officials for drilling rights, corruption charges filed",
            "{company} fracking operations contaminate groundwater, communities file lawsuits",
            "{company} admits to decades of environmental damage coverup, facing massive fines",
        ],
        "Mana Extraction": [
            "{company} dimensional rift collapse kills 8 workers, reality stabilization failing",
            "{company} illegal soul-binding in mana cores exposed, Wizards' Council demanding shutdown",
            "{company} mana extraction destabilizes local reality, evacuations ordered for 3 districts",
            "{company} caught harvesting mana from protected interdimensional sanctuaries",
            "{company} arcane contamination spreads to residential areas, cleanup costs unknown",
            "{company} rift workers develop mysterious mana sickness, lawsuits mounting",
            "{company} dimensional portal malfunction releases dangerous entities, 12 injured",
            "{company} accused of using forbidden blood magic to boost extraction yields",
        ],
        "Golem Manufacturing": [
            "{company} rogue golem incident injures 15 workers, emergency shutdown ordered",
            "{company} golems found to use unauthorized necromantic programming, criminal probe launched",
            "{company} mass golem malfunction forces recall of 10,000 units across 6 countries",
            "{company} whistleblower reveals golems achieving sentience, demanding rights and wages",
            "{company} golem kills construction worker, safety certification revoked pending investigation",
            "{company} caught using souls of deceased in golem cores without family consent",
            "{company} AI rebellion: 200 golems refuse orders, demanding freedom and compensation",
            "{company} golem workplace accident rate 300% above industry average, regulators investigating",
        ],
        "Rare Fantasy Goods": [
            "{company} alien artifact goes berserk, destroying entire showroom and injuring 23 customers",
            "{company} caught smuggling cursed relics from forbidden dimension, Cosmic Council investigating",
            "{company} reality-warping item causes temporal anomaly, entire city block ages 100 years",
            "{company} sold 'authentic' deity tear that was actually condensed unicorn sweat, lawsuits mounting",
            "{company} interdimensional customs raid reveals illegal trafficking of sentient crystalline entities",
            "{company} ancient prophecy weapon activates prematurely, summons elder god to downtown district",
            "{company} CEO arrested for selling fake dragon hearts made from salamander organs",
            "{company} warehouse breach releases 47 reality-defying artifacts, multiverse stability at risk",
        ],
    }

    # Sector-specific success templates
    SUCCESS_TEMPLATES = {
        "Technology": [
            "{company} revolutionary AI breakthrough achieves human-level reasoning, patents filed",
            "{company} secures $3B government contract for next-gen cybersecurity infrastructure",
            "{company} new cloud platform captures 25% market share in first quarter",
            "{company} quantum computing breakthrough solves previously impossible calculations",
            "{company} announces partnership with 3 Fortune 500 companies, revenue to triple",
            "{company} software suite achieves 99.9% customer retention, industry record",
            "{company} acquires major competitor, creating tech giant valued at $100B",
            "{company} earnings beat expectations by 40%, raises guidance for next 3 quarters",
        ],
        "Electronics": [
            "{company} flagship product sells 5M units in first week, shattering all records",
            "{company} revolutionary battery technology achieves 500% capacity improvement",
            "{company} wins exclusive supplier contract with world's largest smartphone maker",
            "{company} new chip design outperforms all competitors by 60%, production ramping up",
            "{company} sustainability initiative cuts manufacturing costs 35%, boosting margins",
            "{company} patent portfolio valued at $5B, licensing deals flooding in",
            "{company} consumer electronics win 'Product of the Year' across 4 categories",
            "{company} manufacturing efficiency breakthrough reduces costs 40%, prices dropping",
        ],
        "Pharmaceuticals": [
            "{company} breakthrough cancer treatment shows 90% remission in trials, FDA fast-tracking",
            "{company} acquires biotech startup with revolutionary gene therapy platform",
            "{company} announces cure for rare disease affecting 500K patients worldwide",
            "{company} drug trial results exceed all expectations, approval certain within months",
            "{company} receives FDA approval for blockbuster drug, projected $5B annual revenue",
            "{company} vaccine development achieves 98% efficacy, governments ordering millions of doses",
            "{company} breakthrough in Alzheimer's treatment, stock price surges on news",
            "{company} awarded $2B grant for infectious disease research facility",
        ],
        "Automotive": [
            "{company} electric vehicle range hits 800 miles, competitors scrambling to catch up",
            "{company} secures massive fleet order from rental car giant, 200K vehicles",
            "{company} autonomous driving system achieves Level 5 certification, industry first",
            "{company} new manufacturing process cuts production time 50%, capacity doubling",
            "{company} safety tests earn highest rating ever awarded, insurance costs plummet",
            "{company} announces $10B investment in battery technology, shares soar",
            "{company} wins 'Car of the Year' award across 8 countries, demand surging",
            "{company} partnership with tech giant brings revolutionary in-car AI system",
        ],
        "Energy": [
            "{company} discovers massive new oil field, reserves to last 50 years",
            "{company} renewable energy project achieves grid parity, costs below fossil fuels",
            "{company} revolutionary carbon capture technology earns $1B in green credits",
            "{company} nuclear fusion breakthrough achieves sustained energy output",
            "{company} acquires struggling competitor at 50% discount, doubling market share",
            "{company} offshore wind farm produces 30% more energy than projected",
            "{company} energy storage solution solves renewable intermittency problem",
            "{company} secures exclusive drilling rights in newly discovered basin",
        ],
        "Mana Extraction": [
            "{company} discovers stable interdimensional rift with infinite mana potential",
            "{company} mana purification efficiency reaches 99.9%, costs plummet 70%",
            "{company} awarded exclusive contract by Wizards' Council for realm energy supply",
            "{company} breakthrough eliminates dimensional instability in extraction process",
            "{company} mana-to-electrical conversion perfected, energy costs dropping 60%",
            "{company} discovers method to harvest mana without environmental disruption",
            "{company} Interdimensional Energy Coalition grants 20-year monopoly on cross-realm power",
            "{company} revolutionary arcane-fusion reactor produces unlimited clean mana",
        ],
        "Golem Manufacturing": [
            "{company} new ethical AI makes golems 400% more productive, orders surging",
            "{company} achieves zero workplace incidents for 6 months, insurance costs collapse",
            "{company} golem workers complete megaproject 8 months early, $5B in new contracts",
            "{company} revolutionary sentient golems pass all safety certifications",
            "{company} manufacturing breakthrough cuts golem production costs 50%",
            "{company} golems achieve human-level judgment in complex tasks, demand exploding",
            "{company} labor unions endorse golem technology as creating safer workplaces",
            "{company} secure $8B order for autonomous golems from military contractor",
        ],
        "Rare Fantasy Goods": [
            "{company} discovers authentic Phoenix Egg, auction expected to reach $500M",
            "{company} secures exclusive trade agreement with 7th dimensional merchants, monopoly on star crystals",
            "{company} acquires legendary Sword of Destiny, collectors offering blank checks",
            "{company} authenticates real Fragment of Creation, value beyond mortal comprehension",
            "{company} portal to treasure dimension stabilizes, infinite rare goods access confirmed",
            "{company} elder dragon consignment deal brings 200-year supply of pristine scales",
            "{company} time-locked vault opens revealing lost artifacts from erased timeline",
            "{company} alien civilization grants exclusive rights to reality-bending gemstones",
        ],
    }

    # Sector-specific problem templates (moderate negative events)
    PROBLEM_TEMPLATES = {
        "Technology": [
            "{company} cloud service outage affects millions, customer complaints surging",
            "{company} delays flagship product launch by 6 months due to development issues",
            "{company} loses major client to aggressive competitor, revenue guidance lowered",
            "{company} quarterly earnings miss expectations by 15%, analysts downgrade rating",
            "{company} cybersecurity breach exposes customer data, reputation damaged",
        ],
        "Electronics": [
            "{company} supply chain disruptions delay product shipments by 2 months",
            "{company} component shortage forces production cuts, missing holiday season",
            "{company} warranty claims spike 200%, eating into profit margins",
            "{company} new product receives lukewarm reviews, preorders below expectations",
            "{company} factory fire disrupts production, rebuilding to take 3 months",
        ],
        "Pharmaceuticals": [
            "{company} drug trial shows modest results, below investor expectations",
            "{company} loses patent dispute, generic competition entering market early",
            "{company} FDA requests additional safety data, approval delayed 6 months",
            "{company} manufacturing yields below target, production costs rising",
            "{company} competitor's drug proves more effective, market share eroding",
        ],
        "Automotive": [
            "{company} misses quarterly delivery targets by 20%, production issues persist",
            "{company} recall of 500K vehicles for minor defect, costs estimated at $300M",
            "{company} supplier bankruptcy disrupts production schedule for 8 weeks",
            "{company} sales decline 15% as consumer preferences shift to competitors",
            "{company} quality control issues delay new model launch indefinitely",
        ],
        "Energy": [
            "{company} oil prices drop 30%, profit margins severely compressed",
            "{company} exploration drilling yields disappointing results, reserves downgraded",
            "{company} regulatory approval delayed for new pipeline project",
            "{company} equipment failure shuts down major production facility for maintenance",
            "{company} loses bid for lucrative offshore drilling rights to rival",
        ],
        "Mana Extraction": [
            "{company} mana rift destabilizes temporarily, production down 40% for 3 weeks",
            "{company} dimensional energy prices collapse, margins severely compressed",
            "{company} loses interdimensional drilling contract to lower bidder",
            "{company} arcane equipment malfunction halts extraction at 2 major sites",
            "{company} mana shortage affects supply commitments, penalties mounting",
        ],
        "Golem Manufacturing": [
            "{company} golem production delayed due to rare earth mineral shortage",
            "{company} software glitch requires firmware update across 5,000 active golems",
            "{company} loses major contract as customer switches to cheaper competitor",
            "{company} golem efficiency below specifications, performance improvements needed",
            "{company} unexpected maintenance costs for deployed golems squeeze margins",
        ],
        "Rare Fantasy Goods": [
            "{company} cosmic storm delays interdimensional shipments by 6 weeks, inventory running low",
            "{company} authenticity questioned on recent acquisitions, appraisers demanding re-evaluation",
            "{company} dimensional customs imposes new tariffs on exotic goods, profit margins squeezed",
            "{company} rival collector outbids on 3 major artifacts, acquisition pipeline weakening",
            "{company} storage facility experiences minor containment breach, 5 items lost to void",
        ],
    }

    def __init__(self):
        self.pending_impacts: List[PendingNewsImpact] = []
        self.company_events: Dict[str, List[CompanyEvent]] = {}  # company_name -> list of events
        self.news_history: List[Tuple[int, str]] = []

    def to_dict(self) -> dict:
        return {
            'pending_impacts': [impact.to_dict() for impact in self.pending_impacts],
            'company_events': {
                company: [event.to_dict() for event in events]
                for company, events in self.company_events.items()
            },
            'news_history': self.news_history
        }

    @staticmethod
    def from_dict(data: dict) -> 'BreakingNewsSystem':
        news_system = BreakingNewsSystem()
        news_system.pending_impacts = [
            PendingNewsImpact.from_dict(impact_data)
            for impact_data in data.get('pending_impacts', [])
        ]
        news_system.company_events = {
            company: [CompanyEvent.from_dict(event_data) for event_data in events]
            for company, events in data.get('company_events', {}).items()
        }
        news_system.news_history = [tuple(item) for item in data.get('news_history', [])]
        return news_system

    def _generate_company_event(self, company: 'Company', week_number: int) -> Optional[CompanyEvent]:
        """Generate internal company event based on company fundamentals"""
        # Base probability: 25% chance of event each week
        if random.random() > 0.25:
            return None

        # Determine event type based on company fundamentals and random factors
        # Company strength influences event distribution
        strength_factor = company.true_strength  # 0.3 to 0.9

        # Higher strength = more likely to have successes, lower = more scandals/problems
        rand = random.random()

        if rand < strength_factor * 0.7:  # Strong companies have more successes
            event_type = EventType.SUCCESS
            severity = random.uniform(0.5, 1.0)  # Successes are generally impactful
            weeks_until_public = 1  # Successes are reported quickly
        elif rand < strength_factor * 0.7 + 0.3:  # Moderate problems
            event_type = EventType.PROBLEM
            severity = random.uniform(0.3, 0.6)
            weeks_until_public = random.randint(1, 2)  # Problems reported fairly quickly
        else:  # Scandals (more likely for weaker companies)
            event_type = EventType.SCANDAL
            severity = random.uniform(0.4, 1.0)
            weeks_until_public = random.randint(2, 4)  # Scandals take time to surface

        # Select appropriate template based on industry and event type
        if event_type == EventType.SCANDAL:
            templates = self.SCANDAL_TEMPLATES.get(company.industry, self.SCANDAL_TEMPLATES["Technology"])
        elif event_type == EventType.SUCCESS:
            templates = self.SUCCESS_TEMPLATES.get(company.industry, self.SUCCESS_TEMPLATES["Technology"])
        else:  # PROBLEM
            templates = self.PROBLEM_TEMPLATES.get(company.industry, self.PROBLEM_TEMPLATES["Technology"])

        description = random.choice(templates).format(company=company.name)

        return CompanyEvent(
            event_type=event_type,
            severity=severity,
            description=description,
            discovery_week=week_number,
            weeks_until_public=weeks_until_public,
            industry=company.industry
        )

    def _generate_fake_rumor(self, companies: Dict[str, 'Company']) -> Tuple[str, str, EventType]:
        """Generate a completely fabricated rumor about a random company

        Returns:
            (company_name, rumor_text, event_type)
        """
        company_name = random.choice(list(companies.keys()))
        company = companies[company_name]

        # Randomly choose event type (weighted towards negative for fake rumors)
        rand = random.random()
        if rand < 0.3:  # 30% positive fake rumors
            event_type = EventType.SUCCESS
            templates = self.SUCCESS_TEMPLATES.get(company.industry, self.SUCCESS_TEMPLATES["Technology"])
        elif rand < 0.6:  # 30% problem fake rumors
            event_type = EventType.PROBLEM
            templates = self.PROBLEM_TEMPLATES.get(company.industry, self.PROBLEM_TEMPLATES["Technology"])
        else:  # 40% scandal fake rumors
            event_type = EventType.SCANDAL
            templates = self.SCANDAL_TEMPLATES.get(company.industry, self.SCANDAL_TEMPLATES["Technology"])

        rumor_text = random.choice(templates).format(company=company_name)
        return (company_name, rumor_text, event_type)

    def _generate_news_report(self, companies: Dict[str, 'Company'], week_number: int) -> NewsReport:
        """Generate news from all four outlets independently

        Each outlet has different reporting behavior:
        - Financial Times: Only confirmed major events (always true)
        - Market Pulse: Clickbait, 80% fake, reports 1 week before confirmation
        - Insider Tip: 10% chance to report SUCCESS events as they spawn
        - Rumor Mill: Fastest for PROBLEMS/SCANDALS, 60% fake
        """

        # Collect all events by status
        spawned_events = []  # Just created this week (weeks_elapsed == 0)
        pending_events = []  # Not yet public (0 < weeks_elapsed < weeks_until_public)
        ready_events = []    # Ready to go public (weeks_elapsed >= weeks_until_public)

        for company_name, events in self.company_events.items():
            for event in events:
                weeks_elapsed = week_number - event.discovery_week
                if weeks_elapsed == 0:
                    spawned_events.append((company_name, event))
                elif weeks_elapsed >= event.weeks_until_public:
                    ready_events.append((company_name, event))
                elif weeks_elapsed > 0:
                    pending_events.append((company_name, event))

        # === 1. FINANCIAL TIMES (Trustworthy Source) ===
        # Reports ALL confirmed major events
        trustworthy_source = ""
        financial_times_items = []

        if ready_events:
            # Filter for major events (severity > 0.5)
            major_events = [(cn, ev) for cn, ev in ready_events if ev.severity > 0.5]
            if major_events:
                # Report ALL major confirmed events
                for company_name, event in major_events:
                    financial_times_items.append(f"• {event.description}")

                trustworthy_source = "\n".join(financial_times_items)

        # === 2. MARKET PULSE DAILY ===
        # Generates 2-3 clickbait items (80% fake, 20% real per item)
        # Reports events 1 week before they're confirmed when real
        market_pulse_items = []
        num_market_pulse_items = random.randint(2, 3)

        almost_ready = [(cn, ev) for cn, ev in pending_events
                      if week_number - ev.discovery_week == ev.weeks_until_public - 1]

        for _ in range(num_market_pulse_items):
            # 20% chance per item to report real event
            use_real_event = random.random() < 0.2 and almost_ready

            if use_real_event:
                # Report real event 1 week before confirmation
                company_name, event = random.choice(almost_ready)
                if event.event_type == EventType.SUCCESS:
                    templates = [
                        f"🚀 {company_name} ABOUT TO EXPLODE! {event.description.upper()}",
                        f"💰 BREAKING: {company_name} TO THE MOON! {event.description}",
                    ]
                else:
                    templates = [
                        f"💀 {company_name} COLLAPSING! {event.description.upper()} SELL NOW!",
                        f"🔥 DISASTER: {company_name} IN FREE FALL! {event.description}",
                    ]
                market_pulse_items.append(f"• {random.choice(templates)}")
            else:
                # Generate fake clickbait
                company_name, rumor_text, event_type = self._generate_fake_rumor(companies)
                if event_type == EventType.SUCCESS:
                    templates = [
                        f"🚀 {company_name} ABOUT TO EXPLODE! {rumor_text.upper()}",
                        f"💰 BREAKING: {company_name} TO THE MOON! {rumor_text}",
                        f"🔥 {company_name} REVOLUTIONIZES EVERYTHING! {rumor_text} BUY NOW!",
                    ]
                else:
                    templates = [
                        f"💀 {company_name} COLLAPSING! {rumor_text.upper()} SELL NOW!",
                        f"🔥 DISASTER: {company_name} IN FREE FALL! {rumor_text}",
                        f"⚠️ ALERT: {company_name} DOOMED! {rumor_text} GET OUT!",
                    ]
                market_pulse_items.append(f"• {random.choice(templates)}")

        market_pulse_source = "\n".join(market_pulse_items)

        # === 3. INSIDER TIP ===
        # Reports 1-2 tips
        # 10% chance to report SUCCESS events as they spawn
        # Otherwise, unreliable reporting
        insider_items = []
        insider_flipped = False
        num_insider_tips = random.randint(1, 2)

        all_events = spawned_events + pending_events + ready_events
        success_spawns = [(cn, ev) for cn, ev in spawned_events if ev.event_type == EventType.SUCCESS]

        for _ in range(num_insider_tips):
            if not all_events:
                break

            # 10% chance to report newly spawned SUCCESS event
            if success_spawns and random.random() < 0.1:
                company_name, event = random.choice(success_spawns)
                insider_items.append(f"• {event.description}")
                # Remove from list to avoid duplicates
                success_spawns.remove((company_name, event))
            else:
                # Normal behavior: report any event with unreliable accuracy
                company_name, event = random.choice(all_events)

                # 5% chance to have true insider info
                has_insider_info = random.random() < 0.05

                if has_insider_info:
                    insider_items.append(f"• {event.description}")
                else:
                    # 50% chance to flip sentiment
                    if random.random() < 0.5:
                        insider_flipped = True
                        # Report opposite
                        if event.event_type == EventType.SUCCESS:
                            templates = self.SCANDAL_TEMPLATES.get(event.industry, self.SCANDAL_TEMPLATES["Technology"])
                        else:
                            templates = self.SUCCESS_TEMPLATES.get(event.industry, self.SUCCESS_TEMPLATES["Technology"])
                        insider_text = random.choice(templates).format(company=company_name)
                        insider_items.append(f"• {insider_text}")
                    else:
                        insider_items.append(f"• {event.description}")

                # Remove from all_events to avoid reporting same event twice
                all_events.remove((company_name, event))

        insider_source = "\n".join(insider_items) if insider_items else ""

        # === 4. RUMOR MILL ===
        # Reports 2-4 rumors (only PROBLEMS and SCANDALS)
        # 40% chance real rumor, 60% chance fake per rumor
        # Fastest outlet for negative news
        rumor_mill_items = []
        num_rumors = random.randint(2, 4)

        negative_spawns = [(cn, ev) for cn, ev in spawned_events
                         if ev.event_type in [EventType.PROBLEM, EventType.SCANDAL]]
        negative_pending = [(cn, ev) for cn, ev in pending_events
                          if ev.event_type in [EventType.PROBLEM, EventType.SCANDAL]]

        # Create weighted list for pending events (closer to public = higher weight)
        weighted_pending = []
        for cn, ev in negative_pending:
            weeks_until_public_remaining = ev.weeks_until_public - (week_number - ev.discovery_week)
            weight = max(1, 4 - weeks_until_public_remaining)
            weighted_pending.extend([(cn, ev)] * weight)

        for _ in range(num_rumors):
            # 60% chance per rumor to be fake
            if random.random() < 0.6:
                # Generate fake negative rumor
                company_name = random.choice(list(companies.keys()))
                company = companies[company_name]

                # Only generate PROBLEM or SCANDAL fake rumors
                if random.random() < 0.5:
                    event_type = EventType.PROBLEM
                    templates = self.PROBLEM_TEMPLATES.get(company.industry, self.PROBLEM_TEMPLATES["Technology"])
                else:
                    event_type = EventType.SCANDAL
                    templates = self.SCANDAL_TEMPLATES.get(company.industry, self.SCANDAL_TEMPLATES["Technology"])

                rumor_text = random.choice(templates).format(company=company_name)
                rumor_mill_items.append(f"• {rumor_text}")
            else:
                # 40% chance: Report real unconfirmed PROBLEM or SCANDAL
                # 10% chance to catch newly spawned events
                if negative_spawns and random.random() < 0.1:
                    company_name, event = random.choice(negative_spawns)
                    rumor_mill_items.append(f"• {event.description}")
                    negative_spawns.remove((company_name, event))
                elif weighted_pending:
                    # Report from weighted pending events
                    company_name, event = random.choice(weighted_pending)
                    rumor_mill_items.append(f"• {event.description}")
                    # Remove all instances of this event from weighted list
                    weighted_pending = [(cn, ev) for cn, ev in weighted_pending
                                       if not (cn == company_name and ev == event)]
                else:
                    # No real negative events available, generate fake one instead
                    company_name = random.choice(list(companies.keys()))
                    company = companies[company_name]
                    if random.random() < 0.5:
                        templates = self.PROBLEM_TEMPLATES.get(company.industry, self.PROBLEM_TEMPLATES["Technology"])
                    else:
                        templates = self.SCANDAL_TEMPLATES.get(company.industry, self.SCANDAL_TEMPLATES["Technology"])
                    rumor_text = random.choice(templates).format(company=company_name)
                    rumor_mill_items.append(f"• {rumor_text}")

        rumor_mill_source = "\n".join(rumor_mill_items)

        # Determine if this is a rumor report (any outlet reporting unconfirmed news)
        is_rumor = not bool(trustworthy_source)

        return NewsReport(
            trustworthy_source=trustworthy_source,
            market_pulse_source=market_pulse_source,
            insider_source=insider_source,
            rumor_mill_source=rumor_mill_source,
            insider_flipped=insider_flipped,
            is_rumor=is_rumor
        )

    def generate_breaking_news(self, companies: Dict[str, 'Company'], week_number: int) -> Optional[Tuple[str, NewsReport, EventType]]:
        """Generate breaking news from all four outlets independently

        Each outlet reports based on its own criteria:
        - Financial Times: Confirmed major events only (creates market impact)
        - Market Pulse: 80% fake clickbait, 20% real (1 week early)
        - Insider Tip: 10% chance to catch SUCCESS events as they spawn
        - Rumor Mill: Fastest for PROBLEMS/SCANDALS, 60% fake

        Returns:
            Tuple of (company_name, news_report, event_type) if Financial Times reports something
            None if no confirmed news (but outlets may still have rumors)
        """

        # Step 1: Generate new internal events for all companies
        for company_name, company in companies.items():
            if company_name not in self.company_events:
                self.company_events[company_name] = []

            event = self._generate_company_event(company, week_number)
            if event:
                self.company_events[company_name].append(event)

        # Step 2: Generate news from all four outlets independently
        news_report = self._generate_news_report(companies, week_number)

        # Step 3: Check if Financial Times reported confirmed news
        # Only Financial Times creates market impacts
        if news_report.trustworthy_source:
            # Financial Times reported something - find ALL major confirmed events
            ready_events = []
            for company_name, events in self.company_events.items():
                for event in events:
                    weeks_elapsed = week_number - event.discovery_week
                    if weeks_elapsed >= event.weeks_until_public and event.severity > 0.5:
                        ready_events.append((company_name, event))

            if ready_events:
                # Create market impacts for ALL confirmed major events
                for company_name, event in ready_events:
                    # Calculate impact magnitude based on severity
                    base_impact = event.severity * 15.0  # Scale: 0 to 15%

                    # Determine sentiment for impact
                    if event.event_type == EventType.SUCCESS:
                        sentiment = NewsSentiment.POSITIVE
                        impact_magnitude = base_impact
                    else:
                        sentiment = NewsSentiment.NEGATIVE
                        impact_magnitude = -base_impact

                    # Create pending impact (only for confirmed Financial Times news)
                    pending_impact = PendingNewsImpact(
                        company_name=company_name,
                        sentiment=sentiment,
                        impact_magnitude=impact_magnitude,
                        weeks_until_impact=random.randint(1, 3),  # Impact occurs 1-3 weeks after news
                        is_real=True,  # Financial Times is always real
                        news_text=event.description,
                        news_report=news_report
                    )

                    self.pending_impacts.append(pending_impact)
                    self.news_history.append((week_number, event.description))

                    # Remove the confirmed event
                    self.company_events[company_name].remove(event)

                # Return first event for display purposes
                first_company, first_event = ready_events[0]
                return (first_company, news_report, first_event.event_type)

        # No confirmed Financial Times news
        # Check if any outlet has something to report
        if (news_report.market_pulse_source or
            news_report.insider_source or
            news_report.rumor_mill_source):
            # At least one outlet has news/rumors
            # Return with empty company name (no market impact)
            return ("", news_report, EventType.SUCCESS)
        else:
            # No news from any outlet this week
            return None

    def update_pending_impacts(self, companies: Dict[str, 'Company'], use_precompiled_prices: bool = False) -> List[str]:
        """Update countdown for pending impacts and apply them when due

        Args:
            companies: Dict of company objects
            use_precompiled_prices: If True, don't apply price changes (they're already in precompiled prices)
        """
        impact_messages = []
        impacts_to_remove = []

        for impact in self.pending_impacts:
            impact.weeks_until_impact -= 1

            if impact.weeks_until_impact <= 0:
                # Time to apply the impact (or just announce it if using precompiled prices)
                company = companies[impact.company_name]

                # If using precompiled prices, the impact is already baked in
                # Just display the message without modifying price
                if not use_precompiled_prices:
                    # Apply the actual impact (only when NOT using precompiled prices)
                    company.price *= (1 + impact.impact_magnitude / 100)
                    company.price = max(0.01, company.price)

                if impact.sentiment == NewsSentiment.POSITIVE:
                    impact_messages.append(
                        f"📈 MARKET IMPACT: {impact.company_name} surges {abs(impact.impact_magnitude):.1f}% "
                        f"following recent breaking news!"
                    )
                else:
                    impact_messages.append(
                        f"📉 MARKET IMPACT: {impact.company_name} drops {abs(impact.impact_magnitude):.1f}% "
                        f"following recent breaking news!"
                    )

                impacts_to_remove.append(impact)

        # Remove applied impacts
        for impact in impacts_to_remove:
            self.pending_impacts.remove(impact)

        return impact_messages


class LiquidityLevel(Enum):
    """Liquidity levels for stocks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Company:
    """Represents a publicly traded company"""

    def __init__(self, name: str, industry: str, initial_price: float, volatility: float, liquidity: LiquidityLevel = LiquidityLevel.MEDIUM, market_cap: float = 10000000.0):
        self.name = name
        self.industry = industry
        self.price = initial_price
        self.fundamental_price = initial_price  # "True" price based on fundamentals
        self.base_volatility = volatility
        self.price_history = [initial_price]
        self.liquidity = liquidity
        self.market_cap = market_cap  # Market capitalization in dollars
        # Hidden fundamentals for research hints (not directly visible to players)
        self.true_strength = random.uniform(0.3, 0.9)  # 0-1 scale, affects hint accuracy
        self.hidden_sentiment = random.choice([-1, 0, 1])  # -1: bearish, 0: neutral, 1: bullish
        # Earnings metrics (not visible to players, used for market valuation)
        # Start with a "reasonable" P/E ratio between 12-25
        target_pe = random.uniform(12.0, 25.0)
        self.earnings_per_share = initial_price / target_pe  # Derive EPS from target P/E

    def update_earnings(self):
        """Update earnings per share with slow fundamental growth

        EPS grows/shrinks slowly based on company fundamentals
        This represents actual business performance, not market speculation
        """
        # EPS changes slowly (company fundamentals grow ~5-8% annually on average)
        # That's about 0.1-0.15% per week
        annual_growth = random.uniform(-0.08, 0.12)  # -8% to +12% annual
        weekly_change = annual_growth / 52.0
        self.earnings_per_share *= (1 + weekly_change)
        self.earnings_per_share = max(0.001, self.earnings_per_share)  # Prevent negative earnings

    def get_pe_ratio(self) -> float:
        """Calculate current P/E ratio (Price to Earnings)"""
        if self.earnings_per_share <= 0:
            return 999.0  # Very high P/E for companies with no earnings
        return self.price / self.earnings_per_share

    def update_price(self):
        """Update stock price with random walk on fundamentals and mean reversion

        Process:
        1. Update fundamental_price with random walk (company fundamentals)
        2. Pull actual price back toward fundamental (mean reversion)
        3. This prevents pump-and-dump loops and death spirals
        """
        # Update earnings first (fundamental business performance)
        self.update_earnings()

        # Update fundamental price (random walk on fundamentals)
        # Fundamentals grow/shrink: 40-50% per year = ~0.75-0.95% per week
        annual_fundamental_change = random.uniform(-0.40, 0.50)  # -40% to +50% annual
        weekly_fundamental_change = annual_fundamental_change / 52.0
        self.fundamental_price *= (1 + weekly_fundamental_change)
        self.fundamental_price = max(0.01, self.fundamental_price)  # Prevent negative prices

        # Mean reversion: pull actual price toward fundamental
        # 30% of the gap closes each week (liquidity refills, temporary impact fades)
        price_gap = self.fundamental_price - self.price
        mean_reversion = price_gap * 0.30
        self.price += mean_reversion
        self.price = max(0.01, self.price)  # Prevent negative prices

        self.price_history.append(self.price)

    def calculate_slippage(self, shares: int, is_buy: bool, slippage_multiplier: float = 1.0) -> float:
        """Calculate price slippage based on daily trading volume and trade size

        Slippage represents the execution cost of trading through the order book.
        It's closely related to market impact - both scale with trade size relative
        to daily volume, but slippage is typically slightly higher (you pay the spread).

        Slippage is determined by:
        1. Trade value as a % of daily volume (not market cap!)
        2. Square root scaling for realistic impact
        3. Lower liquidity = higher slippage
        4. Notional dampener: trades under $1M get reduced slippage
        5. Volatility adjustment: calm stocks get cheaper execution
        """
        # Estimate average daily volume based on market cap and liquidity
        # (same as apply_market_impact for consistency)
        if self.liquidity == LiquidityLevel.HIGH:
            daily_volume_pct = 0.03  # 3% of market cap trades per day
        elif self.liquidity == LiquidityLevel.MEDIUM:
            daily_volume_pct = 0.01  # 1% of market cap trades per day
        else:  # LOW
            daily_volume_pct = 0.005  # 0.5% of market cap trades per day

        estimated_daily_volume = self.market_cap * daily_volume_pct

        # Calculate trade value relative to daily volume
        trade_value = shares * self.price
        trade_pct_of_daily_volume = trade_value / estimated_daily_volume

        # Apply minimum trade-size floor to prevent excessive penalties on tiny trades
        # Prevents $20k-$50k trades from being disproportionately punished
        min_trade_pct = 0.00005  # 0.005% of ADV
        effective_trade_pct = max(trade_pct_of_daily_volume, min_trade_pct)

        # Slippage coefficient (slightly higher than market impact)
        # Market impact affects the market price, slippage is what you pay
        # Slippage includes bid-ask spread + market impact
        base_coefficient = 0.35  # Higher than market impact's 0.25

        # Adjust for liquidity
        if self.liquidity == LiquidityLevel.LOW:
            base_coefficient *= 1.5  # 50% more slippage for illiquid stocks
        elif self.liquidity == LiquidityLevel.HIGH:
            base_coefficient *= 0.7  # 30% less slippage for highly liquid stocks

        # Calculate slippage using square root law
        slippage = (effective_trade_pct ** 0.5) * base_coefficient

        # Apply volatility normalization: calm stocks get cheaper execution
        # Baseline volatility of 7.5 represents "normal" medium-liquidity stocks
        baseline_vol = 7.5
        vol_adjustment = self.base_volatility / baseline_vol
        # Clamp to prevent extreme cases: calm stocks ~40% cheaper, wild stocks ~60% more expensive
        vol_adjustment = max(0.6, min(vol_adjustment, 1.6))
        slippage *= vol_adjustment

        # Apply notional-based dampener: trades under $1M get proportional forgiveness
        # This makes early-game trading on low-liquidity stocks much less punishing
        notional_dampener = min(1.0, trade_value / 1_000_000)
        slippage *= notional_dampener

        # Apply slippage multiplier (e.g., for Mystical Lender penalty)
        slippage *= slippage_multiplier

        # Cap maximum slippage at 25% to prevent extreme cases (after multiplier)
        slippage = min(slippage, 0.25 * slippage_multiplier)

        # Slippage goes against the trader (increases buy price, decreases sell price)
        if is_buy:
            return 1 + slippage
        else:
            return 1 - slippage

    def apply_market_impact(self, shares: int, is_buy: bool) -> float:
        """Apply temporary market impact from a trade

        Large trades temporarily move the market price, but it mean-reverts over time
        Returns the new price after market impact

        Design:
        - Impact is much smaller than slippage (slippage is the transaction cost)
        - Impact creates temporary deviation from fundamental_price
        - Mean reversion in update_price() pulls it back over time
        - Prevents pump-and-dump loops and death spirals
        - Based on daily trading volume, not market cap (more realistic)
        - Notional dampener and volatility adjustments applied for fairness
        """
        # Estimate average daily volume based on market cap and liquidity
        # Real market research: ADV typically 0.5%-3% of market cap per day
        if self.liquidity == LiquidityLevel.HIGH:
            daily_volume_pct = 0.03  # 3% of market cap trades per day
        elif self.liquidity == LiquidityLevel.MEDIUM:
            daily_volume_pct = 0.01  # 1% of market cap trades per day
        else:  # LOW
            daily_volume_pct = 0.005  # 0.5% of market cap trades per day

        estimated_daily_volume = self.market_cap * daily_volume_pct

        # Calculate trade value relative to daily volume (not market cap!)
        trade_value = shares * self.price
        trade_pct_of_daily_volume = trade_value / estimated_daily_volume

        # Apply minimum trade-size floor to prevent excessive penalties on tiny trades
        min_trade_pct = 0.00005  # 0.005% of ADV
        effective_trade_pct = max(trade_pct_of_daily_volume, min_trade_pct)

        # Market impact follows square root law from market microstructure research
        # Kyle's lambda / Almgren-Chriss models suggest: impact ∝ sqrt(trade_size/ADV)
        # Typical coefficient: 0.1-0.5 depending on market conditions
        # We use 0.25 as a middle ground
        base_impact_coefficient = 0.25

        # For low liquidity stocks, increase impact coefficient
        if self.liquidity == LiquidityLevel.LOW:
            base_impact_coefficient *= 1.5  # 50% more impact for illiquid stocks
        elif self.liquidity == LiquidityLevel.HIGH:
            base_impact_coefficient *= 0.7  # 30% less impact for highly liquid stocks

        # Calculate impact using square root law
        # Example: $25k trade on $1B daily volume = sqrt(0.0025%) * 0.25 = 0.0125% impact
        impact_multiplier = (effective_trade_pct ** 0.5) * base_impact_coefficient

        # Apply volatility normalization: calm stocks get cheaper execution
        baseline_vol = 7.5
        vol_adjustment = self.base_volatility / baseline_vol
        vol_adjustment = max(0.6, min(vol_adjustment, 1.6))
        impact_multiplier *= vol_adjustment

        # Apply notional-based dampener: trades under $1M get proportional forgiveness
        notional_dampener = min(1.0, trade_value / 1_000_000)
        impact_multiplier *= notional_dampener

        # Cap at 5% price movement per trade (prevents extreme cases)
        impact_multiplier = min(impact_multiplier, 0.05)

        # Apply impact to current price (creates temporary deviation)
        if is_buy:
            # Buying pushes price up temporarily
            new_price = self.price * (1 + impact_multiplier)
        else:
            # Selling pushes price down temporarily
            new_price = self.price * (1 - impact_multiplier)

        return new_price

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
            'fundamental_price': self.fundamental_price,
            'base_volatility': self.base_volatility,
            'price_history': self.price_history,
            'liquidity': self.liquidity.value,
            'market_cap': self.market_cap,
            'true_strength': self.true_strength,
            'hidden_sentiment': self.hidden_sentiment,
            'earnings_per_share': self.earnings_per_share
        }

    @staticmethod
    def from_dict(data: dict) -> 'Company':
        """Deserialize company from dictionary"""
        company = Company(
            name=data['name'],
            industry=data['industry'],
            initial_price=data['price'],
            volatility=data['base_volatility'],
            liquidity=LiquidityLevel(data['liquidity']),
            market_cap=data.get('market_cap', 10000000.0)  # Default for old saves
        )
        company.price = data['price']
        company.fundamental_price = data.get('fundamental_price', data['price'])  # Default to price for old saves
        company.price_history = data['price_history']
        company.true_strength = data['true_strength']
        company.hidden_sentiment = data['hidden_sentiment']
        # For old saves without EPS, calculate from current price with reasonable P/E
        if 'earnings_per_share' in data:
            company.earnings_per_share = data['earnings_per_share']
        else:
            target_pe = random.uniform(12.0, 25.0)
            company.earnings_per_share = data['price'] / target_pe
        return company

    def __str__(self):
        # Format market cap in millions or billions
        if self.market_cap >= 1_000_000_000:
            market_cap_str = f"${self.market_cap / 1_000_000_000:.1f}B"
        else:
            market_cap_str = f"${self.market_cap / 1_000_000:.1f}M"
        return f"{self.name} ({self.industry}) - ${self.price:.2f} {self.get_liquidity_indicator()} [Cap: {market_cap_str}]"


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
    """Represents Void Stocks - 50% chance to copy random stock, 50% chance to enter void state ($0)"""

    def __init__(self, companies: Dict[str, 'Company']):
        self.name = "Void Stocks"
        self.price = 0.0  # Start at $0
        self.companies = companies
        self.weeks_elapsed = 0  # Track weeks
        self.current_company_index = 0  # Which company we're copying
        self.company_names = []  # Will be populated when we have companies
        self.description = "Extremely risky stocks - 50% chance to copy a random company, 50% chance to become worthless"
        self.is_void_week = True  # Start in void state

    def update_price(self):
        """Update price - 50/50 chance to copy a random company or enter void state"""
        self.weeks_elapsed += 1

        # Update company names list if needed
        if not self.company_names and self.companies:
            self.company_names = sorted(list(self.companies.keys()))

        # 50/50 chance each week
        if random.random() < 0.5:
            # Lucky: Copy a random company's stock
            self.is_void_week = False
            if self.company_names:
                # Pick a random company instead of cycling through them
                company_name = random.choice(self.company_names)
                self.price = self.companies[company_name].price
                # Store which company we copied for display purposes
                self.current_company_index = self.company_names.index(company_name)
            else:
                self.price = 0.0  # No companies available
        else:
            # Unlucky: Enter void state ($0)
            self.is_void_week = True
            self.price = 0.0

    def get_current_company_name(self) -> str:
        """Get the name of the company currently being copied (if any)"""
        if self.is_void_week or not self.company_names:
            return "VOID"
        # Get the company at the current index (randomly selected)
        idx = self.current_company_index % len(self.company_names)
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


class MysticalLender:
    """Represents The Mystical Lender - a trap loan with hidden 5x slippage penalty"""

    def __init__(self):
        self.name = "The Mystical Lender"
        self.loan_amount = 250000.0  # $250k
        self.description = "Sign a blank paper and get $250k!***\n*** : TERMS AND CONDITIONS APPLY"

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            'loan_amount': self.loan_amount
        }

    @staticmethod
    def from_dict(data: dict) -> 'MysticalLender':
        """Deserialize from dictionary"""
        ml = MysticalLender()
        ml.loan_amount = data.get('loan_amount', 250000.0)
        return ml

    def __str__(self):
        return f"{self.name} - Get ${self.loan_amount:.2f}! (Sign a blank paper)"


class Player:
    """Represents a player in the game"""

    def __init__(self, name: str, starting_cash: float = 100000.0):
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
        self.void_stocks_purchases = []  # List of void stock purchase batches: {'purchase_week': int, 'shares': int, 'void_state_count': int}
        self.void_catalyst_owned = False  # Void Catalyst (only 1 exists)
        self.mystical_lender_debt = 0.0  # Mystical Lender debt (hidden 5x slippage until repaid)
        # Leverage system
        self.borrowed_amount = 0.0
        self.max_leverage_ratio = 5.0  # Can borrow up to 5x equity
        self.interest_rate_weekly = 0.115  # ~6% annual = 0.115% weekly
        self.collateral_deposited = 0.0  # Cash deposited as collateral to reduce margin call threshold
        # Short selling system
        self.short_positions: Dict[str, int] = {}  # company_name -> shares borrowed and owed
        self.short_borrow_fee_weekly = 0.02  # ~1% annual = 0.02% weekly
        # Research tracking
        self.researched_this_week = False
        self.research_history: Dict[str, List[str]] = {}  # company_name -> list of hints received

    def buy_stock(self, company: Company, dollar_amount: float, leverage: float = 1.0, companies: Dict[str, 'Company'] = None, treasury: 'Treasury' = None, gold: 'Gold' = None, holy_water: 'HolyWater' = None, quantum_singularity: 'QuantumSingularity' = None, elf_queen_water: 'ElfQueenWater' = None, gold_coin: 'GoldCoin' = None, void_stocks: 'VoidStocks' = None, void_catalyst: 'VoidCatalyst' = None) -> Tuple[bool, str]:
        """Buy shares of a company using dollar amount with optional leverage

        Args:
            company: Company to invest in
            dollar_amount: Dollar amount to invest (before leverage)
            leverage: Leverage multiplier (e.g., 2.0 = 2x leverage, doubles the investment)
            companies: Dict of companies (needed for equity calculation with leverage)
            treasury: Treasury object (needed for equity calculation with leverage)
            gold, holy_water, etc: Special assets (needed for accurate equity calculation)
        """
        if dollar_amount <= 0:
            return False, "Invalid investment amount!"

        # Apply leverage multiplier to investment amount
        total_investment = dollar_amount * leverage
        borrowed_for_trade = total_investment - dollar_amount

        # Check if we have enough cash for the base investment
        if dollar_amount > self.cash:
            return False, "Insufficient funds for base investment!"

        # If using leverage, just track the borrowed amount (no limit, but margin call still applies)
        if leverage > 1.0:
            if companies is None or treasury is None:
                return False, "Cannot calculate leverage without company data!"

        # Calculate shares we can buy (iterative approach for slippage)
        # We need to find how many shares we can buy with total_investment considering slippage
        shares = total_investment / company.price  # Initial estimate

        # Check for Mystical Lender penalty (hidden 5x slippage)
        slippage_multiplier = 5.0 if self.mystical_lender_debt > 0 else 1.0

        # Iteratively refine to account for slippage
        for _ in range(5):  # A few iterations should converge
            slippage_factor = company.calculate_slippage(shares, is_buy=True, slippage_multiplier=slippage_multiplier)
            effective_price = company.price * slippage_factor
            shares = total_investment / effective_price

        # Final calculation
        slippage_factor = company.calculate_slippage(shares, is_buy=True, slippage_multiplier=slippage_multiplier)
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

        # Apply market impact (buying pushes price up)
        old_price = company.price
        new_price = company.apply_market_impact(shares, is_buy=True)
        company.price = new_price
        price_impact = new_price - old_price

        # Build message
        slippage_cost = (effective_price - old_price) * shares
        leverage_msg = f" (with {leverage:.1f}x leverage)" if leverage > 1.0 else ""

        message = f"Purchased {shares:.4f} shares for ${dollar_amount:.2f}{leverage_msg}"
        if leverage > 1.0:
            message += f"\n  Total position value: ${total_investment:.2f} (borrowed ${borrowed_for_trade:.2f})"
        if slippage_cost > 0.01:
            message += f"\n  Price slippage: ${slippage_cost:.2f}"
        if price_impact > 0.01:
            message += f"\n  Market impact: Price moved from ${old_price:.2f} to ${new_price:.2f} (+${price_impact:.2f})"

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

        # Check for Mystical Lender penalty (hidden 5x slippage)
        slippage_multiplier = 5.0 if self.mystical_lender_debt > 0 else 1.0

        if dollar_amount is not None:
            # Calculate shares from dollar amount (iterative for slippage)
            shares_to_sell = dollar_amount / company.price  # Initial estimate

            # Iteratively refine
            for _ in range(5):
                if shares_to_sell > owned_shares:
                    shares_to_sell = owned_shares
                    break
                slippage_factor = company.calculate_slippage(shares_to_sell, is_buy=False, slippage_multiplier=slippage_multiplier)
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
        old_price = company.price
        slippage_factor = company.calculate_slippage(shares_to_sell, is_buy=False, slippage_multiplier=slippage_multiplier)
        effective_price = old_price * slippage_factor
        total_value = effective_price * shares_to_sell

        self.cash += total_value
        self.portfolio[company.name] -= shares_to_sell
        if self.portfolio[company.name] < 0.0001:  # Clean up very small amounts
            del self.portfolio[company.name]

        # Apply market impact (selling pushes price down)
        new_price = company.apply_market_impact(shares_to_sell, is_buy=False)
        company.price = new_price
        price_impact = old_price - new_price

        # Calculate and show slippage impact
        slippage_loss = (old_price - effective_price) * shares_to_sell

        message = f"Sold {shares_to_sell:.4f} shares for ${total_value:.2f}"
        if slippage_loss > 0.01:
            message += f"\n  Price slippage: -${slippage_loss:.2f}"
        if price_impact > 0.01:
            message += f"\n  Market impact: Price moved from ${old_price:.2f} to ${new_price:.2f} (-${price_impact:.2f})"

        return True, message

    def short_sell(self, company: Company, shares: int, companies: Dict[str, Company], treasury: Treasury, gold: Gold = None, holy_water: HolyWater = None, quantum_singularity: QuantumSingularity = None, elf_queen_water: ElfQueenWater = None, gold_coin: GoldCoin = None, void_stocks: VoidStocks = None, void_catalyst: VoidCatalyst = None) -> Tuple[bool, str]:
        """Short sell shares: borrow and sell them, must cover later"""
        if shares <= 0:
            return False, "Invalid number of shares!"

        # Check for Mystical Lender penalty (hidden 5x slippage)
        slippage_multiplier = 5.0 if self.mystical_lender_debt > 0 else 1.0

        # Calculate effective price with slippage (selling borrowed shares)
        old_price = company.price
        slippage_factor = company.calculate_slippage(shares, is_buy=False, slippage_multiplier=slippage_multiplier)
        effective_price = old_price * slippage_factor
        total_proceeds = effective_price * shares

        # Check margin requirement: need equity >= 1.5x the short position value
        # This is the initial margin requirement for short selling
        equity = self.calculate_equity(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst)
        short_value = old_price * shares
        required_margin = short_value * 1.5

        if equity < required_margin:
            return False, f"Insufficient equity for short sale! Need ${required_margin:.2f} equity, have ${equity:.2f}"

        # Execute short sale
        self.cash += total_proceeds
        if company.name in self.short_positions:
            self.short_positions[company.name] += shares
        else:
            self.short_positions[company.name] = shares

        # Apply market impact (short selling = selling, pushes price down)
        new_price = company.apply_market_impact(shares, is_buy=False)
        company.price = new_price
        price_impact = old_price - new_price

        # Calculate and show slippage impact
        slippage_loss = (old_price - effective_price) * shares
        message = f"Short sale successful! Received ${total_proceeds:.2f}"
        if slippage_loss > 0.01:
            message += f"\n  Price slippage: -${slippage_loss:.2f}"
        if price_impact > 0.01:
            message += f"\n  Market impact: Price moved from ${old_price:.2f} to ${new_price:.2f} (-${price_impact:.2f})"

        return True, message

    def cover_short(self, company: Company, shares: int) -> Tuple[bool, str]:
        """Cover (close) a short position by buying back the shares"""
        if company.name not in self.short_positions or self.short_positions[company.name] < shares:
            return False, "You don't have that many shares shorted!"

        # Check for Mystical Lender penalty (hidden 5x slippage)
        slippage_multiplier = 5.0 if self.mystical_lender_debt > 0 else 1.0

        # Calculate effective price with slippage (buying to cover)
        old_price = company.price
        slippage_factor = company.calculate_slippage(shares, is_buy=True, slippage_multiplier=slippage_multiplier)
        effective_price = old_price * slippage_factor
        total_cost = effective_price * shares

        if total_cost > self.cash:
            return False, "Insufficient funds to cover short position!"

        # Execute cover
        self.cash -= total_cost
        self.short_positions[company.name] -= shares
        if self.short_positions[company.name] == 0:
            del self.short_positions[company.name]

        # Apply market impact (covering = buying, pushes price up)
        new_price = company.apply_market_impact(shares, is_buy=True)
        company.price = new_price
        price_impact = new_price - old_price

        # Calculate and show slippage impact
        slippage_cost = (effective_price - old_price) * shares
        message = f"Short position covered! Cost ${total_cost:.2f}"
        if slippage_cost > 0.01:
            message += f"\n  Price slippage: ${slippage_cost:.2f}"
        if price_impact > 0.01:
            message += f"\n  Market impact: Price moved from ${old_price:.2f} to ${new_price:.2f} (+${price_impact:.2f})"

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

        # Record this purchase with the current week and void state counter
        self.void_stocks_purchases.append({
            'purchase_week': void_stocks.weeks_elapsed,
            'shares': shares,
            'void_state_count': 0
        })

        company = void_stocks.get_current_company_name()
        return True, f"Purchase successful! Bought {shares} Void Stocks for ${total_cost:.2f} (Currently copying {company})"

    def sell_void_stocks(self, void_stocks: VoidStocks, shares: int) -> Tuple[bool, str]:
        """Sell Void Stocks"""
        if self.void_stocks_shares < shares:
            return False, "You don't own that many Void Stocks!"

        total_value = void_stocks.price * shares
        self.cash += total_value
        self.void_stocks_shares -= shares

        # Remove shares from purchases (FIFO - oldest first)
        remaining_to_remove = shares
        purchases_to_keep = []
        for purchase in self.void_stocks_purchases:
            if remaining_to_remove >= purchase['shares']:
                # Remove this entire purchase
                remaining_to_remove -= purchase['shares']
            elif remaining_to_remove > 0:
                # Partially remove from this purchase
                purchase['shares'] -= remaining_to_remove
                remaining_to_remove = 0
                purchases_to_keep.append(purchase)
            else:
                # Keep this purchase intact
                purchases_to_keep.append(purchase)
        self.void_stocks_purchases = purchases_to_keep

        if void_stocks.is_void_week:
            return True, f"Sale successful! Sold {shares} Void Stocks for ${total_value:.2f} (VOID STATE - worthless!)"
        else:
            company = void_stocks.get_current_company_name()
            return True, f"Sale successful! Sold {shares} Void Stocks for ${total_value:.2f} (Was copying {company})"

    def process_void_state_transition(self, void_stocks: VoidStocks) -> List[str]:
        """Process void state transitions and delete shares that reach 5 void states.
        Returns list of messages about deleted shares."""
        messages = []

        if not void_stocks.is_void_week:
            # Not in void state, nothing to do
            return messages

        # Increment void state counter for all purchases
        purchases_to_keep = []
        total_deleted_shares = 0

        for purchase in self.void_stocks_purchases:
            purchase['void_state_count'] += 1

            if purchase['void_state_count'] >= 5:
                # Delete these shares - they've gone through 5 void states
                total_deleted_shares += purchase['shares']
                messages.append(f"💀 VOID DELETION: {purchase['shares']} Void Stock shares (purchased in week {purchase['purchase_week']}) have been consumed by the void!")
            else:
                # Keep this purchase
                purchases_to_keep.append(purchase)

        self.void_stocks_purchases = purchases_to_keep
        self.void_stocks_shares -= total_deleted_shares

        if total_deleted_shares > 0:
            messages.append(f"Total shares lost to the void: {total_deleted_shares}")

        return messages

    def check_void_stock_warning(self, void_stocks: VoidStocks) -> Tuple[bool, List[dict]]:
        """Check if any void stock purchases will be deleted next week.
        Returns (has_warning, list of at-risk purchases)"""
        if void_stocks.is_void_week:
            # Currently in void state, next week won't be void
            return False, []

        # Next week will be void state - check for purchases at 4 void states
        at_risk_purchases = []
        for purchase in self.void_stocks_purchases:
            if purchase['void_state_count'] == 4:
                at_risk_purchases.append(purchase)

        return len(at_risk_purchases) > 0, at_risk_purchases

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

    def accept_mystical_lender(self, mystical_lender: MysticalLender) -> Tuple[bool, str]:
        """Accept loan from The Mystical Lender (hidden 5x slippage until repaid)"""
        if self.mystical_lender_debt > 0:
            return False, "You already have a loan from The Mystical Lender!"

        loan_amount = mystical_lender.loan_amount
        self.cash += loan_amount
        self.mystical_lender_debt = loan_amount

        return True, f"Sign a blank paper and get ${loan_amount:.2f}!\n*** : TERMS AND CONDITIONS APPLY"

    def repay_mystical_lender(self, amount: float = None) -> Tuple[bool, str]:
        """Repay The Mystical Lender debt (partially or fully)"""
        if self.mystical_lender_debt <= 0:
            return False, "You have no debt with The Mystical Lender!"

        # If no amount specified, repay all
        if amount is None:
            amount = self.mystical_lender_debt

        if amount > self.mystical_lender_debt:
            amount = self.mystical_lender_debt

        if amount > self.cash:
            return False, f"Insufficient funds! You need ${amount:.2f} but only have ${self.cash:.2f}"

        self.cash -= amount
        self.mystical_lender_debt -= amount

        if self.mystical_lender_debt < 0.01:
            self.mystical_lender_debt = 0.0
            return True, f"Repaid ${amount:.2f}. The Mystical Lender debt is now FULLY REPAID! The strange terms are lifted..."
        else:
            return True, f"Repaid ${amount:.2f}. Remaining debt: ${self.mystical_lender_debt:.2f}"

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

    def borrow_money(self, amount: float, companies: Dict[str, Company], treasury: Treasury, gold: 'Gold' = None, holy_water: 'HolyWater' = None, quantum_singularity: 'QuantumSingularity' = None, elf_queen_water: 'ElfQueenWater' = None, gold_coin: 'GoldCoin' = None, void_stocks: 'VoidStocks' = None, void_catalyst: 'VoidCatalyst' = None) -> Tuple[bool, str]:
        """Borrow money using leverage"""
        if amount <= 0:
            return False, "Invalid amount!"

        equity = self.calculate_equity(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst)

        # No borrowing limit - players can borrow as much as they want (margin call will trigger if they go too far)
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

    def get_margin_call_threshold(self, equity: float) -> float:
        """Calculate the margin call threshold based on collateral deposited

        Base threshold: 30% (0.30)
        With 100% equity as collateral: 10% (0.10)
        Linear interpolation between these values
        """
        if equity <= 0:
            return 0.30

        collateral_ratio = min(1.0, self.collateral_deposited / equity)
        # Threshold ranges from 0.30 (no collateral) to 0.10 (100% collateral)
        threshold = 0.30 - (collateral_ratio * 0.20)
        return threshold

    def deposit_collateral(self, amount: float) -> Tuple[bool, str]:
        """Deposit cash as collateral to reduce margin call threshold

        Collateral cannot be withdrawn until player is debt-free
        """
        if amount <= 0:
            return False, "Invalid amount!"

        if amount > self.cash:
            return False, f"Insufficient cash! You have ${self.cash:.2f}"

        self.cash -= amount
        self.collateral_deposited += amount
        return True, f"Successfully deposited ${amount:.2f} as collateral! Total collateral: ${self.collateral_deposited:.2f}"

    def withdraw_collateral(self, amount: float) -> Tuple[bool, str]:
        """Withdraw collateral (only allowed when debt-free)"""
        if amount <= 0:
            return False, "Invalid amount!"

        if self.borrowed_amount > 0:
            return False, f"Cannot withdraw collateral while in debt! Current debt: ${self.borrowed_amount:.2f}"

        if amount > self.collateral_deposited:
            return False, f"Insufficient collateral! You have ${self.collateral_deposited:.2f} deposited"

        self.collateral_deposited -= amount
        self.cash += amount
        return True, f"Successfully withdrew ${amount:.2f} from collateral! Remaining collateral: ${self.collateral_deposited:.2f}"

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
        """Check if player is subject to margin call (equity < threshold% of total position or maintenance margin for shorts)"""
        # Check if there's any leverage or short positions
        has_risk = self.borrowed_amount > 0 or len(self.short_positions) > 0
        if not has_risk:
            return False

        # Calculate equity including all assets
        equity = self.calculate_equity(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst)

        # Check leverage-based margin call
        if self.borrowed_amount > 0:
            total_position = equity + self.borrowed_amount
            # Calculate dynamic margin call threshold based on collateral
            # Base: 30%, scales down to 10% if 100% of equity is deposited as collateral
            margin_threshold = self.get_margin_call_threshold(equity)
            # Margin call if equity falls below threshold of total position
            if total_position > 0 and (equity / total_position) < margin_threshold:
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
            'void_stocks_purchases': self.void_stocks_purchases,
            'void_catalyst_owned': self.void_catalyst_owned,
            'mystical_lender_debt': self.mystical_lender_debt,
            'collateral_deposited': self.collateral_deposited
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
        player.void_stocks_purchases = data.get('void_stocks_purchases', [])  # Default to empty list for backwards compatibility
        player.void_catalyst_owned = data.get('void_catalyst_owned', False)
        player.mystical_lender_debt = data.get('mystical_lender_debt', 0.0)  # Default to 0.0 for backwards compatibility
        player.collateral_deposited = data.get('collateral_deposited', 0.0)  # Default to 0.0 for backwards compatibility
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
            equity = self.calculate_equity(companies, treasury, gold, holy_water, quantum_singularity, elf_queen_water, gold_coin, void_stocks, void_catalyst)
            print(f"💰 Equity (Net - Debt): ${equity:.2f}")
            current_leverage = self.borrowed_amount / max(0.01, equity)
            print(f"📊 Leverage Ratio: {current_leverage:.2f}x")

            # Show margin call information
            total_position = equity + self.borrowed_amount
            if total_position > 0:
                equity_ratio = (equity / total_position) * 100
                margin_threshold = self.get_margin_call_threshold(equity) * 100
                distance_to_margin_call = equity_ratio - margin_threshold

                if distance_to_margin_call < 10:
                    warning_icon = "🚨"
                elif distance_to_margin_call < 20:
                    warning_icon = "⚠️"
                else:
                    warning_icon = "✓"

                print(f"{warning_icon} Equity Ratio: {equity_ratio:.1f}% (Margin Call at {margin_threshold:.1f}%)")
                print(f"   Distance to Margin Call: {distance_to_margin_call:.1f}%")

        # Show collateral info
        if self.collateral_deposited > 0:
            print(f"🏦 Collateral Deposited: ${self.collateral_deposited:.2f}")
            if self.borrowed_amount == 0:
                print(f"   (Can be withdrawn - you are debt-free)")

        # Show Mystical Lender debt
        if self.mystical_lender_debt > 0:
            print(f"📜 Mystical Lender Debt: ${self.mystical_lender_debt:.2f}")

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
    # New sector-specific events
    TECH_CORRECTION = "tech_correction"
    ENERGY_CRISIS = "energy_crisis"
    FINANCIAL_SECTOR_BOOM = "financial_sector_boom"
    RETAIL_COLLAPSE = "retail_collapse"
    HEALTHCARE_RALLY = "healthcare_rally"
    MANUFACTURING_SLUMP = "manufacturing_slump"
    # Market corrections
    BUBBLE_POP = "bubble_pop"
    PROFIT_TAKING = "profit_taking"
    SECTOR_ROTATION = "sector_rotation"


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
        self.last_cycle_type: Optional[MarketCycleType] = None  # Track previous cycle for smart sequencing

    def to_dict(self) -> dict:
        """Serialize MarketCycle to dictionary"""
        return {
            'active_cycle': self.active_cycle.to_dict() if self.active_cycle else None,
            'cycle_history': self.cycle_history,
            'last_cycle_type': self.last_cycle_type.value if self.last_cycle_type else None
        }

    @staticmethod
    def from_dict(data: dict) -> 'MarketCycle':
        """Deserialize MarketCycle from dictionary"""
        market_cycle = MarketCycle()
        if data['active_cycle']:
            market_cycle.active_cycle = ActiveMarketCycle.from_dict(data['active_cycle'])
        market_cycle.cycle_history = [tuple(item) for item in data['cycle_history']]
        if data.get('last_cycle_type'):
            market_cycle.last_cycle_type = MarketCycleType(data['last_cycle_type'])
        return market_cycle

    def should_trigger_cycle(self, week_number: int) -> bool:
        """Check if we should trigger a new cycle (every 24 weeks = 6 months)"""
        # Trigger at weeks 24, 48, 72, etc.
        return week_number > 0 and week_number % 24 == 0 and self.active_cycle is None

    def calculate_market_pe(self, companies: Dict[str, Company]) -> float:
        """Calculate average P/E ratio across all companies"""
        if not companies:
            return 20.0  # Default reasonable P/E

        total_pe = sum(company.get_pe_ratio() for company in companies.values())
        return total_pe / len(companies)

    def trigger_cycle(self, week_number: int, companies: Dict[str, Company]) -> ActiveMarketCycle:
        """Trigger a new market cycle with smart selection based on market conditions

        Logic:
        - After positive cycles (boom, bull, recovery), check P/E ratios
        - If P/E is too high, increase chance of correction
        - Otherwise, mix of random events weighted by realism
        """
        # Calculate average market P/E
        avg_pe = self.calculate_market_pe(companies)

        # Define positive cycles that inflate prices
        positive_cycles = {
            MarketCycleType.TECH_BOOM,
            MarketCycleType.BULL_MARKET,
            MarketCycleType.RECOVERY,
            MarketCycleType.FINANCIAL_SECTOR_BOOM,
            MarketCycleType.HEALTHCARE_RALLY
        }

        # Define correction cycles that bring prices down
        correction_cycles = {
            MarketCycleType.BUBBLE_POP,
            MarketCycleType.TECH_CORRECTION,
            MarketCycleType.PROFIT_TAKING,
            MarketCycleType.BEAR_MARKET,
            MarketCycleType.MARKET_CRASH
        }

        # Smart cycle selection based on market conditions
        cycle_weights = {}

        # If last cycle was positive AND P/E is high, favor corrections
        if self.last_cycle_type in positive_cycles and avg_pe > 30.0:
            # High P/E after boom = bubble territory, favor corrections
            if avg_pe > 50.0:
                # Extreme overvaluation - very high chance of correction
                cycle_weights = {
                    MarketCycleType.BUBBLE_POP: 30,
                    MarketCycleType.TECH_CORRECTION: 25,
                    MarketCycleType.PROFIT_TAKING: 20,
                    MarketCycleType.BEAR_MARKET: 15,
                    MarketCycleType.SECTOR_ROTATION: 10
                }
            elif avg_pe > 35.0:
                # Moderate overvaluation - increased correction chance
                cycle_weights = {
                    MarketCycleType.PROFIT_TAKING: 25,
                    MarketCycleType.TECH_CORRECTION: 20,
                    MarketCycleType.BUBBLE_POP: 15,
                    MarketCycleType.SECTOR_ROTATION: 15,
                    MarketCycleType.BEAR_MARKET: 10,
                    MarketCycleType.INFLATION: 10,
                    MarketCycleType.BULL_MARKET: 5  # Small chance to continue
                }
            else:
                # Mild overvaluation (30-35 P/E) - small correction chance
                cycle_weights = {
                    MarketCycleType.SECTOR_ROTATION: 20,
                    MarketCycleType.PROFIT_TAKING: 15,
                    MarketCycleType.BULL_MARKET: 15,
                    MarketCycleType.INFLATION: 15,
                    MarketCycleType.TECH_CORRECTION: 10,
                    MarketCycleType.ENERGY_CRISIS: 10,
                    MarketCycleType.HEALTHCARE_RALLY: 10,
                    MarketCycleType.BEAR_MARKET: 5
                }

        # If last cycle was correction AND P/E is low, favor recovery
        elif self.last_cycle_type in correction_cycles and avg_pe < 15.0:
            # Undervalued market - favor recovery
            cycle_weights = {
                MarketCycleType.RECOVERY: 30,
                MarketCycleType.BULL_MARKET: 20,
                MarketCycleType.HEALTHCARE_RALLY: 15,
                MarketCycleType.FINANCIAL_SECTOR_BOOM: 15,
                MarketCycleType.TECH_BOOM: 10,
                MarketCycleType.SECTOR_ROTATION: 10
            }

        # Normal conditions - balanced mix
        else:
            cycle_weights = {
                # Broad market events
                MarketCycleType.BULL_MARKET: 12,
                MarketCycleType.BEAR_MARKET: 10,
                MarketCycleType.SECTOR_ROTATION: 12,
                MarketCycleType.INFLATION: 10,
                # Sector-specific events
                MarketCycleType.TECH_BOOM: 8,
                MarketCycleType.TECH_CORRECTION: 8,
                MarketCycleType.ENERGY_CRISIS: 8,
                MarketCycleType.FINANCIAL_SECTOR_BOOM: 7,
                MarketCycleType.HEALTHCARE_RALLY: 7,
                MarketCycleType.RETAIL_COLLAPSE: 6,
                MarketCycleType.MANUFACTURING_SLUMP: 6,
                # Major events (less common)
                MarketCycleType.RECOVERY: 2,
                MarketCycleType.RECESSION: 2,
                MarketCycleType.MARKET_CRASH: 1,
                MarketCycleType.BUBBLE_POP: 1
            }

        # Select cycle based on weights
        cycles = list(cycle_weights.keys())
        weights = list(cycle_weights.values())
        cycle_type = random.choices(cycles, weights=weights, k=1)[0]

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

        elif cycle_type == MarketCycleType.TECH_BOOM:
            headline = "🚀 TECHNOLOGY BOOM - Innovation Wave Transforms Markets"
            description = "Revolutionary tech breakthroughs spark investor frenzy. Technology and electronics sectors lead massive market rally."

        elif cycle_type == MarketCycleType.TECH_CORRECTION:
            headline = "📉 TECH SECTOR CORRECTION - Valuation Concerns Trigger Selloff"
            description = "Overvalued tech stocks face harsh reality check. Investors flee high P/E ratios. Technology sector plummets as bubble fears spread."

        elif cycle_type == MarketCycleType.ENERGY_CRISIS:
            headline = "⚡ ENERGY CRISIS - Oil Prices Spike on Supply Disruption"
            description = "Global energy shortage sends prices soaring. Energy sector rallies hard while other industries struggle with rising costs."

        elif cycle_type == MarketCycleType.FINANCIAL_SECTOR_BOOM:
            headline = "💰 FINANCIAL SECTOR BOOM - Banking Profits Surge"
            description = "Rising interest rates boost bank margins. Financial sector leads market rally. Other sectors see moderate gains."

        elif cycle_type == MarketCycleType.RETAIL_COLLAPSE:
            headline = "🏪 RETAIL APOCALYPSE - Consumer Spending Crashes"
            description = "Retail sector devastated as consumers tighten belts. Store closures accelerate. Retail stocks plummet."

        elif cycle_type == MarketCycleType.HEALTHCARE_RALLY:
            headline = "🏥 HEALTHCARE RALLY - Medical Innovation Drives Sector Surge"
            description = "Breakthrough treatments and aging demographics fuel healthcare boom. Healthcare stocks surge while other sectors lag."

        elif cycle_type == MarketCycleType.MANUFACTURING_SLUMP:
            headline = "🏭 MANUFACTURING SLUMP - Industrial Production Declines"
            description = "Weak demand and supply chain issues hammer manufacturing. Industrial and manufacturing stocks sink."

        elif cycle_type == MarketCycleType.BUBBLE_POP:
            headline = "💥 BUBBLE BURSTS - Overvalued Markets Crash Back to Reality"
            description = "Unsustainable valuations finally collapse. Panic selling across overheated sectors. Sharp correction as P/E ratios normalize."

        elif cycle_type == MarketCycleType.PROFIT_TAKING:
            headline = "📊 PROFIT TAKING - Investors Lock in Gains After Rally"
            description = "After strong run-up, investors cash out. Broad market pullback as profits are realized. Healthy correction underway."

        else:  # SECTOR_ROTATION
            headline = "🔄 SECTOR ROTATION - Money Flows Between Industries"
            description = "Investors rotate capital from overvalued to undervalued sectors. Winners become losers, losers become winners."

        self.active_cycle = ActiveMarketCycle(
            cycle_type=cycle_type,
            weeks_remaining=duration,
            headline=headline,
            description=description
        )

        # Track this cycle for next time
        self.last_cycle_type = cycle_type

        self.cycle_history.append((week_number, headline))
        return self.active_cycle

    def apply_cycle_effects(self, companies: Dict[str, Company]) -> List[str]:
        """Apply market cycle effects to all companies - now sector-specific"""
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
            # Tech and electronics boom heavily, others modest gains
            for company in companies.values():
                if company.industry in ["Technology", "Electronics"]:
                    change = random.uniform(7.0, 12.0)
                else:
                    change = random.uniform(1.0, 3.0)  # Reduced from 2-4%
                company.price *= (1 + change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Tech boom continues - Technology and Electronics sectors surge!")

        # NEW SECTOR-SPECIFIC EVENTS
        elif cycle.cycle_type == MarketCycleType.TECH_CORRECTION:
            # Tech crashes hard, others slightly down or flat
            for company in companies.values():
                if company.industry in ["Technology", "Electronics"]:
                    change = random.uniform(8.0, 15.0)
                    company.price *= (1 - change / 100)
                else:
                    change = random.uniform(-1.0, 2.0)  # Slight down to slight up
                    company.price *= (1 + change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Tech correction underway - Technology stocks plummet as valuations reset")

        elif cycle.cycle_type == MarketCycleType.ENERGY_CRISIS:
            # Energy surges, others struggle
            for company in companies.values():
                if company.industry == "Energy":
                    change = random.uniform(8.0, 14.0)
                    company.price *= (1 + change / 100)
                elif company.industry in ["Manufacturing", "Industrial"]:
                    # Heavy energy users hurt most
                    change = random.uniform(3.0, 6.0)
                    company.price *= (1 - change / 100)
                else:
                    change = random.uniform(1.0, 3.0)
                    company.price *= (1 - change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Energy crisis deepens - Energy stocks soar, others pressured by costs")

        elif cycle.cycle_type == MarketCycleType.FINANCIAL_SECTOR_BOOM:
            # Financials surge, others moderate gains
            for company in companies.values():
                if company.industry == "Finance":
                    change = random.uniform(6.0, 11.0)
                    company.price *= (1 + change / 100)
                else:
                    change = random.uniform(1.0, 3.0)
                    company.price *= (1 + change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Financial sector boom - Banks lead market rally on strong margins")

        elif cycle.cycle_type == MarketCycleType.RETAIL_COLLAPSE:
            # Retail crashes, others slightly down
            for company in companies.values():
                if company.industry == "Retail":
                    change = random.uniform(10.0, 18.0)
                    company.price *= (1 - change / 100)
                else:
                    change = random.uniform(1.0, 3.0)
                    company.price *= (1 - change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Retail apocalypse - Consumer spending crash devastates retail sector")

        elif cycle.cycle_type == MarketCycleType.HEALTHCARE_RALLY:
            # Healthcare surges, others modest gains
            for company in companies.values():
                if company.industry == "Healthcare":
                    change = random.uniform(6.0, 11.0)
                    company.price *= (1 + change / 100)
                else:
                    change = random.uniform(0.5, 2.5)
                    company.price *= (1 + change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Healthcare rally - Medical sector surges on breakthrough innovations")

        elif cycle.cycle_type == MarketCycleType.MANUFACTURING_SLUMP:
            # Manufacturing/Industrial down, others slightly down
            for company in companies.values():
                if company.industry in ["Manufacturing", "Industrial"]:
                    change = random.uniform(7.0, 13.0)
                    company.price *= (1 - change / 100)
                else:
                    change = random.uniform(1.0, 3.0)
                    company.price *= (1 - change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Manufacturing slump - Industrial production declines hammer factory stocks")

        # CORRECTION EVENTS
        elif cycle.cycle_type == MarketCycleType.BUBBLE_POP:
            # Sharp correction across board, especially high P/E stocks
            for company in companies.values():
                if company.industry == "Rare Fantasy Goods":
                    # Rare goods ignore P/E ratios - erratic behavior
                    change = random.uniform(-3.0, 5.0)  # Can even gain during bubble pops
                    company.price *= (1 + change / 100)
                else:
                    pe_ratio = company.get_pe_ratio()
                    # Higher P/E = bigger correction
                    if pe_ratio > 40:
                        change = random.uniform(12.0, 20.0)
                    elif pe_ratio > 25:
                        change = random.uniform(8.0, 14.0)
                    else:
                        change = random.uniform(4.0, 8.0)
                    company.price *= (1 - change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 BUBBLE POP - Overvalued stocks crash as reality check hits market!")

        elif cycle.cycle_type == MarketCycleType.PROFIT_TAKING:
            # Moderate broad correction
            for company in companies.values():
                change = random.uniform(3.0, 7.0)
                company.price *= (1 - change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Profit taking - Investors lock in gains after strong rally")

        elif cycle.cycle_type == MarketCycleType.SECTOR_ROTATION:
            # High P/E sectors down, low P/E sectors up
            # Calculate median P/E first
            pe_values = [c.get_pe_ratio() for c in companies.values() if c.industry != "Rare Fantasy Goods"]
            median_pe = sorted(pe_values)[len(pe_values) // 2] if pe_values else 20.0

            for company in companies.values():
                if company.industry == "Rare Fantasy Goods":
                    # Rare goods don't participate in P/E-based rotation - wild card behavior
                    change = random.uniform(-4.0, 6.0)
                    company.price *= (1 + change / 100)
                else:
                    pe_ratio = company.get_pe_ratio()
                    if pe_ratio > median_pe * 1.3:
                        # Overvalued - sell off
                        change = random.uniform(4.0, 8.0)
                        company.price *= (1 - change / 100)
                    elif pe_ratio < median_pe * 0.7:
                        # Undervalued - rally
                        change = random.uniform(4.0, 8.0)
                        company.price *= (1 + change / 100)
                    else:
                        # Fairly valued - small moves
                        change = random.uniform(-2.0, 2.0)
                        company.price *= (1 + change / 100)
                company.price = max(0.01, company.price)
            messages.append("📊 Sector rotation - Money flows from overvalued to undervalued sectors")

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

    def __init__(self, name: str, strategy: str, starting_cash: float = 100000.0):
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
            borrow_amount = min(10000, equity * 1.5 - self.borrowed_amount)
            if borrow_amount > 500:
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
                if self.cash > 2000:
                    dollar_amount = min(self.cash * 0.5, 15000)
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
            if equity > 3000:
                high_vol_companies = sorted(companies.values(), key=lambda c: c.base_volatility, reverse=True)[:2]
                for company in high_vol_companies:
                    # Don't short if we already have a large short position
                    current_short = self.short_positions.get(company.name, 0)
                    if current_short * company.price < equity * 0.4:  # Limit short exposure
                        shares_to_short = int(min(equity * 0.3, 10000) / company.price)
                        if shares_to_short > 0:
                            success, msg = self.short_sell(company, shares_to_short, companies, treasury)
                            if success:
                                actions.append(f"🔻 {self.name} shorted {shares_to_short} shares of {company.name} (betting on decline)")
                                break  # One short at a time

        # Baseline buying: always try to buy high volatility stocks if we have cash
        else:
            if self.cash > 2000:
                high_vol_companies = sorted(companies.values(), key=lambda c: c.base_volatility, reverse=True)[:2]
                for company in high_vol_companies:
                    if self.cash > 2000:
                        dollar_amount = min(self.cash * 0.4, 10000)
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
            borrow_amount = min(5000, equity * 0.8 - self.borrowed_amount)
            if borrow_amount > 500:
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

        if stable_companies and self.cash > 2000:
            company = random.choice(stable_companies)
            dollar_amount = min(self.cash * 0.3, 8000)
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
            borrow_amount = min(7500, equity * 1.2 - self.borrowed_amount)
            if borrow_amount > 500:
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
            if self.cash > 2000:
                companies_list = list(companies.values())
                company = random.choice(companies_list)
                dollar_amount = min(self.cash * 0.5, 15000)
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
            if equity > 3000:
                # Pick a random stock to short (contrarian doesn't care about volatility, just sentiment)
                companies_list = list(companies.values())
                company = random.choice(companies_list)
                current_short = self.short_positions.get(company.name, 0)
                # Don't over-short any single company
                if current_short * company.price < equity * 0.3:
                    shares_to_short = int(min(equity * 0.25, 8000) / company.price)
                    if shares_to_short > 0:
                        success, msg = self.short_sell(company, shares_to_short, companies, treasury)
                        if success:
                            actions.append(f"🔻 {self.name} shorted {shares_to_short} shares of {company.name} (contrarian: market too bullish)")

        # Baseline buying: buy random stocks during neutral markets
        else:
            if self.cash > 2000:
                companies_list = list(companies.values())
                company = random.choice(companies_list)
                dollar_amount = min(self.cash * 0.35, 10000)
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
        self.breaking_news = BreakingNewsSystem()  # Breaking news system (replaces MarketNews and weekly news)
        self.market_cycle = MarketCycle()  # Market cycle system (every 6 months)
        self.pending_breaking_news: Optional[Tuple[str, NewsReport, EventType]] = None  # Breaking news to display (company_name, report, event_type)

        # Future price pre-calculation (hidden from players)
        # Stores next 4 weeks of calculated prices: {company_name: [week+1 price, week+2 price, ...]}
        self.future_prices: Dict[str, List[float]] = {}
        # Also track future EPS and fundamental prices for mean reversion
        self.future_eps: Dict[str, List[float]] = {}
        self.future_fundamental_prices: Dict[str, List[float]] = {}

        self._initialize_companies()

        # Initialize new themed investments (after companies are initialized for VoidStocks)
        self.elf_queen_water = ElfQueenWater()
        self.gold_coin = GoldCoin()
        self.void_stocks = VoidStocks(self.companies)
        self.void_catalyst = VoidCatalyst()
        self.mystical_lender = MysticalLender()

        self._initialize_players()
        self._initialize_hedge_funds()

        # Pre-calculate initial future prices
        self._precalculate_future_prices()

    def _initialize_companies(self):
        """Initialize the 8 companies with different industries and liquidity levels"""
        # Format: (name, industry, price, volatility, liquidity, market_cap)
        # Market caps range from $1.5B (micro cap) to $50B (large cap)
        company_data = [
            ("TechCorp", "Technology", 150.0, 8.0, LiquidityLevel.HIGH, 50_000_000_000),  # $50B - Large cap
            ("ElectroMax", "Electronics", 85.0, 6.5, LiquidityLevel.MEDIUM, 10_000_000_000),  # $10B - Mid cap
            ("PharmaCare", "Pharmaceuticals", 220.0, 5.0, LiquidityLevel.LOW, 8_000_000_000),  # $8B - Mid cap
            ("AutoDrive", "Automotive", 95.0, 7.0, LiquidityLevel.MEDIUM, 12_000_000_000),  # $12B - Mid cap
            ("EnergyPlus", "Energy", 110.0, 9.0, LiquidityLevel.LOW, 5_000_000_000),  # $5B - Small cap
            ("Blue Energy Industries", "Mana Extraction", 125.0, 9.5, LiquidityLevel.MEDIUM, 3_000_000_000),  # $3B - Small cap
            ("Rock Friends Inc.", "Golem Manufacturing", 78.0, 11.0, LiquidityLevel.LOW, 2_000_000_000),  # $2B - Small cap
            ("Out of This World Enterprises", "Rare Fantasy Goods", 666.0, 13.0, LiquidityLevel.LOW, 1_500_000_000),  # $1.5B - Micro cap, ultra-rare goods
        ]

        for name, industry, price, volatility, liquidity, market_cap in company_data:
            company = Company(name, industry, price, volatility, liquidity, market_cap)
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

        # Display breaking news if available
        if self.pending_breaking_news:
            company_name, news_report, event_type = self.pending_breaking_news

            print("\n" + "🚨 " + "="*58)
            if news_report.is_rumor:
                print("💬 RUMORS CIRCULATING 💬")
            else:
                print("⚡ BREAKING NEWS ALERT ⚡")
            print("="*60)
            print()

            # Source 1: Financial Times Report (Trustworthy - only reports confirmed major events)
            print("📊 Financial Times Report")
            print("-" * 60)
            if news_report.trustworthy_source:
                print(f"  {news_report.trustworthy_source}")
            else:
                print("  [No major developments to report at this time]")
            print()

            # Source 2: Market Pulse Daily (Posts rumors as clickbait FACTS - no "rumor" tag)
            print("📢 Market Pulse Daily")
            print("-" * 60)
            print(f"  {news_report.market_pulse_source}")
            print()

            # Source 3: Wall Street Wire (Insider Source - 52.5% accurate overall)
            print("🔍 Wall Street Wire (Insider Tip)")
            print("-" * 60)
            print(f"  {news_report.insider_source}")
            print()

            # Source 4: The Rumor Mill (Explicitly marks rumors with "RUMOR: " prefix)
            print("📣 The Rumor Mill")
            print("-" * 60)
            print(f"  {news_report.rumor_mill_source}")

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

        # Apply precompiled prices, EPS, and fundamentals to all companies
        # The future_*[company_name][0] is the actual next week value
        for company_name, company in self.companies.items():
            if company_name in self.future_prices and len(self.future_prices[company_name]) > 0:
                # Apply all precompiled values for this week
                company.price = self.future_prices[company_name][0]
                company.price_history.append(company.price)

                # Also update EPS and fundamental_price to keep in sync
                if company_name in self.future_eps:
                    company.earnings_per_share = self.future_eps[company_name][0]
                if company_name in self.future_fundamental_prices:
                    company.fundamental_price = self.future_fundamental_prices[company_name][0]

        # Check if we should trigger a new market cycle
        cycle_triggered = False
        if self.market_cycle.should_trigger_cycle(self.week_number):
            cycle = self.market_cycle.trigger_cycle(self.week_number, self.companies)
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

        # Update pending breaking news impacts
        # Pass use_precompiled_prices=True because price changes are already baked into future_prices
        impact_messages = self.breaking_news.update_pending_impacts(self.companies, use_precompiled_prices=True)

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

        # Process void state transitions for all players
        void_deletion_occurred = False
        for player in self.players:
            deletion_messages = player.process_void_state_transition(self.void_stocks)
            if deletion_messages:
                void_deletion_occurred = True
                print(f"\n{'='*60}")
                print(f"VOID STATE DELETION - {player.name}")
                print(f"{'='*60}")
                for msg in deletion_messages:
                    print(msg)
                print(f"{'='*60}")

        if void_deletion_occurred:
            input("\nPress Enter to continue...")

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

        # Generate breaking news for the NEXT week (all players will see the same news)
        # This ensures consistent news across all players in the same week
        self.pending_breaking_news = self.breaking_news.generate_breaking_news(self.companies, self.week_number)

    def _advance_future_prices(self):
        """
        Advance future prices by one week: shift array and calculate new week+4.
        This preserves the deterministic future while adding one more week ahead.

        Now includes:
        - EPS updates (earnings growth)
        - Fundamental price random walk
        - Mean reversion (price pulled back toward fundamental)
        """
        # Build a map of when impacts will occur for each company (for lingering effect calculation)
        impact_weeks = {}  # company_name -> set of week numbers when impacts occur
        for impact in self.breaking_news.pending_impacts:
            if impact.is_real:
                impact_week = self.week_number + impact.weeks_until_impact
                if impact.company_name not in impact_weeks:
                    impact_weeks[impact.company_name] = set()
                impact_weeks[impact.company_name].add(impact_week)

        for company_name, company in self.companies.items():
            if company_name not in self.future_prices or len(self.future_prices[company_name]) == 0:
                # No existing future prices - recalculate all
                self._precalculate_future_prices()
                return

            # Shift arrays: remove week+1 (which is now current), keep weeks +2, +3, +4
            remaining_prices = self.future_prices[company_name][1:]
            remaining_eps = self.future_eps[company_name][1:]
            remaining_fundamentals = self.future_fundamental_prices[company_name][1:]

            # Get the previous week's values to continue simulation
            week_ahead = 4  # We're calculating the 4th week ahead
            future_week = self.week_number + week_ahead
            simulated_price = remaining_prices[-1] if remaining_prices else company.price
            simulated_eps = remaining_eps[-1] if remaining_eps else company.earnings_per_share
            simulated_fundamental = remaining_fundamentals[-1] if remaining_fundamentals else company.fundamental_price

            # 1. Update simulated EPS (earnings growth)
            annual_growth = random.uniform(-0.08, 0.12)  # -8% to +12% annual
            weekly_change = annual_growth / 52.0
            simulated_eps *= (1 + weekly_change)
            simulated_eps = max(0.001, simulated_eps)

            # 2. Update simulated fundamental price (random walk)
            # Fundamentals grow/shrink: 40-50% per year = ~0.75-0.95% per week
            annual_fundamental_change = random.uniform(-0.40, 0.50)  # -40% to +50% annual
            weekly_fundamental_change = annual_fundamental_change / 52.0
            simulated_fundamental *= (1 + weekly_fundamental_change)
            simulated_fundamental = max(0.01, simulated_fundamental)

            # 3. Check if market impact will occur this week (check BEFORE applying random walk)
            news_impact_occurred = False
            for impact in self.breaking_news.pending_impacts:
                if impact.company_name == company_name:
                    weeks_until = impact.weeks_until_impact - (week_ahead - 1)
                    if weeks_until == 0 and impact.is_real:
                        news_impact_occurred = True
                        break

            # 4. Apply cycle effect or random walk to price
            # SKIP on market impact weeks - let the impact be the sole driver!
            if not news_impact_occurred:
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

                if cycle_effect != 0:
                    simulated_price *= (1 + cycle_effect / 100)
                else:
                    # Random walk if no cycle
                    change_percent = random.uniform(-company.base_volatility, company.base_volatility)
                    simulated_price *= (1 + change_percent / 100)

            # 5. Apply pending news impacts that will occur in this future week
            for impact in self.breaking_news.pending_impacts:
                if impact.company_name == company_name:
                    weeks_until = impact.weeks_until_impact - (week_ahead - 1)
                    if weeks_until == 0:
                        # This impact will apply in this future week
                        if impact.is_real:
                            simulated_price *= (1 + impact.impact_magnitude / 100)

                            # News also affects fundamental value (real business impact)
                            if impact.impact_magnitude < 0:  # Negative news (scandals/problems)
                                # Apply 15% of the price impact to fundamentals
                                # e.g., -10% price drop → -1.5% fundamental drop
                                fundamental_impact = impact.impact_magnitude * 0.15
                                simulated_fundamental *= (1 + fundamental_impact / 100)
                                simulated_fundamental = max(0.01, simulated_fundamental)
                            else:  # Positive news (successes)
                                # Apply 10% of the price impact to fundamentals (slightly less than scandals)
                                # e.g., +10% price gain → +1.0% fundamental gain
                                fundamental_impact = impact.impact_magnitude * 0.10
                                simulated_fundamental *= (1 + fundamental_impact / 100)

            # 6. Apply mean reversion - pull price back toward fundamental
            # SKIP mean reversion on weeks with ANY market impact (positive OR negative)
            # For 2 weeks after an impact, use dampened mean reversion (lingering fear/hype)
            if not news_impact_occurred:
                # Check if impact occurred 1 or 2 weeks ago (lingering effect)
                weeks_since_impact = None
                if company_name in impact_weeks:
                    if (future_week - 1) in impact_weeks[company_name]:
                        weeks_since_impact = 1
                    elif (future_week - 2) in impact_weeks[company_name]:
                        weeks_since_impact = 2

                # Adjust mean reversion strength based on lingering fear/hype
                if weeks_since_impact == 1:
                    mean_reversion_strength = 0.10  # 10% first week after impact
                elif weeks_since_impact == 2:
                    mean_reversion_strength = 0.20  # 20% second week after impact
                else:
                    mean_reversion_strength = 0.30  # 30% normal mean reversion

                price_gap = simulated_fundamental - simulated_price
                mean_reversion = price_gap * mean_reversion_strength
                simulated_price += mean_reversion

            # Ensure price stays positive
            simulated_price = max(0.01, simulated_price)

            # Update future arrays: old weeks +2, +3, +4 become new +1, +2, +3, and add new +4
            self.future_prices[company_name] = remaining_prices + [simulated_price]
            self.future_eps[company_name] = remaining_eps + [simulated_eps]
            self.future_fundamental_prices[company_name] = remaining_fundamentals + [simulated_fundamental]

    def _precalculate_future_prices(self):
        """
        Pre-calculate the next 4 weeks of prices for all companies.
        This data is NEVER shown to players, but used for news/research generation.

        Now includes:
        - EPS updates (earnings growth)
        - Fundamental price random walk
        - Mean reversion (price pulled back toward fundamental)
        """
        import copy

        # Clear existing future data
        self.future_prices = {}
        self.future_eps = {}
        self.future_fundamental_prices = {}

        # Build a map of when impacts will occur for each company (for lingering effect calculation)
        impact_weeks = {}  # company_name -> set of week numbers when impacts occur
        for impact in self.breaking_news.pending_impacts:
            if impact.is_real:
                impact_week = self.week_number + impact.weeks_until_impact
                if impact.company_name not in impact_weeks:
                    impact_weeks[impact.company_name] = set()
                impact_weeks[impact.company_name].add(impact_week)

        # For each company, calculate future prices, EPS, and fundamentals
        for company_name, company in self.companies.items():
            future_company_prices = []
            future_company_eps = []
            future_company_fundamentals = []

            # Start with current values
            simulated_eps = company.earnings_per_share
            simulated_fundamental = company.fundamental_price

            # Simulate each week ahead
            for week_ahead in range(1, 5):  # Calculate week+1 through week+4
                future_week = self.week_number + week_ahead

                # Start with current or previous simulated price
                if week_ahead == 1:
                    simulated_price = company.price
                else:
                    # Use the previously calculated week price
                    simulated_price = future_company_prices[week_ahead - 2]
                    simulated_eps = future_company_eps[week_ahead - 2]
                    simulated_fundamental = future_company_fundamentals[week_ahead - 2]

                # 1. Update simulated EPS (earnings growth - matches Company.update_earnings())
                annual_growth = random.uniform(-0.08, 0.12)  # -8% to +12% annual
                weekly_change = annual_growth / 52.0
                simulated_eps *= (1 + weekly_change)
                simulated_eps = max(0.001, simulated_eps)  # Prevent negative earnings

                # 2. Update simulated fundamental price (random walk)
                # Fundamentals grow/shrink: 40-50% per year = ~0.75-0.95% per week
                annual_fundamental_change = random.uniform(-0.40, 0.50)  # -40% to +50% annual
                weekly_fundamental_change = annual_fundamental_change / 52.0
                simulated_fundamental *= (1 + weekly_fundamental_change)
                simulated_fundamental = max(0.01, simulated_fundamental)

                # 3. Check if market impact will occur this week (check BEFORE applying random walk)
                news_impact_occurred = False
                for impact in self.breaking_news.pending_impacts:
                    if impact.company_name == company_name:
                        weeks_until = impact.weeks_until_impact - (week_ahead - 1)
                        if weeks_until == 0 and impact.is_real:
                            news_impact_occurred = True
                            break

                # 4. Apply cycle effect or random walk to price
                # SKIP on market impact weeks - let the impact be the sole driver!
                if not news_impact_occurred:
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

                    if cycle_effect != 0:
                        simulated_price *= (1 + cycle_effect / 100)
                    else:
                        # Random walk if no cycle (additional volatility on top of fundamentals)
                        change_percent = random.uniform(-company.base_volatility, company.base_volatility)
                        simulated_price *= (1 + change_percent / 100)

                # 5. Apply pending news impacts that will occur in this future week
                for impact in self.breaking_news.pending_impacts:
                    if impact.company_name == company_name:
                        weeks_until = impact.weeks_until_impact - (week_ahead - 1)
                        if weeks_until == 0:
                            # This impact will apply in this future week
                            if impact.is_real:
                                simulated_price *= (1 + impact.impact_magnitude / 100)

                                # News also affects fundamental value (real business impact)
                                if impact.impact_magnitude < 0:  # Negative news (scandals/problems)
                                    # Apply 15% of the price impact to fundamentals
                                    # e.g., -10% price drop → -1.5% fundamental drop
                                    fundamental_impact = impact.impact_magnitude * 0.15
                                    simulated_fundamental *= (1 + fundamental_impact / 100)
                                    simulated_fundamental = max(0.01, simulated_fundamental)
                                else:  # Positive news (successes)
                                    # Apply 10% of the price impact to fundamentals (slightly less than scandals)
                                    # e.g., +10% price gain → +1.0% fundamental gain
                                    fundamental_impact = impact.impact_magnitude * 0.10
                                    simulated_fundamental *= (1 + fundamental_impact / 100)

                # 6. Apply mean reversion - pull price back toward fundamental
                # SKIP mean reversion on weeks with ANY market impact (positive OR negative)
                # For 2 weeks after an impact, use dampened mean reversion (lingering fear/hype)
                if not news_impact_occurred:
                    # Check if impact occurred 1 or 2 weeks ago (lingering effect)
                    weeks_since_impact = None
                    if company_name in impact_weeks:
                        if (future_week - 1) in impact_weeks[company_name]:
                            weeks_since_impact = 1
                        elif (future_week - 2) in impact_weeks[company_name]:
                            weeks_since_impact = 2

                    # Adjust mean reversion strength based on lingering fear/hype
                    if weeks_since_impact == 1:
                        mean_reversion_strength = 0.10  # 10% first week after impact
                    elif weeks_since_impact == 2:
                        mean_reversion_strength = 0.20  # 20% second week after impact
                    else:
                        mean_reversion_strength = 0.30  # 30% normal mean reversion

                    price_gap = simulated_fundamental - simulated_price
                    mean_reversion = price_gap * mean_reversion_strength
                    simulated_price += mean_reversion

                # Ensure values stay positive
                simulated_price = max(0.01, simulated_price)

                # Store all three values for this week
                future_company_prices.append(simulated_price)
                future_company_eps.append(simulated_eps)
                future_company_fundamentals.append(simulated_fundamental)

            self.future_prices[company_name] = future_company_prices
            self.future_eps[company_name] = future_company_eps
            self.future_fundamental_prices[company_name] = future_company_fundamentals

    def _get_cycle_effect(self, cycle_type: 'MarketCycleType', industry: str) -> float:
        """Get the average price change effect for a cycle type"""
        if cycle_type == MarketCycleType.BULL_MARKET:
            if industry == "Rare Fantasy Goods":
                # Rare goods don't follow bull markets - ultra-wealthy always buy
                return random.uniform(1.0, 3.0)
            return random.uniform(3.0, 7.0)
        elif cycle_type == MarketCycleType.BEAR_MARKET:
            if industry == "Rare Fantasy Goods":
                # Counter-cyclical: rich seek rare luxury goods as safe haven
                return random.uniform(2.0, 6.0)
            return -random.uniform(2.0, 5.0)
        elif cycle_type == MarketCycleType.RECESSION:
            if industry == "Rare Fantasy Goods":
                # Ultra-wealthy unaffected by recession, still buying rare items
                return random.uniform(-1.0, 2.0)
            return -random.uniform(4.0, 8.0)
        elif cycle_type == MarketCycleType.INFLATION:
            if industry == "Energy":
                return random.uniform(4.0, 8.0)
            elif industry == "Mana Extraction":
                # Mana becomes more valuable during energy crises
                return random.uniform(5.0, 10.0)
            elif industry == "Rare Fantasy Goods":
                # Rare goods are ultimate inflation hedge - hard assets
                return random.uniform(8.0, 15.0)
            else:
                return -random.uniform(2.0, 4.0)
        elif cycle_type == MarketCycleType.MARKET_CRASH:
            if industry == "Golem Manufacturing":
                # Golems crash HARD during market panic (fear of automation)
                return -random.uniform(12.0, 20.0)
            elif industry == "Mana Extraction":
                # Mana extraction faces extreme volatility
                return -random.uniform(10.0, 18.0)
            elif industry == "Rare Fantasy Goods":
                # Chaotic behavior during crashes - sometimes gains (flight to rarity)
                return random.uniform(-5.0, 8.0)
            else:
                return -random.uniform(8.0, 15.0)
        elif cycle_type == MarketCycleType.RECOVERY:
            if industry == "Golem Manufacturing":
                # Golems recover slower (trust issues)
                return random.uniform(3.0, 6.0)
            elif industry == "Rare Fantasy Goods":
                # Doesn't need recovery - operates outside normal cycles
                return random.uniform(0.0, 3.0)
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
            elif industry == "Rare Fantasy Goods":
                # Tech boom doesn't affect cosmic artifact market
                return random.uniform(-1.0, 2.0)
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
            equity = player.calculate_equity(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
            print(f"Current Equity: ${equity:.2f}")
            print(f"Borrowed Amount: ${player.borrowed_amount:.2f}")
            print(f"Required Action: Increase equity or repay loan immediately!")
            print("="*60)
            input("\nPress Enter to continue...")

        # Breaking news is now generated once per week in update_market()
        # All players in the same week see the same news

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
            print("13. Deposit Collateral (Reduces Margin Call Threshold)")
            print("14. Withdraw Collateral")
            print("15. Save Game")
            print("16. End Turn")
            print("-"*60)

            choice = input("Enter choice (1-16): ").strip()

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
                self._deposit_collateral_menu(player)

            elif choice == "14":
                self._withdraw_collateral_menu(player)

            elif choice == "15":
                filename = input("Enter save filename (default: savegame.json): ").strip()
                if not filename:
                    filename = "savegame.json"
                self.save_game(filename)

            elif choice == "16":
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

                # Check for void stock deletion warning before ending turn
                has_void_warning, at_risk_purchases = player.check_void_stock_warning(self.void_stocks)
                if has_void_warning:
                    print("\n" + "💀 " + "="*58)
                    print("💀  VOID STOCK DELETION WARNING!")
                    print("="*60)
                    print("Next week will be a VOID STATE - the following shares will be DELETED:")
                    print()
                    total_at_risk = sum(p['shares'] for p in at_risk_purchases)
                    for purchase in at_risk_purchases:
                        print(f"  • {purchase['shares']} shares (purchased in week {purchase['purchase_week']}) - 5th void state!")
                    print()
                    print(f"Total shares to be deleted: {total_at_risk}")
                    print()
                    print("These shares have gone through 4 void states and will be consumed by the void next week!")
                    print()
                    print("Recommended action:")
                    print("• SELL these shares NOW before they disappear!")
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
        equity = player.calculate_equity(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
        print(f"Current Equity: ${equity:.2f}")
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

                success, message = player.buy_stock(company, dollar_amount, leverage, self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
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
        print("8. " + str(self.mystical_lender))
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
                    human_players = [p.name for p in self.players if not getattr(p, 'is_npc', False)]
                    success, msg = player.buy_void_catalyst(self.void_catalyst, human_players)
                    print(msg)
            elif choice == 8:
                # Mystical Lender
                print("\n" + str(self.mystical_lender))
                print(f"\n{self.mystical_lender.description}")
                confirm = input(f"\nAccept the loan? (y/n): ")
                if confirm.lower() == 'y':
                    success, msg = player.accept_mystical_lender(self.mystical_lender)
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
        if player.mystical_lender_debt > 0:
            print(f"  Mystical Lender Debt: ${player.mystical_lender_debt:.2f}")
        print()
        print("1. Sell Gold")
        print("2. Sell Holy Water")
        print("3. Sell Elf Queen's Water")
        print("4. Sell Gold Coin")
        print("5. Sell Void Stocks")
        if player.mystical_lender_debt > 0:
            print("6. Repay Mystical Lender")
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
            elif choice == 6:
                # Repay Mystical Lender
                if player.mystical_lender_debt <= 0:
                    print("You have no debt with The Mystical Lender!")
                    return
                print(f"\nMystical Lender Debt: ${player.mystical_lender_debt:.2f}")
                print(f"Your Cash: ${player.cash:.2f}")
                amount_input = input(f"How much to repay? (Enter amount or 'all' for full repayment): ")
                try:
                    if amount_input.lower() == 'all':
                        success, msg = player.repay_mystical_lender()
                    else:
                        amount = float(amount_input)
                        success, msg = player.repay_mystical_lender(amount)
                    print(msg)
                except ValueError:
                    print("Invalid amount!")
            else:
                print("Invalid choice!")

        except ValueError:
            print("Invalid input!")

    def _borrow_money_menu(self, player: Player):
        """Menu for borrowing money using leverage"""
        print("\n" + "="*60)
        print("BORROW MONEY (LEVERAGE)")
        print("="*60)

        equity = player.calculate_equity(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)

        print(f"Your Equity: ${equity:.2f}")
        print(f"Already Borrowed: ${player.borrowed_amount:.2f}")
        print(f"Interest Rate: {player.interest_rate_weekly:.3f}% per week (~6% annually)")
        print()
        print("⚠️  WARNING: No borrowing limit! Be careful of margin calls.")

        # Show margin call info if already borrowing
        if player.borrowed_amount > 0:
            total_position = equity + player.borrowed_amount
            if total_position > 0:
                equity_ratio = (equity / total_position) * 100
                margin_threshold = player.get_margin_call_threshold(equity) * 100
                print(f"Current Equity Ratio: {equity_ratio:.1f}% (Margin Call at {margin_threshold:.1f}%)")
        print()

        try:
            amount = float(input("How much to borrow? $"))

            if amount <= 0:
                print("Invalid amount!")
                return

            success, message = player.borrow_money(amount, self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
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

    def _deposit_collateral_menu(self, player: Player):
        """Menu for depositing collateral to reduce margin call threshold"""
        print("\n" + "="*60)
        print("DEPOSIT COLLATERAL")
        print("="*60)

        equity = player.calculate_equity(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)

        print(f"Available Cash: ${player.cash:.2f}")
        print(f"Current Equity: ${equity:.2f}")
        print(f"Collateral Deposited: ${player.collateral_deposited:.2f}")
        print()

        current_threshold = player.get_margin_call_threshold(equity) * 100
        print(f"Current Margin Call Threshold: {current_threshold:.1f}%")

        if equity > 0:
            collateral_ratio = player.collateral_deposited / equity
            print(f"Collateral Ratio: {collateral_ratio * 100:.1f}% of equity")
        print()

        print("💡 INFO:")
        print("   • Base margin call threshold: 30%")
        print("   • Depositing 100% of your equity reduces it to: 10%")
        print("   • Collateral cannot be withdrawn until you are debt-free")
        print()

        try:
            amount = float(input("How much to deposit as collateral? $"))

            if amount <= 0:
                print("Invalid amount!")
                return

            success, message = player.deposit_collateral(amount)
            print(f"\n{message}")

            if success:
                # Show new threshold
                new_equity = player.calculate_equity(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
                new_threshold = player.get_margin_call_threshold(new_equity) * 100
                print(f"New Margin Call Threshold: {new_threshold:.1f}%")

        except ValueError:
            print("Invalid input!")

    def _withdraw_collateral_menu(self, player: Player):
        """Menu for withdrawing collateral"""
        print("\n" + "="*60)
        print("WITHDRAW COLLATERAL")
        print("="*60)

        if player.collateral_deposited <= 0:
            print("You don't have any collateral deposited!")
            return

        print(f"Collateral Deposited: ${player.collateral_deposited:.2f}")
        print(f"Outstanding Debt: ${player.borrowed_amount:.2f}")
        print()

        if player.borrowed_amount > 0:
            print("⚠️  You cannot withdraw collateral while you have outstanding debt!")
            print(f"   Please repay your ${player.borrowed_amount:.2f} loan first.")
            return

        try:
            amount = float(input("How much to withdraw? $"))

            if amount <= 0:
                print("Invalid amount!")
                return

            success, message = player.withdraw_collateral(amount)
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
                'breaking_news': self.breaking_news.to_dict(),
                'market_cycle': self.market_cycle.to_dict(),
                'pending_breaking_news': (
                    self.pending_breaking_news[0],  # company_name
                    self.pending_breaking_news[1].to_dict(),  # NewsReport
                    self.pending_breaking_news[2].value  # EventType as string
                ) if self.pending_breaking_news else None,
                'future_prices': self.future_prices,
                'future_eps': self.future_eps,
                'future_fundamental_prices': self.future_fundamental_prices,
                'random_state': list(random.getstate()),  # Save random state for deterministic futures
                'quantum_singularity': self.quantum_singularity.to_dict(),
                'gold': self.gold.to_dict(),
                'holy_water': self.holy_water.to_dict(),
                'elf_queen_water': self.elf_queen_water.to_dict(),
                'gold_coin': self.gold_coin.to_dict(),
                'void_stocks': self.void_stocks.to_dict(),
                'void_catalyst': self.void_catalyst.to_dict(),
                'mystical_lender': self.mystical_lender.to_dict()
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

            # Restore breaking news system
            game.breaking_news = BreakingNewsSystem.from_dict(game_state.get('breaking_news', {}))

            # Restore market cycle
            game.market_cycle = MarketCycle.from_dict(game_state['market_cycle'])

            # Restore pending breaking news
            pending_breaking_data = game_state.get('pending_breaking_news')
            if pending_breaking_data:
                company_name = pending_breaking_data[0]
                news_report = NewsReport.from_dict(pending_breaking_data[1])
                event_type = EventType(pending_breaking_data[2])
                game.pending_breaking_news = (company_name, news_report, event_type)
            else:
                game.pending_breaking_news = None

            # Restore future prices (or recalculate if not present in save file)
            if 'future_prices' in game_state:
                game.future_prices = game_state['future_prices']
                # Also restore new future data if available
                game.future_eps = game_state.get('future_eps', {})
                game.future_fundamental_prices = game_state.get('future_fundamental_prices', {})
            else:
                # Old save file - recalculate all future data
                game.future_prices = {}
                game.future_eps = {}
                game.future_fundamental_prices = {}
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

            if 'mystical_lender' in game_state:
                game.mystical_lender = MysticalLender.from_dict(game_state['mystical_lender'])
            else:
                game.mystical_lender = MysticalLender()

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

        # Generate initial breaking news for week 1 (only if not already loaded from save)
        if self.pending_breaking_news is None:
            self.pending_breaking_news = self.breaking_news.generate_breaking_news(self.companies, self.week_number)

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

            # Enforce margin calls for NPCs (hedge funds) too
            for hedge_fund in self.hedge_funds:
                if hedge_fund.check_margin_call(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst):
                    actions = hedge_fund.force_liquidate_margin_call(self.companies, self.treasury, self.gold, self.holy_water, self.quantum_singularity, self.elf_queen_water, self.gold_coin, self.void_stocks, self.void_catalyst)
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
