"""
Date Parser
Extract and parse dates from natural language text
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

from src.core.logger import setup_logger


class DateParser:
    """Extracts and parses dates from natural language"""

    def __init__(self):
        self.logger = setup_logger("nlp.date_parser")

        # Compile regex patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for date extraction"""
        # Relative dates
        self.relative_patterns = [
            (r"\btoday\b", lambda: datetime.now()),
            (r"\btomorrow\b", lambda: datetime.now() + timedelta(days=1)),
            (r"\byesterday\b", lambda: datetime.now() - timedelta(days=1)),
            (r"\bnext week\b", lambda: datetime.now() + timedelta(weeks=1)),
            (r"\bthis week\b", lambda: datetime.now()),
            (r"\bnext month\b", lambda: datetime.now() + timedelta(days=30)),
            (r"\bthis month\b", lambda: datetime.now()),
        ]

        # Day-specific patterns
        self.day_patterns = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
            "mon": 0,
            "tue": 1,
            "wed": 2,
            "thu": 3,
            "fri": 4,
            "sat": 5,
            "sun": 6,
        }

        # Month names
        self.month_names = {
            "january": 1,
            "jan": 1,
            "february": 2,
            "feb": 2,
            "march": 3,
            "mar": 3,
            "april": 4,
            "apr": 4,
            "may": 5,
            "june": 6,
            "jun": 6,
            "july": 7,
            "jul": 7,
            "august": 8,
            "aug": 8,
            "september": 9,
            "sep": 9,
            "sept": 9,
            "october": 10,
            "oct": 10,
            "november": 11,
            "nov": 11,
            "december": 12,
            "dec": 12,
        }

    def parse_date(self, text: str) -> Optional[datetime]:
        """Parse date from text"""
        text_lower = text.lower()

        # 1. Try relative dates
        for pattern, date_func in self.relative_patterns:
            if re.search(pattern, text_lower):
                return date_func()

        # 2. Try "in X days/weeks/months"
        in_pattern = r"\bin (\d+) (day|week|month)s?\b"
        match = re.search(in_pattern, text_lower)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)

            if unit == "day":
                return datetime.now() + timedelta(days=amount)
            elif unit == "week":
                return datetime.now() + timedelta(weeks=amount)
            elif unit == "month":
                return datetime.now() + timedelta(days=amount * 30)

        # 3. Try "next/this <day>"
        for day_name, day_num in self.day_patterns.items():
            # Next <day>
            pattern = rf"\bnext {day_name}\b"
            if re.search(pattern, text_lower):
                return self._next_weekday(day_num)

            # This <day>
            pattern = rf"\bthis {day_name}\b"
            if re.search(pattern, text_lower):
                return self._this_weekday(day_num)

            # Just <day> (assume next occurrence)
            pattern = rf"\b{day_name}\b"
            if re.search(pattern, text_lower):
                return self._next_weekday(day_num)

        # 4. Try "on <day>"
        on_day_pattern = r"\bon (\w+)\b"
        match = re.search(on_day_pattern, text_lower)
        if match:
            day_name = match.group(1)
            if day_name in self.day_patterns:
                return self._next_weekday(self.day_patterns[day_name])

        # 5. Try specific date formats
        # MM/DD/YYYY or MM-DD-YYYY
        date_pattern = r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b"
        match = re.search(date_pattern, text)
        if match:
            try:
                month = int(match.group(1))
                day = int(match.group(2))
                year = int(match.group(3))
                if year < 100:
                    year += 2000
                return datetime(year, month, day)
            except ValueError:
                pass

        # 6. Try "Month Day" or "Day Month"
        # Month Day (e.g., "January 15")
        for month_name, month_num in self.month_names.items():
            pattern = rf"\b{month_name} (\d{{1,2}})\b"
            match = re.search(pattern, text_lower)
            if match:
                day = int(match.group(1))
                year = datetime.now().year
                try:
                    date = datetime(year, month_num, day)
                    # If date is in the past, assume next year
                    if date < datetime.now():
                        date = datetime(year + 1, month_num, day)
                    return date
                except ValueError:
                    pass

            # Day Month (e.g., "15 January")
            pattern = rf"\b(\d{{1,2}}) {month_name}\b"
            match = re.search(pattern, text_lower)
            if match:
                day = int(match.group(1))
                year = datetime.now().year
                try:
                    date = datetime(year, month_num, day)
                    if date < datetime.now():
                        date = datetime(year + 1, month_num, day)
                    return date
                except ValueError:
                    pass

        # 7. Try "end of week/month"
        if re.search(r"\bend of (the )?week\b", text_lower):
            return self._end_of_week()

        if re.search(r"\bend of (the )?month\b", text_lower):
            return self._end_of_month()

        return None

    def extract_date_from_text(self, text: str) -> Tuple[Optional[datetime], str]:
        """Extract date and return cleaned text"""
        date = self.parse_date(text)

        if date:
            # Remove date-related phrases from text
            cleaned = text

            # Remove common date patterns
            patterns = [
                r"\b(today|tomorrow|yesterday)\b",
                r"\b(next|this) (week|month|year)\b",
                r"\bin \d+ (day|week|month)s?\b",
                r"\b(next|this) \w+(day)?\b",
                r"\bon \w+\b",
                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
                r"\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec) \d{1,2}\b",
                r"\b\d{1,2} (january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b",
                r"\bend of (the )?(week|month)\b",
            ]

            for pattern in patterns:
                cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

            # Clean up extra whitespace
            cleaned = re.sub(r"\s+", " ", cleaned).strip()

            return date, cleaned

        return None, text

    def _next_weekday(self, target_day: int) -> datetime:
        """Get next occurrence of weekday"""
        today = datetime.now()
        current_day = today.weekday()

        days_ahead = target_day - current_day
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7

        return today + timedelta(days=days_ahead)

    def _this_weekday(self, target_day: int) -> datetime:
        """Get this week's occurrence of weekday"""
        today = datetime.now()
        current_day = today.weekday()

        days_ahead = target_day - current_day
        if days_ahead < 0:  # Already passed, use next week
            days_ahead += 7

        return today + timedelta(days=days_ahead)

    def _end_of_week(self) -> datetime:
        """Get end of current week (Sunday)"""
        today = datetime.now()
        days_until_sunday = 6 - today.weekday()
        return today + timedelta(days=days_until_sunday)

    def _end_of_month(self) -> datetime:
        """Get end of current month"""
        today = datetime.now()
        next_month = today.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)


# Global instance
_date_parser: Optional[DateParser] = None


def get_date_parser() -> DateParser:
    """Get global date parser"""
    global _date_parser
    if _date_parser is None:
        _date_parser = DateParser()
    return _date_parser
