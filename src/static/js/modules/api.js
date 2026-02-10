/**
 * [API]: Pure Data Layer
 */
import { API_BASE } from './config.js';
import { getTg } from './auth.js';

const tg = getTg();

async function fetchWithHeaders(endpoint, options = {}) {
    const headers = { 
        'ngrok-skip-browser-warning': 'true',
        'Content-Type': 'application/json',
        ...options.headers 
    };
    return fetch(`${API_BASE}${endpoint}`, { ...options, headers });
}

export async function fetchChannels() {
    const res = await fetchWithHeaders('/api/channels');
    return res.json();
}

export async function fetchUserChannels(userId) {
    const res = await fetchWithHeaders(`/api/channels/user/${userId}`);
    return res.json();
}

export async function fetchUserDeals(userId) {
    const res = await fetchWithHeaders(`/api/deals/user/${userId}`);
    return res.json();
}

export async function updateChannelPrice(channelId, userId, price) {
    return fetchWithHeaders(`/api/channels/${channelId}`, {
        method: 'PUT',
        body: JSON.stringify({ user_id: userId, price_post: price })
    });
}

export async function createDeal(payload) {
    return fetchWithHeaders('/api/deals/create', {
        method: 'POST',
        body: JSON.stringify(payload)
    });
}

export async function acceptDeal(id, userId) {
    return fetchWithHeaders(`/api/deals/${id}/accept`, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId })
    });
}

export async function rejectDeal(id, userId, reason) {
    return fetchWithHeaders(`/api/deals/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, content: reason })
    });
}

export async function submitDraft(id, userId, content) {
    return fetchWithHeaders(`/api/deals/${id}/submit-draft`, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, content })
    });
}

export async function confirmPayment(id, userId, txHash) {
    return fetchWithHeaders(`/api/deals/${id}/confirm-payment`, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, transaction_hash: txHash })
    });
}

// [FIX]: Added Approve Draft function
export async function approveDraft(id, userId) {
    return fetchWithHeaders(`/api/deals/${id}/approve`, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId })
    });
}

// [FIX]: Added Request Revision function
export async function requestRevision(id, userId, reason) {
    return fetchWithHeaders(`/api/deals/${id}/request-revision`, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, content: reason })
    });
}

// [ESCROW FIX]: Save wallet address when user connects
export async function saveWallet(userId, walletAddress) {
    return fetchWithHeaders('/api/user/wallet', {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, wallet_address: walletAddress })
    });
}

// [ROLE FIX]: Save user role when they select a path
export async function saveRole(userId, role) {
    return fetchWithHeaders('/api/user/role', {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, role: role })
    });
}

// [HARDENING]: Raise a dispute on a deal
export async function disputeDeal(dealId, userId, reason) {
    return fetchWithHeaders(`/api/deals/${dealId}/dispute`, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, reason: reason })
    });
}

