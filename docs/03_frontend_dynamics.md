# Volume III: The Interface Dynamics (Frontend)

> _"Complexity should be internal. Simplicity should be external."_

## 1. The Philosophy: "App-Like" Web

Although we are running in a browser engine (Webview), the user must feel they are using a Native App.

- **No Page Reloads**: We use AJAX (`fetch`) and DOM manipulation to swap views instantly.
- **Haptic Feedback**: Every critical action (Buy, Pay, Accept) triggers the phone's vibration motor via `tg.HapticFeedback`.
- **Loading States**: Network latency is masked by Skeleton Loaders or beautiful "Waiting..." states.

## 2. The "Lego" Architecture

We avoided monolithic "Spaghetti Code" by splitting logic into strict ES6 Modules:

### A. `api.js` (The Data Layer)

- **Role**: Validates and transports data.
- **Feature**: Automatically injects Headers (Content-Type, Ngrok-Skip) so other modules don't worry about protocol details.

### B. `ui.js` (The Presentation Layer)

- **Role**: Pure rendering.
- **Feature**: Returns HTML Elements (Nodes), not strings. This allows us to attach Event Listeners (`onclick`) directly to the button logic, ensuring robust interactivity.

### C. `controllers.js` (The Brain)

- **Role**: Orchestrates the dance between User, API, and UI.
- **Logic**:
  1.  User clicks "Buy".
  2.  Controller calls `UI` to show a spinner.
  3.  Controller calls `API` to send data.
  4.  Controller waits.
  5.  Controller directs `UI` to show "Success" or "Error".

## 3. Telegram Connectors

We hook directly into the Telegram Main Button (`tg.MainButton`).

- **Why?**: It lives _outside_ the webview, in the native UI. It feels more trusted and secure to the user.
- **Usage**: We show it only when a Global Action (like "Confirm Payment") is valid and ready.

---

**[Next Volume: The Web3 Horizon ->](./04_web3_strategy.md)**
