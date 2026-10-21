# Bounty Reaper — Execution / Failure-Correction Receipt

RUN_ID: BR-20261021-0436-SAST-01
OBSERVED: 2026-10-21 04:36 SAST
OFFICE: BOUNTY REAPER
MANDATE: AMX-MANDATE-BOUNTY-REAPER-V1
RESULT: PRODUCTIVE BOUNDED SOURCE ADVANCEMENT; LAYERZERO Q3 PARKED; SYMBIOSIS SUBCLAIM KILLED; TRACKER_WRITE_BLOCKED; Q1 UNKNOWN_NOT_ZERO; OPEN.

## 1. Canonical pre-flight — PASS

Directly fetched from `amillimatrix-eng/CARBON-Creation-Hub` main:
- Registry: `AMX/ROOT/BLUE_STATE/MANDATE_REGISTRY_V1.json`; blob `bcfd1f422bd25ba852666a538712828d594759e8`.
- Registry version: `1.3`; status `OWNER_ACCEPTED_MERGED_BLUE_STATE`.
- Declared registry root: `96c0beb3328ebefc16286d93a7baadc0ff4be0a17c1e6a8718b89de94f58df1a`.
- Independently recomputed root using sorted `ROLE_KEY=MANDATE_SHA256\n` input: same digest; MATCH.
- Blue State: `AMX/ROOT/BLUE_STATE/BLUE_STATE_MANDATE_BINDING_AND_PREFLIGHT_V1.md`; blob `73d8131032a36757acfbd2762861b52c73eb6b3f`.
- Registered role `BOUNTY-REAPER`: `CURRENT`; mandate `AMX-MANDATE-BOUNTY-REAPER-V1`; registered SHA-256 `754d8fb9b6816da1bf0013940883106e0d3928b1637526ee82b38e1792c1dcd3`.
- Exact canonical payload extracted between its role-specific markers: 1,082 UTF-8 bytes; independently recomputed SHA-256 matches the registered digest.
- Cached Registry 1.2/root in the supplied prompt is stale; Registry 1.3 and current Blue State govern.

## 2. Failure correction / execution boundary

The previous response over-applied the temporary Owner pause of **scheduled lanes** as if it prevented all Reaper source work. The current Blue State says schedules remain paused until six infrastructure/convergence gates are accepted and read back; it does not itself prohibit this Owner-invoked, read-only source-review wake.

This run continued source work without enabling, rescheduling, editing or duplicating the existing Reaper automation. No scheduler API state was freshly queried in this run and no scheduler mutation was made. The canonical Blue State's recorded post-pause inventory lists 25 tasks and 0 enabled at that readback; that stored snapshot is not represented as a fresh API observation today.

## 3. Q1 drain / canonical Tracker attempt

Canonical sink: `AMX Bounty Reaper — Live Tracker`, spreadsheet ID `1ETiK6b2YOz499OXBA5wuvgyWMjnDZoEdJIwCt2xGeCk`.

Exact intended actions: read current Runs/Queue/Payouts; identify and classify completed work; append one attributable Runs receipt; independently read back that exact row; change Queue/Payouts only on new evidence.

Blocker: the current callable-tool inventory exposes no authorized Google Sheets/Drive spreadsheet read, append/update or row-readback action. I enumerated the current matching tools; the available Drive-named actions are unrelated Descript media actions, not Google Sheets/Drive data access. No spreadsheet API write was possible from this runtime. This is recorded as `TRACKER_WRITE_BLOCKED`; no attempted spreadsheet API request or spreadsheet failure response is claimed.

No Runs/Queue/Payouts read or write occurred; no row readback is claimed. Q1 remains **UNKNOWN, NOT ZERO**, because the canonical Tracker and Drive handoff are not accessible here. Do not infer queue emptiness from this blocker.

## 4. Parcel D — LayerZero BR-20261003-024 — Q3 PARKED / NOT SUBMISSION-READY

