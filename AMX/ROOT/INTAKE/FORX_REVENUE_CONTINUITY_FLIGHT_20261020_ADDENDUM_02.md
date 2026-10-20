# FORX REVENUE-CONTINUITY FLIGHT — ADDENDUM 02 — CURRENT NOTICE GATES / MANIFEST V10

**Existing flight:** AMX-FLT-20261020-FORX-112604-e36918bb  
**Authorization:** AMX-AUTH-20261020-FORX-112604-cf4bfa22  
**Observation time:** 2026-10-20T12:09:30Z / 14:09:30 SAST  
**Status:** IN_FLIGHT — current official notice details and hard gates reconciled; all items still RAW_UNQUALIFIED pending iSCOPE review.  
**Primary flight packet:** [Segment 01](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/blob/main/AMX/ROOT/INTAKE/FORX_REVENUE_CONTINUITY_FLIGHT_20261020_112604Z.md)  
**Earlier append/readback record:** [Addendum 01](https://github.com/amillimatrix-eng/CARBON-Creation-Hub/blob/main/AMX/ROOT/INTAKE/FORX_REVENUE_CONTINUITY_FLIGHT_20261020_ADDENDUM_01.md)

## Canonical staging readback

- Manifest `overdrive/forx_staging/manifest.json`: blob `b1c01fb1eef1ae5f73d411df7a06d86eb786d124`, manifest version 10, next sequence 11, 954 current unique source keys, 961 gross observation versions.
- Delta 0009: `overdrive/forx_staging/delta-0009-forx-20261020-open-procurement-systems.json`, blob `01107aafd408b230097eae6d882e94fa9d25a64d`, sequence 9, six raw signals.
- Delta 0010: `overdrive/forx_staging/delta-0010-forx-20261020-procurement-current-gate-upserts.json`, blob `3395f685cd3b63846941296fa6eecd375a72a138`, sequence 10, three same-source-key upserts that refine current hard gates for UNDP Sierra Leone, UNICEF Moodle, and UNDP Philippines.
- The source-upsert batch reuses three existing source keys/record IDs. It adds zero unique-source-key growth. Gross observation versions increase from 958 to 961. No commercial ledger entries were changed and no revenue is credited by staging.

## Updated evidence and dispositions

### P1 — UNDP Sierra Leone real-time trade-data platform

Official notice: https://www.ungm.org/Public/Notice/317127  
Official procurement-notices page: https://procurement-notices.undp.org/view_negotiation.cfm?nego_id=50409  
Reference: UNDP-SLE-00334 / RFP-019/26. Current notice deadline: 22-Oct-2026 23:59 New York time (2026-10-23 03:59Z / 05:59 SAST).

The notice requires a “qualified and experienced firm” and describes an integrated bilateral trade-data platform with data validation/updating, APIs/data governance, analytics/dashboards, market intelligence, tariff/customs/standards/rules-of-origin information, testing, training and handover. The official procurement page confirms use of UNDP Quantum and a no-duplicate-profile rule.

**Hard-gate access blocker:** the linked UNDP SharePoint solicitation folder redirected to a Microsoft 365 Security/login page; no TOR content, evaluation thresholds, required comparable project references, legal registration/turnover requirements, budget or payment milestones were retrieved. The fact that the public notice describes suitable system-building work does not establish bidder eligibility. iSCOPE should only advance if the actual firm/entity, references, trade-domain expertise, delivery team and portal access can be proven from available evidence before the deadline. If not, kill/hold the bid. Do not contact the procurer or submit from FORX.

### P2 — UNICEF Moodle Workplace LMS

Official notice: https://www.ungm.org/Public/Notice/311133  
Reference: RFPS 503950. The current notice header says **25-Oct-2026 23:59 (GMT+1)**, corresponding to 22:59Z. However, the text of Amendment No. 2 on the notice says the extension is to **25 October 2026 at 23:59 CEST**, which would correspond to 21:59Z. This is a one-hour timezone inconsistency and must not be silently rationalized. Use **2026-10-25 21:59Z / 23:59 SAST as the conservative internal cutoff** until iSCOPE independently verifies the controlling amendment or the tender-system timestamp.

The public notice says Technical and Commercial Proposals should be sent as separate emails to `supplybid@unicef.org`; each email including attachments is limited to 25 MB, batches may be used, and the proposal must remain valid for at least 180 days. The notice lists TOR annexes, price schedules, Amendment No. 1/No. 2, Q&A, Data Processing Agreement and Agora plugin documents. Attempted direct Amendment No. 2 download returned 403; detailed Moodle experience criteria, DPA obligations, service/hosting levels and pricing remain uninspected.

iSCOPE must verify the controlling deadline and hard gates (Moodle Workplace references, hosting and support capability, SLA, information-security/DPA compliance, delivery capacity, price/margin) before recommending any response. Nothing has been emailed or submitted.

### P3 — UNDP Philippines circular-economy / solid-waste information-management platform

Official notice: https://www.ungm.org/Public/Notice/318058  
Reference: UNDP-PHL-00981. Deadline: 28-Oct-2026 05:00 GMT-4 = 2026-10-28 09:00Z / 11:00 SAST.

The current official notice says the pre-bid conference occurred on 19-Oct-2026 via Zoom (Philippine time) and the confirmation-of-attendance deadline was 16-Oct-2026. Both dates have passed. The notice does not clearly establish from the accessed text whether attendance is a mandatory eligibility condition. iSCOPE must check the tender and, if the session was mandatory or otherwise required for eligibility, promptly kill the route. Do not imply the pre-bid session was attended or that an extension is available.

### P4 — UNDP Bosnia and Herzegovina programme-budgeting software

Official notice: https://www.ungm.org/Public/Notice/318176  
Reference UNDP-BIH-01681. Deadline displayed as 29-Oct-2026 10:00 GMT-4 (14:00Z / 16:00 SAST). Still RAW_UNQUALIFIED pending review of the full solicitation, required budgeting/finance references, integrations, deliverables, portal route and economic terms.

### P5 — WTO OSH management software

Official notice: https://www.ungm.org/Public/Notice/315503  
Reference RFP-2026-238-WTO. Deadline displayed as 28-Oct-2026 14:00 GMT+2 (12:00Z / 14:00 SAST). The notice expressly seeks a well-established firm. Hard-fit hold remains until OSH product/functionality, vendor-size/establishment, delivered references, security and implementation criteria are verified.

### Lower priority — UNESCO correspondence-management RFI

Official notice: https://www.ungm.org/Public/Notice/309729  
Deadline: 30-Oct-2026 17:00 GMT+1 (16:00Z / 18:00 SAST). This is an RFI for solution information and indicative TCO, not an award or established paid demand. Keep below executable paid routes unless an evidence-backed product/partner fit justifies the work.

## Handoff / action order

1. iSCOPE to obtain or verify the controlling deadline and firm-eligibility requirements for the Sierra Leone opportunity; no bid recommendation while the full TOR is unavailable.
2. iSCOPE to resolve the UNICEF cutoff conflict and Moodle-specific capability requirements.
3. iSCOPE to determine if the missed Philippines pre-bid session is a mandatory gate; kill quickly if eligibility fails.
4. Triage Bosnia and WTO only after P1–P3 hard gates; preserve UNESCO as market intelligence, not revenue.
5. FORX continues broad lawful public-source and direct-buyer discovery in parallel and consumes only attributable downstream outcomes. The six records remain RAW_UNQUALIFIED. No outbound buyer contact, bid, award, invoice, acceptance or money-in is recorded.
6. Root/T-GOV still owns the flight pointer in `AMX/ROOT/INTAKE/INTAKE_INDEX.md`. Two prior writes failed with 409 blob-SHA conflicts; no Index pointer update is claimed. The existing Index must be reread at the latest main-head and updated in a serialized write, preserving concurrent changes.
7. The existing `FIRST BREATH — FORX Continuous Play Sweep` run request was accepted, but the last recorded run timestamp did not advance. The separate scheduled worker’s output remains unverified. The flight continues under its own explicit register events; do not call the scheduler acknowledgement proof of worker execution.

## Directive 23

- **Expected outcome:** hard-gate research preserved in the source records; iSCOPE directed to the highest-value routes with accurate deadline and eligibility constraints; no invented readiness or revenue; existing runtime and record histories preserved.
- **Owner:** FORX for source discovery and provenance; iSCOPE for qualification/kill decisions; PRI for any separately authorized external commercial submission; Root/T-GOV for Intake index and flight closure.
- **Action:** perform the sequence above; continue alternative discovery while inaccessible procurement documents or eligibility remain unresolved.
- **Dependencies:** authenticated/unrestricted access to controlling solicitation documents where required; evidence of legal bidder identity, delivered references and technical capacity; Index pointer write at a current serialized head.
- **Evidence:** official notices linked above; delta-009/manifest-v9; delta-010/manifest-v10; current portal-fetch outputs; issue comments on existing iSCOPE Issue #4 and Root Issue #31.
- **Readback/persistence:** all three current source records, manifest v10, delta-009 and delta-010 were fetched after writes; current Root/iSCOPE route comments were created and must be independently read back with the next register checkpoint.
- **Safety/preservation:** no new contact, no bid, no duplicate profile, no spend, no guessed cutoff, no false award/payment, no overwrite of concurrent index state.
- **Disposition:** CURRENT SOURCE GATES PERSISTED / FLIGHT IN_FLIGHT.
- **Remaining work:** iSCOPE gate outcomes; Root Index pointer serialized write; continued discovery; separate scheduled-worker receipt if exposed; eventual post-flight deep sync and explicit Root landing.
