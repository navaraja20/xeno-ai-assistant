// XENO Browser Extension - Gmail Integration Content Script

(function() {
  'use strict';

  class GmailIntegration {
    constructor() {
      this.init();
    }

    init() {
      console.log('XENO Gmail integration loaded');
      
      // Listen for messages from popup/background
      chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        this.handleMessage(message, sender, sendResponse);
        return true;
      });

      // Add XENO quick actions to Gmail
      this.enhanceGmail();
      
      // Observe for Gmail updates (Gmail uses dynamic content)
      this.observeGmailChanges();
    }

    handleMessage(message, sender, sendResponse) {
      switch (message.type) {
        case 'get_email_context':
          this.getEmailContext()
            .then(context => sendResponse({ success: true, ...context }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        case 'gmail_get_selected_email':
          this.getSelectedEmail()
            .then(email => sendResponse({ success: true, ...email }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        case 'gmail_quick_reply':
          this.quickReply(message.data)
            .then(() => sendResponse({ success: true }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        default:
          sendResponse({ success: false, error: 'Unknown message type' });
      }
    }

    observeGmailChanges() {
      // Gmail updates content dynamically, observe changes
      const observer = new MutationObserver(() => {
        this.enhanceGmail();
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    }

    enhanceGmail() {
      // Add XENO button to compose toolbar
      this.addComposeEnhancements();
      
      // Add XENO actions to email threads
      this.addThreadEnhancements();
      
      // Add priority indicators
      this.addPriorityIndicators();
    }

    addComposeEnhancements() {
      // Find compose windows
      const composeWindows = document.querySelectorAll('[role="dialog"]:not([data-xeno-enhanced])');
      
      composeWindows.forEach(window => {
        window.setAttribute('data-xeno-enhanced', 'true');
        
        // Find toolbar
        const toolbar = window.querySelector('[role="toolbar"]');
        if (!toolbar) return;
        
        // Create XENO AI assist button
        const xenoBtn = document.createElement('div');
        xenoBtn.className = 'xeno-compose-btn';
        xenoBtn.innerHTML = `
          <div style="
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 6px 12px;
            background: #5865F2;
            color: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            margin: 0 4px;
          ">
            ⚡ XENO AI
          </div>
        `;
        
        xenoBtn.addEventListener('click', () => {
          this.showAIAssist(window);
        });
        
        toolbar.appendChild(xenoBtn);
      });
    }

    addThreadEnhancements() {
      // Find email threads
      const threads = document.querySelectorAll('[data-message-id]:not([data-xeno-enhanced])');
      
      threads.forEach(thread => {
        thread.setAttribute('data-xeno-enhanced', 'true');
        
        // Create XENO action buttons
        const actionBar = thread.querySelector('[role="toolbar"]');
        if (!actionBar) return;
        
        // Add quick reply button
        const quickReplyBtn = this.createThreadActionButton('⚡ Quick Reply', () => {
          this.initiateQuickReply(thread);
        });
        
        // Add create task button
        const taskBtn = this.createThreadActionButton('✅ Task', () => {
          this.createTaskFromEmail(thread);
        });
        
        // Add schedule button
        const scheduleBtn = this.createThreadActionButton('📅 Schedule', () => {
          this.scheduleEventFromEmail(thread);
        });
        
        actionBar.appendChild(quickReplyBtn);
        actionBar.appendChild(taskBtn);
        actionBar.appendChild(scheduleBtn);
      });
    }

    createThreadActionButton(text, onClick) {
      const btn = document.createElement('div');
      btn.style.cssText = `
        display: inline-flex;
        align-items: center;
        padding: 4px 8px;
        margin: 0 2px;
        background: #f1f3f4;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        font-weight: 500;
        color: #5f6368;
        transition: background 0.2s;
      `;
      btn.textContent = text;
      
      btn.addEventListener('mouseenter', () => {
        btn.style.background = '#e8eaed';
      });
      
      btn.addEventListener('mouseleave', () => {
        btn.style.background = '#f1f3f4';
      });
      
      btn.addEventListener('click', onClick);
      
      return btn;
    }

    addPriorityIndicators() {
      // Add ML-based priority indicators to emails
      const emailRows = document.querySelectorAll('[role="row"]:not([data-xeno-priority])');
      
      emailRows.forEach(async row => {
        row.setAttribute('data-xeno-priority', 'checking');
        
        // Extract email info
        const subject = row.querySelector('[data-thread-perm-id]')?.textContent;
        const sender = row.querySelector('[email]')?.getAttribute('email');
        
        if (!subject || !sender) return;
        
        // Get priority from XENO ML model
        const priority = await this.getPriorityPrediction(subject, sender);
        
        if (priority === 'high') {
          // Add visual indicator
          const indicator = document.createElement('span');
          indicator.style.cssText = `
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #ED4245;
            border-radius: 50%;
            margin-right: 6px;
          `;
          
          const subjectCell = row.querySelector('[data-thread-perm-id]');
          if (subjectCell) {
            subjectCell.prepend(indicator);
          }
        }
      });
    }

    async getPriorityPrediction(subject, sender) {
      // Request priority from XENO desktop app
      return new Promise((resolve) => {
        chrome.runtime.sendMessage({
          type: 'predict_email_priority',
          data: { subject, sender }
        }, (response) => {
          resolve(response?.priority || 'medium');
        });
      });
    }

    async showAIAssist(composeWindow) {
      // Show XENO AI assistant panel
      const panel = document.createElement('div');
      panel.style.cssText = `
        position: absolute;
        top: 50px;
        right: 20px;
        background: white;
        border: 1px solid #dadce0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        min-width: 300px;
      `;
      
      panel.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <strong style="color: #5865F2; font-size: 14px;">⚡ XENO AI Assistant</strong>
          <button id="xeno-ai-close" style="background: none; border: none; cursor: pointer; font-size: 18px;">&times;</button>
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          <button class="xeno-ai-action" data-action="professional">Make it professional</button>
          <button class="xeno-ai-action" data-action="friendly">Make it friendly</button>
          <button class="xeno-ai-action" data-action="concise">Make it concise</button>
          <button class="xeno-ai-action" data-action="expand">Expand details</button>
          <button class="xeno-ai-action" data-action="grammar">Fix grammar</button>
        </div>
      `;
      
      // Add styles
      panel.querySelectorAll('.xeno-ai-action').forEach(btn => {
        btn.style.cssText = `
          padding: 8px 12px;
          background: #f1f3f4;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 13px;
          text-align: left;
        `;
        
        btn.addEventListener('mouseenter', () => btn.style.background = '#e8eaed');
        btn.addEventListener('mouseleave', () => btn.style.background = '#f1f3f4');
        
        btn.addEventListener('click', () => {
          this.applyAIAction(composeWindow, btn.dataset.action);
          panel.remove();
        });
      });
      
      panel.querySelector('#xeno-ai-close').addEventListener('click', () => {
        panel.remove();
      });
      
      composeWindow.appendChild(panel);
    }

    async applyAIAction(composeWindow, action) {
      // Get current email body
      const bodyElement = composeWindow.querySelector('[contenteditable="true"][aria-label*="Message"]');
      if (!bodyElement) return;
      
      const currentBody = bodyElement.textContent;
      
      // Show loading indicator
      this.showNotification('XENO AI is processing...', 'info');
      
      // Send to XENO for AI processing
      chrome.runtime.sendMessage({
        type: 'ai_rewrite_email',
        data: {
          body: currentBody,
          action: action
        }
      }, (response) => {
        if (response?.success && response.rewrittenBody) {
          bodyElement.textContent = response.rewrittenBody;
          bodyElement.dispatchEvent(new Event('input', { bubbles: true }));
          this.showNotification('Email rewritten successfully', 'success');
        } else {
          this.showNotification('Failed to rewrite email', 'error');
        }
      });
    }

    async getEmailContext() {
      try {
        // Get current email address if composing to someone
        const toField = document.querySelector('input[name="to"]');
        const email = toField?.value || '';
        
        return { email };
      } catch (error) {
        console.error('Failed to get email context:', error);
        return {};
      }
    }

    async getSelectedEmail() {
      try {
        // Get currently open email
        const subject = document.querySelector('[data-legacy-thread-id] h2')?.textContent?.trim();
        const bodyElement = document.querySelector('[data-message-id] .a3s.aiL');
        const body = bodyElement?.textContent?.trim();
        const sender = document.querySelector('[email]')?.getAttribute('email');
        
        return { subject, body, sender };
      } catch (error) {
        console.error('Failed to get selected email:', error);
        return {};
      }
    }

    async initiateQuickReply(thread) {
      // Find or create reply box
      const replyBtn = thread.querySelector('[role="button"][aria-label*="Reply"]');
      if (replyBtn) {
        replyBtn.click();
        
        await this.sleep(500);
        
        // Show XENO quick templates
        this.showQuickReplyTemplates();
      }
    }

    showQuickReplyTemplates() {
      const templates = {
        'Thank you': 'Thank you for your email. I appreciate you reaching out.',
        'Received': 'Thank you, I have received this and will review it shortly.',
        'Meeting': 'Thank you for the invitation. I would be happy to meet. What time works best for you?',
        'Follow-up': 'Following up on my previous email. Please let me know if you need any additional information.'
      };
      
      // Create template picker
      const picker = document.createElement('div');
      picker.style.cssText = `
        position: fixed;
        bottom: 100px;
        right: 20px;
        background: white;
        border: 1px solid #dadce0;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
      `;
      
      picker.innerHTML = `
        <div style="font-weight: 600; margin-bottom: 8px; color: #5865F2;">Quick Reply Templates</div>
        ${Object.entries(templates).map(([name, text]) => `
          <div class="xeno-template" data-text="${text}" style="
            padding: 8px;
            cursor: pointer;
            border-radius: 4px;
            margin: 4px 0;
            font-size: 13px;
          ">${name}</div>
        `).join('')}
      `;
      
      picker.querySelectorAll('.xeno-template').forEach(item => {
        item.addEventListener('mouseenter', () => item.style.background = '#f1f3f4');
        item.addEventListener('mouseleave', () => item.style.background = 'white');
        
        item.addEventListener('click', () => {
          const replyBox = document.querySelector('[aria-label*="Reply"] [contenteditable="true"]');
          if (replyBox) {
            replyBox.textContent = item.dataset.text;
            replyBox.dispatchEvent(new Event('input', { bubbles: true }));
          }
          picker.remove();
        });
      });
      
      document.body.appendChild(picker);
      
      setTimeout(() => picker.remove(), 10000);
    }

    async createTaskFromEmail(thread) {
      try {
        const subject = thread.querySelector('[data-thread-perm-id]')?.textContent?.trim();
        const sender = thread.querySelector('[email]')?.getAttribute('email');
        
        if (!subject) return;
        
        chrome.runtime.sendMessage({
          type: 'create_task',
          data: {
            title: `Email: ${subject}`,
            notes: `From: ${sender}\nReview and respond to this email.`,
            priority: 'medium'
          }
        });
        
        this.showNotification('Task created from email', 'success');
      } catch (error) {
        this.showNotification('Failed to create task', 'error');
      }
    }

    async scheduleEventFromEmail(thread) {
      try {
        const subject = thread.querySelector('[data-thread-perm-id]')?.textContent?.trim();
        
        if (!subject) return;
        
        // Open calendar modal in popup
        chrome.runtime.sendMessage({
          type: 'trigger_action',
          action: 'calendar',
          prefill: { title: subject }
        });
        
        this.showNotification('Opening calendar...', 'info');
      } catch (error) {
        this.showNotification('Failed to schedule event', 'error');
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
        bottom: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        z-index: 999999;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      `;
      toast.textContent = message;
      
      document.body.appendChild(toast);
      
      setTimeout(() => toast.remove(), 3000);
    }

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  }

  // Initialize Gmail integration
  new GmailIntegration();
})();