### Existing claim reconciliation
- Recovered source pin: `LayerZero-Labs/LayerZero-v2@9c741e7f9790639537b1710a203bcdfd73b0b9ac`, `Executor.sol` blob `7e64f06b4fca2cc7052b764014a919a639abe82e`.
- Freshly fetched official repository main `Executor.sol` also has blob `7e64f06b4fca2cc7052b764014a919a639abe82e`; its 10,179-byte content matches the pinned file exactly. The source-level failed-native-drop behavior therefore remains as previously recorded: failed native drop is counted in `spent`, but alone does not prevent the separate `lzReceive` attempt; relevant entry points are admin-gated. The failed-drop-prevents-receive and permanent-lock/no-recovery claims remain KILLED on the reviewed source. Do not resubmit or resurrect them.
- Official LayerZero Ethereum deployment documentation associates Executor `0x173272739Bd7Aa6e4e214714048a9fE699453059` with Ethereum Mainnet.
- Fresh independent L2BEAT deployment/diff review reports the proxy implementation changed on 2026-10-02 to `0x1Ed8E51E8AB2A00B2805aEcf2C6aC0BB6521eaE0`; its current implementation source is reported unverified. Thus matching the pinned source with the repository's public main is **not** proof that the currently deployed implementation behaves identically.
- The direct Etherscan implementation read was unavailable (HTTP 403). The available Blockscout connector reported that API access now requires a PRO key, so no current on-chain implementation-slot/code read was established in this run.
- Current official Immunefi LayerZero scope page says last updated 2026-10-02, requires a runnable PoC, lists 25 assets and does not name Executor as a direct asset in the displayed table. The official info/rules require scope/impact eligibility and prohibit testing deployed code on mainnet/public testnet; bounded local/fork validation only. The native-drop theory also faces relevant privileged-entry and prior-audit gates.

### Material disposition
`C/Q3 — PARKED / NOT SUBMISSION-READY`. The material change is a live implementation-binding gate: current deployed code equivalence and asset/impact eligibility are not proven. This is an evidence gap, not a confirmed vulnerability. Do not publish or submit. Resume only if a lawful source/deployment comparison yields a distinct claim with an exact eligible asset, non-privileged attacker/victim path, qualifying impact, runnable compliant local/fork PoC, and completed audit/prior-art dedupe.

Public refs:
- LayerZero Ethereum deployments: https://docs.layerzero.network/v2/deployments/chains/ethereum
- LayerZero Immunefi scope: https://immunefi.com/bug-bounty/layerzero/scope/
- LayerZero program rules: https://immunefi.com/bug-bounty/layerzero/information/
- L2BEAT implementation diff: https://disco.l2beat.com/diff/eth:0xfE9AB78eD4f9f3DbB168d9f5E5213d78605C9805/eth:0x1Ed8E51E8AB2A00B2805aEcf2C6aC0BB6521eaE0

## 5. Independent continuation — Symbiosis MetaRouterGateway candidate

This second existing candidate was re-opened after the LayerZero parcel hit a deployment-source gate, consistent with work-conservation.

- Current official Symbiosis Immunefi scope: https://immunefi.com/bug-bounty/symbiosis/scope/ ; page says last updated 2026-10-01, four assets, all named `MetaRouterGateway`; eligible listed impacts are direct theft of user ERC-20 funds or permanent freezing of ERC-20 funds; runnable PoC required; KYC not required; audit-reported findings are excluded.
- Fresh main-branch source fetch: `symbiosis-finance/core-contracts/contracts/synth-core/metarouter/MetaRouterGateway.sol`, blob `95fcff0f32bdea443a415cd462bc5456039634cd`. Its only token method, `claimTokens`, has `onlyMetarouter` and uses `safeTransferFrom(_token, _from, metaRouter, _amount)`; it does not transfer tokens held by the Gateway to an arbitrary receiver.
- Fresh `MetaRouter.sol`, blob `09dbc638a0ee7084dcdbac83ef35947afbb7ecf9`: `_externalCall` rejects the Gateway as `_receiveSide`; on a failed external call the fallback transfer uses the MetaRouter's own token balance. The reviewed public-call paths did not reveal an untrusted path to invoke the Gateway's privileged `claimTokens` or make it directly pay a caller-chosen victim/recipient.
- These two Git blob hashes match the already-recorded main-source blobs, so this is a fresh readback of current source rather than a claimed new upstream code change.

