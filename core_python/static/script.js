document.addEventListener('DOMContentLoaded', function() {
    const socket = io();

    // --- Chart Initialization (No changes here) ---
    const netTrafficLayout = {
        xaxis: { title: 'Time' },
        yaxis: { title: 'Bytes/sec' },
        margin: { t: 30, l: 50, r: 30, b: 40 },
        paper_bgcolor: '#16213e',
        plot_bgcolor: '#16213e',
        font: { color: '#e0e0e0' }
    };
    Plotly.newPlot('net-traffic-chart', [
        { y: [], x: [], type: 'scatter', mode: 'lines', name: 'Sent' },
        { y: [], x: [], type: 'scatter', mode: 'lines', name: 'Received' }
    ], netTrafficLayout);

    const alertPieLayout = {
        title: 'Alert Distribution',
        paper_bgcolor: '#16213e',
        plot_bgcolor: '#16213e',
        font: { color: '#e0e0e0' }
    };
    Plotly.newPlot('alert-pie-chart', [
        { values: [], labels: [], type: 'pie' }
    ], alertPieLayout);

    // --- REMOVED: Client-side rate calculation variables are no longer needed ---
    // let lastNetSent = 0;
    // let lastNetRecv = 0;
    // let lastTimestamp = Date.now();

    // --- WebSocket Event Handlers ---
    socket.on('connect', () => {
        console.log('Connected to server');
    });

    // --- MODIFIED: Listen for the new 'system_metrics_update' event ---
    socket.on('system_metrics_update', (metrics) => {
        // This event now only carries system data
        updateHostMetrics(metrics); 
    });

    // --- NEW: Listen for the pre-calculated network rate from the server ---
    socket.on('network_traffic_update', (rateData) => {
        // rateData is an object like { sent: 1234.5, received: 0 }
        updateNetworkChart(rateData.sent, rateData.received);
    });

    socket.on('new_alert', (alert) => {
        addAlertToLog(alert);
        updateAlertPieChart(alert.type);
    });

    // --- UI Update Functions ---
    // Minor key changes to match Python agent data
    function updateHostMetrics(metrics) {
        document.getElementById('cpu-usage').textContent = `${metrics.cpu_usage.toFixed(1)}%`;
        document.getElementById('mem-usage').textContent = `${metrics.memory_usage.toFixed(1)}%`;
        document.getElementById('cpu-load').textContent = metrics.cpu_load.toFixed(2);

        const processTableBody = document.getElementById('processes-table-body');
        processTableBody.innerHTML = ''; // Clear old data
        if (metrics.top_processes) {
            metrics.top_processes.forEach(p => {
                let row = processTableBody.insertRow();
                row.innerHTML = `<td>${p.pid}</td><td>${p.name}</td><td>${p.cpu_percent.toFixed(1)}</td><td>${p.memory_percent.toFixed(1)}</td>`;
            });
        }
    }

    // This function now receives the final rate directly
    function updateNetworkChart(sentRate, recvRate) {
        const currentTime = new Date().toLocaleTimeString();
        Plotly.extendTraces('net-traffic-chart', {
            x: [[currentTime], [currentTime]],
            y: [[sentRate], [recvRate]]
        }, [0, 1], 20); // Keep 20 data points on the graph
    }
    
    // Unchanged functions below
    function addAlertToLog(alert) {
        const alertTable = document.getElementById('alert-log').getElementsByTagName('tbody')[0];
        let newRow = alertTable.insertRow(0);
        newRow.className = `severity-${alert.severity.toLowerCase()}`;
        newRow.innerHTML = `<td>${new Date().toLocaleTimeString()}</td><td>${alert.severity}</td><td>${alert.type}</td><td>${alert.description}</td>`;
        if (alertTable.rows.length > 10) {
            alertTable.deleteRow(10);
        }
    }

    let alertCounts = {};
    function updateAlertPieChart(alertType) {
        alertCounts[alertType] = (alertCounts[alertType] || 0) + 1;
        const data = [{
            values: Object.values(alertCounts),
            labels: Object.keys(alertCounts),
            type: 'pie'
        }];
        Plotly.react('alert-pie-chart', data, alertPieLayout);
    }
});