# Bounty Reaper — Follow-on bounded parcel receipt

RUN_ID: BR-20261021-0503-SAST-01
OBSERVED: 2026-10-21 05:03 SAST (03:03 UTC)
OFFICE: BOUNTY REAPER
MANDATE: AMX-MANDATE-BOUNTY-REAPER-V1
RESULT: PREFLIGHT_PASS; 1INCH ORDERREGISTRATOR CLAIM KILLED AGAINST LATEST RELEASE; NATIVE-ORDER REWARD-LOCK THEORY KILLED ON REVIEWED SOURCE; TRACKER ACCESS STILL BLOCKED; Q1 UNKNOWN_NOT_ZERO; OPEN / NONTERMINAL.

## 1. Mandatory wake pre-flight

Directly fetched current canonical GitHub paths:
- Registry: `AMX/ROOT/BLUE_STATE/MANDATE_REGISTRY_V1.json`; version 1.3; blob `bcfd1f422bd25ba852666a538712828d594759e8`.
- Declared and independently recomputed registry root: `96c0beb3328ebefc16286d93a7baadc0ff4be0a17c1e6a8718b89de94f58df1a` — MATCH.
- Blue State: `AMX/ROOT/BLUE_STATE/BLUE_STATE_MANDATE_BINDING_AND_PREFLIGHT_V1.md`; blob `73d8131032a36757acfbd2762861b52c73eb6b3f`.
- Role: `BOUNTY-REAPER`; mandate ID `AMX-MANDATE-BOUNTY-REAPER-V1`; registered status `CURRENT`.
- Exact marker-bounded canonical payload = 1,082 UTF-8 bytes; independently recomputed SHA-256 `754d8fb9b6816da1bf0013940883106e0d3928b1637526ee82b38e1792c1dcd3` — MATCH.
- Current Blue State/flight readback says the existing Reaper remains disabled pending route/infra acceptance. This run did not read scheduler API state directly and made no enablement, cadence, prompt, or schedule changes. No new worker created.

## 2. Existing 1inch timestamp hypothesis — A / KILLED FOR LATEST RELEASE

Current official GitHub release page shows v4.3.4 as the latest published release, dated 2026-09-24: https://github.com/1inch/limit-order-protocol/releases

Exact source comparison:
- Latest release `4.3.4/contracts/helpers/OrderRegistrator.sol`, blob `c16e30831f6c44c88b4e1e7ece8f560c9301922e`: validates the extension and maker signature and emits `OrderRegistered`, but has no `announcedAt` mapping and no first-registration timestamp write.
- Current `main/contracts/helpers/OrderRegistrator.sol`, blob `0317e58286e438d246a95c742851797b51a655ec`, does add `announcedAt[orderHash]`, records only its first timestamp, and rejects a later registration for that order.
- Current official Immunefi scope page says the program applies only to latest tag/releases, updated 2026-10-14, requires PoC/KYC, excludes theoretical/speculative issues without demonstrated impact, and expressly prohibits submitting AI-generated reports: https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/

**Disposition:** the old timestamp-front-run hypothesis is not promoted and is killed as a report candidate against the latest release: the feature it alleged is absent from latest tag v4.3.4; main-branch-only behavior cannot substitute for eligible released code. Even on main, prior review had no demonstrated theft, freeze, or other qualifying impact. No report generated or submitted.

## 3. Same program, separate current-release Native Order cancellation check — bounded kill

Because v4.3.4 adds NativeOrderFactory/NativeOrderImpl and the official scope has generalized Limit Order Protocol assets, the smallest follow-on check was whether resolver reward calculation can make an expired order's residual WETH permanently unrecoverable.

Exact v4.3.4 public-source reads:
- `contracts/extensions/NativeOrderFactory.sol`, blob `e7c120d97d9e7c60dd76a370cbcaf05f0f935667`.
- `contracts/extensions/NativeOrderImpl.sol`, blob `231a0687feb02ea13137fdcc0e86663959c26400`.
- `contracts/libraries/MakerTraitsLib.sol`, blob `a17fde162ba9e2d0f226898c416a60ac3e329593`.
- `test/LimitOrderProtocol.js`, blob `69d82722c216a98d0b3fbf5a35b61cb5b4a70dce`.
- The repository's v4.3.4 deployment manifests include NativeOrderFactory entries at Arbitrum `0xe12E0f117d23a5ccc57f8935CD8c4E80cD91FF01` and zkSync `0xFd1d18173D2f179a45Bf21F755a261AAe7C2d769`. These source manifests do not themselves prove the precise currently deployed implementation or which exact address maps to Immunefi's generalized asset entry.

