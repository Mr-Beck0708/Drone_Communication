// Wireshark-Style Logic
const socket = io();
let currentNetworks = [];
let selectedBSSID = null;
let packetCount = 0;
let signalChart = null;

// Initialize
window.addEventListener('load', () => {
    initChart();

    // Connect socket
    socket.on('connect', () => updateStatus('Connected to Profile: Drone Live Capture'));
    socket.on('disconnect', () => updateStatus('Disconnected', true));

    // Receive data
    socket.on('scan_update', (data) => {
        if (data.networks) {
            currentNetworks = data.networks;
            renderTable(currentNetworks);
            updatePacketCount(currentNetworks.length);

            // If selection exists, update details pane live
            if (selectedBSSID) {
                const net = currentNetworks.find(n => n.bssid === selectedBSSID);
                if (net) renderDetails(net);
            }

            updateChart(currentNetworks);
        }
    });

    // Request initial data
    socket.emit('request_update');
});

// Update Status Bar
function updateStatus(msg, isError = false) {
    document.getElementById('connection-text').textContent = msg;
    document.getElementById('status-icon').style.backgroundColor = isError ? '#cc0000' : '#66bb6a';
}

function updatePacketCount(count) {
    packetCount += count; // Just simulating total packets seen over time
    document.getElementById('packet-count').textContent = `Packets: ${packetCount} · Displayed: ${currentNetworks.length}`;
}

// Render Main Table (Packet List)
function renderTable(networks) {
    const tbody = document.getElementById('networks-tbody');
    tbody.innerHTML = '';

    networks.forEach((net, index) => {
        const tr = document.createElement('tr');

        // Protocol Coloring
        let rowClass = 'row-wpa2';
        if (net.encryption.includes('Open')) rowClass = 'row-open';
        else if (net.encryption.includes('WPA3')) rowClass = 'row-wpa3';
        tr.className = rowClass;

        if (net.bssid === selectedBSSID) tr.classList.add('selected');

        // Selection Handler
        tr.onclick = () => {
            // Remove previous selection
            document.querySelectorAll('.ws-table tbody tr').forEach(r => r.classList.remove('selected'));
            tr.classList.add('selected');
            selectedBSSID = net.bssid;
            renderDetails(net);
        };

        // Columns matching HTML headers
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${(Date.now() / 1000).toFixed(6)}</td>
            <td>${net.bssid || 'ff:ff:ff:ff:ff:ff'}</td>
            <td><strong>${net.ssid || '<Missing SSID>'}</strong></td>
            <td>${net.channel}</td>
            <td>${net.signal_strength} dBm</td>
            <td>IEEE 802.11 (${net.encryption})</td>
            <td>${net.frequency || '2.4'} GHz</td>
        `;
        tbody.appendChild(tr);
    });
}

// Render Details Pane (Packet Details)
function renderDetails(net) {
    const container = document.getElementById('details-content');

    // Generic Wireshark-style tree structure
    const html = `
        <div class="detail-tree-root">
            <span class="detail-expander">▼</span>
            <span class="detail-label">Frame 1:</span> 
            <span class="detail-value">${net.ssid.length + 50} bytes on wire, captured on Drone Interface wlan0</span>
        </div>
        
        <div class="detail-tree-root">
            <span class="detail-expander">▼</span>
            <span class="detail-label">Radiotap Header v0, Length 24</span> 
        </div>
        
        <div class="detail-tree-root">
            <span class="detail-expander">▼</span>
            <span class="detail-label">IEEE 802.11 Beacon frame, Flags: ........</span>
            <div style="margin-left: 20px; color: #aaa;">
                <div>Type/Subtype: Beacon frame (8)</div>
                <div>Frame Control Field: 0x8000</div>
                <div>Duration: 0 microseconds</div>
                <div>Destination address: ff:ff:ff:ff:ff:ff (Broadcast)</div>
                <div>Source address: ${net.bssid}</div>
                <div>BSS Id: ${net.bssid}</div>
            </div>
        </div>
        
        <div class="detail-tree-root">
            <span class="detail-expander">▼</span>
            <span class="detail-label">IEEE 802.11 Wireless LAN</span>
             <div style="margin-left: 20px; color: #aaa;">
                <div><strong>Tagged parameters (SSID: ${net.ssid})</strong></div>
                <div>Tag: SSID parameter set: ${net.ssid}</div>
                <div>Tag: Supported Rates</div>
                <div>Tag: DS Parameter set: Current Channel: ${net.channel}</div>
                <div><strong>Signal Strength: ${net.signal_strength} dBm</strong></div>
                <div>Encryption: ${net.encryption}</div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// Signal Graph (Replacing Bytes pane)
function initChart() {
    const ctx = document.getElementById('signal-chart').getContext('2d');
    signalChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Signal Strength (dBm)',
                data: [],
                backgroundColor: '#3a7ca5',
                borderColor: '#66bb6a',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    suggestedMin: -100,
                    suggestedMax: -30,
                    grid: { color: '#444' }
                },
                x: {
                    ticks: { display: false }, // Hide labels for clean look
                    grid: { display: false }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function updateChart(networks) {
    if (!signalChart) return;

    // Sort by signal
    const sorted = [...networks].sort((a, b) => b.signal_strength - a.signal_strength);

    signalChart.data.labels = sorted.map(n => n.ssid.substring(0, 10));
    signalChart.data.datasets[0].data = sorted.map(n => n.signal_strength);
    signalChart.update('none'); // Update without animation for "live" feel
}

// Filter Simulation
document.getElementById('wireshark-filter').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const val = e.target.value.toLowerCase();
        // Implement simple client-side filter
        const filtered = currentNetworks.filter(n =>
            n.ssid.toLowerCase().includes(val) ||
            n.encryption.toLowerCase().includes(val)
        );
        renderTable(filtered);
    }
});
