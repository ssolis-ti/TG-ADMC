/**
 * [CONTROLLERS]: Business Logic
 */
import * as API from './api.js?v=21';
import * as UI from './ui.js?v=21';
import * as Wallet from './wallet.js?v=21';
import { getUserId, getTg, safeAlert, safeMainButton } from './auth.js?v=21';
import { ROLES, ESCROW_ADDRESS } from './config.js?v=21';

const tg = getTg();

// [SAFE]: Progress wrappers
const showProgress = () => safeMainButton('showProgress');
const hideProgress = () => safeMainButton('hideProgress');

// --- Action Handlers ---
// [TACTICS]: User Interactions that Trigger State Changes.

export async function handleEditPrice(channelId, currentPrice) {
    /**
     * [ACTION]: El Negociador (Set Price).
     * [FLOW]: UI Prompt -> API PUT -> DB Update -> Refresh UI.
     * [VALIDATION]: Min 0.1 TON strict.
     */
    const newPrice = prompt(`Enter new asking price (TON):`, currentPrice);
    if (!newPrice || isNaN(newPrice)) return;
    
    if (parseFloat(newPrice) < 0.1) {
        safeAlert("Minimum price is 0.1 TON");
        return;
    }

    try {
        showProgress();
        const res = await API.updateChannelPrice(channelId, getUserId(), parseFloat(newPrice));
        hideProgress();
        
        if (res.ok) {
            safeAlert("Price Updated!");
            loadMyChannels(document.getElementById('dynamic-content')); 
        } else {
            safeAlert("Failed to update price.");
        }
    } catch (e) {
        hideProgress();
        safeAlert("Error updating price.");
    }
}

export async function handleBuyAd(channel) {
    /**
     * [ACTION]: Create Campaign Offer.
     * [FLOW]: Wallet Gate -> Brief Input -> Amount Input -> Create Deal -> Show Next Steps.
     * [GROWTH]: Clear CTAs, celebrate success, guide next action.
     */
    
    // [GATE 1]: Require wallet connection
    if (!Wallet.requireWallet()) return;
    
    if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
    
    // [UX]: Open Campaign Modal
    const modal = document.getElementById('campaign-modal');
    const contentInput = document.getElementById('campaign-content');
    const amountInput = document.getElementById('campaign-amount');
    const submitBtn = document.getElementById('campaign-submit-btn');
    
    // Reset and Prefill
    modal.style.display = 'flex';
    // [UX]: Pre-filled template for easy testing
    contentInput.value = `<b>🚀 MEGA OFFER: Premium Ads!</b>\n\nScale your project with our high-converting traffic sources.\n\n<i>✨ Features:</i>\n• High Retention\n• Verified Channels\n• Instant Start\n\n<a href="https://t.me/AdTGram_Bot">👉 START NOW</a>`;
    amountInput.value = channel.price_post;
    


    // One-time event handler for this specific click
    submitBtn.onclick = async () => {
        const brief = contentInput.value;
        const amount = parseFloat(amountInput.value);
        
        if (!brief || brief.trim() === "") {
            safeAlert("❌ Content is required.");
            return;
        }
        if (!amount || isNaN(amount)) {
            safeAlert("❌ Valid amount required.");
            return;
        }
        
        // Close modal
        modal.style.display = 'none';

        try {
            showProgress();
            
            // [STEP 1]: Create Deal Record First
            const res = await API.createDeal({
                advertiser_id: getUserId(),
                channel_id: channel.id,
                brief: brief.trim(),
                amount: amount
            });
            const data = await res.json();
            
            if (data.status !== 'created') {
                hideProgress();
                safeAlert("❌ Failed to create deal record.");
                return;
            }
            
            const dealId = data.deal_id;
            
            // [STEP 2]: Trigger Payment Immediately (Pre-Paid)
            // [AUDIT FIX]: Use centralized Escrow Address
            const destinationAddress = ESCROW_ADDRESS; 
            
            try {
                // [FIX]: Use exported sendPayment function instead of direct tonConnectUI access
                const txHash = await Wallet.sendPayment(amount, dealId);
                
                // [STEP 3]: Lock Funds
                // [AUDIT FIX]: Passed getUserId() as second arg
                await API.confirmPayment(dealId, getUserId(), txHash);
                
                hideProgress();
                safeAlert(
                    `✅ Offer Sent & Paid!\n\n` +
                    `💰 Amount: ${amount} TON (Locked)\n` +
                    `📍 Next: Owner accepts -> Auto Publish.`
                );
                document.querySelector('.tab[data-tab="deals"]')?.click();
                
            } catch (txErr) {
                hideProgress();
                console.error("[PAYMENT ERROR]", txErr);
                // [FIX]: Don't show false error - payment may have succeeded
                // TON Connect sometimes throws when returning from wallet app
                const errorMsg = txErr.message || "";
                if (errorMsg.includes('cancel') || errorMsg.includes('rejected')) {
                    safeAlert("❌ Payment was cancelled. Please try again.");
                } else {
                    // Payment likely went through, just the callback failed
                    safeAlert(
                        "⏳ Payment processing...\n\n" +
                        "If you confirmed in your wallet, the payment was likely successful.\n" +
                        "Check your Deals in a few moments."
                    );
                    document.querySelector('.tab[data-tab="deals"]')?.click();
                }
            }

        } catch (e) {
            hideProgress();
            safeAlert("Error: " + e.message);
        }
    };
}

// --- Loaders ---

