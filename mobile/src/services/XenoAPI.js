/**
 * XENO API Service
 * Handles communication with XENO desktop backend
 */

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:5000/api'; // Update with your server IP

class XenoAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use(async config => {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Authentication
  async login(email, password) {
    try {
      const response = await this.client.post('/auth/login', {email, password});
      if (response.data.token) {
        await AsyncStorage.setItem('auth_token', response.data.token);
      }
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async logout() {
    await AsyncStorage.removeItem('auth_token');
  }

  // Dashboard
  async getDashboard() {
    try {
      const response = await this.client.get('/dashboard');
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async getTimeline(limit = 20) {
    try {
      const response = await this.client.get('/timeline', {params: {limit}});
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  // Notifications
  async getNotifications(unreadOnly = false) {
    try {
      const response = await this.client.get('/notifications', {
        params: {unread_only: unreadOnly},
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async markNotificationRead(notificationId) {
    try {
      const response = await this.client.post(
        `/notifications/${notificationId}/read`,
      );
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async registerPushToken(token) {
    try {
      const response = await this.client.post('/push-token', {token});
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  // Email
  async getEmails(folder = 'INBOX', limit = 50) {
    try {
      const response = await this.client.get('/emails', {
        params: {folder, limit},
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async sendEmail(to, subject, body) {
    try {
      const response = await this.client.post('/emails/send', {
        to,
        subject,
        body,
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  // Calendar
  async getCalendarEvents(daysAhead = 7) {
    try {
      const response = await this.client.get('/calendar/events', {
        params: {days_ahead: daysAhead},
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async createCalendarEvent(eventData) {
    try {
      const response = await this.client.post('/calendar/events', eventData);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  // Voice Command
  async executeVoiceCommand(command) {
    try {
      const response = await this.client.post('/voice/execute', {command});
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  // GitHub
  async getGitHubRepos() {
    try {
      const response = await this.client.get('/github/repos');
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async getGitHubStats() {
    try {
      const response = await this.client.get('/github/stats');
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  // LinkedIn Jobs
  async getJobs(keywords = '', location = '') {
    try {
      const response = await this.client.get('/jobs', {
        params: {keywords, location},
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  async applyToJob(jobId) {
    try {
      const response = await this.client.post(`/jobs/${jobId}/apply`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  // AI Chat
  async sendMessage(message, context = []) {
    try {
      const response = await this.client.post('/ai/chat', {message, context});
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  _handleError(error) {
    if (error.response) {
      return new Error(
        error.response.data.message || 'Server error occurred',
      );
    } else if (error.request) {
      return new Error('Network error - cannot reach server');
    } else {
      return new Error(error.message);
    }
  }
}

export default new XenoAPI();
