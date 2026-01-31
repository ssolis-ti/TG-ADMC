/**
 * [MAIN]: Application Entry Point
 */
import { getTg, getUserId, forceSetId, safeAlert } from './auth.js?v=8';
import { UI, ROLES } from './config.js?v=8';
import * as Controllers from './controllers.js?v=8';
import { initWallet, isWalletConnected, requireWallet, getWalletAddress } from './wallet.js?v=8';
import { saveRole } from './api.js?v=8';
import './debug.js?v=8'; // [DEMO] Hidden debug panel (Ctrl+Shift+D)

const tg = getTg();
tg.expand();

// State
let currentRole = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initWallet();
    
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
