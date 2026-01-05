// WiFi Network Intelligence Dashboard - JavaScript

// Initialize Socket.IO connection
const socket = io();

// Charts
let signalChart = null;
let securityChart = null;

// Data storage
let currentNetworks = [];
let filteredNetworks = [];

// Connection handling
socket.on('connect', function () {
    console.log('Connected to dashboard server');
    document.getElementById('client-status').classList.remove('disconnected');
    document.getElementById('client-status').classList.add('connected');
    socket.emit('request_update');
});

socket.on('disconnect', function () {
    console.log('Disconnected from dashboard server');
    document.getElementById('client-status').classList.remove('connected');
    document.getElementById('client-status').classList.add('disconnected');
});

// Drone status updates
socket.on('drone_status', function (data) {
    const statusDot = document.getElementById('drone-status');
    const statusText = document.getElementById('drone-name');

    if (data.connected) {
        statusDot.classList.remove('disconnected');
        statusDot.classList.add('connected');
        statusText.textContent = `Drone: ${data.drone_id}`;
    } else {
        statusDot.classList.remove('connected');
        statusDot.classList.add('disconnected');
        statusText.textContent = 'Drone: Disconnected';
    }
});

// Scan data updates
socket.on('scan_update', function (scanData) {
    currentNetworks = scanData.networks || [];
    updateDashboard(scanData);
    updateLastUpdate();
});

// Statistics updates
socket.on('stats_update', function (stats) {
    updateStatistics(stats);
});

// Update dashboard with scan data
function updateDashboard(scanData) {
    // Apply filters
    applyFilters();

    // Update table
    updateNetworksTable(filteredNetworks);

    // Update charts
    updateCharts(filteredNetworks);
}

// Update statistics panel
function updateStatistics(stats) {
    document.getElementById('stat-total').textContent = stats.total_networks_seen || 0;
    document.getElementById('stat-avg').textContent =
        stats.avg_signal ? `${Math.round(stats.avg_signal)} dBm` : '0 dBm';
    document.getElementById('stat-strongest').textContent =
        stats.strongest_network ? stats.strongest_network.ssid : '-';
    document.getElementById('stat-scans').textContent = stats.total_scans || 0;
}

// Update networks table
function updateNetworksTable(networks) {
    const tbody = document.getElementById('networks-tbody');

    if (!networks || networks.length === 0) {
        tbody.innerHTML = '<tr class="no-data"><td colspan="6">No networks found</td></tr>';
        return;
    }

    // Sort by signal strength (strongest first)
    const sorted = [...networks].sort((a, b) =>
        (b.signal_strength || -100) - (a.signal_strength || -100)
    );

    tbody.innerHTML = sorted.map(network => {
        const signal = network.signal_strength || -100;
        const signalClass = getSignalClass(signal);
        const signalBar = getSignalBar(signal);
        const securityClass = getSecurityClass(network.encryption);
        const securityIcon = getSecurityIcon(network.encryption);

        return `
            <tr class="new-entry">
                <td><strong>${escapeHtml(network.ssid || 'Hidden')}</strong></td>
                <td class="${signalClass}">
                    <span class="signal-bar">${signalBar}</span>
                    ${signal} dBm
                </td>
                <td class="${securityClass}">
                    <span class="security-icon">${securityIcon}</span>
                    ${network.encryption || 'Unknown'}
                </td>
                <td>${network.channel || '?'}</td>
                <td><code>${network.bssid || 'N/A'}</code></td>
                <td>${network.frequency || 'N/A'}</td>
            </tr>
        `;
    }).join('');
}

// Update charts
function updateCharts(networks) {
    if (!networks || networks.length === 0) return;

    // Signal distribution chart
    updateSignalChart(networks);

    // Security types chart
    updateSecurityChart(networks);
}

function updateSignalChart(networks) {
    const ctx = document.getElementById('signal-chart').getContext('2d');

    // Count networks by signal range
    const ranges = {
        'Excellent\n(>= -50)': 0,
        'Good\n(-50 to -60)': 0,
        'Fair\n(-60 to -70)': 0,
        'Weak\n(-70 to -80)': 0,
        'Very Weak\n(< -80)': 0
    };

    networks.forEach(n => {
        const signal = n.signal_strength || -100;
        if (signal >= -50) ranges['Excellent\n(>= -50)']++;
        else if (signal >= -60) ranges['Good\n(-50 to -60)']++;
        else if (signal >= -70) ranges['Fair\n(-60 to -70)']++;
        else if (signal >= -80) ranges['Weak\n(-70 to -80)']++;
        else ranges['Very Weak\n(< -80)']++;
    });

    if (signalChart) signalChart.destroy();

    signalChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(ranges),
            datasets: [{
                label: 'Networks',
                data: Object.values(ranges),
                backgroundColor: [
                    '#0f9d58',
                    '#8bc34a',
                    '#f4b400',
                    '#ff9800',
                    '#db4437'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#9aa0a6', stepSize: 1 },
                    grid: { color: '#3d4349' }
                },
                x: {
                    ticks: { color: '#9aa0a6' },
                    grid: { color: '#3d4349' }
                }
            }
        }
    });
}

