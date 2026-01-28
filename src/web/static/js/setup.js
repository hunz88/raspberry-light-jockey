// Light Jockey Setup Script

let discoveredLights = [];
let identifyingLights = new Set();

// DOM Elements
const discoverBtn = document.getElementById('discoverBtn');
const saveBtn = document.getElementById('saveBtn');
const testAllBtn = document.getElementById('testAllBtn');
const offBtn = document.getElementById('offBtn');
const statusMessage = document.getElementById('statusMessage');
const lightsContainer = document.getElementById('lightsContainer');

// Event Listeners
discoverBtn.addEventListener('click', discoverLights);
saveBtn.addEventListener('click', saveConfiguration);
testAllBtn.addEventListener('click', testAllLights);
offBtn.addEventListener('click', turnOffAll);

// Discover lights on network
async function discoverLights() {
    showStatus('Ricerca luci in corso...', 'info');
    discoverBtn.disabled = true;
    discoverBtn.textContent = '🔍 Ricerca...';

    try {
        const response = await fetch('/api/discover', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            discoveredLights = data.lights;
            showStatus(`✅ Trovate ${data.count} luci!`, 'success');
            renderLights();
            enableButtons();
        } else {
            showStatus(`❌ Errore: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Errore di rete: ${error.message}`, 'error');
    } finally {
        discoverBtn.disabled = false;
        discoverBtn.textContent = '🔍 Scopri Luci sulla Rete';
    }
}

// Render lights list
function renderLights() {
    if (discoveredLights.length === 0) {
        lightsContainer.innerHTML = '<p style="text-align: center; color: #6c757d;">Nessuna luce trovata. Clicca "Scopri Luci" per iniziare.</p>';
        return;
    }

    lightsContainer.innerHTML = `
        <h2 style="margin-bottom: 20px; color: #495057;">
            💡 Luci Trovate: ${discoveredLights.length}
        </h2>
        ${discoveredLights.map((light, index) => renderLightCard(light, index)).join('')}
    `;

    // Attach event listeners
    discoveredLights.forEach((light, index) => {
        const card = document.getElementById(`light-${index}`);

        // Identify button
        const identifyBtn = card.querySelector('.identify-btn');
        identifyBtn.addEventListener('click', () => identifyLight(light.mac, index));

        // Name input
        const nameInput = card.querySelector('.name-input');
        nameInput.addEventListener('change', (e) => {
            discoveredLights[index].name = e.target.value;
        });

        // Zone select
        const zoneSelect = card.querySelector('.zone-select');
        zoneSelect.addEventListener('change', (e) => {
            discoveredLights[index].zone = e.target.value;
        });

        // Position input
        const positionInput = card.querySelector('.position-input');
        positionInput.addEventListener('change', (e) => {
            discoveredLights[index].position = parseInt(e.target.value);
        });
    });
}

// Render single light card
function renderLightCard(light, index) {
    const zoneColor = ZONES.find(z => z.id === light.zone)?.color || '#6c757d';

    return `
        <div id="light-${index}" class="light-card" style="border-left: 4px solid ${zoneColor}">
            <div class="light-header">
                <div class="light-info">
                    <h3>💡 ${light.name}</h3>
                    <div class="light-meta">
                        <strong>IP:</strong> ${light.ip} |
                        <strong>MAC:</strong> ${light.mac}
                    </div>
                </div>
                <button class="identify-btn">
                    🔴 Identifica (5s)
                </button>
            </div>
            <div class="light-config">
                <div class="form-group">
                    <label>Nome</label>
                    <input type="text"
                           class="name-input"
                           value="${light.name}"
                           placeholder="es: DJ Console - Sinistra 1">
                </div>
                <div class="form-group">
                    <label>Zona</label>
                    <select class="zone-select">
                        <option value="unassigned" ${light.zone === 'unassigned' ? 'selected' : ''}>
                            Non Assegnato
                        </option>
                        ${ZONES.map(zone => `
                            <option value="${zone.id}" ${light.zone === zone.id ? 'selected' : ''}>
                                ${zone.name}
                            </option>
                        `).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>Posizione</label>
                    <input type="number"
                           class="position-input"
                           value="${light.position >= 0 ? light.position : index}"
                           min="0"
                           max="100">
                </div>
            </div>
        </div>
    `;
}

// Identify a light (flash RED for 5 seconds)
async function identifyLight(mac, index) {
    if (identifyingLights.has(mac)) {
        showStatus('⚠️ Questa luce sta già lampeggiando', 'info');
        return;
    }

    const card = document.getElementById(`light-${index}`);
    const identifyBtn = card.querySelector('.identify-btn');

    identifyingLights.add(mac);
    card.classList.add('identifying');
    identifyBtn.disabled = true;
    identifyBtn.textContent = '🔴 Lampeggiando...';

    showStatus(`🔴 Identificazione luce ${mac.slice(-8)}... Guarda quale lampeggia in ROSSO!`, 'info');

    try {
        const response = await fetch('/api/lights/identify', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({light: mac, duration: 5})
        });

        const data = await response.json();

        if (data.success) {
            showStatus(`✅ Luce identificata!`, 'success');
        } else {
            showStatus(`❌ Errore: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Errore: ${error.message}`, 'error');
    } finally {
        // Wait for identify to finish (5 seconds + buffer)
        setTimeout(() => {
            identifyingLights.delete(mac);
            card.classList.remove('identifying');
            identifyBtn.disabled = false;
            identifyBtn.textContent = '🔴 Identifica (5s)';
        }, 5500);
    }
}

// Save configuration
async function saveConfiguration() {
    // Validate: all lights should have a zone
    const unassigned = discoveredLights.filter(l => l.zone === 'unassigned');

    if (unassigned.length > 0) {
        const confirm = window.confirm(
            `${unassigned.length} luci non sono assegnate a una zona.\n` +
            `Verranno salvate solo le luci assegnate. Continuare?`
        );

        if (!confirm) return;
    }

    showStatus('💾 Salvataggio configurazione...', 'info');
    saveBtn.disabled = true;

    // Update lights via API
    try {
        for (const light of discoveredLights) {
            if (light.zone !== 'unassigned') {
                await fetch('/api/lights/assign', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        mac: light.mac,
                        name: light.name,
                        zone: light.zone,
                        position: light.position
                    })
                });
            }
        }

        // Save to config
        const response = await fetch('/api/config/save', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showStatus(
                `✅ Configurazione salvata! ${data.count} luci configurate.\n` +
                `Ora puoi avviare il Light Jockey con: python3 main.py`,
                'success'
            );
        } else {
            showStatus(`❌ Errore nel salvataggio: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Errore: ${error.message}`, 'error');
    } finally {
        saveBtn.disabled = false;
    }
}

// Test all lights with white color
async function testAllLights() {
    showStatus('🎨 Test colore bianco su tutte le luci...', 'info');

    try {
        const response = await fetch('/api/test-color', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({r: 255, g: 255, b: 255})
        });

        const data = await response.json();

        if (data.success) {
            showStatus('✅ Tutte le luci impostate a bianco!', 'success');
        } else {
            showStatus(`❌ Errore: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Errore: ${error.message}`, 'error');
    }
}

// Turn off all lights
async function turnOffAll() {
    showStatus('⚫ Spegnimento luci...', 'info');

    try {
        const response = await fetch('/api/lights/off', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showStatus('✅ Luci spente!', 'success');
        } else {
            showStatus(`❌ Errore: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Errore: ${error.message}`, 'error');
    }
}

// Show status message
function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;

    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            statusMessage.className = 'status-message';
        }, 5000);
    }
}

// Enable buttons after discovery
function enableButtons() {
    saveBtn.disabled = false;
    testAllBtn.disabled = false;
    offBtn.disabled = false;
}

// Initial state
showStatus('Clicca "Scopri Luci" per iniziare la configurazione', 'info');
