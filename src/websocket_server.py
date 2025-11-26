"""
XENO Browser Extension - WebSocket Server
Enables real-time sync between desktop app and browser extension
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Set, Dict, Any
import websockets
from websockets.server import WebSocketServerProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XENOBrowserServer:
    """WebSocket server for browser extension communication"""
    
    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.desktop_client: WebSocketServerProtocol = None
        self.message_handlers: Dict[str, callable] = {}
        
        # Register default message handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register message type handlers"""
        self.message_handlers = {
            'handshake': self.handle_handshake,
            'send_email': self.handle_send_email,
            'create_calendar_event': self.handle_create_calendar,
            'create_task': self.handle_create_task,
            'voice_command': self.handle_voice_command,
            'save_content': self.handle_save_content,
            'sync_activity': self.handle_sync_activity,
            'open_dashboard': self.handle_open_dashboard,
            'predict_email_priority': self.handle_predict_priority,
            'ai_rewrite_email': self.handle_ai_rewrite,
            'analyze_repository': self.handle_analyze_repo
        }
    
    async def start(self):
        """Start the WebSocket server"""
        try:
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info(f"XENO Browser Server started on ws://{self.host}:{self.port}")
                await asyncio.Future()  # Run forever
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new client connection"""
        self.clients.add(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"New client connected: {client_info}")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_info}")
        except Exception as e:
            logger.error(f"Error handling client {client_info}: {e}")
        finally:
            self.clients.remove(websocket)
            if websocket == self.desktop_client:
                self.desktop_client = None
    
    async def process_message(self, websocket: WebSocketServerProtocol, message: str):
        """Process incoming message from client"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if not message_type:
                logger.warning("Received message without type")
                return
            
            logger.info(f"Received message: {message_type}")
            
            # Find and execute handler
            handler = self.message_handlers.get(message_type)
            if handler:
                await handler(websocket, data)
            else:
                logger.warning(f"No handler for message type: {message_type}")
                await self.send_error(websocket, f"Unknown message type: {message_type}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            await self.send_error(websocket, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error(websocket, str(e))
    
    async def handle_handshake(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle initial handshake from client"""
        source = data.get('source')
        version = data.get('version')
        
        logger.info(f"Handshake from {source} v{version}")
        
        # Identify desktop client
        if source == 'desktop-app':
            self.desktop_client = websocket
            logger.info("Desktop client identified")
        
        # Send acknowledgment
        await self.send_message(websocket, {
            'type': 'handshake_ack',
            'server_version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        })
    
    async def handle_send_email(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle email send request from browser"""
        email_data = data.get('data', {})
        
        # Forward to desktop app (which has email integration)
        if self.desktop_client:
            await self.send_message(self.desktop_client, {
                'type': 'send_email',
                'data': email_data
            })
            
            # Send confirmation back to browser
            await self.send_message(websocket, {
                'type': 'email_sent',
                'status': 'success'
            })
        else:
            await self.send_error(websocket, "Desktop app not connected")
    
    async def handle_create_calendar(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle calendar event creation from browser"""
        event_data = data.get('data', {})
        
        # Forward to desktop app
        if self.desktop_client:
            await self.send_message(self.desktop_client, {
                'type': 'create_calendar_event',
                'data': event_data
            })
            
            await self.send_message(websocket, {
                'type': 'calendar_created',
                'status': 'success'
            })
        else:
            await self.send_error(websocket, "Desktop app not connected")
    
    async def handle_create_task(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle task creation from browser"""
        task_data = data.get('data', {})
        
        # Forward to desktop app
        if self.desktop_client:
            await self.send_message(self.desktop_client, {
                'type': 'create_task',
                'data': task_data
            })
            
            await self.send_message(websocket, {
                'type': 'task_created',
                'status': 'success'
            })
        else:
            await self.send_error(websocket, "Desktop app not connected")
    
    async def handle_voice_command(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle voice command from browser"""
        voice_data = data.get('data', {})
        
        # Forward to desktop app for processing
        if self.desktop_client:
            await self.send_message(self.desktop_client, {
                'type': 'voice_command',
                'data': voice_data
            })
        else:
            await self.send_error(websocket, "Desktop app not connected")
    
    async def handle_save_content(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle content save request from browser"""
        content_data = data.get('data', {})
        
        # Forward to desktop app
        if self.desktop_client:
            await self.send_message(self.desktop_client, {
                'type': 'save_content',
                'data': content_data
            })
        else:
            await self.send_error(websocket, "Desktop app not connected")
    
    async def handle_sync_activity(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle activity sync from browser"""
        activities = data.get('activities', [])
        
        # Forward to desktop app
        if self.desktop_client:
            await self.send_message(self.desktop_client, {
                'type': 'sync_activity',
                'activities': activities
            })
    
    async def handle_open_dashboard(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle open dashboard request from browser"""
        # Forward to desktop app to bring window to front
        if self.desktop_client:
            await self.send_message(self.desktop_client, {
                'type': 'show_window'
            })
    
    async def handle_predict_priority(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle email priority prediction request"""
        email_data = data.get('data', {})
        
        # Forward to desktop app (which has ML models)
        if self.desktop_client:
            # Request prediction
            await self.send_message(self.desktop_client, {
                'type': 'predict_email_priority',
                'data': email_data,
                'reply_to': id(websocket)  # Include websocket ID for routing response
            })
        else:
            # Return default priority if desktop not connected
            await self.send_message(websocket, {
                'type': 'priority_prediction',
                'priority': 'medium'
            })
    
    async def handle_ai_rewrite(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle AI email rewrite request"""
        rewrite_data = data.get('data', {})
        
        # Forward to desktop app (which has AI integration)
        if self.desktop_client:
            await self.send_message(self.desktop_client, {
                'type': 'ai_rewrite_email',
                'data': rewrite_data,
                'reply_to': id(websocket)
            })
        else:
            await self.send_error(websocket, "Desktop app not connected")
    
    async def handle_analyze_repo(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle repository analysis request"""
        repo_data = data.get('data', {})
        
        # Forward to desktop app for AI analysis
        if self.desktop_client:
            await self.send_message(self.desktop_client, {
                'type': 'analyze_repository',
                'data': repo_data
            })
    
    async def send_message(self, websocket: WebSocketServerProtocol, message: Dict[str, Any]):
        """Send message to specific client"""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def send_error(self, websocket: WebSocketServerProtocol, error: str):
        """Send error message to client"""
        await self.send_message(websocket, {
            'type': 'error',
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
    
    async def broadcast(self, message: Dict[str, Any], exclude: WebSocketServerProtocol = None):
        """Broadcast message to all clients except excluded one"""
        for client in self.clients:
            if client != exclude:
                await self.send_message(client, message)
    
    async def notify_activity_update(self):
        """Notify all clients of activity update"""
        await self.broadcast({
            'type': 'activity_update',
            'timestamp': datetime.now().isoformat()
        })


async def main():
    """Main entry point"""
    server = XENOBrowserServer(host='localhost', port=8765)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
