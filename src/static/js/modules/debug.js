/**
 * [DEBUG]: Admin Debug Panel for Hackathon Demo
 * Hidden panel accessible via keyboard shortcut: Ctrl+Shift+D
 */

const ADMIN_KEY = 'hackathon2026';
const API_BASE = '';

// Panel HTML
const debugPanelHTML = `
<div id="debug-panel" style="
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.95);
    z-index: 9999;
    padding: 20px;
    overflow: auto;
    font-family: monospace;
    color: #00ff00;
">
    <div style="max-width: 600px; margin: 0 auto;">
        <h2 style="color: #0088cc; margin-bottom: 20px;">
            🛠️ TG-ADMC Debug Panel
            <button onclick="closeDebugPanel()" style="float:right; background:#ff4444; border:none; color:white; padding:5px 10px; cursor:pointer;">✕ Close</button>
        </h2>
        
        <div id="debug-status" style="background: #1a1a1a; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <strong>System Status:</strong> <span id="sys-status">Loading...</span>
        </div>
        
        <div style="display: grid; gap: 10px;">
            <button onclick="debugAction('health')" class="debug-btn">📊 Health Check</button>
            <button onclick="debugAction('info')" class="debug-btn">📈 System Info</button>
            <button onclick="debugAction('reset')" class="debug-btn" style="background: #ff8800;">🔄 Reset Deals (Keep Users/Channels)</button>
            <button onclick="debugAction('purge')" class="debug-btn" style="background: #ff4444;">🗑️ PURGE ALL (Complete Reset)</button>
            <button onclick="debugAction('cache')" class="debug-btn" style="background: #8844ff;">🧹 Clear Browser Cache</button>
            <button onclick="debugAction('wallet')" class="debug-btn" style="background: #0088cc;">💎 Disconnect Wallet</button>
        </div>
        
        <div id="debug-output" style="
            background: #0a0a0a;
            padding: 15px;
            margin-top: 15px;
            border-radius: 8px;
            white-space: pre-wrap;
            max-height: 300px;
            overflow: auto;
        ">Ready for commands...</div>
        
        <div style="margin-top: 20px; font-size: 12px; color: #666;">
            <strong>Keyboard Shortcuts:</strong><br>
            Ctrl+Shift+D - Toggle this panel<br>
            ESC - Close panel
        </div>
    </div>
</div>
<style>
.debug-btn {
    background: #2a2a2a;
    border: 1px solid #444;
    color: #fff;
    padding: 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
}
.debug-btn:hover {
    background: #3a3a3a;
    transform: scale(1.02);
}
</style>
`;

// Inject panel into DOM
function initDebugPanel() {
    document.body.insertAdjacentHTML('beforeend', debugPanelHTML);
    console.log('[DEBUG] Admin panel initialized. Press Ctrl+Shift+D to open.');
}

// Toggle visibility
function toggleDebugPanel() {
    const panel = document.getElementById('debug-panel');
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        if (panel.style.display === 'block') {
            debugAction('health');
        }
    }
}

function closeDebugPanel() {
    const panel = document.getElementById('debug-panel');
    if (panel) panel.style.display = 'none';
}

// Make functions global
window.toggleDebugPanel = toggleDebugPanel;
window.closeDebugPanel = closeDebugPanel;

// Action handler
async function debugAction(action) {
    const output = document.getElementById('debug-output');
    output.textContent = `Executing: ${action}...\n`;
    
    try {
        switch (action) {
            case 'health':
                const health = await fetch(`${API_BASE}/admin/health`).then(r => r.json());
                output.textContent = `✅ HEALTH CHECK\n${JSON.stringify(health, null, 2)}`;
                document.getElementById('sys-status').textContent = health.status;
                break;
                
            case 'info':
                const info = await fetch(`${API_BASE}/admin/info`).then(r => r.json());
                output.textContent = `📊 SYSTEM INFO\n${JSON.stringify(info, null, 2)}`;
                break;
                
            case 'reset':
                if (!confirm('Reset all deals? Users and channels will be preserved.')) return;
                const reset = await fetch(`${API_BASE}/admin/reset-db?key=${ADMIN_KEY}`, { method: 'POST' }).then(r => r.json());
                output.textContent = `🔄 RESET RESULT\n${JSON.stringify(reset, null, 2)}`;
                break;
                
            case 'purge':
                if (!confirm('⚠️ DANGER: This will delete ALL data (users, channels, deals). Continue?')) return;
                const purge = await fetch(`${API_BASE}/admin/purge-all?key=${ADMIN_KEY}`, { method: 'POST' }).then(r => r.json());
                output.textContent = `🗑️ PURGE RESULT\n${JSON.stringify(purge, null, 2)}`;
                break;
                
            case 'cache':
                // Clear localStorage
                localStorage.clear();
                // Clear sessionStorage
                sessionStorage.clear();
                output.textContent = `🧹 CACHE CLEARED\n- LocalStorage: cleared\n- SessionStorage: cleared\n\nReloading page...`;
                setTimeout(() => location.reload(true), 1000);
                break;
                
            case 'wallet':
                // Disconnect wallet via TON Connect
                if (typeof TON_CONNECT_UI !== 'undefined') {
                    const tc = document.querySelector('tc-root');
                    if (tc && tc._tonConnectUI) {
                        await tc._tonConnectUI.disconnect();
                    }
                }
                localStorage.removeItem('ton-connect-storage_bridge-connection');
                localStorage.removeItem('ton-connect-ui_wallet-info');
                output.textContent = `💎 WALLET DISCONNECTED\n- TON Connect session cleared\n- Reload to reconnect`;
                break;
                
            default:
                output.textContent = 'Unknown action';
        }
    } catch (e) {
        output.textContent = `❌ ERROR\n${e.message}`;
    }
}

window.debugAction = debugAction;

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+Shift+D - Toggle debug panel
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        toggleDebugPanel();
    }
    // ESC - Close panel
    if (e.key === 'Escape') {
        closeDebugPanel();
    }
});

// Auto-init when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDebugPanel);
} else {
    initDebugPanel();
}

export { initDebugPanel, toggleDebugPanel };

