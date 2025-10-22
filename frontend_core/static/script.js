document.addEventListener('DOMContentLoaded', function() {
    const socket = io();

    // --- Chart Initialization ---
    const netTrafficLayout = {
        xaxis: { title: 'Time' },
        yaxis: { title: 'Bytes/sec' },
        margin: { t: 30, l: 50, r: 30, b: 40 },
        paper_bgcolor: '#16213e',
        plot_bgcolor: '#16213e',
        font: { color: '#e0e0e0' }
    };
    Plotly.newPlot('net-traffic-chart', [{ y:, type: 'scatter', name: 'Sent' }, { y:, type: 'scatter', name: 'Received' }], netTrafficLayout);

    const alertPieLayout = {
        title: 'Alert Distribution',
        paper_bgcolor: '#16213e',
        plot_bgcolor: '#16213e',
        font: { color: '#e0e0e0' }
    };
    Plotly.newPlot('alert-pie-chart', [{ values:, labels:, type: 'pie' }], alertPieLayout);

    let lastNetSent = 0;
    let lastNetRecv = 0;
    let lastTimestamp = Date.now();

    // --- WebSocket Event Handlers ---
    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('update_metrics', (metrics) => {
        if (metrics.type === 'host_metrics') {
            updateHostMetrics(metrics.data);
        } else if (metrics.type === 'network_flow') {
            // For network charts, we calculate rate of change
            const now = Date.now();
            const interval = (now - lastTimestamp) / 1000;
            const sentRate = (metrics.data.net_bytes_sent - lastNetSent) / interval;
            const recvRate = (metrics.data.net_bytes_recv - lastNetRecv) / interval;
            
            lastNetSent = metrics.data.net_bytes_sent;
            lastNetRecv = metrics.data.net_bytes_recv;
            lastTimestamp = now;

            updateNetworkChart(sentRate, recvRate);
        }
    });

    socket.on('new_alert', (alert) => {
        addAlertToLog(alert);
        updateAlertPieChart(alert.type);
    });

    // --- UI Update Functions ---
    function updateHostMetrics(data) {
        document.getElementById('cpu-usage').textContent = `${data.cpu_usage_percent.toFixed(1)}%`;
        document.getElementById('mem-usage').textContent = `${data.memory_usage_percent.toFixed(1)}%`;
        document.getElementById('cpu-load').textContent = data.cpu_load_avg_1m.toFixed(2);

        const processTable = document.getElementById('process-list').getElementsByTagName('tbody');
        processTable.innerHTML = ''; // Clear old data
        data.top_processes.forEach(p => {
            let row = processTable.insertRow();
            row.innerHTML = `<td>${p.pid}</td><td>${p.name}</td><td>${p.cpu_percent.toFixed(1)}</td><td>${p.memory_percent.toFixed(1)}</td>`;
        });
    }

    function updateNetworkChart(sentRate, recvRate) {
        Plotly.extendTraces('net-traffic-chart', { y:,] }, , 20); // Keep 20 points
    }

    function addAlertToLog(alert) {
        const alertTable = document.getElementById('alert-log').getElementsByTagName('tbody');
        let newRow = alertTable.insertRow(0); // Add to top
        newRow.className = `severity-${alert.severity.toLowerCase()}`;
        newRow.innerHTML = `<td>${new Date().toLocaleTimeString()}</td><td>${alert.severity}</td><td>${alert.type}</td><td>${alert.description}</td>`;
        if (alertTable.rows.length > 10) {
            alertTable.deleteRow(10); // Keep log size manageable
        }
    }

    let alertCounts = {};
    function updateAlertPieChart(alertType) {
        alertCounts = (alertCounts |

| 0) + 1;
        const data = [{
            values: Object.values(alertCounts),
            labels: Object.keys(alertCounts),
            type: 'pie'
        }];
        Plotly.react('alert-pie-chart', data, alertPieLayout);
    }
});