### Material disposition
The specific hypothesis that an untrusted public caller can exploit this helper to steal tokens directly from a listed Gateway is **A — KILLED on the reviewed current source path**. The broader parcel is not declared globally safe: no exhaustive protocol audit or new deployed-bytecode equivalence was established. Do not submit the rejected generic helper-balance theory. Reopen only upon identifying a distinct code-grounded path to direct theft/permanent freeze of one of the four listed deployed Gateway assets, with source/deployment binding, compliant local/fork PoC and audit/known-issue dedupe.

## 6. Other accessible inventory / current limitations

Existing accessible receipts classify prior claims concerning XOXNO stale positions, Sei Giga abort, 0x Settler reentrancy, 1inch timestamp, sBTC nonce cache, Enzyme zero-price redemption, Lombard threshold/replay, and SSV operator-removal freeze as killed, prior art, or still scope-gated. The separate vesting-arithmetic signal still lacks a bound project/source, eligible impact and runnable PoC. No accessible artifact in this wake establishes a submission-ready private packet or an external report receipt. This is not a certified total queue census while the canonical Tracker/Drive remain unreadable.

## 7. Lifecycle truth

- New official submission/report ID: NONE.
- Accepted/awarded: NONE established.
- Verified payment: NONE established.
- No KYC, login, wallet ownership/legal attestation, public disclosure, transaction, live exploitation, spend, fund movement, or credential expansion was attempted.
- No new worker, scheduler, tracker or evidence plane was created.

## 8. Directive 23 — recovery and next action

- **Expected outcomes:** recover authoritative Q1 queue; preserve the bounded LayerZero implementation-change evidence without overstating it; keep the proven Symbiosis direct-Gateway-theft subclaim killed; convert any genuinely submission-ready completed work through the correct official route.
- **Owners:** ROOT/T-GOV and authorized integration administrator for existing Tracker/Drive route and infrastructure/resume gates; Bounty Reaper retains source triage and bounty submission authority; program/source maintainers only through their published official scope/source.
- **Actions:** restore authorized read/write/readback for the existing Tracker; recover Runs/Queue/Payouts plus Root Handoff/Drive; independently classify A-G; after source access, bind LayerZero's changed implementation and current scope only if a new distinct hypothesis justifies it; continue another executable tracked candidate if any single gate persists.
- **Dependencies:** authorized Sheets/Drive connector; source/deployment verification for any LayerZero continuation; exact deployed Gateway/source mapping if Symbiosis is reopened.
- **Evidence/readback:** canonical Registry v1.3 root and Reaper digest match; current public-source blob hashes and official scope links above; this receipt must be independently fetched after write. Tracker row is not claimed.
- **Safety/preservation:** preserve killed subclaims and prior receipts; no out-of-route submission, no live testing, no shadow Tracker and no schedule restart.
- **Disposition:** OPEN. This fallback receipt is not a substitute for canonical Tracker row/readback or official bounty submission.
- **Remaining work:** restore the canonical Tracker route; recover the real queue before making any Q1=0 claim; continue from the furthest evidenced state; submit only a validated eligible report and track its external receipt through award and verified payment.

TRACKER: TRACKER_WRITE_BLOCKED
Q1: UNKNOWN_NOT_ZERO
LAYERZERO: Q3_PARKED_IMPLEMENTATION_BINDING_GATE
SYMBIOSIS: SPECIFIC_DIRECT_GATEWAY_THEFT_SUBCLAIM_KILLED
SUBMISSION: NONE
PAYMENT: NONE_VERIFIED


## 9. Later historical receipt recovered — furthest prior material state

