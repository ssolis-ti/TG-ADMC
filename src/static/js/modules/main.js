/**
 * [MAIN]: Application Entry Point
 */
import { getTg, getUserId, forceSetId, safeAlert } from './auth.js?v=30';
import { UI, ROLES } from './config.js?v=30';
import * as Controllers from './controllers.js?v=30';
import { initWallet, isWalletConnected, requireWallet, getWalletAddress } from './wallet.js?v=30';
import { saveRole } from './api.js?v=30';
import './debug.js?v=30'; // [DEMO] Hidden debug panel (Ctrl+Shift+D)

const tg = getTg();
tg.expand();

// State
let currentRole = null;

// Initialization
// Initialization
document.addEventListener('DOMContentLoaded', () => {
    // [DEBUG]: Global Error Handler for Mobile
    window.onerror = function(msg, url, line, col, error) {
        alert("JS ERROR: " + msg + " @ " + line + ":" + col);
    };

    initTabs();
    
    // [DEBUG]: Status Indicator
    const debugStatus = document.createElement('div');
    debugStatus.id = "debug-status";
    debugStatus.style.cssText = "position:fixed; bottom:25px; right:5px; font-size:10px; color:#0f0; background:#000; padding:2px; z-index:9999;";
    debugStatus.innerText = "Status: Init Wallet...";
    document.body.appendChild(debugStatus);

    try {
        initWallet();
        debugStatus.innerText = "Status: Wallet OK";
    } catch (e) {
        debugStatus.innerText = "Status: Wallet FAIL";
        debugStatus.style.color = "#f00";
        alert("⚠️ CRITICAL: Wallet Init Failed!\n\n" + e.message);
    }
    
    // [DEBUG]: Show User ID in UI for verification
    const debugId = getUserId();
    const idDisplay = document.createElement('div');
    idDisplay.style.cssText = "position:fixed; bottom:5px; right:5px; font-size:10px; color:#ccc; opacity:0.5; pointer-events:none; z-index:9999;";
    idDisplay.innerText = "ID: " + debugId;
    document.body.appendChild(idDisplay);
    
    // Bind Role Switchers
    window.switchMode = switchMode;
    window.forceSetId = forceSetId;
});

async function switchMode(role) {
    // [WALLET GATE]: Must connect wallet before selecting role
    if (!requireWallet()) {
        safeAlert("🔐 Please connect your TON wallet first to continue!");
        return;
    }
    
    const walletAddr = getWalletAddress();
    console.log("[MAIN] Role selected:", role, "Wallet:", walletAddr);
    
    // [ROLE FIX]: Save role to backend
    try {
        const userId = getUserId();
        if (userId) {
            const res = await saveRole(userId, role);
            console.log("[MAIN] Role saved to backend:", res);
        }
    } catch (e) {
        console.error("[MAIN] Failed to save role:", e);
    }
    
    if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
    currentRole = role;

    document.getElementById(UI.VIEWS.DASHBOARD).style.display = 'none';
    document.querySelector(`.${UI.VIEWS.TABS}`).style.display = 'flex';
    document.getElementById(UI.VIEWS.CONTENT).style.display = 'block';

    const tabLeft = document.getElementById(UI.TABS.LEFT);
    const tabRight = document.getElementById(UI.TABS.RIGHT);

    if (role === ROLES.ADVERTISER) {
        tabLeft.innerText = "Marketplace";
        tabRight.innerText = "Sent Offers";
        activateTab('left');
    } else {
        tabLeft.innerText = "My Channels";
        tabRight.innerText = "Inbox";
        activateTab('right');
    }
}

function initTabs() {
    document.getElementById(UI.TABS.LEFT).addEventListener('click', () => activateTab('left'));
    document.getElementById(UI.TABS.RIGHT).addEventListener('click', () => activateTab('right'));
}

function activateTab(side) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById(`tab-${side}`).classList.add('active');

    const container = document.getElementById(UI.VIEWS.CONTENT);
    
    if (currentRole === ROLES.ADVERTISER) {
        if (side === 'left') Controllers.loadChannels(container);
        else Controllers.loadUserDeals(container, currentRole);
    } else {
        if (side === 'left') Controllers.loadMyChannels(container);
        else Controllers.loadUserDeals(container, currentRole);
    }
}

// Wallet initialized via wallet.js module

