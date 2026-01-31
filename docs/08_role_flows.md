# 🔀 Role Flows: Who Does What, When

> **Codex Alignment**: "A stranger can complete a deal without reading a manual."

---

## The Two Actors

| Role                 | Goal                       | Entry Point                |
| -------------------- | -------------------------- | -------------------------- |
| **📡 Channel Owner** | Sell ad space, get paid    | "I own a Channel" button   |
| **📢 Advertiser**    | Buy ad space, run campaign | "I want to Buy Ads" button |

---

## 📡 Channel Owner Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: REGISTER CHANNEL                                        │
│ [Action]: Paste @channel link in bot chat                       │
│ [Result]: Bot verifies admin status → Channel appears in Marketplace │
├─────────────────────────────────────────────────────────────────┤
│ STEP 2: SET PRICE                                               │
│ [Action]: Click "Set Price" on channel card                     │
│ [Result]: Price updated in database                             │
├─────────────────────────────────────────────────────────────────┤
│ STEP 3: RECEIVE OFFER                                           │
│ [Trigger]: Advertiser sends offer                               │
│ [View]: "Inbox" tab → Deal card with status "CREATED"           │
│ [Action]: Click "Accept Deal"                                   │
│ [Result]: Status → ACCEPTED                                     │
├─────────────────────────────────────────────────────────────────┤
│ STEP 4: SUBMIT DRAFT                                            │
│ [Trigger]: After accepting                                      │
│ [View]: Deal card shows "Submit Draft" button                   │
│ [Action]: Click "Submit Draft" → Enter ad content               │
│ [Result]: Status → DRAFT_SUBMITTED (goes to Advertiser)         │
├─────────────────────────────────────────────────────────────────┤
│ STEP 5: WAIT FOR PAYMENT                                        │
│ [Trigger]: Advertiser approves draft and pays                   │
│ [View]: Deal status → LOCKED                                    │
│ [Action]: NONE (wait for auto-post)                             │
├─────────────────────────────────────────────────────────────────┤
│ STEP 6: AUTO-POST & GET PAID                                    │
│ [Trigger]: Scheduler posts to channel                           │
│ [View]: Deal status → COMPLETED                                 │
│ [Result]: Funds released (Future: auto-transfer to wallet)      │
└─────────────────────────────────────────────────────────────────┘
```

### Owner Tools Needed:

- ✅ Channel Registration (via Bot)
- ✅ Price Setting (via UI)
- ✅ Accept Deal Button
- ✅ Submit Draft Button
- ⚠️ **MISSING**: Wallet connection for receiving funds

---

## 📢 Advertiser Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: BROWSE MARKETPLACE                                      │
│ [View]: "Marketplace" tab → List of verified channels           │
│ [Action]: Click "Buy Ad" on desired channel                     │
├─────────────────────────────────────────────────────────────────┤
│ STEP 2: SEND OFFER                                              │
│ [Action]: Enter offer amount → Submit                           │
│ [Result]: Deal created with status "CREATED"                    │
│ [View]: "Sent Offers" tab → Deal appears                        │
├─────────────────────────────────────────────────────────────────┤
│ STEP 3: WAIT FOR OWNER ACCEPTANCE                               │
│ [View]: Deal status = "CREATED" → Waiting...                    │
│ [Trigger]: Owner accepts → Status → ACCEPTED                    │
├─────────────────────────────────────────────────────────────────┤
│ STEP 4: WAIT FOR DRAFT                                          │
│ [View]: Deal status = "ACCEPTED" → Waiting...                   │
│ [Trigger]: Owner submits draft → Status → DRAFT_SUBMITTED       │
├─────────────────────────────────────────────────────────────────┤
│ STEP 5: REVIEW & APPROVE DRAFT                                  │
│ [View]: Deal card shows draft content + "Approve" or "Revise"   │
│ [Action]: Click "Approve" → Status → AWAITING_PAYMENT           │
│ [Result]: "Pay Now" button appears                              │
├─────────────────────────────────────────────────────────────────┤
│ STEP 6: PAY VIA TON CONNECT                                     │
│ [Prerequisite]: Wallet connected                                │
│ [Action]: Click "Pay X TON" → Tonkeeper prompt → Confirm        │
│ [Result]: Transaction sent → Backend verifies → Status → LOCKED │
├─────────────────────────────────────────────────────────────────┤
│ STEP 7: CAMPAIGN LIVE                                           │
│ [View]: Deal status → PUBLISHED → COMPLETED                     │
│ [Result]: Ad is live on channel                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Advertiser Tools Needed:

- ✅ Marketplace Browse
- ✅ Create Offer
- ⚠️ **MISSING**: Approve Draft Button
- ⚠️ **MISSING**: Request Revision Button
- ✅ Pay Button (shows on `drafted` status, should show on `awaiting`)
- ✅ Wallet Connection

---

## 🔴 Current Bugs Identified

| #   | Bug                       | Root Cause                                     | Fix                          |
| --- | ------------------------- | ---------------------------------------------- | ---------------------------- |
| 1   | Accept Deal fails         | API expects `content` field even for Accept    | Fix backend schema           |
| 2   | Pay button never appears  | UI shows Pay only on `drafted`, not `awaiting` | Fix UI condition             |
| 3   | No Approve button         | UI missing this action for Advertiser          | Add Approve button           |
| 4   | No Revise button          | UI missing this action for Advertiser          | Add Revise button            |
| 5   | Owner can't receive funds | No wallet prompt for Owner                     | Add wallet connect for Owner |

---

## 🔧 Required Fixes

### Fix 1: Backend Accept Schema

`routes.py` - Accept endpoint should not require `content` (only `user_id`).

### Fix 2: UI Status Conditions

`ui.js` - Pay button should appear on `awaiting` status, not `drafted`.

### Fix 3: Add Approve/Revise Buttons for Advertiser

`ui.js` - When status is `drafted`, show Approve + Revise buttons, not Pay.

### Fix 4: Add API functions

`api.js` - Add `approveDraft()` and `requestRevision()` functions.

### Fix 5: Wire up Controllers

`controllers.js` - Add `onApprove` and `onRevise` handlers.

---

_Document Version: 1.0_
_Aligned with The Codex_
