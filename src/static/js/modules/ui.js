/**
 * [UI]: Pure Rendering Logic
 */
import { getTg } from './auth.js';

const tg = getTg();

// Helpers
export function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export function formatNumber(num) {
    return new Intl.NumberFormat('en-US', { notation: "compact", compactDisplay: "short" }).format(num);
}

// Components
export function renderChannelCard(channel, isOwnerView, callbacks) {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
        <div class="card-header">
            <h3>${escapeHtml(channel.title)}</h3>
            ${channel.verified ? '<span class="verified-badge">✅ Verified</span>' : ''}
        </div>
        <div class="stats-grid">
            <div class="stat-box"><span class="stat-val">${formatNumber(channel.subscribers)}</span><span class="stat-label">Subs</span></div>
            <div class="stat-box"><span class="stat-val">👁️ ${formatNumber(channel.avg_views)}</span><span class="stat-label">Avg Views</span></div>
            <div class="stat-box"><span class="stat-val">🌍 ${channel.language.toUpperCase()}</span><span class="stat-label">Lang</span></div>
            <div class="stat-box"><span class="stat-val">💎 ${Math.round(channel.premium_ratio * 100)}%</span><span class="stat-label">Premium</span></div>
        </div>
        <div id="action-container" style="margin-top:10px"></div>
    `;

    const actionContainer = card.querySelector('#action-container');
    
    if (isOwnerView) {
        const info = document.createElement('div');
        info.innerHTML = `<div style="text-align:center; color:#aaa; font-size:12px; margin-bottom:5px">Current Price: ${channel.price_post} TON</div>`;
        
        const btn = document.createElement('button');
        btn.className = 'btn btn-secondary';
        btn.innerText = '✏️ Set Price';
        btn.onclick = () => callbacks.onEditPrice(channel.id, channel.price_post);
        
        actionContainer.appendChild(info);
        actionContainer.appendChild(btn);
    } else {
        const btn = document.createElement('button');
        btn.className = 'btn';
        btn.innerHTML = `Buy Ad • ${channel.price_post} TON`;
        btn.onclick = () => callbacks.onBuyAd(channel);
        actionContainer.appendChild(btn);
    }

    return card;
}

export function renderDealCard(deal, isAdvertiser, callbacks) {
    // [GROWTH]: Visual progress indicator
    const statusFlow = ['created', 'accepted', 'drafted', 'awaiting', 'locked', 'scheduled', 'published', 'completed'];
    const currentStep = statusFlow.indexOf(deal.status.toLowerCase()) + 1;
    const progress = Math.round((currentStep / statusFlow.length) * 100);
    
    // [GROWTH]: Status-specific messages
    const statusMessages = {
        'created': isAdvertiser ? '⏳ Waiting for owner to accept...' : '📩 New offer! Accept or reject.',
        'accepted': isAdvertiser ? '⏳ Owner accepted! Waiting for draft...' : '✏️ Create your ad draft.',
        'drafted': isAdvertiser ? '📝 Review the draft and approve.' : '⏳ Waiting for advertiser approval...',
        'awaiting': isAdvertiser ? '💎 Approved! Pay to lock funds.' : '⏳ Waiting for payment...',
        'locked': '🔒 Funds locked in escrow.',
        'scheduled': '📅 Scheduled for auto-post.',
        'published': '📢 Posted! Verifying...',
        'completed': '✅ Campaign complete!'
    };
    
    const card = document.createElement('div');
    card.className = 'card deal-card';
    card.innerHTML = `
        <div class="card-header">
            <span class="status-tag status-${deal.status.toLowerCase()}">${deal.status.toUpperCase()}</span>
            <small>💎 ${deal.amount_ton} TON</small>
        </div>
        <div class="progress-bar-container" style="background:#333; border-radius:4px; height:6px; margin:8px 0;">
            <div class="progress-bar" style="width:${progress}%; background:linear-gradient(90deg,#0088cc,#00d4aa); height:100%; border-radius:4px; transition:width 0.3s;"></div>
        </div>
        <div class="status-message" style="font-size:12px; color:#aaa; margin-bottom:8px;">
            ${statusMessages[deal.status.toLowerCase()] || '...'}
        </div>
        <div class="deal-body">
            <strong>Brief:</strong> ${escapeHtml(deal.ad_brief)}
            ${deal.ad_draft ? `<div class="draft-box" style="background:#1a1a1a; padding:8px; border-radius:4px; margin-top:8px;"><strong>📝 Draft:</strong> ${escapeHtml(deal.ad_draft)}</div>` : ''}
        </div>
        <div class="deal-actions" style="margin-top:10px;"></div>
    `;

    const actions = card.querySelector('.deal-actions');

    if (isAdvertiser) {
        // [FIX]: Correct flow - Approve/Revise on drafted, Pay on awaiting
        if (deal.status === 'drafted') {
            // Advertiser sees draft, can approve or request changes
            const approveBtn = document.createElement('button');
            approveBtn.className = 'btn btn-sm';
            approveBtn.innerText = '✅ Approve Draft';
            approveBtn.onclick = () => callbacks.onApprove(deal.id);
            
            const reviseBtn = document.createElement('button');
            reviseBtn.className = 'btn btn-sm btn-secondary';
            reviseBtn.style.marginLeft = '5px';
            reviseBtn.innerText = '✏️ Request Changes';
            reviseBtn.onclick = () => callbacks.onRevise(deal.id);
            
            actions.appendChild(approveBtn);
            actions.appendChild(reviseBtn);
        } else if (deal.status === 'awaiting') {
            // Advertiser approved, now must pay
            const btn = document.createElement('button');
            btn.className = 'btn btn-sm btn-primary';
            btn.innerText = `💎 Pay ${deal.amount_ton} TON`;
            btn.onclick = () => callbacks.onPay(deal.id, deal.amount_ton);
            actions.appendChild(btn);
        } else {
            actions.innerHTML = `<span class="wait-msg">Status: ${deal.status}</span>`;
        }
    } else {
        // OWNER VIEW
        if (deal.status === 'created' || deal.status === 'locked') {
            // [SIMPLIFIED FLOW]: Owner only needs to Accept or Reject
            // For LOCKED (Pre-Paid) deals, Accept = Auto-Publish
            const acceptBtn = document.createElement('button');
            acceptBtn.className = 'btn btn-sm';
            acceptBtn.innerText = deal.status === 'locked' ? '✅ Accept & Publish' : '✅ Accept Deal';
            acceptBtn.onclick = () => callbacks.onAccept(deal.id);
            
            const rejectBtn = document.createElement('button');
            rejectBtn.className = 'btn btn-sm btn-secondary';
            rejectBtn.style.marginLeft = '5px';
            rejectBtn.innerText = '❌ Reject';
            rejectBtn.onclick = () => callbacks.onReject ? callbacks.onReject(deal.id) : alert('Reject not implemented');
            
            actions.appendChild(acceptBtn);
            actions.appendChild(rejectBtn);
        } else {
            actions.innerHTML = `<span class="wait-msg">Status: ${deal.status}</span>`;
        }
    }

    return card;
}

