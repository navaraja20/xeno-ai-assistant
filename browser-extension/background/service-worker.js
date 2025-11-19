// XENO Browser Extension - Service Worker (Background Script)

class XenoServiceWorker {
  constructor() {
    this.ws = null;
    this.connected = false;
    this.serverUrl = 'ws://localhost:8765';
    this.recentActivity = [];
    this.maxActivityItems = 20;
    
    this.init();
  }

  init() {
    console.log('XENO Service Worker initialized');
    
    // Load settings
    this.loadSettings();
    
    // Setup listeners
    this.setupListeners();
    
    // Connect to desktop app
    this.connectWebSocket();
    
    // Load saved activity
    this.loadActivity();
  }

  async loadSettings() {
    try {
      const result = await chrome.storage.sync.get(['serverUrl']);
      if (result.serverUrl) {
        this.serverUrl = result.serverUrl;
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  }

  setupListeners() {
    // Context menu items
    chrome.runtime.onInstalled.addListener(() => {
      this.createContextMenus();
    });

    // Command shortcuts
    chrome.commands.onCommand.addListener((command) => {
      this.handleCommand(command);
    });

    // Tab updates (for context awareness)
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete') {
        this.onTabUpdated(tabId, tab);
      }
    });

    // Messages from popup and content scripts
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep channel open for async response
    });

    // Alarms for periodic tasks
    chrome.alarms.create('sync-activity', { periodInMinutes: 5 });
    chrome.alarms.onAlarm.addListener((alarm) => {
      if (alarm.name === 'sync-activity') {
        this.syncActivity();
      }
    });
  }

  createContextMenus() {
    // Remove existing menus
    chrome.contextMenus.removeAll();

    // Quick Email
    chrome.contextMenus.create({
      id: 'quick-email',
      title: 'Send Quick Email',
      contexts: ['selection', 'page']
    });

    // Quick Calendar
    chrome.contextMenus.create({
      id: 'quick-calendar',
      title: 'Create Calendar Event',
      contexts: ['selection', 'page']
    });

    // Quick Task
    chrome.contextMenus.create({
      id: 'quick-task',
      title: 'Create Task',
      contexts: ['selection', 'page']
    });

    // Save to XENO
    chrome.contextMenus.create({
      id: 'save-to-xeno',
      title: 'Save to XENO',
      contexts: ['selection', 'page', 'link']
    });

    // Context menu click handler
    chrome.contextMenus.onClicked.addListener((info, tab) => {
      this.handleContextMenuClick(info, tab);
    });
  }

  handleCommand(command) {
    console.log('Command:', command);
    
    switch (command) {
      case 'quick-email':
        this.openPopupAction('email');
        break;
      case 'quick-calendar':
        this.openPopupAction('calendar');
        break;
      case 'open-xeno':
        this.openDashboard();
        break;
    }
  }

  async handleContextMenuClick(info, tab) {
    const selection = info.selectionText || '';
    
    switch (info.menuItemId) {
      case 'quick-email':
        // Open popup with pre-filled email
        await chrome.storage.local.set({
          pendingAction: {
            type: 'email',
            data: { body: selection }
          }
        });
        chrome.action.openPopup();
        break;
        
      case 'quick-calendar':
        // Open popup with pre-filled calendar
        await chrome.storage.local.set({
          pendingAction: {
            type: 'calendar',
            data: { title: selection }
          }
        });
        chrome.action.openPopup();
        break;
        
      case 'quick-task':
        // Open popup with pre-filled task
        await chrome.storage.local.set({
          pendingAction: {
            type: 'task',
            data: { title: selection }
          }
        });
        chrome.action.openPopup();
        break;
        
      case 'save-to-xeno':
        this.saveToXeno({
          url: info.linkUrl || info.pageUrl || tab.url,
          title: selection || tab.title,
          content: selection
        });
        break;
    }
  }

  openPopupAction(action) {
    chrome.action.openPopup();
    // Send message to popup when it opens
    setTimeout(() => {
      chrome.runtime.sendMessage({ type: 'trigger-action', action });
    }, 100);
  }

  async onTabUpdated(tabId, tab) {
    // Check if tab is on supported site
    if (!tab.url) return;

    const supportedSites = [
      'linkedin.com',
      'github.com',
      'mail.google.com',
      'calendar.google.com'
    ];

    const isSupportedSite = supportedSites.some(site => tab.url.includes(site));
    
    if (isSupportedSite) {
      // Update badge to show XENO is active on this page
      chrome.action.setBadgeText({ text: '✓', tabId });
      chrome.action.setBadgeBackgroundColor({ color: '#57F287', tabId });
    } else {
      chrome.action.setBadgeText({ text: '', tabId });
    }
  }

  handleMessage(message, sender, sendResponse) {
    console.log('Received message:', message.type);

    switch (message.type) {
      case 'send_email':
        this.sendEmail(message.data)
          .then(() => sendResponse({ success: true }))
          .catch(error => sendResponse({ success: false, error: error.message }));
        break;

      case 'create_calendar_event':
        this.createCalendarEvent(message.data)
          .then(() => sendResponse({ success: true }))
          .catch(error => sendResponse({ success: false, error: error.message }));
        break;

      case 'create_task':
        this.createTask(message.data)
          .then(() => sendResponse({ success: true }))
          .catch(error => sendResponse({ success: false, error: error.message }));
        break;

      case 'voice_command':
        this.processVoiceCommand(message.data)
          .then(() => sendResponse({ success: true }))
          .catch(error => sendResponse({ success: false, error: error.message }));
        break;

      case 'get_activity':
        sendResponse({ activity: this.recentActivity });
        break;

      case 'save_to_xeno':
        this.saveToXeno(message.data)
          .then(() => sendResponse({ success: true }))
          .catch(error => sendResponse({ success: false, error: error.message }));
        break;

      case 'open_dashboard':
        this.openDashboard();
        sendResponse({ success: true });
        break;

      default:
        sendResponse({ success: false, error: 'Unknown message type' });
    }
  }

  connectWebSocket() {
    try {
      this.ws = new WebSocket(this.serverUrl);

      this.ws.onopen = () => {
        console.log('Connected to XENO desktop');
        this.connected = true;
        
        // Send handshake
        this.sendMessage({
          type: 'handshake',
          source: 'browser-extension',
          version: chrome.runtime.getManifest().version
        });

        // Update icon to show connected state
        chrome.action.setIcon({
          path: {
            16: '../icons/icon16.png',
            32: '../icons/icon32.png',
            48: '../icons/icon48.png',
            128: '../icons/icon128.png'
          }
        });
      };

      this.ws.onclose = () => {
        console.log('Disconnected from XENO desktop');
        this.connected = false;
        
        // Update icon to show disconnected state
        // (Could use greyscale version)
        
        // Attempt to reconnect after 5 seconds
        setTimeout(() => this.connectWebSocket(), 5000);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleWebSocketMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      
      // Retry connection after 5 seconds
      setTimeout(() => this.connectWebSocket(), 5000);
    }
  }

  sendMessage(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      return true;
    } else {
      console.warn('WebSocket not connected, queuing message');
      // Could implement message queue here
      return false;
    }
  }

  handleWebSocketMessage(message) {
    console.log('WebSocket message:', message.type);

    switch (message.type) {
      case 'activity_sync':
        // Desktop app sent activity update
        if (message.activities) {
          this.recentActivity = message.activities;
          this.saveActivity();
        }
        break;

      case 'notification':
        // Show notification from desktop
        this.showNotification(message.title, message.body);
        break;

      case 'command':
        // Desktop app requesting action
        this.executeCommand(message.command, message.data);
        break;

      default:
        console.log('Unknown WebSocket message type:', message.type);
    }
  }

  async sendEmail(data) {
    // Add to activity
    this.addActivity({
      type: 'email',
      title: `Email to ${data.to}`,
      timestamp: Date.now()
    });

    // Send to desktop app via WebSocket
    if (this.sendMessage({
      type: 'send_email',
      data
    })) {
      this.showNotification('Email Sent', `Email to ${data.to} sent successfully`);
    } else {
      throw new Error('Failed to send email - not connected to desktop app');
    }
  }

  async createCalendarEvent(data) {
    // Add to activity
    this.addActivity({
      type: 'calendar',
      title: `Event: ${data.title}`,
      timestamp: Date.now()
    });

    // Send to desktop app via WebSocket
    if (this.sendMessage({
      type: 'create_calendar_event',
      data
    })) {
      this.showNotification('Event Created', `Calendar event "${data.title}" created`);
    } else {
      throw new Error('Failed to create event - not connected to desktop app');
    }
  }

  async createTask(data) {
    // Add to activity
    this.addActivity({
      type: 'task',
      title: `Task: ${data.title}`,
      timestamp: Date.now()
    });

    // Send to desktop app via WebSocket
    if (this.sendMessage({
      type: 'create_task',
      data
    })) {
      this.showNotification('Task Created', `Task "${data.title}" created`);
    } else {
      throw new Error('Failed to create task - not connected to desktop app');
    }
  }

  async processVoiceCommand(data) {
    // Send to desktop app for processing
    if (this.sendMessage({
      type: 'voice_command',
      data
    })) {
      this.addActivity({
        type: 'voice',
        title: `Voice: ${data.transcript}`,
        timestamp: Date.now()
      });
    } else {
      throw new Error('Failed to process voice command - not connected to desktop app');
    }
  }

  async saveToXeno(data) {
    // Add to activity
    this.addActivity({
      type: 'saved',
      title: `Saved: ${data.title}`,
      timestamp: Date.now()
    });

    // Send to desktop app
    if (this.sendMessage({
      type: 'save_content',
      data
    })) {
      this.showNotification('Saved to XENO', data.title);
    } else {
      throw new Error('Failed to save - not connected to desktop app');
    }
  }

  openDashboard() {
    // Send message to desktop app to bring window to front
    this.sendMessage({
      type: 'open_dashboard'
    });
  }

  executeCommand(command, data) {
    // Execute command from desktop app
    switch (command) {
      case 'open_tab':
        chrome.tabs.create({ url: data.url });
        break;
        
      case 'focus_tab':
        chrome.tabs.query({ url: data.url }, (tabs) => {
          if (tabs.length > 0) {
            chrome.tabs.update(tabs[0].id, { active: true });
            chrome.windows.update(tabs[0].windowId, { focused: true });
          }
        });
        break;
        
      case 'close_tab':
        chrome.tabs.query({ url: data.url }, (tabs) => {
          if (tabs.length > 0) {
            chrome.tabs.remove(tabs[0].id);
          }
        });
        break;
    }
  }

  addActivity(activity) {
    this.recentActivity.unshift(activity);
    
    // Keep only last N items
    if (this.recentActivity.length > this.maxActivityItems) {
      this.recentActivity = this.recentActivity.slice(0, this.maxActivityItems);
    }
    
    this.saveActivity();
  }

  async saveActivity() {
    try {
      await chrome.storage.local.set({ recentActivity: this.recentActivity });
    } catch (error) {
      console.error('Failed to save activity:', error);
    }
  }

  async loadActivity() {
    try {
      const result = await chrome.storage.local.get(['recentActivity']);
      if (result.recentActivity) {
        this.recentActivity = result.recentActivity;
      }
    } catch (error) {
      console.error('Failed to load activity:', error);
    }
  }

  async syncActivity() {
    // Periodically sync activity with desktop app
    if (this.connected) {
      this.sendMessage({
        type: 'sync_activity',
        activities: this.recentActivity
      });
    }
  }

  showNotification(title, message) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: '../icons/icon128.png',
      title: title,
      message: message,
      priority: 1
    });
  }
}

// Initialize service worker
const serviceWorker = new XenoServiceWorker();

// Keep service worker alive
chrome.runtime.onStartup.addListener(() => {
  console.log('XENO extension started');
});