export async function loadChannels(container) {
    container.innerHTML = '<div class="state-message">Loading marketplace...</div>';
    try {
        const channels = await API.fetchChannels();
        container.innerHTML = '';
        if (channels.length === 0) {
            container.innerHTML = '<div class="state-message">No channels found.</div>';
            return;
        }
        channels.forEach(ch => {
            const card = UI.renderChannelCard(ch, false, { onBuyAd: handleBuyAd });
            container.appendChild(card);
        });
    } catch (e) {
        container.innerHTML = `<div class="state-message">Error: ${e.message}</div>`;
    }
}

export async function loadMyChannels(container) {
    const userId = getUserId();
    if (!userId) {
        // [FIX P0]: Restored error handling with debug info
        const debugInfo = JSON.stringify(window.Telegram.WebApp.initDataUnsafe || {});
        container.innerHTML = `
            <div class="state-message">
                <p>⚠️ No User ID Detected.</p>
                <code style="font-size:10px; display:block; margin:10px 0; word-break:break-all;">${debugInfo}</code>
                <p>Please open this from the Telegram Bot Menu.</p>
                <button class="btn" onclick="window.location.reload()">🔄 Retry</button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '<div class="state-message">Fetching your channels...</div>';
    try {
        const channels = await API.fetchUserChannels(userId);
        container.innerHTML = '';
        if (channels.length === 0) {
            container.innerHTML = '<div class="state-message">No channels registered.</div>';
            return;
        }
        channels.forEach(ch => {
            const card = UI.renderChannelCard(ch, true, { onEditPrice: handleEditPrice });
            container.appendChild(card);
        });
    } catch (e) {
        container.innerHTML = `<div class="state-message">Error fetching channels.</div>`;
    }
}

// [POLLING]: State for auto-refresh
let dealsPollingInterval = null;

export async function loadUserDeals(container, role, isSilent = false) {
    const userId = getUserId();
    if (!userId) return;

    // Clear previous interval if this is a fresh load (not a silent refresh)
    // allowing the interval to "survive" its own recursive call would be wrong if we want strict control,
    // but here we want to RESET it on every manual tab switch, and maintain it on recursive calls.
    // simpler: valid polling is linked to the container lifecycle.
    
    if (!isSilent) {
        if (dealsPollingInterval) clearInterval(dealsPollingInterval);
        container.innerHTML = '<div class="state-message">Syncing deals...</div>';
    } 
    
    try {
        const allDeals = await API.fetchUserDeals(userId);
        const filtered = allDeals.filter(d => d.user_role === role);
        
        // [POLLING]: Setup new interval if not already running or if we just cleared it
        if (!isSilent) {
             dealsPollingInterval = setInterval(() => {
                if (document.body.contains(container) && container.style.display !== 'none') {
                    loadUserDeals(container, role, true);
                } else {
                    clearInterval(dealsPollingInterval);
                }
            }, 5000); 
        }

        if (!isSilent) container.innerHTML = '';
        
        if (filtered.length === 0) {
            container.innerHTML = `<div class="state-message">No deals found.</div>`;
            return;
        }

        // Use a wrapper to build content off-DOM then swap (reduces flicker)
        const listWrapper = document.createElement('div');
        
        const isAdvertiser = role === ROLES.ADVERTISER;
        filtered.forEach(deal => {
            const card = UI.renderDealCard(deal, isAdvertiser, {
                onPay: async (id, amt) => {
                     try {
                        // [BLOCKCHAIN]: Real Transaction
                        // [AUDIT FIX]: Passing 'id' allows Wallet to attach it as a Comment/Memo in V2.
                        const boc = await Wallet.sendPayment(amt, id);
                        
                        showProgress();
                        // Verify on Backend
                        const res = await API.confirmPayment(id, userId, boc);
                        hideProgress();

                        if (res.ok) {
                             safeAlert(`✅ Paid ${amt} TON! Funds locked.`);
                             loadUserDeals(container, role);
                        } else {
                             safeAlert("⚠️ Payment sent but backend sync failed.");
                        }
                     } catch (e) {
                        safeAlert("Transaction cancelled.");
                     }
                },
                onAccept: async (id) => {
                    showProgress();
                    const res = await API.acceptDeal(id, userId);
                    hideProgress();
                    if (res.ok) {
                        safeAlert("✅ Deal Accepted! Now submit your draft.");
                    }
                    loadUserDeals(container, role);
                },
                onSubmitDraft: async (id) => {
                    // [FIX]: Prompt owner for actual draft content
                    const content = prompt("Enter your ad draft (text/content):");
                    if (!content) return;
                    
                    showProgress();
                    await API.submitDraft(id, userId, content);
                    hideProgress();
                    safeAlert("📝 Draft submitted for approval!");
                    loadUserDeals(container, role);
                },
                // [FIX]: New handlers for Advertiser
                onApprove: async (id) => {
                    showProgress();
                    const res = await API.approveDraft(id, userId);
                    hideProgress();
                    if (res.ok) {
                        safeAlert("✅ Draft Approved! Now proceed to payment.");
                    }
                    loadUserDeals(container, role);
                },
                onRevise: async (id) => {
                    const reason = prompt("What changes do you need?");
                    if (!reason) return;
                    
                    showProgress();
                    await API.requestRevision(id, userId, reason);
                    hideProgress();
                    safeAlert("📝 Revision requested.");
                    loadUserDeals(container, role);
                }
            });
            listWrapper.appendChild(card);
        });

        // [UX]: Swap content instantly
        container.innerHTML = '';
        container.appendChild(listWrapper);

    } catch (e) {
        if (!isSilent) container.innerHTML = `<div class="state-message">Error loading deals.</div>`;
    }
}

