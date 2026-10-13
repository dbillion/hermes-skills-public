#!/usr/bin/env python3
"""
LinkedIn Post Generator - Reverse-engineered pattern-based post creation.

Generates compelling LinkedIn posts using proven structural patterns that emphasize
tools, solutions, and user benefits.

Usage:
    python generate.py --topic "Real-time collaboration" --pattern psb --tone professional
    python generate.py --use-case "Context switching pain" --solution-type tool
"""

import json
import argparse
import random
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

# Pattern definitions
PATTERNS = {
    'psb': {
        'name': 'Problem → Solution → Benefit',
        'description': 'Hook on problem, present solution, deliver concrete benefit',
        'structure': ['hook', 'body', 'cta'],
    },
    'journey': {
        'name': '"I used to..." → "Then I discovered..."',
        'description': 'Personal story of frustration → discovery → outcome',
        'structure': ['hook', 'body', 'cta'],
    },
    'dia': {
        'name': 'Data + Insight + Action',
        'description': 'Striking stat → interpretation → engagement question',
        'structure': ['hook', 'body', 'cta'],
    },
    'fuv': {
        'name': 'Feature → Use Case → Value',
        'description': 'Feature announcement → real scenario → ROI/benefit',
        'structure': ['hook', 'body', 'cta'],
    },
    'list': {
        'name': 'List + Insight',
        'description': 'Numbered/bulleted items → meta-pattern or invitation',
        'structure': ['hook', 'body', 'cta'],
    },
}

# Tone templates
TONE_PROFILES = {
    'professional': {
        'hooks_prefix': ['The data shows...', 'Enterprise leaders report...', 'Our research reveals...'],
        'body_style': 'metric-driven, authoritative',
        'cta_style': 'business-impact question',
    },
    'conversational': {
        'hooks_prefix': ['I used to...', 'Here\'s what surprised me...', 'The real issue is...'],
        'body_style': 'personal anecdote, relatable',
        'cta_style': 'peer engagement question',
    },
    'thought-leader': {
        'hooks_prefix': ['We\'ve been solving the wrong problem...', 'The pattern nobody talks about...', 'What actually matters...'],
        'body_style': 'framework-driven, forward-thinking',
        'cta_style': 'framework or principle question',
    },
    'founder': {
        'hooks_prefix': ['Biggest mistake I made...', 'Here\'s what changed everything...', 'I was wrong about...'],
        'body_style': 'scrappy, outcome-focused, learning-oriented',
        'cta_style': 'action question or admission',
    },
    'creator': {
        'hooks_prefix': ['Behind the scenes...', 'Here\'s how we actually...', 'Nobody talks about this part...'],
        'body_style': 'process-transparent, journey-focused',
        'cta_style': 'community invitation',
    },
}

# Engagement drivers database
ENGAGEMENT_DRIVERS = {
    'tool_focus': [
        'Real-world tool or feature mentioned',
        'Specific product capability highlighted',
        'Integration or workflow benefit shown',
    ],
    'metric_driven': [
        'Specific percentage or number provided',
        'Time savings quantified',
        'ROI or business impact stated',
    ],
    'relatable': [
        'Common pain point addressed',
        'Personal vulnerability shown',
        'Industry problem articulated',
    ],
    'actionable': [
        'Clear question for engagement',
        'Framework to apply',
        'Thought-provoking concept',
    ],
}

# Hashtag suggestions by topic
HASHTAG_SUGGESTIONS = {
    'collaboration': ['#engineering', '#teamwork', '#productivity', '#techtools', '#devtools'],
    'productivity': ['#productivity', '#efficiency', '#workflow', '#shipping', '#devtools'],
    'ai': ['#ai', '#llm', '#artificialintelligence', '#technology', '#futureofwork'],
    'leadership': ['#leadership', '#management', '#teambuilding', '#techleadership', '#startup'],
    'engineering': ['#engineering', '#softwareengineering', '#codereview', '#devtools', '#shipping'],
    'default': ['#tech', '#productivity', '#innovation', '#leadership', '#devtools'],
}