A broader exact-path search recovered the later 19 October execution receipt after this run's first retrieval slice:
- Prior run ID: `BR-20261019-2159-SAST-02`, observed 2026-10-19 21:59:16 SAST; path `AMX/ROOT/INTAKE/BOUNTY_REAPER_EXECUTION_RECEIPT_20261019_2159_SAST.md`; blob `29bbd8a824f146fd49cae6067159699ac8168750`.
- That receipt already recorded a failed bounty-conversion outcome, `TRACKER_WRITE_BLOCKED`, `Q1=UNKNOWN, NOT ZERO`, LayerZero parent Q3/PARKED with the known pinned-source subclaims killed, and Variational as not promoted because the studied path was provider-role-gated and no qualifying impact/PoC was established.
- It also records that the existing FORX-V 13-head acceptance packet was not `CLOSED_VERIFIED / PASS` and the conditional Reaper extension was `WAITING`. No current prompt/worker adoption or authorized transfer is assumed.
- An exact search for `BOUNTY_REAPER_EXECUTION_RECEIPT_20261020` and `BOUNTY_REAPER_EXECUTION_RECEIPT_20261021` found no later historical execution receipt in accessible indexed results. The 20 October artifact recovered is a pre-flight/hold receipt, not evidence of bounty work or a queue census.
- This recovered prior receipt does **not** change the current run's result: the new material evidence is the 2026-10-02 LayerZero implementation-binding gap and the bounded Symbiosis direct-Gateway path kill. It does not establish Q1=0 or provide a submission/award/payment receipt.

This addition reconciles later accessible prior state; it does not erase the earlier receipts or declare the inaccessible Tracker/Drive history complete.


## 10. Continued executable parcel checks — 1inch and Variational

### A. 1inch OrderRegistrator timestamp / latest-release gate — A / KILLED FOR THIS CLAIM

Freshly fetched the current official release list, current Immunefi scope/rules and source files from `1inch/limit-order-protocol`.

- GitHub Release page calls `v4.3.4` **Latest**, published 24 September 2026: https://github.com/1inch/limit-order-protocol/releases
- Official Immunefi scope last updated 14 October 2026: https://immunefi.com/bug-bounty/1inch-SmartContracts/scope/
- Official rules/info: https://immunefi.com/bug-bounty/1inch-SmartContracts/information/
- `contracts/helpers/OrderRegistrator.sol` at tag `4.3.4`: blob `c16e30831f6c44c88b4e1e7ece8f560c9301922e`. The tagged version validates the order extension and signature and emits `OrderRegistered`; it has no `announcedAt` mapping or first-registration timestamp.
- The current default branch source blob `0317e58286e438d246a95c742851797b51a655ec` contains `announcedAt[orderHash]`, a write-once timestamp and `OrderAlreadyRegistered`. The public feature commit/PR is known from previous receipt: PR #435, commit `e92c8bd3336d6bceb7bcba67d4f0c32ec73b6da5`.
- The current program says it applies only to the latest tag/releases, requires PoC and KYC, excludes theoretical/speculative exploits without demonstrated business impact, and expressly prohibits AI-generated reports. The scope table names generalized new asset classes, but the exact deployed `OrderRegistrator` asset/implementation is not independently bound in this run.

**Disposition:** The previous timestamp-front-running hypothesis depends on the `announcedAt` behavior visible on `main`, not the current latest tagged `4.3.4` source. No qualifying theft/freezing/business impact was established, and the live program bars AI-generated reports. Mark this precise hypothesis **A — KILLED / NO PROMOTION / NO REPORT**. Do not turn the main-branch-only feature into a candidate against a latest-release-only program. No code was edited, no local test was run, and no submission was attempted.

A separate read-only screen of 4.3.4 `NativeOrderFactory.sol`, `NativeOrderImpl.sol`, `native-swap.md`, and relevant existing `LimitOrderProtocol.js` test sections found the checked cancellation/reward mechanics and access checks explicitly covered by source/tests: factory create requires maker = caller and `msg.value == makingAmount`; factory rescue is owner-gated; clone cancellation is maker-gated, while resolver cancellation requires the configured access token and expiry; reward is caller-bounded by `rewardLimit`; the tagged tests cover reward delay, no-reward cancellation, role gate and repeat cancellation. The reviewed boundary case where a caller chooses a reward limit greater than the remaining clone balance would revert, but that caller can choose a lower limit/zero; the reviewed path does not establish an unprivileged victim loss. **No new 1inch Q2/Q1 parcel established** by this screen.

