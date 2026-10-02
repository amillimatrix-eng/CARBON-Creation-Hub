# AMX External Human-Cadence Interaction Control

Status: ACTIVE OPERATIONAL CONTROL
Date: 2026-10-02

## Purpose

AMilliMATRiX automation may operate at machine speed internally, but third-party human-facing services should be interacted with at a normal human cadence by default.

## Control

For external websites and platforms involving authentication, forms, applications, messaging, account changes, or other interactive UI:

- Use deliberate human-scale pacing instead of burst-speed clicking, typing, navigation, or retries.
- Avoid repeated submissions and rapid refresh/retry loops.
- Preserve the current session and state rather than opening duplicate sessions or accounts.
- Respect provider rate limits, cooldowns, verification steps, and ordinary UI timing.
- If a service returns anomalous errors, verification challenges, rate limits, or repeated failures, slow down further before retrying.
- Internal Matrix work, local compute, repository operations, evidence processing, and other non-human-facing machine workflows may continue at machine speed where appropriate.

## Intent

This is a pacing and reliability control, not a new human gate. The Matrix should remain autonomous while interacting with external human-facing systems in a way that reduces accidental race conditions, duplicate actions, provider-side throttling, and false automation-abuse signals.

This control does not authorize bypassing provider security, anti-abuse controls, authentication, or rate limits.

## Operational shorthand

**INTERNAL = MACHINE SPEED**
**EXTERNAL HUMAN-FACING = HUMAN CADENCE**
**ERROR/CHALLENGE = SLOW DOWN, PRESERVE STATE, RETRY ONCE DELIBERATELY**
