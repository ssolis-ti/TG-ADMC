/**
 * [WALLET]: TON Connect Integration
 * Handles wallet connection and blockchain transactions.
 */
import { getTg, safeAlert, getUserId } from './auth.js?v=30';
import { ESCROW_ADDRESS } from './config.js?v=30';
import { saveWallet } from './api.js?v=30';

const tg = getTg();
let tonConnectUI = null;

export function initWallet() {
    console.log("[WALLET] Initializing TON Connect...");
    
    try {
        // Check if TON Connect library loaded
        if (typeof TON_CONNECT_UI === 'undefined') {
            const err = "TON_CONNECT_UI library not loaded!";
            console.error("[WALLET]", err);
            safeAlert("⚠️ Critical Error: " + err);
            return;
        }
        console.log("[WALLET] Library loaded ✓");
        
        const btnRoot = document.getElementById('ton-connect-btn');
        if (!btnRoot) {
            const err = "Button root element not found!";
            console.error("[WALLET]", err);
            safeAlert("⚠️ Critical Error: " + err);
            return;
        }
        console.log("[WALLET] Button root found ✓");

        // [AUDIT]: Verified manifest URL is accessible via HTTPS
        // Required for correct deep linking in Tonkeeper
        const manifestUrl = `${window.location.origin}/static/tonconnect-manifest.json`;
        console.log("[WALLET] Manifest URL:", manifestUrl);

        try {
            tonConnectUI = new TON_CONNECT_UI.TonConnectUI({
                manifestUrl: manifestUrl,
                buttonRootId: 'ton-connect-btn',
                
                // [TG-COMPAT]: Critical configuration for Telegram WebApps
                // Source: https://docs.tonconsole.com/ & TON Connect Best Practices
                uiOptions: {
                    twaReturnUrl: 'https://t.me/AdTGram_Bot/app',
                    actionsConfiguration: {
                        // Allow wallet app to handle the redirect
                        returnStrategy: 'tg://resolve', 
                        // REMOVED: skipRedirectToWallet was blocking transaction requests
                        // Now Tonkeeper should receive the transaction request
                    }
                },
                
                // [CONNECTIVITY]: Wallet Prioritization
                // Explicitly listing supported wallets helps with "Brave" interference
                walletsListConfiguration: {
                    includeWallets: [
                        {
                            appName: "tonkeeper",
                            name: "Tonkeeper",
                            imageUrl: "https://tonkeeper.com/assets/tonkeeper.png",
                            aboutUrl: "https://tonkeeper.com",
                            universalLink: "https://app.tonkeeper.com/ton-connect",
                            bridgeUrl: "https://bridge.tonapi.io/bridge",
                            platforms: ["ios", "android", "chrome", "firefox"]
                        }
                    ]
                }
            });

            // [RESILIENCE]: Watch for connection stalls
            // If connection takes too long, we might be blocked by Brave Shields or Network
            setTimeout(() => {
                 if (tonConnectUI && tonConnectUI.wallet && !tonConnectUI.connected) {
                     console.warn("[WALLET] Connection taking longer than expected. Check Brave Shields?");
                 }
            }, 10000);

            btnRoot.style.display = 'block';
            console.log("[WALLET] TonConnectUI initialized ✓ (TG-Compat Mode + Hardened Config)");

        } catch (initErr) {
            console.error("[WALLET] Init Failed:", initErr);
            safeAlert("Connection Error: " + initErr.message); 
            return;
        }

        // [TG-COMPAT]: Manual Button Logic
        const manualBtn = document.getElementById('manual-connect-btn');
        const manualContainer = document.getElementById('manual-connect-container');
        
        if (manualBtn) {
            manualBtn.addEventListener('click', () => {
                console.log("[WALLET] Manual Connect Clicked");
                tonConnectUI.modal.open();
            });
        }

        // Status change listener
        tonConnectUI.onStatusChange(async (wallet) => {
            if (wallet) {
                console.log("[WALLET] Connected:", wallet.account.address);
                safeAlert("✅ Wallet connected!");
                if (manualContainer) manualContainer.style.display = 'none';
                
                // [ESCROW FIX]: Save wallet address to backend for payout
                try {
                    const userId = getUserId();
                    if (userId) {
                        const res = await saveWallet(userId, wallet.account.address);
                        console.log("[WALLET] Saved to backend:", res);
                    }
                } catch (e) {
                    console.error("[WALLET] Failed to save wallet:", e);
                }
            } else {
                console.log("[WALLET] Disconnected");
                if (manualContainer) manualContainer.style.display = 'block';
            }
        });

    } catch (e) {
        console.error("[WALLET] Init Error:", e);
        safeAlert("Wallet Init Error: " + e.message);
    }
}


