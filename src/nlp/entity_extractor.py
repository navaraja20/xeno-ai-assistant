"""
Entity Extractor
Extract entities (people, projects, locations, etc.) from text
"""

import re
from typing import Dict, List, Set

from src.core.logger import setup_logger


class EntityExtractor:
    """Extracts named entities from text"""

    def __init__(self):
        self.logger = setup_logger("nlp.entities")

        # Common entity patterns
        self.patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, List]:
        """Initialize entity extraction patterns"""
        return {
            # People (mentioned with @)
            'mentions': [
                r'@(\w+)',  # @username
                r'\bwith (@?\w+)\b',  # with someone
                r'\b(ask|email|call|contact|notify) (@?\w+)\b',  # action + person
            ],
            # Projects/tags (mentioned with #)
            'projects': [
                r'#(\w+)',  # #project
                r'\bfor (#?\w+) project\b',  # for X project
            ],
            # Locations
            'locations': [
                r'\bat (\w+(?:\s+\w+)*)\b',  # at location
                r'\bin (\w+(?:\s+\w+)*)\b',  # in location
            ],
            # URLs
            'urls': [
                r'https?://[^\s]+',
                r'www\.[^\s]+',
            ],
            # Email addresses
            'emails': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            ],
            # Phone numbers
            'phones': [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
                r'\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            ],
            # File paths
            'files': [
                r'\b[\w/\\]+\.[a-zA-Z]{2,4}\b',  # file.ext
            ],
            # Actions/verbs
            'actions': [
                r'\b(create|build|design|implement|fix|update|review|test|deploy|write|send|call|email|meet|discuss|plan)\b',
            ],
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract all entities from text"""
        entities = {
            'mentions': [],
            'projects': [],
            'locations': [],
            'urls': [],
            'emails': [],
            'phones': [],
            'files': [],
            'actions': [],
            'capitalized': [],  # Potential proper nouns
        }

        # Extract based on patterns
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    entities[entity_type].extend(matches)

        # Extract capitalized words (potential proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Filter out common words
        common_words = {
            'I', 'The', 'This', 'That', 'These', 'Those',
            'What', 'When', 'Where', 'Why', 'How', 'Who',
            'Can', 'Could', 'Should', 'Would', 'Will', 'Must',
        }
        
        entities['capitalized'] = [
            word for word in capitalized 
            if word not in common_words and len(word) > 2
        ]

        # Deduplicate
        for entity_type in entities:
            entities[entity_type] = list(set(entities[entity_type]))

        return entities

    def extract_assignee(self, text: str) -> str:
        """Extract assignee from text"""
        # Look for @mentions
        mention_pattern = r'@(\w+)'
        matches = re.findall(mention_pattern, text)
        if matches:
            return matches[0]

        # Look for "assign to"
        assign_pattern = r'\bassign(?:ed)? to (@?\w+)\b'
        match = re.search(assign_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).lstrip('@')

        # Look for "for <person>"
        for_pattern = r'\bfor (@?\w+)\b'
        match = re.search(for_pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).lstrip('@')
            # Make sure it's a person (capitalized)
            if name[0].isupper():
                return name

        return None

    def extract_category(self, text: str) -> str:
        """Extract category from text"""
        text_lower = text.lower()

        # Category keywords
        categories = {
            'Development': ['code', 'develop', 'implement', 'build', 'program', 'bug', 'feature'],
            'Meeting': ['meeting', 'call', 'discussion', 'presentation', 'demo'],
            'Documentation': ['documentation', 'docs', 'readme', 'guide', 'manual', 'write'],
            'Review': ['review', 'feedback', 'check', 'approve', 'inspect'],
            'Testing': ['test', 'qa', 'quality', 'verify'],
            'Planning': ['plan', 'design', 'brainstorm', 'strategy', 'roadmap'],
            'Research': ['research', 'investigate', 'explore', 'study', 'learn'],
            'Communication': ['email', 'message', 'notify', 'inform', 'contact'],
        }

        # Count matches for each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score

        if category_scores:
            return max(category_scores, key=category_scores.get)

        return 'General'

    def extract_tags(self, text: str) -> List[str]:
        """Extract potential tags from text"""
        tags = set()

        # Extract #hashtags
        hashtags = re.findall(r'#(\w+)', text)
        tags.update(hashtags)

        # Extract key verbs (actions)
        actions = re.findall(
            r'\b(fix|bug|feature|update|upgrade|optimize|refactor|deploy|release)\b',
            text,
            re.IGNORECASE
        )
        tags.update(a.lower() for a in actions)

        # Extract technology/domain terms
        tech_terms = re.findall(
            r'\b(api|database|frontend|backend|ui|ux|security|performance|testing|qa)\b',
            text,
            re.IGNORECASE
        )
        tags.update(t.lower() for t in tech_terms)

        return list(tags)

    def clean_text(self, text: str, entities: Dict[str, List[str]] = None) -> str:
        """Remove extracted entities from text"""
        cleaned = text

        if entities is None:
            entities = self.extract_entities(text)

        # Remove mentions
        for mention in entities.get('mentions', []):
            cleaned = re.sub(rf'@{re.escape(mention)}\b', '', cleaned, flags=re.IGNORECASE)

        # Remove hashtags
        for project in entities.get('projects', []):
            cleaned = re.sub(rf'#{re.escape(project)}\b', '', cleaned, flags=re.IGNORECASE)

        # Remove URLs
        for url in entities.get('urls', []):
            cleaned = cleaned.replace(url, '')

        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned


# Global instance
_entity_extractor: Optional[EntityExtractor] = None


def get_entity_extractor() -> EntityExtractor:
    """Get global entity extractor"""
    global _entity_extractor
    if _entity_extractor is None:
        _entity_extractor = EntityExtractor()
    return _entity_extractor