@dataclass
class LinkedInPost:
    """Structured LinkedIn post output."""
    hook: str
    body: str
    cta: str
    pattern_used: str
    tone_used: str
    engagement_drivers: List[str]
    suggested_hashtags: List[str]
    full_post: Optional[str] = None

    def render_full(self) -> str:
        """Render complete post with formatting."""
        return f"{self.hook}\n\n{self.body}\n\n{self.cta}\n\n{' '.join(self.suggested_hashtags)}"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['full_post'] = self.render_full()
        return data


class LinkedInPostGenerator:
    """Generate LinkedIn posts using reverse-engineered patterns."""

    def __init__(self):
        self.patterns = PATTERNS
        self.tones = TONE_PROFILES
        self.engagement_db = ENGAGEMENT_DRIVERS
        self.hashtag_db = HASHTAG_SUGGESTIONS

    def create(
        self,
        topic: str,
        pattern: str = 'psb',
        tone: str = 'professional',
        highlights: Optional[List[str]] = None,
        length: str = 'medium',
        use_case: Optional[str] = None,
        solution_type: Optional[str] = None,
    ) -> LinkedInPost:
        """
        Generate a LinkedIn post.

        Args:
            topic: Main subject for the post
            pattern: Which framework to use (psb, journey, dia, fuv, list)
            tone: Voice style (professional, conversational, thought-leader, founder, creator)
            highlights: Key benefits/features to emphasize
            length: Post length (short, medium, long)
            use_case: Specific problem or scenario
            solution_type: Type of solution (tool, process, framework, insight)

        Returns:
            LinkedInPost with structured content
        """
        if pattern not in self.patterns:
            raise ValueError(f"Unknown pattern: {pattern}. Choose from: {list(self.patterns.keys())}")

        if tone not in self.tones:
            raise ValueError(f"Unknown tone: {tone}. Choose from: {list(self.tones.keys())}")

        # Generate post sections
        if pattern == 'psb':
            post = self._generate_psb(topic, tone, highlights, use_case)
        elif pattern == 'journey':
            post = self._generate_journey(topic, tone, highlights)
        elif pattern == 'dia':
            post = self._generate_dia(topic, tone, highlights)
        elif pattern == 'fuv':
            post = self._generate_fuv(topic, tone, highlights, solution_type)
        elif pattern == 'list':
            post = self._generate_list(topic, tone, highlights, use_case)

        # Extract engagement drivers
        drivers = self._identify_engagement_drivers(post, highlights)

        # Generate hashtags
        hashtags = self._suggest_hashtags(topic)

        # Create final post object
        result = LinkedInPost(
            hook=post['hook'],
            body=post['body'],
            cta=post['cta'],
            pattern_used=pattern,
            tone_used=tone,
            engagement_drivers=drivers,
            suggested_hashtags=hashtags,
        )

        return result

    def _generate_psb(self, topic: str, tone: str, highlights: Optional[List[str]], use_case: Optional[str]) -> Dict:
        """Generate Problem → Solution → Benefit pattern."""
        prefix = random.choice(self.tones[tone]['hooks_prefix'])

        if tone == 'conversational':
            hook = f"{prefix} {use_case or f'working on {topic}'} was frustrating."
        elif tone == 'thought-leader':
            hook = f"{prefix.capitalize()} {topic.lower()}."
        else:
            hook = f"{prefix} {topic}."

        body_parts = []
        if highlights:
            body_parts.append(f"The key: {', '.join(highlights)}.")
        body_parts.append(f"This changes how teams approach {topic}.")

        body = " ".join(body_parts)

        cta_options = [
            f"What's your biggest {topic} challenge?",
            f"How would this change your {topic} workflow?",
            f"Does this resonate with your team's {topic} experience?",
        ]
        cta = random.choice(cta_options)

        return {
            'hook': hook,
            'body': body,
            'cta': cta,
        }

    def _generate_journey(self, topic: str, tone: str, highlights: Optional[List[str]]) -> Dict:
        """Generate Journey pattern."""
        hook = f"I used to think {topic} was a minor problem."

        body_parts = [f"Then I realized:"]
        if highlights:
            body_parts.extend([f"• {h}" for h in highlights])
        else:
            body_parts.append(f"The real cost of poor {topic} is hidden in everyday friction.")

        body = "\n".join(body_parts)

        cta = f"That changed everything about how I approach {topic}. What's your breakthrough moment?"

        return {
            'hook': hook,
            'body': body,
            'cta': cta,
        }

    def _generate_dia(self, topic: str, tone: str, highlights: Optional[List[str]]) -> Dict:
        """Generate Data + Insight + Action pattern."""
        metrics = [
            '30%', '40%', '50%', '2x', '3x', '4x',
            '2 hours', '3 days', '1 week', '25%', '60%',
        ]
        metric = random.choice(metrics)

        hook = f"Here's what we found: teams struggle with {topic} {metric} more than they realize."

        insights = [
            f"It's not about {topic} directly—it's about the compound cost of losing focus.",
            f"The pattern: {topic} creates a cascade of smaller inefficiencies.",
            f"What actually matters: whether your team can reason through {topic} clearly.",
        ]
        body = random.choice(insights)

        if highlights:
            body += f"\n\nWhat works: {', '.join(highlights)}."

        cta = f"How much of your team's capacity gets tied up in {topic}?"

        return {
            'hook': hook,
            'body': body,
            'cta': cta,
        }

    def _generate_fuv(self, topic: str, tone: str, highlights: Optional[List[str]], solution_type: Optional[str]) -> Dict:
        """Generate Feature → Use Case → Value pattern."""
        feature = solution_type or 'feature'
        hook = f"Just shipped: improved {topic}."

        scenario_options = [
            f"Picture this: you're working on {topic}, and suddenly everything is clearer.",
            f"Real scenario: your team is solving a {topic} problem, and it just got 10x easier.",
            f"Imagine: {topic} is no longer a blocker.",
        ]
        body = random.choice(scenario_options)

        if highlights:
            body += f" Because of {', '.join(highlights)}."

        value_options = [
            f"Result: {random.choice(['30% faster', '50% faster', '2x faster'])} shipping.",
            f"Impact: teams now ship {topic}-related features {random.choice(['30% faster', '2 weeks earlier', 'without friction'])}.",
            f"Outcome: {topic} went from a pain point to a non-issue.",
        ]
        cta = random.choice(value_options)

        return {
            'hook': hook,
            'body': body,
            'cta': cta,
        }

    def _generate_list(self, topic: str, tone: str, highlights: Optional[List[str]], use_case: Optional[str]) -> Dict:
        """Generate List + Insight pattern."""
        list_intro_options = [
            f"Here's what kills {topic}:",
            f"Common {topic} mistakes:",
            f"What we learned about {topic}:",
        ]
        hook = random.choice(list_intro_options)

        body_items = highlights or [
            "Scattered decisions",
            "Missing context",
            "Async delays",
            "Onboarding friction",
            "Tool fragmentation",
        ]

        body = "\n".join([f"• {item}" for item in body_items[:5]])

        meta_insights = [
            f"The pattern: every problem traces back to the same root cause.",
            f"What's not obvious: the cost is compounded, not isolated.",
            f"The opportunity: fix one, and several others improve too.",
        ]
        cta = f"{random.choice(meta_insights)} Which of these is your team's biggest blocker?"

        return {
            'hook': hook,
            'body': body,
            'cta': cta,
        }

    def _identify_engagement_drivers(self, post: Dict, highlights: Optional[List[str]]) -> List[str]:
        """Identify what makes this post engaging."""
        drivers = []

        if highlights:
            drivers.append('Specific benefits highlighted')

        if any(word in post['body'].lower() for word in ['40%', '30%', '2x', '3x', 'faster', 'hours']):
            drivers.append('Metric-driven insight')

        if 'i used to' in post['hook'].lower() or 'frustrat' in post['body'].lower():
            drivers.append('Relatable pain point')

        if '?' in post['cta']:
            drivers.append('Engagement question')

        return drivers or ['Structured insight', 'Clear CTA']

    def _suggest_hashtags(self, topic: str) -> List[str]:
        """Suggest relevant hashtags."""
        keywords = topic.lower().split()
        relevant_tags = self.hashtag_db.get('default', [])

        # Match topic keywords to hashtag categories
        if any(k in ['collab', 'sync', 'team', 'async'] for k in keywords):
            relevant_tags = self.hashtag_db.get('collaboration', self.hashtag_db['default'])
        elif any(k in ['speed', 'ship', 'produc', 'efficien'] for k in keywords):
            relevant_tags = self.hashtag_db.get('productivity', self.hashtag_db['default'])

        return random.sample(relevant_tags, min(5, len(relevant_tags)))


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description='Generate LinkedIn posts using reverse-engineered patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python generate.py --topic "Real-time collaboration" --pattern psb --tone professional
  python generate.py --use-case "Context switching" --solution-type tool --tone conversational
  python generate.py --topic "AI productivity" --pattern dia --highlights "context","speed","focus"
        ''',
    )

    parser.add_argument('--topic', type=str, help='Main subject for the post')
    parser.add_argument('--pattern', type=str, default='psb', choices=list(PATTERNS.keys()),
                        help='Post structure pattern')
    parser.add_argument('--tone', type=str, default='professional', choices=list(TONE_PROFILES.keys()),
                        help='Voice style')
    parser.add_argument('--highlights', type=str, help='Comma-separated benefits/features to emphasize')
    parser.add_argument('--use-case', type=str, help='Specific problem or scenario')
    parser.add_argument('--solution-type', type=str, choices=['tool', 'process', 'framework', 'insight'],
                        help='Type of solution')
    parser.add_argument('--length', type=str, default='medium', choices=['short', 'medium', 'long'],
                        help='Post length')
    parser.add_argument('--variations', type=int, default=1, help='Number of post variations to generate')
    parser.add_argument('--output', type=str, choices=['json', 'text'], default='text',
                        help='Output format')

    args = parser.parse_args()

    # Validate required arguments
    if not args.topic and not args.use_case:
        parser.error('Either --topic or --use-case is required')

    if not args.topic and args.use_case:
        args.topic = args.use_case

    # Parse highlights
    highlights = None
    if args.highlights:
        highlights = [h.strip() for h in args.highlights.split(',')]

    # Generate posts
    generator = LinkedInPostGenerator()
    posts = []

    for i in range(args.variations):
        # Vary pattern if multiple variations requested
        if args.variations > 1:
            pattern = random.choice(list(PATTERNS.keys()))
        else:
            pattern = args.pattern

        post = generator.create(
            topic=args.topic,
            pattern=pattern,
            tone=args.tone,
            highlights=highlights,
            length=args.length,
            use_case=args.use_case,
            solution_type=args.solution_type,
        )
        posts.append(post)

    # Output
    if args.output == 'json':
        output = json.dumps([p.to_dict() for p in posts], indent=2)
        print(output)
    else:
        for i, post in enumerate(posts, 1):
            if len(posts) > 1:
                print(f"\n{'='*60}")
                print(f"POST {i} ({post.pattern_used} | {post.tone_used})")
                print('='*60)
            print(f"\n{post.render_full()}\n")
            print(f"Engagement drivers: {', '.join(post.engagement_drivers)}")


if __name__ == '__main__':
    main()
