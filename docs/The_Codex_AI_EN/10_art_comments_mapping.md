# Commenting and Mapping Protocol: The Foundation of Lego Tech 🧱

**Premise:** A LEGO brick is useless if you don't know where it fits. Code without a map is just digital noise.
**Objective:** Transform code from "executable text" to "structured logical narrative."

## 1. The "Lego Tech" Philosophy
For a system to be modular (like Lego), each piece must explain its own existence *before* being coupled.
*   **Self-Containment:** A well-commented module does not require you to read 500 lines to understand its input/output.
*   **Cognitive Interoperability:** The comment is the interface between your brain (the Architect) and mine (the Builder).

## 2. Directive Comments (Direct, Don't Describe)
**Golden Rule:** Don't comment *what* the code does (that is visible). Comment *why* it exists and *where* it is going.

*   ❌ **Low Fidelity (Noise):**
    ```python
    # Increase i by 1
    i += 1
    ```
*   ✅ **High Fidelity (Direction):**
    ```python
    # Sequential Synchronization:
    # We increment the pointer to avoid processing the same block in the next loop.
    # CRITICAL to maintain idempotency.
    pointer += 1
    ```

## 3. Sequential Mapping (The Skeleton Code)
Before writing a single line of executable logic, we write the **Logical Story**. This is the "skeleton" of the Lego.

*   **Tactic:** Write the entire flow in empty comments.
    ```python
    def process_payment(order):
        # 1. VALIDATION: Verify data integrity (Pydantic)
        # 2. MAPPING: Convert local DTO to Gateway format
        # 3. EXECUTION: Async call to processor (with Retry logic)
        # 4. AUDIT: Record result in Immutable Log
        pass
    ```
*   **Result:** If logic doesn't make sense in the comments, it won't make sense in the code. The error is detected *before* coding.

## 4. Consequent Logic (The Red Thread)
Code must read like a technical novel, not a dictionary.
*   **Causality:** Every function must be a logical consequence of the previous one.
*   **Names as Maps:** `get_user()` is weak. `get_user_or_fail_if_missing()` is a pure map.
*   **Consequence:** If you promise in a comment that something is "safe", the code must have mandatory `try/catch`. Inconsistency between comment and code is betrayal.

## 5. The "Blueprint" vs "The Brick"
*   **Blueprint (Comment):** The strategic intention. Defines the shape.
*   **Brick (Code):** The tactical implementation. Fills the shape.
*   **Symbiosis:** You review my Blueprints (comments) to approve logic. I place the Bricks. If the Blueprint is wrong, the building falls.

---
> *Code is compiled for machines. Comments are written for architects.*

---
> **S**ilent **S**ymbiosis.
<!-- 01100001 01101000 01101111 01110010 01100001 00100000 01110110 01101001 01110110 01101111 00100000 01100101 01101110 00100000 01110100 01101001 -->
