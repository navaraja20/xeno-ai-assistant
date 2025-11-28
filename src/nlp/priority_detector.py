"""
Priority Detector
Detect task priority from natural language
"""

import re
from typing import Optional, Tuple

from src.core.logger import setup_logger


class PriorityDetector:
    """Detects task priority from text"""

    def __init__(self):
        self.logger = setup_logger("nlp.priority")

        # Priority keywords
        self.priority_keywords = {
            'critical': [
                'critical', 'urgent', 'asap', 'emergency', 'immediately',
                'crucial', 'vital', 'must do', 'top priority', 'highest priority'
            ],
            'high': [
                'high priority', 'important', 'high', 'significant',
                'essential', 'pressing', 'priority', 'soon'
            ],
            'medium': [
                'medium', 'moderate', 'normal', 'regular', 'standard'
            ],
            'low': [
                'low priority', 'low', 'minor', 'when possible',
                'if time', 'eventually', 'someday', 'maybe'
            ],
        }

        # Compile patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for priority detection"""
        self.priority_patterns = {}

        for priority, keywords in self.priority_keywords.items():
            # Create pattern for each priority level
            pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'
            self.priority_patterns[priority] = re.compile(pattern, re.IGNORECASE)

        # Exclamation marks (urgency indicators)
        self.exclamation_pattern = re.compile(r'!+')

        # Deadline-based urgency
        self.deadline_patterns = [
            (r'\btoday\b', 'critical'),
            (r'\basap\b', 'critical'),
            (r'\btomorrow\b', 'high'),
            (r'\bthis week\b', 'high'),
            (r'\bnext week\b', 'medium'),
        ]

    def detect_priority(self, text: str) -> str:
        """Detect priority from text"""
        text_lower = text.lower()

        # 1. Check for explicit priority keywords
        priority_scores = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
        }

        for priority, pattern in self.priority_patterns.items():
            matches = pattern.findall(text_lower)
            priority_scores[priority] += len(matches)

        # 2. Check exclamation marks
        exclamations = self.exclamation_pattern.findall(text)
        if exclamations:
            max_exclamations = max(len(e) for e in exclamations)
            if max_exclamations >= 3:
                priority_scores['critical'] += 3
            elif max_exclamations >= 2:
                priority_scores['high'] += 2
            else:
                priority_scores['high'] += 1

        # 3. Check deadline-based urgency
        for pattern, priority in self.deadline_patterns:
            if re.search(pattern, text_lower):
                priority_scores[priority] += 2

        # 4. Check for negative words (might indicate low priority)
        low_indicators = ['later', 'whenever', 'no rush', 'no hurry']
        for indicator in low_indicators:
            if indicator in text_lower:
                priority_scores['low'] += 1

        # 5. Determine final priority
        max_score = max(priority_scores.values())
        if max_score == 0:
            return 'medium'  # Default priority

        # Return priority with highest score
        for priority in ['critical', 'high', 'medium', 'low']:
            if priority_scores[priority] == max_score:
                return priority

        return 'medium'

    def extract_priority_from_text(self, text: str) -> Tuple[str, str]:
        """Extract priority and return cleaned text"""
        priority = self.detect_priority(text)
        cleaned = text

        # Remove priority-related phrases
        for keywords in self.priority_keywords.values():
            for keyword in keywords:
                # Remove the keyword
                pattern = r'\b' + re.escape(keyword) + r'\b'
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Remove excessive exclamation marks (keep one if present)
        if '!' in cleaned:
            cleaned = re.sub(r'!+', '!', cleaned)

        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return priority, cleaned


# Global instance
_priority_detector: Optional[PriorityDetector] = None


def get_priority_detector() -> PriorityDetector:
    """Get global priority detector"""
    global _priority_detector
    if _priority_detector is None:
        _priority_detector = PriorityDetector()
    return _priority_detector
