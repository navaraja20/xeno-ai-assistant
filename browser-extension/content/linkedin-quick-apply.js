// XENO Browser Extension - LinkedIn Quick Apply Content Script

(function() {
  'use strict';

  class LinkedInIntegration {
    constructor() {
      this.init();
    }

    init() {
      console.log('XENO LinkedIn integration loaded');

      // Listen for messages from popup/background
      chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        this.handleMessage(message, sender, sendResponse);
        return true; // Keep channel open for async response
      });

      // Add XENO quick action buttons to job postings
      this.observeJobPostings();
    }

    handleMessage(message, sender, sendResponse) {
      switch (message.type) {
        case 'linkedin_quick_apply':
          this.quickApply()
            .then(result => sendResponse({ success: true, result }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        case 'linkedin_get_profile':
          this.getProfileData()
            .then(profile => sendResponse({ success: true, profile }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        case 'linkedin_connect':
          this.sendConnectionRequest()
            .then(() => sendResponse({ success: true }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        case 'get_job_details':
          this.getJobDetails()
            .then(details => sendResponse({ success: true, details }))
            .catch(error => sendResponse({ success: false, error: error.message }));
          break;

        default:
          sendResponse({ success: false, error: 'Unknown message type' });
      }
    }

    observeJobPostings() {
      // Observer to add XENO buttons to job listings
      const observer = new MutationObserver((mutations) => {
        this.addQuickApplyButtons();
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true
      });

      // Initial check
      this.addQuickApplyButtons();
    }

    addQuickApplyButtons() {
      // Find all job cards that don't have XENO button yet
      const jobCards = document.querySelectorAll('.job-card-container:not([data-XENO-enhanced])');

      jobCards.forEach(card => {
        card.setAttribute('data-XENO-enhanced', 'true');

        // Create XENO quick apply button
        const XENOBtn = document.createElement('button');
        XENOBtn.className = 'XENO-quick-apply-btn';
        XENOBtn.innerHTML = '⚡ XENO Quick Apply';
        XENOBtn.style.cssText = `
          background: #5865F2;
          color: white;
          border: none;
          padding: 6px 12px;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          margin: 4px 0;
        `;

        XENOBtn.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          this.quickApplyFromCard(card);
        });

        // Insert button
        const actionArea = card.querySelector('.job-card-container__action');
        if (actionArea) {
          actionArea.prepend(XENOBtn);
        }
      });
    }

    async quickApplyFromCard(card) {
      try {
        // Extract job details from card
        const jobTitle = card.querySelector('.job-card-list__title')?.textContent?.trim();
        const company = card.querySelector('.job-card-container__company-name')?.textContent?.trim();
        const location = card.querySelector('.job-card-container__metadata-item')?.textContent?.trim();

        // Click the job to open details panel
        const titleLink = card.querySelector('.job-card-list__title');
        if (titleLink) {
          titleLink.click();
        }

        // Wait for details panel to load
        await this.sleep(1000);

        // Start quick apply process
        await this.quickApply();

      } catch (error) {
        console.error('Quick apply from card failed:', error);
        this.showXENONotification('Failed to quick apply', 'error');
      }
    }

    async quickApply() {
      try {
        // Find Easy Apply button
        const easyApplyBtn = document.querySelector('button[aria-label*="Easy Apply"]') ||
                            document.querySelector('button.jobs-apply-button');

        if (!easyApplyBtn) {
          throw new Error('Easy Apply button not found. Is this an Easy Apply job?');
        }

        // Get job details before applying
        const jobDetails = await this.getJobDetails();

        // Click Easy Apply
        easyApplyBtn.click();

        await this.sleep(500);

        // Auto-fill application form
        await this.autoFillApplication();

        // Send job details to XENO for tracking
        chrome.runtime.sendMessage({
          type: 'create_task',
          data: {
            title: `Follow up: ${jobDetails.title} at ${jobDetails.company}`,
            notes: `Applied via LinkedIn Easy Apply\nJob URL: ${window.location.href}`,
            priority: 'medium'
          }
        });

        this.showXENONotification('Quick Apply started! Check the form before submitting.');

        return jobDetails;

      } catch (error) {
        console.error('Quick apply failed:', error);
        throw error;
      }
    }

    async autoFillApplication() {
      // Wait for modal to appear
      await this.sleep(500);

      const modal = document.querySelector('.jobs-easy-apply-modal');
      if (!modal) return;

      // Get stored user data from XENO
      const userData = await this.getUserData();

      // Auto-fill common fields
      const fields = {
        'First name': userData.firstName,
        'Last name': userData.lastName,
        'Email': userData.email,
        'Phone': userData.phone,
        'LinkedIn profile': userData.linkedInUrl
      };

      for (const [label, value] of Object.entries(fields)) {
        if (!value) continue;

        const input = Array.from(modal.querySelectorAll('input')).find(inp => {
          const labelText = inp.parentElement?.querySelector('label')?.textContent;
          return labelText?.toLowerCase().includes(label.toLowerCase());
        });

        if (input && !input.value) {
          input.value = value;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }

      // Check for resume upload
      const fileInput = modal.querySelector('input[type="file"]');
      if (fileInput && userData.resumePath) {
        // Note: Can't auto-upload file due to browser security
        this.highlightElement(fileInput.parentElement);
      }
    }

    async getUserData() {
      // Request user data from XENO desktop app
      return new Promise((resolve) => {
        chrome.storage.sync.get(['userData'], (result) => {
          resolve(result.userData || {});
        });
      });
    }

    async getJobDetails() {
      try {
        const details = {
          title: document.querySelector('.job-details-jobs-unified-top-card__job-title')?.textContent?.trim() ||
                 document.querySelector('.jobs-unified-top-card__job-title')?.textContent?.trim(),
          company: document.querySelector('.job-details-jobs-unified-top-card__company-name')?.textContent?.trim() ||
                   document.querySelector('.jobs-unified-top-card__company-name')?.textContent?.trim(),
          location: document.querySelector('.job-details-jobs-unified-top-card__bullet')?.textContent?.trim() ||
                    document.querySelector('.jobs-unified-top-card__bullet')?.textContent?.trim(),
          description: document.querySelector('.jobs-description-content__text')?.textContent?.trim(),
          url: window.location.href,
          timestamp: Date.now()
        };

        // Extract salary if available
        const salaryElement = document.querySelector('.job-details-jobs-unified-top-card__job-insight');
        if (salaryElement) {
          details.salary = salaryElement.textContent.trim();
        }

        return details;
      } catch (error) {
        console.error('Failed to extract job details:', error);
        return {
          url: window.location.href,
          timestamp: Date.now()
        };
      }
    }

    async getProfileData() {
      try {
        // Check if we're on a profile page
        if (!window.location.pathname.includes('/in/')) {
          throw new Error('Not on a LinkedIn profile page');
        }

        const profile = {
          name: document.querySelector('.text-heading-xlarge')?.textContent?.trim(),
          headline: document.querySelector('.text-body-medium')?.textContent?.trim(),
          location: document.querySelector('.text-body-small.inline')?.textContent?.trim(),
          url: window.location.href,
          timestamp: Date.now()
        };

        // Extract about section
        const aboutSection = document.querySelector('#about')?.parentElement?.querySelector('.inline-show-more-text');
        if (aboutSection) {
          profile.about = aboutSection.textContent.trim();
        }

        // Extract experience
        const experienceSection = document.querySelector('#experience');
        if (experienceSection) {
          const experiences = [];
          const expItems = experienceSection.parentElement.querySelectorAll('.pvs-list__paged-list-item');

          expItems.forEach(item => {
            const title = item.querySelector('.mr1.hoverable-link-text')?.textContent?.trim();
            const company = item.querySelector('.t-14.t-normal span[aria-hidden="true"]')?.textContent?.trim();
            const duration = item.querySelector('.t-14.t-normal.t-black--light span[aria-hidden="true"]')?.textContent?.trim();

            if (title) {
              experiences.push({ title, company, duration });
            }
          });

          profile.experience = experiences;
        }

        return profile;
      } catch (error) {
        console.error('Failed to extract profile data:', error);
        throw error;
      }
    }

    async sendConnectionRequest() {
      try {
        // Find Connect button
        const connectBtn = Array.from(document.querySelectorAll('button')).find(btn =>
          btn.textContent.trim().toLowerCase() === 'connect'
        );

        if (!connectBtn) {
          throw new Error('Connect button not found');
        }

        connectBtn.click();

        await this.sleep(500);

        // Look for "Add a note" option and click it
        const addNoteBtn = Array.from(document.querySelectorAll('button')).find(btn =>
          btn.textContent.toLowerCase().includes('add a note')
        );

        if (addNoteBtn) {
          addNoteBtn.click();
          await this.sleep(300);

          // Get personalized note from XENO
          const note = await this.getConnectionNote();
          const textarea = document.querySelector('textarea[name="message"]');
          if (textarea && note) {
            textarea.value = note;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
          }
        }

        this.showXENONotification('Connection request ready. Review and send!');

      } catch (error) {
        console.error('Failed to send connection request:', error);
        throw error;
      }
    }

    async getConnectionNote() {
      // Could be generated by XENO AI based on profile
      return 'Hi! I came across your profile and would love to connect and learn more about your experience.';
    }

    highlightElement(element) {
      element.style.border = '2px solid #5865F2';
      element.style.animation = 'XENO-pulse 1s infinite';

      // Add CSS animation if not exists
      if (!document.getElementById('XENO-animations')) {
        const style = document.createElement('style');
        style.id = 'XENO-animations';
        style.textContent = `
          @keyframes XENO-pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(88, 101, 242, 0.7); }
            50% { box-shadow: 0 0 0 10px rgba(88, 101, 242, 0); }
          }
        `;
        document.head.appendChild(style);
      }
    }

    showXENONotification(message, type = 'info') {
      // Create toast notification
      const toast = document.createElement('div');
      toast.className = 'XENO-toast';
      toast.textContent = message;
      toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'error' ? '#ED4245' : '#5865F2'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        z-index: 999999;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: XENO-slide-in 0.3s ease-out;
      `;

      document.body.appendChild(toast);

      setTimeout(() => {
        toast.style.animation = 'XENO-slide-out 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    }

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  }

  // Initialize LinkedIn integration
  new LinkedInIntegration();
})();
