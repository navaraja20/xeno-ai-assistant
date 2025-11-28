// XENO Browser Extension - GitHub Integration Content Script

(function() {
  'use strict';

  class GitHubIntegration {
    constructor() {
      this.init();
    }

    init() {
      console.log('XENO GitHub integration loaded');

      // Listen for messages from popup/background
      chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        this.handleMessage(message, sender, sendResponse);
        return true;
      });

      // Add XENO quick actions to repository pages
      this.enhanceRepositoryPage();

      // Observe for page navigation (GitHub uses AJAX navigation)
      this.observeNavigation();
    }

    handleMessage(message, sender, sendResponse) {
      switch (message.type) {
        case 'github_star':
          this.starRepository()
            .then(() => sendResponse({ success: true }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        case 'github_watch':
          this.watchRepository()
            .then(() => sendResponse({ success: true }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        case 'github_get_repo_info':
          this.getRepositoryInfo()
            .then(info => sendResponse({ success: true, info }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        case 'github_clone_command':
          this.getCloneCommand()
            .then(command => sendResponse({ success: true, command }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        default:
          sendResponse({ success: false, error: 'Unknown message type' });
      }
    }

    observeNavigation() {
      // GitHub uses turbo for navigation, observe URL changes
      let lastUrl = location.href;

      new MutationObserver(() => {
        const currentUrl = location.href;
        if (currentUrl !== lastUrl) {
          lastUrl = currentUrl;
          this.enhanceRepositoryPage();
        }
      }).observe(document.body, { childList: true, subtree: true });
    }

    enhanceRepositoryPage() {
      // Check if we're on a repository page
      if (!this.isRepositoryPage()) return;

      // Add XENO quick actions panel
      this.addQuickActionsPanel();

      // Add XENO badges to interesting files
      this.enhanceFileExplorer();
    }

    isRepositoryPage() {
      // Check if URL matches repository pattern
      const path = window.location.pathname;
      const parts = path.split('/').filter(p => p);
      return parts.length >= 2 && !['search', 'trending', 'explore', 'settings'].includes(parts[0]);
    }

    addQuickActionsPanel() {
      // Check if panel already exists
      if (document.querySelector('.XENO-github-panel')) return;

      // Create XENO panel
      const panel = document.createElement('div');
      panel.className = 'XENO-github-panel';
      panel.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #2b2d31;
        border: 1px solid #40444b;
        border-radius: 8px;
        padding: 12px;
        z-index: 9999;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        min-width: 200px;
      `;

      panel.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
          <span style="font-size: 16px;">⚡</span>
          <strong style="color: #5865F2; font-size: 14px;">XENO Actions</strong>
          <button id="XENO-panel-close" style="margin-left: auto; background: none; border: none; color: #b5bac1; cursor: pointer; font-size: 18px;">&times;</button>
        </div>
        <div style="display: flex; flex-direction: column; gap: 6px;">
          <button id="XENO-save-repo" class="XENO-action-btn">💾 Save to XENO</button>
          <button id="XENO-create-task" class="XENO-action-btn">✅ Create Task</button>
          <button id="XENO-copy-info" class="XENO-action-btn">📋 Copy Info</button>
          <button id="XENO-analyze" class="XENO-action-btn">🔍 Analyze Repo</button>
        </div>
      `;

      // Add styles for buttons
      const style = document.createElement('style');
      style.textContent = `
        .XENO-action-btn {
          background: #313338;
          border: 1px solid #40444b;
          color: #ffffff;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 13px;
          cursor: pointer;
          text-align: left;
          transition: all 0.2s;
        }
        .XENO-action-btn:hover {
          background: #404249;
          border-color: #5865F2;
        }
      `;
      document.head.appendChild(style);

      document.body.appendChild(panel);

      // Add event listeners
      document.getElementById('XENO-panel-close').addEventListener('click', () => {
        panel.remove();
      });

      document.getElementById('XENO-save-repo').addEventListener('click', () => {
        this.saveRepositoryToXENO();
      });

      document.getElementById('XENO-create-task').addEventListener('click', () => {
        this.createTaskFromRepo();
      });

      document.getElementById('XENO-copy-info').addEventListener('click', () => {
        this.copyRepositoryInfo();
      });

      document.getElementById('XENO-analyze').addEventListener('click', () => {
        this.analyzeRepository();
      });
    }

    enhanceFileExplorer() {
      // Add XENO badges to README, package.json, requirements.txt, etc.
      const importantFiles = ['README.md', 'package.json', 'requirements.txt', 'Dockerfile', 'docker-compose.yml'];

      const fileLinks = document.querySelectorAll('[role="rowheader"] a.Link--primary');

      fileLinks.forEach(link => {
        const filename = link.textContent.trim();

        if (importantFiles.includes(filename) && !link.querySelector('.XENO-badge')) {
          const badge = document.createElement('span');
          badge.className = 'XENO-badge';
          badge.textContent = '⚡';
          badge.style.cssText = 'margin-left: 6px; color: #5865F2;';
          link.appendChild(badge);
        }
      });
    }

    async starRepository() {
      try {
        // Find star button
        const starBtn = document.querySelector('button[data-hydro-click*="star"]') ||
                       document.querySelector('button.btn-sm.btn-with-count');

        if (!starBtn) {
          throw new Error('Star button not found');
        }

        // Check if already starred
        const isStarred = starBtn.getAttribute('aria-label')?.includes('Unstar');

        if (isStarred) {
          this.showNotification('Repository already starred', 'info');
          return;
        }

        starBtn.click();
        this.showNotification('Repository starred successfully', 'success');

      } catch (error) {
        console.error('Failed to star repository:', error);
        throw error;
      }
    }

    async watchRepository() {
      try {
        // Find watch button
        const watchBtn = document.querySelector('button[data-hydro-click*="watch"]');

        if (!watchBtn) {
          throw new Error('Watch button not found');
        }

        watchBtn.click();

        // Wait for dropdown
        await this.sleep(300);

        // Click "All Activity" option
        const allActivityBtn = Array.from(document.querySelectorAll('button')).find(btn =>
          btn.textContent.includes('All Activity')
        );

        if (allActivityBtn) {
          allActivityBtn.click();
        }

        this.showNotification('Now watching repository', 'success');

      } catch (error) {
        console.error('Failed to watch repository:', error);
        throw error;
      }
    }

    async getRepositoryInfo() {
      try {
        const info = {
          url: window.location.href,
          fullName: this.getRepoFullName(),
          description: document.querySelector('[data-pjax="#repo-content-pjax-container"] p')?.textContent?.trim(),
          stars: this.extractNumber(document.querySelector('#repo-stars-counter-star')?.textContent),
          forks: this.extractNumber(document.querySelector('#repo-network-counter')?.textContent),
          watchers: this.extractNumber(document.querySelector('[href$="/watchers"]')?.textContent),
          language: document.querySelector('[itemprop="programmingLanguage"]')?.textContent?.trim(),
          topics: Array.from(document.querySelectorAll('[data-octo-click="topic_click"] a')).map(a => a.textContent.trim()),
          lastUpdated: document.querySelector('relative-time')?.getAttribute('datetime'),
          license: document.querySelector('a[data-turbo-frame="repo-content-turbo-frame"]')?.textContent?.trim(),
          timestamp: Date.now()
        };

        // Get README preview
        const readme = document.querySelector('#readme .markdown-body');
        if (readme) {
          info.readmePreview = readme.textContent.substring(0, 500).trim();
        }

        return info;
      } catch (error) {
        console.error('Failed to get repository info:', error);
        throw error;
      }
    }

    async getCloneCommand() {
      const fullName = this.getRepoFullName();
      return `git clone https://github.com/${fullName}.git`;
    }

    getRepoFullName() {
      const path = window.location.pathname;
      const parts = path.split('/').filter(p => p);
      return parts.length >= 2 ? `${parts[0]}/${parts[1]}` : '';
    }

    extractNumber(text) {
      if (!text) return 0;
      const match = text.match(/[\d,]+/);
      return match ? parseInt(match[0].replace(/,/g, '')) : 0;
    }

    async saveRepositoryToXENO() {
      try {
        const info = await this.getRepositoryInfo();

        chrome.runtime.sendMessage({
          type: 'save_to_XENO',
          data: {
            type: 'github-repo',
            title: info.fullName,
            url: info.url,
            content: JSON.stringify(info, null, 2)
          }
        });

        this.showNotification('Repository saved to XENO', 'success');
      } catch (error) {
        this.showNotification('Failed to save repository', 'error');
      }
    }

    async createTaskFromRepo() {
      try {
        const info = await this.getRepositoryInfo();

        chrome.runtime.sendMessage({
          type: 'create_task',
          data: {
            title: `Review: ${info.fullName}`,
            notes: `GitHub Repository\nURL: ${info.url}\nLanguage: ${info.language}\nStars: ${info.stars}`,
            priority: 'medium'
          }
        });

        this.showNotification('Task created in XENO', 'success');
      } catch (error) {
        this.showNotification('Failed to create task', 'error');
      }
    }

    async copyRepositoryInfo() {
      try {
        const info = await this.getRepositoryInfo();
        const text = `# ${info.fullName}\n\n${info.description}\n\n**URL:** ${info.url}\n**Language:** ${info.language}\n**Stars:** ${info.stars}\n**Forks:** ${info.forks}\n\n**Clone:**\n\`\`\`\ngit clone https://github.com/${info.fullName}.git\n\`\`\``;

        await navigator.clipboard.writeText(text);
        this.showNotification('Repository info copied to clipboard', 'success');
      } catch (error) {
        this.showNotification('Failed to copy info', 'error');
      }
    }

    async analyzeRepository() {
      try {
        const info = await this.getRepositoryInfo();

        // Send to XENO for AI analysis
        chrome.runtime.sendMessage({
          type: 'analyze_repository',
          data: info
        });

        this.showNotification('Analysis request sent to XENO', 'success');
      } catch (error) {
        this.showNotification('Failed to analyze repository', 'error');
      }
    }

    showNotification(message, type = 'info') {
      const colors = {
        success: '#57F287',
        error: '#ED4245',
        info: '#5865F2'
      };

      const toast = document.createElement('div');
      toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        z-index: 999999;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.3s ease-out;
      `;
      toast.textContent = message;

      // Add animation
      if (!document.getElementById('XENO-github-animations')) {
        const style = document.createElement('style');
        style.id = 'XENO-github-animations';
        style.textContent = `
          @keyframes slideIn {
            from {
              transform: translateX(400px);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
          @keyframes slideOut {
            from {
              transform: translateX(0);
              opacity: 1;
            }
            to {
              transform: translateX(400px);
              opacity: 0;
            }
          }
        `;
        document.head.appendChild(style);
      }

      document.body.appendChild(toast);

      setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    }

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  }

  // Initialize GitHub integration
  new GitHubIntegration();
})();