Bounded result:
- `cancelExpiredOrderByResolver` is restricted to callers holding the configured resolver access token and requires the signed order to be expired.
- When a non-zero reward is requested, reward is capped by caller-provided `rewardLimit` and the base-fee formula. If residual WETH balance is below the computed reward, `balance -= resolverReward` reverts before payout; that is a failed rewarded cancellation attempt, not itself fund theft.
- The same resolver can use `rewardLimit=0` to cancel without a reward; the repository's latest-tag tests explicitly cover successful resolver cancellation without reward. The original maker also has `cancelOrder`; the maker-gated `withdraw` path can invoke WETH withdrawal and forward native currency when necessary.
- Thus the bounded theory “setting/encountering a resolver reward above residual balance permanently locks the maker's funds” is **A / KILLED on the reviewed source paths**. No local tests were executed in this wake; existing repository tests were inspected, and no live chain/testnet, transaction, exploit, or funds movement was used.
- No distinct eligible economic impact was established. The exact deployed contract/address-to-scope mapping and full audit/known-issue dedupe remain unbound. Do not submit this theory.

## 4. Canonical Live Tracker — exact current blocker evidence

Canonical sink remains the existing Google Sheet `AMX Bounty Reaper — Live Tracker`, spreadsheet ID `1ETiK6b2YOz499OXBA5wuvgyWMjnDZoEdJIwCt2xGeCk`.

Actions attempted:
1. Enumerated current callable tools for authorized Sheets/Drive read/write/append/row-readback; no such direct action is exposed.
2. Fetched the exact existing spreadsheet URL through the available read-only page fetcher; result was `login_required`.
3. Read the available TinyFish wallet status (read-only): balance `-1.051248 USD`, auto-reload unconfigured. A metered browser/login attempt was not run; no wallet top-up, credential change, or profile setup was made.
4. The existing profile metadata lists `amillimatrix@gmail.com` as having a Google sign-in claim dated 2026-10-18, but its current session validity is unverified. No login is claimed.

Result: `TRACKER_WRITE_BLOCKED`. No Runs/Queue/Payouts read, row append, row readback or Queue/Payouts update occurred. Current Q1 is **UNKNOWN, NOT ZERO**. This is an access and execution-context blocker, not evidence that no Q1 exists.

## 5. Existing flight continuity / receipt truth

This receipt continues the already open flight:
`AMX-FLT-20261012-DSYNC-145440-9fb44f0c`, segment 14. It is not a new worker or flight. The current flight-register readback is the canonical continuity record.

- Root Intake receipt: this file; independent fetch/readback is required after commit.
- Tracker Runs row: not written.
- Official bounty submissions/report IDs: none established in this run.
- Acceptance/award/receivable/payment: none verified.
- No scheduler changes, live-target testing, transactions, fund movement, spend, credential expansion, KYC/legal attestation, public disclosure, or out-of-route submission occurred.

## 6. Directive 23 — action/owner record

- **Expected outcome:** convert eligible completed bounty work through official routes, keeping queue/lifecycle truth exact.
- **Work performed:** revalidated Registry v1.3 and mandate digest; killed the old 1inch timestamp hypothesis against current latest release; tested the smallest source-level lock/reward theory in v4.3.4 NativeOrder cancellation and killed that theory.
- **Owner:** Bounty Reaper owns crypto-bounty review and official submission; ROOT/T-GOV and the authorized integration owner own the existing tracker/execution-context access route and resume gates.
- **Dependencies:** authorized Tracker writer and independent reader in the Reaper execution context; current queue recovery; exact eligible deployed target, impact, runnable rule-compliant PoC and audit dedupe for any future report.
- **Evidence/readback:** v4.3.4 latest release/source hashes and official scope above; persist this receipt to existing Root Intake and independently fetch it.
- **Safety/preservation:** preserve killed claims; one existing Reaper only; do not restart the paused schedule; do not submit AI-generated material to 1inch; no live testing or fund movement.
- **Disposition:** two bounded 1inch subclaims killed/not promoted. No eligible submission package established.
- **Remaining work:** restore the canonical Tracker route with its authorized identity/session; then read Runs/Queue/Payouts and drain any Q1 before any new discovery. If Tracker remains gated, continue one distinct existing executable parcel with source-backed scope/impact; keep the flight open.

TRACKER: TRACKER_WRITE_BLOCKED
Q1: UNKNOWN_NOT_ZERO
ONEINCH_TIMESTAMP: KILLED_AGAINST_LATEST_RELEASE
NATIVE_ORDER_REWARD_LOCK: KILLED_ON_REVIEWED_SOURCE
SUBMISSION: NONE_ESTABLISHED
PAYMENT: NONE_VERIFIED
TERMINAL: NO