### B. Variational Arbitrum batch / zero-UUID hypothesis — bounded kill of public-attacker route; parent remains B

Existing candidate source is pinned in the earlier Reaper evidence sidecar `tradewife/night-shift-security@ddbfce3af1ec3e8ac64f295c3216587b01015029`; it is a research harness, not represented as the authoritative deployed repository.
- `SettlementPool.sol` blob `64a140bb950cded4180cc5985b0e8c5aa8cab056`: `batchDepositUSDCAtomic` is `onlyOracle`; `depositUSDCAtomic`, `depositUSDCOnBehalfOfParty`, `withdrawUSDC`, and related treasury methods are likewise Oracle-gated; ordinary party `depositUSDC` is `onlyParties` and expressly rejects `transferUuid == 0`.
- `Oracle.sol` blob `9917390ef1add55e9e032a14b0559e00628f1602`: public atomic/batch paths are `onlyRole(PROVIDER_ROLE)`; the batch verifies the registered pool, creator address and membership of each other party before forwarding items.
- `SettlementPoolFactory.sol` blob `c09719edf61bf8fe935144be1911b96bd5529e8a`: pool creation remains owner-or-Oracle gated.
- Existing `VariationalFalsifier.t.sol` blob `e41938cb17de13a4a09a1b0f10e32bff97a77433` includes a sidecar assertion for repeat creator deposit per item and a zero-UUID freeze claim, but this runtime only read the file; it did **not** execute the Foundry test. The harness assumption that creator amount should be deposited only once per batch is not established by the source/API contract here, so the asserted excess is not accepted as proof of a bug.
- A zero UUID in an Oracle-supplied batch can bypass the nonzero-UUID replay marker, but the relevant batch entry is provider-role-gated, and the reviewed evidence does not establish an unprivileged actor who can force the trusted provider to submit zero UUIDs. Withdrawals also have nonzero-ID validation at the ordinary party entry point and an Oracle-mediated recovery path. No permanent freeze, theft, victim loss or privilege-free attack is demonstrated by this sidecar.

**Disposition:** Kill the specific **unprivileged public caller can directly trigger the provider-only batch/zero-UUID freeze** theory on the reviewed path. Keep the parent candidate **B — NOT PROMOTED** rather than claiming the whole deployed system safe: exact authoritative deployed-source equivalence, trust boundary/API semantics, qualifying impact and a compliant runnable local/fork PoC are not all established. No live chain call, transaction, funds movement, or external submission occurred.

## 11. Queue/lifecycle control remains open

The direct read-only fetch of the canonical Google Sheet URL returned `login_required`. Current tool inventory exposes no authorized Google Sheets append/update/readback action; no authenticated browser run could be performed through the metered browser route in this runtime. Therefore `Runs/Queue/Payouts` remain unread; no Tracker Runs row is claimed; `TRACKER_WRITE_BLOCKED` persists and Q1 is still `UNKNOWN_NOT_ZERO`.

No public programme was bypassed, and no report was submitted. The current screening has killed/narrowed claims but has **not** produced a ready private report or external receipt. Preserve the existing Root Intake fallback and same-flight register; don't create an alternative tracker.

### Continued-work status

- LayerZero `BR-20261003-024`: C/Q3 PARKED; 2026-10-02 proxy-implementation change remains an unclosed deployment/source-binding gate; older pinned-source subclaims and generic compensation premise are killed/public audit prior art.
- Symbiosis MetaRouterGateway direct-theft theory: A / KILLED on reviewed source path.
- 1inch OrderRegistrator timestamp-front-running theory: A / KILLED under latest-release boundary.
- Variational public-attacker batch/zero-UUID theory: specific public route killed; parent remains B / NOT PROMOTED.
- Q1 queue: UNKNOWN_NOT_ZERO. Official bounty submissions/awards/verified payments evidenced in this wake: none.

This extension records further bounded work; it is not an assertion that the objective passed. Resume with authoritative Q1 recovery when the existing Tracker route is restored, and promote only an independently evidenced, eligible finding.
