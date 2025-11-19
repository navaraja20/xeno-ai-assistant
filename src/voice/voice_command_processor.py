"""
Voice Command Processor with Natural Language Understanding
Handles complex voice commands with context awareness
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class CommandIntent(Enum):
    """Voice command intents"""
    # Email
    SEND_EMAIL = "send_email"
    CHECK_EMAIL = "check_email"
    READ_EMAIL = "read_email"
    
    # Calendar
    CREATE_EVENT = "create_event"
    CHECK_SCHEDULE = "check_schedule"
    RESCHEDULE_EVENT = "reschedule_event"
    
    # Tasks
    CREATE_TASK = "create_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    
    # Integration Hub
    RUN_WORKFLOW = "run_workflow"
    CREATE_WORKFLOW = "create_workflow"
    
    # General
    SEARCH = "search"
    QUESTION = "question"
    REMINDER = "set_reminder"
    TIMER = "set_timer"
    WEATHER = "check_weather"
    NEWS = "check_news"
    
    # Control
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    SETTINGS = "change_settings"
    
    # Unknown
    UNKNOWN = "unknown"


@dataclass
class VoiceCommand:
    """Parsed voice command"""
    intent: CommandIntent
    entities: Dict[str, Any]
    parameters: Dict[str, Any]
    confidence: float
    raw_text: str
    language: str = "en-US"


class NaturalLanguageProcessor:
    """Process natural language voice commands"""
    
    def __init__(self):
        self.intent_patterns = self._initialize_patterns()
        self.entity_extractors = self._initialize_extractors()
        
    def _initialize_patterns(self) -> Dict[CommandIntent, List[str]]:
        """Initialize regex patterns for intent recognition"""
        return {
            # Email patterns
            CommandIntent.SEND_EMAIL: [
                r"send (?:an? )?email to (.+)",
                r"email (.+) (?:saying|about|regarding) (.+)",
                r"compose (?:an? )?email to (.+)",
                r"write (?:an? )?email to (.+)"
            ],
            CommandIntent.CHECK_EMAIL: [
                r"check (?:my )?(?:email|inbox)",
                r"any new (?:emails|messages)",
                r"do i have (?:any )?(?:email|messages)",
                r"show (?:me )?(?:my )?(?:email|inbox)"
            ],
            CommandIntent.READ_EMAIL: [
                r"read (?:my )?(?:latest|newest|recent) email",
                r"read email from (.+)",
                r"what did (.+) say",
                r"open email from (.+)"
            ],
            
            # Calendar patterns
            CommandIntent.CREATE_EVENT: [
                r"schedule (?:a )?(?:meeting|event|appointment) (?:with |for )?(.+)",
                r"add (?:a )?(?:meeting|event) (?:on |at |for )?(.+)",
                r"create (?:a )?(?:meeting|event|appointment) (.+)",
                r"book (?:a )?(?:meeting|appointment) (?:with )?(.+)"
            ],
            CommandIntent.CHECK_SCHEDULE: [
                r"what's (?:on )?my schedule (?:for )?(.+)?",
                r"what do i have (?:on |for |today|tomorrow|this week)?",
                r"show (?:me )?my (?:calendar|schedule|agenda)",
                r"any (?:meetings|events) (?:today|tomorrow|this week)?"
            ],
            CommandIntent.RESCHEDULE_EVENT: [
                r"reschedule (.+) (?:to |for )?(.+)",
                r"move (.+) (?:meeting|event) (?:to )?(.+)",
                r"change (.+) (?:to )?(.+)"
            ],
            
            # Task patterns
            CommandIntent.CREATE_TASK: [
                r"(?:add|create) (?:a )?task (?:to )?(.+)",
                r"remind me to (.+)",
                r"i need to (.+)",
                r"(?:add|put) (.+) (?:to|on) my (?:todo|to-do) list"
            ],
            CommandIntent.LIST_TASKS: [
                r"what (?:are )?my tasks",
                r"show (?:me )?my (?:tasks|to-?do list)",
                r"what do i need to do",
                r"list my tasks"
            ],
            CommandIntent.COMPLETE_TASK: [
                r"(?:mark|complete|finish|done) (?:task )?(.+)",
                r"i (?:finished|completed|did) (.+)",
                r"cross off (.+)"
            ],
            
            # Workflow patterns
            CommandIntent.RUN_WORKFLOW: [
                r"run (?:the )?(.+) workflow",
                r"execute (?:the )?(.+) (?:workflow|automation)",
                r"trigger (.+) workflow",
                r"start (?:the )?(.+) (?:workflow|automation)"
            ],
            
            # General patterns
            CommandIntent.SEARCH: [
                r"search (?:for )?(.+)",
                r"look up (.+)",
                r"find (?:me )?(?:information (?:on|about) )?(.+)",
                r"google (.+)"
            ],
            CommandIntent.QUESTION: [
                r"what (?:is|are|was|were) (.+)",
                r"how (?:do|does|can|to) (.+)",
                r"when (?:is|was|will) (.+)",
                r"where (?:is|are|can) (.+)",
                r"who (?:is|are|was) (.+)",
                r"why (?:is|are|did) (.+)"
            ],
            CommandIntent.REMINDER: [
                r"remind me (?:to )?(.+) (?:at|in|on) (.+)",
                r"set (?:a )?reminder (?:to )?(.+) (?:at|for) (.+)",
                r"don't let me forget (?:to )?(.+)"
            ],
            CommandIntent.TIMER: [
                r"set (?:a )?timer (?:for )?(.+)",
                r"timer (?:for )?(.+)",
                r"countdown (?:for )?(.+)"
            ],
            CommandIntent.WEATHER: [
                r"what's the weather (?:like )?(?:in |for )?(.+)?",
                r"how's the weather (?:in |for )?(.+)?",
                r"will it rain (?:today|tomorrow)?",
                r"temperature (?:in |for )?(.+)?"
            ],
            CommandIntent.NEWS: [
                r"what's (?:in )?the news",
                r"tell me the news",
                r"news (?:about )?(.+)?",
                r"headlines"
            ],
            
            # Control patterns
            CommandIntent.OPEN_APP: [
                r"open (.+)",
                r"launch (.+)",
                r"start (.+) app"
            ],
            CommandIntent.CLOSE_APP: [
                r"close (.+)",
                r"quit (.+)",
                r"exit (.+)"
            ],
            CommandIntent.SETTINGS: [
                r"change (.+) (?:to )?(.+)",
                r"set (.+) (?:to )?(.+)",
                r"adjust (.+) (?:to )?(.+)"
            ]
        }
    
    def _initialize_extractors(self) -> Dict[str, callable]:
        """Initialize entity extraction functions"""
        return {
            'email': self._extract_email,
            'date': self._extract_date,
            'time': self._extract_time,
            'duration': self._extract_duration,
            'person': self._extract_person,
            'location': self._extract_location,
            'number': self._extract_number
        }
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def _extract_date(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract date from natural language"""
        text_lower = text.lower()
        
        # Relative dates
        if 'today' in text_lower:
            return {'date': datetime.now(), 'original': 'today'}
        elif 'tomorrow' in text_lower:
            return {'date': datetime.now() + timedelta(days=1), 'original': 'tomorrow'}
        elif 'yesterday' in text_lower:
            return {'date': datetime.now() - timedelta(days=1), 'original': 'yesterday'}
        elif 'next week' in text_lower:
            return {'date': datetime.now() + timedelta(weeks=1), 'original': 'next week'}
        elif 'next month' in text_lower:
            return {'date': datetime.now() + timedelta(days=30), 'original': 'next month'}
        
        # Day of week
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(days):
            if day in text_lower:
                today = datetime.now()
                days_ahead = i - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return {'date': today + timedelta(days=days_ahead), 'original': day}
        
        # Specific date patterns (MM/DD/YYYY, DD-MM-YYYY, etc.)
        date_patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', '%d-%m-%Y'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d')
        ]
        
        for pattern, fmt in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date = datetime.strptime(match.group(0), fmt)
                    return {'date': date, 'original': match.group(0)}
                except:
                    pass
        
        return None
    
    def _extract_time(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract time from natural language"""
        text_lower = text.lower()
        
        # Named times
        time_map = {
            'morning': '9:00',
            'noon': '12:00',
            'afternoon': '14:00',
            'evening': '18:00',
            'night': '20:00',
            'midnight': '00:00'
        }
        
        for key, value in time_map.items():
            if key in text_lower:
                return {'time': value, 'original': key}
        
        # Specific time patterns (HH:MM, H:MM AM/PM)
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'(\d{1,2})\s*(am|pm)',
            r'at (\d{1,2})'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return {'time': match.group(0), 'original': match.group(0)}
        
        return None
    
    def _extract_duration(self, text: str) -> Optional[Dict[str, int]]:
        """Extract duration/timer length"""
        # Extract numbers with time units
        patterns = [
            (r'(\d+)\s*hours?', 'hours'),
            (r'(\d+)\s*minutes?', 'minutes'),
            (r'(\d+)\s*seconds?', 'seconds'),
            (r'(\d+)\s*days?', 'days')
        ]
        
        duration = {}
        for pattern, unit in patterns:
            match = re.search(pattern, text.lower())
            if match:
                duration[unit] = int(match.group(1))
        
        return duration if duration else None
    
    def _extract_person(self, text: str) -> Optional[str]:
        """Extract person name"""
        # Look for capitalized words (simple heuristic)
        name_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b'
        match = re.search(name_pattern, text)
        return match.group(1) if match else None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location"""
        # Look for "in X" or "at X" patterns
        location_patterns = [
            r'in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'at ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number"""
        match = re.search(r'\b(\d+)\b', text)
        return int(match.group(1)) if match else None
    
    def parse_command(self, text: str, context: Optional[Dict[str, Any]] = None) -> VoiceCommand:
        """Parse voice command into structured format"""
        text = text.strip()
        
        # Detect intent
        intent = self._detect_intent(text)
        
        # Extract entities
        entities = {}
        for entity_type, extractor in self.entity_extractors.items():
            extracted = extractor(text)
            if extracted is not None:
                entities[entity_type] = extracted
        
        # Extract parameters based on intent
        parameters = self._extract_parameters(text, intent, context)
        
        # Calculate confidence
        confidence = self._calculate_confidence(text, intent, entities, parameters)
        
        return VoiceCommand(
            intent=intent,
            entities=entities,
            parameters=parameters,
            confidence=confidence,
            raw_text=text
        )
    
    def _detect_intent(self, text: str) -> CommandIntent:
        """Detect command intent from text"""
        text_lower = text.lower()
        
        best_intent = CommandIntent.UNKNOWN
        best_score = 0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # Calculate match quality
                    score = len(re.search(pattern, text_lower).group(0)) / len(text)
                    if score > best_score:
                        best_score = score
                        best_intent = intent
        
        return best_intent
    
    def _extract_parameters(
        self,
        text: str,
        intent: CommandIntent,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract intent-specific parameters"""
        parameters = {}
        context = context or {}
        
        if intent == CommandIntent.SEND_EMAIL:
            # Extract recipient and message
            patterns = [
                r"email (.+?) (?:saying|about|that) (.+)",
                r"send email to (.+?) (?:saying|about) (.+)",
                r"email (.+)"
            ]
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    parameters['recipient'] = match.group(1).strip()
                    if len(match.groups()) > 1:
                        parameters['message'] = match.group(2).strip()
                    break
        
        elif intent == CommandIntent.CREATE_EVENT:
            # Extract event details
            match = re.search(r"(?:meeting|event|appointment) (?:with |about )?(.+?)(?:\s+(?:at|on|for)\s+(.+))?$", text.lower())
            if match:
                parameters['title'] = match.group(1).strip()
                if match.group(2):
                    parameters['when'] = match.group(2).strip()
        
        elif intent == CommandIntent.CREATE_TASK:
            # Extract task description
            patterns = [
                r"task (?:to )?(.+)",
                r"remind me to (.+)",
                r"i need to (.+)",
                r"(?:add|put) (.+) (?:to|on)"
            ]
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    parameters['description'] = match.group(1).strip()
                    break
        
        elif intent == CommandIntent.RUN_WORKFLOW:
            # Extract workflow name
            match = re.search(r"(?:run|execute|trigger|start) (?:the )?(.+?) workflow", text.lower())
            if match:
                parameters['workflow_name'] = match.group(1).strip()
        
        elif intent == CommandIntent.SEARCH:
            # Extract search query
            patterns = [
                r"search (?:for )?(.+)",
                r"look up (.+)",
                r"find (?:me )?(?:information (?:on|about) )?(.+)",
                r"google (.+)"
            ]
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    parameters['query'] = match.group(1).strip()
                    break
        
        elif intent == CommandIntent.REMINDER:
            # Extract reminder details
            match = re.search(r"remind me (?:to )?(.+?)(?:\s+(?:at|in|on)\s+(.+))?$", text.lower())
            if match:
                parameters['message'] = match.group(1).strip()
                if match.group(2):
                    parameters['when'] = match.group(2).strip()
        
        elif intent == CommandIntent.TIMER:
            # Extract duration
            match = re.search(r"timer (?:for )?(.+)", text.lower())
            if match:
                parameters['duration'] = match.group(1).strip()
        
        elif intent == CommandIntent.OPEN_APP:
            # Extract app name
            match = re.search(r"(?:open|launch|start) (.+?)(?:\s+app)?$", text.lower())
            if match:
                parameters['app_name'] = match.group(1).strip()
        
        return parameters
    
    def _calculate_confidence(
        self,
        text: str,
        intent: CommandIntent,
        entities: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for parsed command"""
        if intent == CommandIntent.UNKNOWN:
            return 0.0
        
        # Base confidence from intent match
        confidence = 0.6
        
        # Boost confidence if entities found
        if entities:
            confidence += 0.2 * min(len(entities) / 3, 1.0)
        
        # Boost confidence if parameters extracted
        if parameters:
            confidence += 0.2 * min(len(parameters) / 2, 1.0)
        
        return min(confidence, 1.0)


class VoiceCommandExecutor:
    """Execute parsed voice commands"""
    
    def __init__(self, xeno_app):
        """
        Initialize with reference to main XENO application
        
        Args:
            xeno_app: Main XENO application instance
        """
        self.app = xeno_app
        self.nlp = NaturalLanguageProcessor()
    
    async def execute(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute voice command"""
        result = {
            'success': False,
            'message': '',
            'data': None
        }
        
        try:
            if command.intent == CommandIntent.SEND_EMAIL:
                result = await self._execute_send_email(command)
            
            elif command.intent == CommandIntent.CHECK_EMAIL:
                result = await self._execute_check_email(command)
            
            elif command.intent == CommandIntent.CREATE_EVENT:
                result = await self._execute_create_event(command)
            
            elif command.intent == CommandIntent.CHECK_SCHEDULE:
                result = await self._execute_check_schedule(command)
            
            elif command.intent == CommandIntent.CREATE_TASK:
                result = await self._execute_create_task(command)
            
            elif command.intent == CommandIntent.LIST_TASKS:
                result = await self._execute_list_tasks(command)
            
            elif command.intent == CommandIntent.COMPLETE_TASK:
                result = await self._execute_complete_task(command)
            
            elif command.intent == CommandIntent.RUN_WORKFLOW:
                result = await self._execute_run_workflow(command)
            
            elif command.intent == CommandIntent.SEARCH:
                result = await self._execute_search(command)
            
            elif command.intent == CommandIntent.REMINDER:
                result = await self._execute_set_reminder(command)
            
            elif command.intent == CommandIntent.TIMER:
                result = await self._execute_set_timer(command)
            
            elif command.intent == CommandIntent.WEATHER:
                result = await self._execute_check_weather(command)
            
            elif command.intent == CommandIntent.OPEN_APP:
                result = await self._execute_open_app(command)
            
            else:
                result['message'] = f"Intent {command.intent.value} not implemented yet"
        
        except Exception as e:
            result['success'] = False
            result['message'] = f"Error executing command: {str(e)}"
        
        return result
    
    async def _execute_send_email(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute send email command"""
        recipient = command.parameters.get('recipient')
        message = command.parameters.get('message', '')
        
        if not recipient:
            return {'success': False, 'message': 'No recipient specified'}
        
        # Call email manager
        # await self.app.email_manager.send_email(recipient, message)
        
        return {
            'success': True,
            'message': f"Email sent to {recipient}",
            'data': {'recipient': recipient, 'message': message}
        }
    
    async def _execute_check_email(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute check email command"""
        # emails = await self.app.email_manager.get_unread_emails()
        
        return {
            'success': True,
            'message': f"You have 5 new emails",  # Placeholder
            'data': {'count': 5}
        }
    
    async def _execute_create_event(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute create event command"""
        title = command.parameters.get('title', 'New Event')
        when = command.parameters.get('when', 'today')
        
        return {
            'success': True,
            'message': f"Created event: {title} for {when}",
            'data': {'title': title, 'when': when}
        }
    
    async def _execute_check_schedule(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute check schedule command"""
        return {
            'success': True,
            'message': "You have 3 meetings today",  # Placeholder
            'data': {'meeting_count': 3}
        }
    
    async def _execute_create_task(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute create task command"""
        description = command.parameters.get('description', 'New task')
        
        return {
            'success': True,
            'message': f"Task created: {description}",
            'data': {'description': description}
        }
    
    async def _execute_list_tasks(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute list tasks command"""
        return {
            'success': True,
            'message': "You have 7 tasks pending",  # Placeholder
            'data': {'task_count': 7}
        }
    
    async def _execute_complete_task(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute complete task command"""
        task_name = command.parameters.get('task_name', '')
        
        return {
            'success': True,
            'message': f"Task completed: {task_name}",
            'data': {'task': task_name}
        }
    
    async def _execute_run_workflow(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute run workflow command"""
        workflow_name = command.parameters.get('workflow_name', '')
        
        # Call workflow engine
        # await self.app.workflow_engine.execute_workflow(workflow_name)
        
        return {
            'success': True,
            'message': f"Running workflow: {workflow_name}",
            'data': {'workflow': workflow_name}
        }
    
    async def _execute_search(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute search command"""
        query = command.parameters.get('query', '')
        
        return {
            'success': True,
            'message': f"Searching for: {query}",
            'data': {'query': query}
        }
    
    async def _execute_set_reminder(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute set reminder command"""
        message = command.parameters.get('message', '')
        when = command.parameters.get('when', 'later')
        
        return {
            'success': True,
            'message': f"Reminder set: {message} at {when}",
            'data': {'message': message, 'when': when}
        }
    
    async def _execute_set_timer(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute set timer command"""
        duration = command.parameters.get('duration', '1 minute')
        
        return {
            'success': True,
            'message': f"Timer set for {duration}",
            'data': {'duration': duration}
        }
    
    async def _execute_check_weather(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute check weather command"""
        location = command.entities.get('location', 'your location')
        
        return {
            'success': True,
            'message': f"The weather in {location} is sunny, 72°F",  # Placeholder
            'data': {'location': location, 'temp': 72, 'condition': 'sunny'}
        }
    
    async def _execute_open_app(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute open app command"""
        app_name = command.parameters.get('app_name', '')
        
        return {
            'success': True,
            'message': f"Opening {app_name}",
            'data': {'app': app_name}
        }
