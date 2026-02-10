/**
 * [AUTH]: Identity and Session Management
 */
const tg = window.Telegram.WebApp;

// [DEV MODE]: Auto-assign ID when testing in browser
const DEV_MODE = !tg.initDataUnsafe?.user;
if (DEV_MODE) {
    console.warn("[AUTH] DEV MODE: Auto-assigning test user ID 99999");
}

export function getUserId() {
    // 1. Priority: Telegram WebApp Data (Production — tamper-proof)
    const user = tg.initDataUnsafe?.user;
    if (user && user.id) return user.id;

    // 2. URL Parameter (DEV_MODE only — never in production)
    if (DEV_MODE) {
        const urlParams = new URLSearchParams(window.location.search);
        const paramId = urlParams.get('user_id');
        if (paramId) return parseInt(paramId);
    }

    // 3. Persistence (LocalStorage)
    let setID = localStorage.getItem('sim_user_id');
    
    // [FIX]: Force reset legacy default ID (99999) to ensure uniqueness
    if (setID && parseInt(setID) === 99999) {
        setID = null; // Treat as empty to trigger regeneration
        localStorage.removeItem('sim_user_id');
    }

    if (setID) return parseInt(setID);

    // 4. [DEV MODE]: Auto-fallback for browser testing
    if (DEV_MODE) {
        // [FIX]: Generate random ID to support multi-user simulation on diff devices
        if (!setID) {
            const randomId = Math.floor(Math.random() * 89999) + 10000;
            localStorage.setItem('sim_user_id', randomId);
            return randomId;
        }
    }

    return null;
}

export function forceSetId() {
    const newId = prompt("Enter new Simulation ID:", "11111");
    if (newId) {
        localStorage.setItem('sim_user_id', newId);
        window.location.reload();
    }
}

export function getTg() {
    return tg;
}

// [SAFE]: Wrapper for showAlert that works in browser too
export function safeAlert(message) {
    if (tg.showAlert) {
        try {
            tg.showAlert(message);
        } catch (e) {
            alert(message);
        }
    } else {
        alert(message);
    }
}

// [SAFE]: Wrapper for MainButton that works in browser too
export function safeMainButton(action) {
    if (tg.MainButton && typeof tg.MainButton[action] === 'function') {
        try {
            tg.MainButton[action]();
        } catch (e) {
            console.log(`[UI] MainButton.${action}() not available`);
        }
    }
}