// [GATE]: Check if wallet is connected
export function isWalletConnected() {
    const connected = tonConnectUI && tonConnectUI.wallet ? true : false;
    console.log("[WALLET GATE] isWalletConnected:", connected, "tonConnectUI:", !!tonConnectUI, "wallet:", !!tonConnectUI?.wallet);
    return connected;
}

// [IDENTITY]: Get connected wallet address
export function getWalletAddress() {
    if (tonConnectUI && tonConnectUI.wallet) {
        return tonConnectUI.wallet.account.address;
    }
    return null;
}

// [GATE]: Force wallet connection modal - BLOCKING
export function requireWallet() {
    console.log("[WALLET GATE] requireWallet called");
    
    // [CRITICAL CHECK]: If UI is not initialized, we cannot proceed
    if (!tonConnectUI) {
        safeAlert("⚠️ Wallet System Not Initialized! Refresh page.");
        return false;
    }

    const connected = isWalletConnected();
    
    if (!connected) {
        console.log("[WALLET GATE] NOT CONNECTED - Opening modal, blocking entry");
        try {
            tonConnectUI.modal.open();
        } catch (e) {
            console.error("[WALLET GATE] Failed to open modal:", e);
            safeAlert("Error opening wallet modal: " + e.message);
        }
        return false;
    }
    
    console.log("[WALLET GATE] CONNECTED - Allowing entry");
    return true;
}



/**
 * Sends TON to a destination address.
 * @param {number} amountTon - Amount in TON (e.g., 1.5)
 * @param {string} dealId - [AUDIT]: Required for Memo/Comment
 * @returns {Promise<string>} - The transaction BOC (Hash)
 */
export async function sendPayment(amountTon, dealId) {
    console.log("[PAYMENT] Starting payment...", { amountTon, dealId });
    
    if (!tonConnectUI || !tonConnectUI.wallet) {
        console.error("[PAYMENT] Wallet not connected!");
        safeAlert("Please connect your TON wallet first!");
        tonConnectUI.modal.open();
        throw new Error("Wallet not connected");
    }

    const nanoAmount = Math.floor(amountTon * 1000000000).toString();
    console.log("[PAYMENT] Amount in nano:", nanoAmount);
    
    // [TESTNET WALLET]: Escrow address
    const escrowAddress = ESCROW_ADDRESS;
    console.log("[PAYMENT] Sending to:", escrowAddress);

    const transaction = {
        validUntil: Math.floor(Date.now() / 1000) + 300, // 5 min
        messages: [
            {
                address: escrowAddress,
                amount: nanoAmount
                // payload omitted for MVP simplicity
            }
        ]
    };
    
    console.log("[PAYMENT] Transaction object:", JSON.stringify(transaction));

    try {
        console.log("[PAYMENT] Sending transaction via TON Connect...");
        const result = await tonConnectUI.sendTransaction(transaction);
        console.log("[PAYMENT] Success! BOC:", result.boc);
        return result.boc;
    } catch (e) {
        console.error("[PAYMENT] Transaction failed:", e);
        // More specific error message
        if (e.message && e.message.includes('cancel')) {
            throw new Error("Transaction was cancelled by user");
        }
        throw e;
    }
}