function updateSecurityChart(networks) {
    const ctx = document.getElementById('security-chart').getContext('2d');

    // Count by security type
    const security = {};
    networks.forEach(n => {
        const type = n.encryption || 'Unknown';
        security[type] = (security[type] || 0) + 1;
    });

    if (securityChart) securityChart.destroy();

    securityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(security),
            datasets: [{
                data: Object.values(security),
                backgroundColor: [
                    '#4285f4',
                    '#0f9d58',
                    '#f4b400',
                    '#db4437',
                    '#9aa0a6'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#9aa0a6' }
                }
            }
        }
    });
}

// Filter functions
function applyFilters() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const securityFilter = document.getElementById('filter-security').value;
    const signalFilter = document.getElementById('filter-signal').value;

    filteredNetworks = currentNetworks.filter(network => {
        // Search filter
        if (searchTerm && !network.ssid.toLowerCase().includes(searchTerm)) {
            return false;
        }

        // Security filter
        if (securityFilter && !network.encryption.includes(securityFilter)) {
            return false;
        }

        // Signal filter
        if (signalFilter) {
            const signal = network.signal_strength || -100;
            if (signalFilter === 'strong' && signal < -60) return false;
            if (signalFilter === 'medium' && (signal >= -60 || signal < -75)) return false;
            if (signalFilter === 'weak' && signal >= -75) return false;
        }

        return true;
    });
}

// Event listeners
document.getElementById('search-input').addEventListener('input', () => {
    applyFilters();
    updateNetworksTable(filteredNetworks);
    updateCharts(filteredNetworks);
});

document.getElementById('filter-security').addEventListener('change', () => {
    applyFilters();
    updateNetworksTable(filteredNetworks);
    updateCharts(filteredNetworks);
});

document.getElementById('filter-signal').addEventListener('change', () => {
    applyFilters();
    updateNetworksTable(filteredNetworks);
    updateCharts(filteredNetworks);
});

// Export to CSV
document.getElementById('export-btn').addEventListener('click', () => {
    if (!currentNetworks || currentNetworks.length === 0) {
        alert('No data to export');
        return;
    }

    const csv = convertToCSV(currentNetworks);
    downloadCSV(csv, `wifi_scan_${Date.now()}.csv`);
});

function convertToCSV(networks) {
    const headers = ['SSID', 'Signal (dBm)', 'Security', 'Channel', 'BSSID', 'Frequency'];
    const rows = networks.map(n => [
        n.ssid || 'Hidden',
        n.signal_strength || '-100',
        n.encryption || 'Unknown',
        n.channel || 'N/A',
        n.bssid || 'N/A',
        n.frequency || 'N/A'
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Helper functions
function getSignalClass(signal) {
    if (signal >= -60) return 'signal-strong';
    if (signal >= -75) return 'signal-medium';
    return 'signal-weak';
}

function getSignalBar(signal) {
    if (signal >= -50) return '████';
    if (signal >= -60) return '███ ';
    if (signal >= -70) return '██  ';
    if (signal >= -80) return '█   ';
    return '▌   ';
}

function getSecurityClass(encryption) {
    if (!encryption) return 'sec-open';
    if (encryption.includes('WPA3')) return 'sec-wpa3';
    if (encryption.includes('WPA2')) return 'sec-wpa2';
    if (encryption.includes('WEP')) return 'sec-wep';
    if (encryption.includes('Open')) return 'sec-open';
    return '';
}

function getSecurityIcon(encryption) {
    if (!encryption || encryption.includes('Open')) return '🔓';
    if (encryption.includes('WPA3')) return '🔒';
    if (encryption.includes('WPA2')) return '🔐';
    return '🔑';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function updateLastUpdate() {
    const now = new Date();
    document.getElementById('last-update').textContent = now.toLocaleTimeString();
}

// Initialize on load
window.addEventListener('load', () => {
    console.log('Dashboard initialized');
    // Initialize with empty charts
    updateCharts([]);
});
