// XENO Browser Extension - Popup Script

class XenoPopup {
  constructor() {
    this.ws = null;
    this.connected = false;
    this.currentTab = null;
    this.serverUrl = 'ws://localhost:8765'; // Default WebSocket server
    
    this.init();
  }

  async init() {
    // Load settings
    await this.loadSettings();
    
    // Get current tab
    await this.getCurrentTab();
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Connect to desktop app
    this.connectWebSocket();
    
    // Load recent activity
    this.loadRecentActivity();
    
    // Update context actions based on current site
    this.updateContextActions();
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

  async getCurrentTab() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      this.currentTab = tab;
    } catch (error) {
      console.error('Failed to get current tab:', error);
    }
  }

  connectWebSocket() {
    try {
      this.ws = new WebSocket(this.serverUrl);

      this.ws.onopen = () => {
        console.log('Connected to XENO desktop');
        this.connected = true;
        this.updateConnectionStatus(true);
        
        // Send initial handshake
        this.sendMessage({
          type: 'handshake',
          source: 'browser-extension',
          version: chrome.runtime.getManifest().version
        });
      };

      this.ws.onclose = () => {
        console.log('Disconnected from XENO desktop');
        this.connected = false;
        this.updateConnectionStatus(false);
        
        // Attempt to reconnect after 5 seconds
        setTimeout(() => this.connectWebSocket(), 5000);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.updateConnectionStatus(false);
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.updateConnectionStatus(false);
    }
  }

  updateConnectionStatus(connected) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    if (connected) {
      statusDot.classList.add('online');
      statusDot.classList.remove('offline');
      statusText.textContent = 'Connected';
    } else {
      statusDot.classList.add('offline');
      statusDot.classList.remove('online');
      statusText.textContent = 'Offline';
    }
  }

  sendMessage(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected');
    }
  }

  handleMessage(message) {
    switch (message.type) {
      case 'activity_update':
        this.loadRecentActivity();
        break;
      case 'email_sent':
        this.showNotification('Email sent successfully');
        this.closeModal('email-modal');
        break;
      case 'calendar_created':
        this.showNotification('Calendar event created');
        this.closeModal('calendar-modal');
        break;
      case 'task_created':
        this.showNotification('Task created successfully');
        this.closeModal('task-modal');
        break;
      case 'error':
        this.showNotification(message.error, 'error');
        break;
      default:
        console.log('Unknown message type:', message.type);
    }
  }

  setupEventListeners() {
    // Quick action buttons
    document.getElementById('quick-email-btn').addEventListener('click', () => this.openModal('email-modal'));
    document.getElementById('quick-calendar-btn').addEventListener('click', () => this.openModal('calendar-modal'));
    document.getElementById('quick-task-btn').addEventListener('click', () => this.openModal('task-modal'));
    document.getElementById('quick-voice-btn').addEventListener('click', () => this.startVoiceCommand());

    // Modal close buttons
    document.querySelectorAll('.close-modal').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const modal = e.target.closest('.modal');
        if (modal) {
          this.closeModal(modal.id);
        }
      });
    });

    // Modal background click to close
    document.querySelectorAll('.modal').forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          this.closeModal(modal.id);
        }
      });
    });

    // Email modal
    document.getElementById('send-email-btn').addEventListener('click', () => this.sendEmail());
    document.getElementById('cancel-email-btn').addEventListener('click', () => this.closeModal('email-modal'));
    document.getElementById('email-template').addEventListener('change', (e) => this.applyEmailTemplate(e.target.value));

    // Calendar modal
    document.getElementById('create-calendar-btn').addEventListener('click', () => this.createCalendarEvent());
    document.getElementById('cancel-calendar-btn').addEventListener('click', () => this.closeModal('calendar-modal'));

    // Task modal
    document.getElementById('create-task-btn').addEventListener('click', () => this.createTask());
    document.getElementById('cancel-task-btn').addEventListener('click', () => this.closeModal('task-modal'));

    // Open dashboard button
    document.getElementById('open-dashboard-btn').addEventListener('click', () => this.openDashboard());

    // Settings link
    document.getElementById('settings-link').addEventListener('click', () => this.openSettings());
  }

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'flex';
      
      // Pre-fill email if on Gmail
      if (modalId === 'email-modal' && this.currentTab?.url?.includes('mail.google.com')) {
        this.prefillEmailFromGmail();
      }
    }
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'none';
      
      // Clear form fields
      const form = modal.querySelector('form') || modal;
      const inputs = form.querySelectorAll('input, textarea, select');
      inputs.forEach(input => {
        if (input.type === 'select-one') {
          input.selectedIndex = 0;
        } else {
          input.value = '';
        }
      });
    }
  }

  async sendEmail() {
    const to = document.getElementById('email-to').value.trim();
    const subject = document.getElementById('email-subject').value.trim();
    const body = document.getElementById('email-body').value.trim();

    if (!to || !subject || !body) {
      this.showNotification('Please fill in all fields', 'error');
      return;
    }

    // Send via WebSocket to desktop app
    this.sendMessage({
      type: 'send_email',
      data: { to, subject, body }
    });
  }

  async createCalendarEvent() {
    const title = document.getElementById('event-title').value.trim();
    const startTime = document.getElementById('event-start').value;
    const endTime = document.getElementById('event-end').value;
    const description = document.getElementById('event-description').value.trim();

    if (!title || !startTime || !endTime) {
      this.showNotification('Please fill in all required fields', 'error');
      return;
    }

    // Validate times
    if (new Date(startTime) >= new Date(endTime)) {
      this.showNotification('End time must be after start time', 'error');
      return;
    }

    // Send via WebSocket to desktop app
    this.sendMessage({
      type: 'create_calendar_event',
      data: { title, startTime, endTime, description }
    });
  }

  async createTask() {
    const title = document.getElementById('task-title').value.trim();
    const notes = document.getElementById('task-notes').value.trim();
    const priority = document.getElementById('task-priority').value;

    if (!title) {
      this.showNotification('Please enter a task title', 'error');
      return;
    }

    // Send via WebSocket to desktop app
    this.sendMessage({
      type: 'create_task',
      data: { title, notes, priority }
    });
  }

  applyEmailTemplate(template) {
    const bodyField = document.getElementById('email-body');
    
    const templates = {
      'thank-you': 'Dear [Name],\n\nThank you for [reason]. I truly appreciate [specific detail].\n\nBest regards,\n[Your Name]',
      'follow-up': 'Hi [Name],\n\nI wanted to follow up on [topic] from our previous conversation.\n\n[Details]\n\nLooking forward to hearing from you.\n\nBest,\n[Your Name]',
      'meeting': 'Hi [Name],\n\nI would like to schedule a meeting to discuss [topic].\n\nWould [proposed time] work for you?\n\nBest regards,\n[Your Name]'
    };

    if (template && templates[template]) {
      bodyField.value = templates[template];
    }
  }

  async prefillEmailFromGmail() {
    try {
      // Send message to content script to extract email context
      const response = await chrome.tabs.sendMessage(this.currentTab.id, {
        type: 'get_email_context'
      });
      
      if (response && response.email) {
        document.getElementById('email-to').value = response.email;
      }
    } catch (error) {
      console.log('Could not extract email from Gmail:', error);
    }
  }

  async startVoiceCommand() {
    try {
      // Request microphone permission and start voice recognition
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Show voice input UI (could expand into a modal)
      this.showNotification('Listening... Speak your command');
      
      // Use Web Speech API
      const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      recognition.lang = 'en-US';
      recognition.continuous = false;
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.processVoiceCommand(transcript);
        stream.getTracks().forEach(track => track.stop());
      };
      
      recognition.onerror = (error) => {
        console.error('Voice recognition error:', error);
        this.showNotification('Voice recognition failed', 'error');
        stream.getTracks().forEach(track => track.stop());
      };
      
      recognition.start();
    } catch (error) {
      console.error('Microphone access denied:', error);
      this.showNotification('Microphone access required for voice commands', 'error');
    }
  }

  processVoiceCommand(transcript) {
    console.log('Voice command:', transcript);
    
    // Send to desktop app for processing
    this.sendMessage({
      type: 'voice_command',
      data: { transcript }
    });
    
    this.showNotification(`Processing: "${transcript}"`);
  }

  async loadRecentActivity() {
    // Request from storage or background script
    try {
      const result = await chrome.storage.local.get(['recentActivity']);
      const activities = result.recentActivity || [];
      
      const activityList = document.getElementById('activity-list');
      
      if (activities.length === 0) {
        activityList.innerHTML = '<div style="text-align: center; color: #b5bac1; padding: 20px;">No recent activity</div>';
        return;
      }
      
      activityList.innerHTML = activities.slice(0, 5).map(activity => `
        <div class="activity-item">
          <div class="activity-icon">${this.getActivityIcon(activity.type)}</div>
          <div class="activity-content">
            <div class="activity-title">${this.escapeHtml(activity.title)}</div>
            <div class="activity-time">${this.formatTimeAgo(activity.timestamp)}</div>
          </div>
        </div>
      `).join('');
    } catch (error) {
      console.error('Failed to load recent activity:', error);
    }
  }

  updateContextActions() {
    if (!this.currentTab || !this.currentTab.url) return;

    const contextSection = document.getElementById('context-section');
    const contextTitle = document.getElementById('context-title');
    const contextActions = document.getElementById('context-actions');
    
    let actions = [];
    let title = '';

    if (this.currentTab.url.includes('linkedin.com')) {
      title = 'LinkedIn Actions';
      actions = [
        { text: '⚡ Quick Apply to Job', handler: () => this.linkedinQuickApply() },
        { text: '👤 Save Profile Info', handler: () => this.linkedinSaveProfile() },
        { text: '📨 Send Connection Request', handler: () => this.linkedinConnect() }
      ];
    } else if (this.currentTab.url.includes('github.com')) {
      title = 'GitHub Actions';
      actions = [
        { text: '⭐ Star Repository', handler: () => this.githubStar() },
        { text: '📋 Copy Repo Info', handler: () => this.githubCopyInfo() },
        { text: '🔔 Watch Repository', handler: () => this.githubWatch() }
      ];
    } else if (this.currentTab.url.includes('mail.google.com')) {
      title = 'Gmail Actions';
      actions = [
        { text: '✍️ Quick Compose', handler: () => this.openModal('email-modal') },
        { text: '📅 Schedule from Email', handler: () => this.gmailScheduleEvent() },
        { text: '✅ Create Task from Email', handler: () => this.gmailCreateTask() }
      ];
    }

    if (actions.length > 0) {
      contextSection.style.display = 'block';
      contextTitle.textContent = title;
      contextActions.innerHTML = actions.map((action, index) => `
        <button class="context-btn" data-action-index="${index}">
          ${this.escapeHtml(action.text)}
        </button>
      `).join('');
      
      // Add event listeners
      actions.forEach((action, index) => {
        const btn = contextActions.querySelector(`[data-action-index="${index}"]`);
        if (btn) {
          btn.addEventListener('click', action.handler);
        }
      });
    } else {
      contextSection.style.display = 'none';
    }
  }

  // Context-specific actions
  async linkedinQuickApply() {
    try {
      await chrome.tabs.sendMessage(this.currentTab.id, { type: 'linkedin_quick_apply' });
      this.showNotification('Starting LinkedIn quick apply...');
    } catch (error) {
      this.showNotification('Failed to start quick apply', 'error');
    }
  }

  async linkedinSaveProfile() {
    try {
      const response = await chrome.tabs.sendMessage(this.currentTab.id, { type: 'linkedin_get_profile' });
      if (response && response.profile) {
        this.sendMessage({
          type: 'save_linkedin_profile',
          data: response.profile
        });
        this.showNotification('Profile saved successfully');
      }
    } catch (error) {
      this.showNotification('Failed to save profile', 'error');
    }
  }

  async linkedinConnect() {
    try {
      await chrome.tabs.sendMessage(this.currentTab.id, { type: 'linkedin_connect' });
      this.showNotification('Connection request sent');
    } catch (error) {
      this.showNotification('Failed to send connection request', 'error');
    }
  }

  async githubStar() {
    try {
      await chrome.tabs.sendMessage(this.currentTab.id, { type: 'github_star' });
      this.showNotification('Repository starred');
    } catch (error) {
      this.showNotification('Failed to star repository', 'error');
    }
  }

  async githubCopyInfo() {
    try {
      const response = await chrome.tabs.sendMessage(this.currentTab.id, { type: 'github_get_repo_info' });
      if (response && response.info) {
        await navigator.clipboard.writeText(JSON.stringify(response.info, null, 2));
        this.showNotification('Repository info copied to clipboard');
      }
    } catch (error) {
      this.showNotification('Failed to copy repository info', 'error');
    }
  }

  async githubWatch() {
    try {
      await chrome.tabs.sendMessage(this.currentTab.id, { type: 'github_watch' });
      this.showNotification('Now watching repository');
    } catch (error) {
      this.showNotification('Failed to watch repository', 'error');
    }
  }

  async gmailScheduleEvent() {
    try {
      const response = await chrome.tabs.sendMessage(this.currentTab.id, { type: 'gmail_get_selected_email' });
      if (response && response.subject) {
        document.getElementById('event-title').value = response.subject;
        this.openModal('calendar-modal');
      }
    } catch (error) {
      this.openModal('calendar-modal');
    }
  }

  async gmailCreateTask() {
    try {
      const response = await chrome.tabs.sendMessage(this.currentTab.id, { type: 'gmail_get_selected_email' });
      if (response && response.subject) {
        document.getElementById('task-title').value = response.subject;
        if (response.body) {
          document.getElementById('task-notes').value = response.body.substring(0, 200);
        }
        this.openModal('task-modal');
      }
    } catch (error) {
      this.openModal('task-modal');
    }
  }

  openDashboard() {
    // Send message to background to open desktop dashboard
    this.sendMessage({
      type: 'open_dashboard'
    });
    window.close();
  }

  openSettings() {
    chrome.runtime.openOptionsPage();
  }

  showNotification(message, type = 'success') {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: '../icons/icon128.png',
      title: 'XENO',
      message: message,
      priority: type === 'error' ? 2 : 1
    });
  }

  getActivityIcon(type) {
    const icons = {
      email: '📧',
      calendar: '📅',
      task: '✅',
      voice: '🎤',
      linkedin: '💼',
      github: '💻',
      default: '📌'
    };
    return icons[type] || icons.default;
  }

  formatTimeAgo(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new XenoPopup();
});
