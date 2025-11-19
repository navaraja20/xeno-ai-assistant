// XENO Browser Extension - Options Page Script

class OptionsPage {
  constructor() {
    this.defaultSettings = {
      serverUrl: 'ws://localhost:8765',
      userData: {
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        linkedInUrl: ''
      },
      features: {
        enableQuickApply: true,
        enableGitHub: true,
        enableGmail: true,
        enableAiAssist: true,
        enablePriority: true,
        enableContextMenu: true,
        enableNotifications: true
      },
      stats: {
        emails: 0,
        tasks: 0,
        events: 0
      }
    };

    this.init();
  }

  async init() {
    // Load saved settings
    await this.loadSettings();
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Test connection on load
    this.testConnection();
    
    // Load statistics
    this.loadStatistics();
  }

  async loadSettings() {
    try {
      const result = await chrome.storage.sync.get([
        'serverUrl',
        'userData',
        'features'
      ]);

      // Server URL
      document.getElementById('server-url').value = 
        result.serverUrl || this.defaultSettings.serverUrl;

      // User Data
      const userData = result.userData || this.defaultSettings.userData;
      document.getElementById('first-name').value = userData.firstName || '';
      document.getElementById('last-name').value = userData.lastName || '';
      document.getElementById('email').value = userData.email || '';
      document.getElementById('phone').value = userData.phone || '';
      document.getElementById('linkedin-url').value = userData.linkedInUrl || '';

      // Features
      const features = result.features || this.defaultSettings.features;
      document.getElementById('enable-quick-apply').checked = features.enableQuickApply !== false;
      document.getElementById('enable-github').checked = features.enableGitHub !== false;
      document.getElementById('enable-gmail').checked = features.enableGmail !== false;
      document.getElementById('enable-ai-assist').checked = features.enableAiAssist !== false;
      document.getElementById('enable-priority').checked = features.enablePriority !== false;
      document.getElementById('enable-context-menu').checked = features.enableContextMenu !== false;
      document.getElementById('enable-notifications').checked = features.enableNotifications !== false;

    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  }

  async loadStatistics() {
    try {
      const result = await chrome.storage.local.get(['stats']);
      const stats = result.stats || this.defaultSettings.stats;

      document.getElementById('stat-emails').textContent = stats.emails || 0;
      document.getElementById('stat-tasks').textContent = stats.tasks || 0;
      document.getElementById('stat-events').textContent = stats.events || 0;

    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  }

  setupEventListeners() {
    // Save button
    document.getElementById('save-btn').addEventListener('click', () => {
      this.saveSettings();
    });

    // Reset button
    document.getElementById('reset-btn').addEventListener('click', () => {
      this.resetSettings();
    });

    // Test connection button
    document.getElementById('test-connection').addEventListener('click', () => {
      this.testConnection();
    });

    // Auto-save on change (optional)
    const inputs = document.querySelectorAll('input[type="text"], input[type="url"], input[type="checkbox"]');
    inputs.forEach(input => {
      input.addEventListener('change', () => {
        // Could implement auto-save here
      });
    });
  }

  async saveSettings() {
    try {
      const settings = {
        serverUrl: document.getElementById('server-url').value.trim(),
        userData: {
          firstName: document.getElementById('first-name').value.trim(),
          lastName: document.getElementById('last-name').value.trim(),
          email: document.getElementById('email').value.trim(),
          phone: document.getElementById('phone').value.trim(),
          linkedInUrl: document.getElementById('linkedin-url').value.trim()
        },
        features: {
          enableQuickApply: document.getElementById('enable-quick-apply').checked,
          enableGitHub: document.getElementById('enable-github').checked,
          enableGmail: document.getElementById('enable-gmail').checked,
          enableAiAssist: document.getElementById('enable-ai-assist').checked,
          enablePriority: document.getElementById('enable-priority').checked,
          enableContextMenu: document.getElementById('enable-context-menu').checked,
          enableNotifications: document.getElementById('enable-notifications').checked
        }
      };

      // Validate URL
      if (settings.serverUrl && !settings.serverUrl.startsWith('ws://') && !settings.serverUrl.startsWith('wss://')) {
        this.showNotification('Invalid WebSocket URL. Must start with ws:// or wss://', false);
        return;
      }

      // Save to storage
      await chrome.storage.sync.set(settings);

      // Show success notification
      this.showNotification('Settings saved successfully!', true);

      // Notify background script to reload connection
      chrome.runtime.sendMessage({ type: 'reload_settings' });

    } catch (error) {
      console.error('Failed to save settings:', error);
      this.showNotification('Failed to save settings', false);
    }
  }

  async resetSettings() {
    if (!confirm('Are you sure you want to reset all settings to defaults?')) {
      return;
    }

    try {
      // Reset to defaults
      await chrome.storage.sync.set(this.defaultSettings);
      
      // Reload page to show defaults
      location.reload();

    } catch (error) {
      console.error('Failed to reset settings:', error);
      this.showNotification('Failed to reset settings', false);
    }
  }

  async testConnection() {
    const serverUrl = document.getElementById('server-url').value.trim();
    const statusIndicator = document.getElementById('connection-status');
    const testBtn = document.getElementById('test-connection');

    if (!serverUrl) {
      this.updateConnectionStatus(false, 'No server URL configured');
      return;
    }

    // Update UI
    testBtn.textContent = 'Testing...';
    testBtn.disabled = true;

    try {
      // Attempt WebSocket connection
      const ws = new WebSocket(serverUrl);

      ws.onopen = () => {
        console.log('Test connection successful');
        this.updateConnectionStatus(true, 'Connected to XENO Desktop');
        ws.close();
        testBtn.textContent = 'Test Connection';
        testBtn.disabled = false;
      };

      ws.onerror = (error) => {
        console.error('Test connection failed:', error);
        this.updateConnectionStatus(false, 'Failed to connect. Is XENO Desktop running?');
        testBtn.textContent = 'Test Connection';
        testBtn.disabled = false;
      };

      ws.onclose = () => {
        testBtn.textContent = 'Test Connection';
        testBtn.disabled = false;
      };

      // Timeout after 5 seconds
      setTimeout(() => {
        if (ws.readyState === WebSocket.CONNECTING) {
          ws.close();
          this.updateConnectionStatus(false, 'Connection timeout');
          testBtn.textContent = 'Test Connection';
          testBtn.disabled = false;
        }
      }, 5000);

    } catch (error) {
      console.error('Connection test error:', error);
      this.updateConnectionStatus(false, 'Connection error');
      testBtn.textContent = 'Test Connection';
      testBtn.disabled = false;
    }
  }

  updateConnectionStatus(connected, message) {
    const statusIndicator = document.getElementById('connection-status');
    
    if (connected) {
      statusIndicator.className = 'status-indicator connected';
      statusIndicator.innerHTML = `
        <span class="status-dot"></span>
        <span>${message}</span>
      `;
    } else {
      statusIndicator.className = 'status-indicator disconnected';
      statusIndicator.innerHTML = `
        <span class="status-dot"></span>
        <span>${message}</span>
      `;
    }
  }

  showNotification(message, success = true) {
    const notification = document.getElementById('save-notification');
    notification.textContent = message;
    notification.style.background = success ? '#57F287' : '#ED4245';
    notification.classList.add('show');

    setTimeout(() => {
      notification.classList.remove('show');
    }, 3000);
  }
}

// Initialize options page when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new OptionsPage();
});
