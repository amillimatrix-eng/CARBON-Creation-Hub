# Bounty Reaper — Segment 12 receipt
Observed 2026-10-19 19:48 SAST. Run BR-20261019-1948-SAST-03.
Flight `AMX-FLT-20261012-DSYNC-145440-9fb44f0c`, segment 12. Result: productive read-only configuration review; no bounty submission.

## Pre-flight
Registry v1.3 blob `bcfd1f422bd25ba852666a538712828d594759e8`; recomputed root `96c0beb3328ebefc16286d93a7baadc0ff4be0a17c1e6a8718b89de94f58df1a` matches. Blue State blob `213ce700c3f5b7e6fa96481436b956323d338ccb`. Bounty Reaper mandate CURRENT; digest `754d8fb9b6816da1bf0013940883106e0d3928b1637526ee82b38e1792c1dcd3` matches. Existing Reaper task `6abf8e6d6a188191aee2b5d3fe24a9c9` is enabled, but its prompt still uses registry v1.2 and lacks the required 13-head/every-flight contract; adoption is unresolved.

## Tracker and lifecycle
Canonical Live Tracker `1ETiK6b2YOz499OXBA5wuvgyWMjnDZoEdJIwCt2xGeCk` cannot be read/written by an authorized Sheets/Drive route here. No Runs row/readback is claimed. `TRACKER_WRITE_BLOCKED`; Q1 `UNKNOWN, NOT ZERO`. Accessible durable receipts show 0 verified external submissions, report IDs, awards or payments; the lifetime total remains unknown.

## Stargate existing signal — five fresh read-only configuration checks
Target: Ethereum FeeLibV1ETH `0x3E368B6C95c6fEfB7A16dCc0D756389F3c658a06`; source blob `bea4e8a01305bb91e68027ef6e8afa08bc0ace31`. Current program scope lists FeeLibV1ETH; official references: [Immunefi scope](https://immunefi.com/bug-bounty/stargate/scope/) and [mainnet contracts](https://docs.stargate.finance/resources/contracts/mainnet-contracts).

Latest read-only `feeConfigs(eid)` tuples `[paused,z1Bound,z2Bound,z1Ppm,z2Ppm,z3Ppm,rewardPpm]`:
- EID 30183: `[false,0,0,100,100,100,0]`
- EID 30181: `[false,0,0,800,800,800,0]`
- EID 30214: `[false,407905,1223716,1417,1403,1397,0]`
- EID 30151: `[false,415203,1245611,421,406,600,0]`
- EID 30138: `[false,0,0,0,0,0,0]`

Rates are millionths; 1,000,000 ppm equals 100%. None of these five additional samples is close to 100%. EID 30183, which had previously returned HTTP 429, now returned valid state. Earlier receipt `BOUNTY_REAPER_EXECUTION_RECEIPT_20261015_1445_SAST.md` documented EIDs 30101/30102/30106/30109 as zeroed and 30110/30111/30184 as 100 ppm. Thus the 100%-fee hypothesis is **KILLED for the sampled routes only**; unqueried routes remain unknown. No configuration was changed and no submission was made.

## 13-head continuation note
The current Reaper prompt still does not consume the persisted 13-head method. The prior same-flight Root Intake report records the complete 13-head gap and existing-owner remedies. This receipt adds the five route readbacks; it does not claim FORX-V acceptance or runtime adoption.

1. Instigator — sampled values contradict 100% premise → seek distinct deviation → Reaper.
2. Specification — use actual state, not theoretical bounds → preserve exact tuples → Reaper.
3. Provenance — source/address/EIDs recorded → retain source links → Reaper.
4. Efficiency — EID 30183 rate limit resolved → no retry loop → Reaper.
5. Continuity A — Tracker unavailable → restore authorized access → ROOT.
6. ROI — no bounty lifecycle success → continue existing eligible work → Reaper.
7. Failure node — Tracker and prompt drift are separate → repair separately → ROOT/T-COD.
8. Routing — submit only through official program → no unsupported submission → Reaper.
9. Continuity B — current sample not anomalous → do not revive claim → Reaper.
10. Verification — view-call results recorded → read back receipt → Reaper.
11. Optimization — route sample narrowed → continue next executable parcel → Reaper.
12. Weighted continuation — preserve only distinct residuals → continue flight → Reaper.
13. Literal test — submitted? no; paid? no; five route reads? yes → keep flight open → Reaper.

Safety: read-only contract calls only. No live exploit, testnet/mainnet transaction, fund movement, spend, credential changes, external submission or public disclosure. Next: read this receipt back, update the existing Intake Index/issue #31, append and read back the same Segment 12 checkpoint. Keep Tracker and runtime-adoption blockers open.
