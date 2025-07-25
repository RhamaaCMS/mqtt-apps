// MQTT Admin Dashboard JavaScript

class MqttDashboard {
    constructor() {
        this.isConnected = false;
        this.statusCheckInterval = null;
        this.messageRefreshInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.startStatusCheck();
        this.startMessageRefresh();
    }

    bindEvents() {
        // Connection controls
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-mqtt-action="connect"]')) {
                e.preventDefault();
                this.connect();
            }
            if (e.target.matches('[data-mqtt-action="disconnect"]')) {
                e.preventDefault();
                this.disconnect();
            }
            if (e.target.matches('[data-mqtt-action="refresh"]')) {
                e.preventDefault();
                this.refreshStatus();
            }
        });

        // Form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.matches('#mqtt-publish-form')) {
                e.preventDefault();
                this.publishMessage(e.target);
            }
            if (e.target.matches('#mqtt-subscribe-form')) {
                e.preventDefault();
                this.subscribeTopic(e.target);
            }
        });

        // Auto-refresh toggles
        const autoRefreshToggle = document.getElementById('mqtt-auto-refresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startMessageRefresh();
                } else {
                    this.stopMessageRefresh();
                }
            });
        }
    }

    async connect() {
        try {
            this.showLoading('Connecting to MQTT broker...');
            const response = await fetch('/mqtt/connect/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Connected to MQTT broker successfully', 'success');
                this.updateConnectionStatus(true);
            } else {
                this.showAlert(data.message || 'Failed to connect', 'error');
            }
        } catch (error) {
            this.showAlert('Error connecting to MQTT broker', 'error');
            console.error('Connection error:', error);
        } finally {
            this.hideLoading();
        }
    }

    async disconnect() {
        try {
            this.showLoading('Disconnecting from MQTT broker...');
            const response = await fetch('/mqtt/disconnect/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Disconnected from MQTT broker', 'info');
                this.updateConnectionStatus(false);
            } else {
                this.showAlert(data.message || 'Failed to disconnect', 'error');
            }
        } catch (error) {
            this.showAlert('Error disconnecting from MQTT broker', 'error');
            console.error('Disconnection error:', error);
        } finally {
            this.hideLoading();
        }
    }

    async publishMessage(form) {
        try {
            const formData = new FormData(form);
            const data = {
                topic: formData.get('topic'),
                payload: formData.get('payload'),
                qos: parseInt(formData.get('qos') || '1'),
                retain: formData.get('retain') === 'on'
            };

            if (!data.topic || !data.payload) {
                this.showAlert('Topic and payload are required', 'warning');
                return;
            }

            this.showLoading('Publishing message...');
            const response = await fetch('/mqtt/publish/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('Message published successfully', 'success');
                form.reset();
                this.refreshMessages();
            } else {
                this.showAlert(result.message || 'Failed to publish message', 'error');
            }
        } catch (error) {
            this.showAlert('Error publishing message', 'error');
            console.error('Publish error:', error);
        } finally {
            this.hideLoading();
        }
    }

    async subscribeTopic(form) {
        try {
            const formData = new FormData(form);
            const data = {
                topic: formData.get('topic'),
                description: formData.get('description') || '',
                qos: parseInt(formData.get('qos') || '1')
            };

            if (!data.topic) {
                this.showAlert('Topic is required', 'warning');
                return;
            }

            this.showLoading('Subscribing to topic...');
            const response = await fetch('/mqtt/subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(`Subscribed to topic: ${data.topic}`, 'success');
                form.reset();
                this.refreshTopics();
            } else {
                this.showAlert(result.message || 'Failed to subscribe to topic', 'error');
            }
        } catch (error) {
            this.showAlert('Error subscribing to topic', 'error');
            console.error('Subscribe error:', error);
        } finally {
            this.hideLoading();
        }
    }

    async refreshStatus() {
        try {
            const response = await fetch('/mqtt/status/');
            const data = await response.json();
            
            if (data.success) {
                this.updateConnectionStatus(data.is_connected);
                this.updateStats(data.stats);
                this.updateConnectionInfo(data.connection);
            }
        } catch (error) {
            console.error('Status refresh error:', error);
        }
    }

    async refreshMessages() {
        const messagesContainer = document.getElementById('mqtt-recent-messages');
        if (!messagesContainer) return;

        try {
            // This would need to be implemented in the backend
            // For now, we'll just reload the page section
            location.reload();
        } catch (error) {
            console.error('Message refresh error:', error);
        }
    }

    async refreshTopics() {
        // Reload topics section
        location.reload();
    }

    updateConnectionStatus(connected) {
        this.isConnected = connected;
        
        // Update status indicator
        const indicator = document.querySelector('.mqtt-status-indicator');
        if (indicator) {
            indicator.className = `mqtt-status-indicator ${connected ? 'connected' : 'disconnected'}`;
        }

        // Update status text
        const statusText = document.getElementById('mqtt-status-text');
        if (statusText) {
            statusText.textContent = connected ? 'Connected' : 'Disconnected';
            statusText.className = connected ? 'status-success' : 'status-error';
        }

        // Update buttons
        const connectBtn = document.querySelector('[data-mqtt-action="connect"]');
        const disconnectBtn = document.querySelector('[data-mqtt-action="disconnect"]');
        
        if (connectBtn) connectBtn.style.display = connected ? 'none' : 'inline-block';
        if (disconnectBtn) disconnectBtn.style.display = connected ? 'inline-block' : 'none';
    }

    updateStats(stats) {
        if (!stats) return;

        const topicsCount = document.getElementById('mqtt-topics-count');
        const messagesCount = document.getElementById('mqtt-messages-count');

        if (topicsCount) topicsCount.textContent = stats.active_topics || '0';
        if (messagesCount) messagesCount.textContent = stats.total_messages || '0';
    }

    updateConnectionInfo(connection) {
        if (!connection) return;

        const brokerInfo = document.getElementById('mqtt-broker-info');
        if (brokerInfo && connection.broker_host) {
            brokerInfo.textContent = `${connection.broker_host}:${connection.broker_port}`;
        }

        const lastConnected = document.getElementById('mqtt-last-connected');
        if (lastConnected && connection.last_connected) {
            const date = new Date(connection.last_connected);
            lastConnected.textContent = date.toLocaleString();
        }

        const lastError = document.getElementById('mqtt-last-error');
        if (lastError) {
            lastError.textContent = connection.last_error || 'None';
            lastError.style.color = connection.last_error ? '#dc3545' : '#28a745';
        }
    }

    startStatusCheck() {
        this.refreshStatus(); // Initial check
        this.statusCheckInterval = setInterval(() => {
            this.refreshStatus();
        }, 30000); // Check every 30 seconds
    }

    stopStatusCheck() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
            this.statusCheckInterval = null;
        }
    }

    startMessageRefresh() {
        this.messageRefreshInterval = setInterval(() => {
            this.refreshMessages();
        }, 10000); // Refresh every 10 seconds
    }

    stopMessageRefresh() {
        if (this.messageRefreshInterval) {
            clearInterval(this.messageRefreshInterval);
            this.messageRefreshInterval = null;
        }
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('mqtt-alerts');
        if (!alertContainer) return;

        const alert = document.createElement('div');
        alert.className = `mqtt-alert mqtt-alert-${type}`;
        alert.textContent = message;

        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = 'float: right; background: none; border: none; font-size: 1.2em; cursor: pointer;';
        closeBtn.onclick = () => alert.remove();
        alert.appendChild(closeBtn);

        alertContainer.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    showLoading(message = 'Loading...') {
        const loader = document.getElementById('mqtt-loader');
        if (loader) {
            loader.textContent = message;
            loader.style.display = 'block';
        }
    }

    hideLoading() {
        const loader = document.getElementById('mqtt-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.mqtt-dashboard')) {
        window.mqttDashboard = new MqttDashboard();
    }
});

// Export for use in other scripts
window.MqttDashboard = MqttDashboard;