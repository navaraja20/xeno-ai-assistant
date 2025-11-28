"""
Task Parser
Parse natural language into structured task data
"""

import re
from datetime import datetime
from typing import Any, Dict, Optional

from src.core.logger import setup_logger
from src.nlp.date_parser import get_date_parser
from src.nlp.entity_extractor import get_entity_extractor
from src.nlp.priority_detector import get_priority_detector


class TaskParser:
    """Parses natural language into structured task data"""

    def __init__(self):
        self.logger = setup_logger("nlp.task_parser")

        # Get NLP components
        self.date_parser = get_date_parser()
        self.priority_detector = get_priority_detector()
        self.entity_extractor = get_entity_extractor()

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse natural language text into task structure"""
        original_text = text
        task_data = {}

        # 1. Extract priority
        priority, text = self.priority_detector.extract_priority_from_text(text)
        task_data["priority"] = priority

        # 2. Extract date
        due_date, text = self.date_parser.extract_date_from_text(text)
        if due_date:
            task_data["due_date"] = due_date.strftime("%Y-%m-%d")

        # 3. Extract entities
        entities = self.entity_extractor.extract_entities(text)

        # 4. Extract assignee
        assignee = self.entity_extractor.extract_assignee(text)
        if assignee:
            task_data["assignee"] = assignee

        # 5. Extract category
        category = self.entity_extractor.extract_category(text)
        task_data["category"] = category

        # 6. Extract tags
        tags = self.entity_extractor.extract_tags(text)
        if tags:
            task_data["tags"] = tags

        # 7. Extract URLs
        if entities.get("urls"):
            task_data["urls"] = entities["urls"]

        # 8. Extract emails
        if entities.get("emails"):
            task_data["emails"] = entities["emails"]

        # 9. Extract actions
        if entities.get("actions"):
            task_data["actions"] = entities["actions"]

        # 10. Clean text for title/description
        cleaned_text = self.entity_extractor.clean_text(text, entities)

        # 11. Extract title and description
        title, description = self._split_title_description(cleaned_text)
        task_data["title"] = title
        if description:
            task_data["description"] = description

        # 12. Set default status
        task_data["status"] = "pending"

        # 13. Store original text
        task_data["original_text"] = original_text

        # 14. Add metadata
        task_data["created_at"] = datetime.now().isoformat()
        task_data["parsed_by"] = "nlp"

        return task_data

    def _split_title_description(self, text: str) -> tuple:
        """Split text into title and description"""
        # If text is short, use it as title
        if len(text) <= 100:
            return text.strip(), None

        # Look for sentence breaks
        sentences = re.split(r"[.!?]\s+", text)

        if len(sentences) == 1:
            # Single long sentence - use first 100 chars as title
            title = text[:100].strip()
            description = text.strip()
        else:
            # Use first sentence as title, rest as description
            title = sentences[0].strip()
            description = " ".join(sentences[1:]).strip()

        return title, description if description else None

    def parse_bulk(self, text: str) -> list:
        """Parse multiple tasks from text"""
        tasks = []

        # Split by newlines
        lines = text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove bullet points
            line = re.sub(r"^[-*•]\s*", "", line)

            # Parse as task
            if line:
                task = self.parse(line)
                tasks.append(task)

        return tasks

    def suggest_improvements(self, text: str) -> Dict[str, Any]:
        """Suggest improvements to task text"""
        suggestions = {
            "has_priority": False,
            "has_due_date": False,
            "has_category": False,
            "has_assignee": False,
            "improvements": [],
        }

        # Check if has priority
        priority = self.priority_detector.detect_priority(text)
        if priority != "medium":  # medium is default
            suggestions["has_priority"] = True
        else:
            suggestions["improvements"].append(
                'Consider adding priority (e.g., "high priority", "urgent", "low priority")'
            )

        # Check if has due date
        due_date = self.date_parser.parse_date(text)
        if due_date:
            suggestions["has_due_date"] = True
        else:
            suggestions["improvements"].append(
                'Consider adding a due date (e.g., "tomorrow", "next week", "Jan 15")'
            )

        # Check if has category indicators
        category = self.entity_extractor.extract_category(text)
        if category != "General":
            suggestions["has_category"] = True
        else:
            suggestions["improvements"].append(
                'Consider adding category keywords (e.g., "meeting", "code", "review")'
            )

        # Check if has assignee
        assignee = self.entity_extractor.extract_assignee(text)
        if assignee:
            suggestions["has_assignee"] = True
        else:
            suggestions["improvements"].append(
                'Consider adding assignee (e.g., "@john", "for Sarah")'
            )

        # Check length
        if len(text) < 10:
            suggestions["improvements"].append(
                "Task description is very short - consider adding more details"
            )

        return suggestions

    def extract_subtasks(self, text: str) -> list:
        """Extract potential subtasks from text"""
        subtasks = []

        # Look for numbered lists
        numbered = re.findall(r"^\s*(\d+)[.)]\s*(.+)$", text, re.MULTILINE)
        for num, task_text in numbered:
            subtasks.append(
                {
                    "order": int(num),
                    "text": task_text.strip(),
                }
            )

        # Look for lettered lists
        lettered = re.findall(r"^\s*([a-z])[.)]\s*(.+)$", text, re.MULTILINE)
        for letter, task_text in lettered:
            subtasks.append(
                {
                    "order": ord(letter) - ord("a") + 1,
                    "text": task_text.strip(),
                }
            )

        # Look for bullet points
        bullets = re.findall(r"^\s*[-*•]\s*(.+)$", text, re.MULTILINE)
        for i, task_text in enumerate(bullets, 1):
            subtasks.append(
                {
                    "order": i,
                    "text": task_text.strip(),
                }
            )

        return subtasks


# Global instance
_task_parser: Optional[TaskParser] = None


def get_task_parser() -> TaskParser:
    """Get global task parser"""
    global _task_parser
    if _task_parser is None:
        _task_parser = TaskParser()
    return _task_parser
