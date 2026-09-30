# AMX ACCESS CONTINUITY MANIFEST

Purpose: prevent loss of operational access when any single interactive workspace, Work session, Coffee instance, connector, or transport becomes unavailable.

## Custody invariant
No operationally necessary state may exist only inside one ChatGPT Work/workspace/session.

Work is an execution surface, not sole custody.

## Independently reachable recovery surface
Repository: amillimatrix-eng/CARBON-Creation-Hub

Recovery order:
1. CONTINUITY.md
2. ACCESS_CONTINUITY.md
3. overdrive/state.json
4. overdrive/opportunities.json
5. newest overdrive/receipts/
6. open repository issues
7. latest workflow runs
8. releases/ and RIGHTS.md

## Workspace-loss rule
If a ChatGPT Work/workspace becomes unavailable:
- do not treat its unavailability as loss of authority, state, completion, or cancellation;
- resume from the durable recovery surface;
- preserve the inaccessible workspace identifier as a pointer if known;
- do not recreate completed systems merely because the workspace transport is unavailable;
- recover only missing operational material through an authorized reachable source.

## Redundancy requirement
For every operational dependency, maintain:
- authoritative object/pointer;
- independently reachable recovery pointer or copy where permitted;
- latest evidenced state;
- invocation/access route;
- last receipt;
- next action;
- access status: VERIFIED / DEGRADED / UNVERIFIED.

## Access acceptance
A pointer is not enough. Access continuity is VERIFIED only after an independent surface can read back the required recovery material.

## Security
Do not duplicate secrets, credentials, private tokens, KYC material, or restricted customer data into public repositories. Store references and recovery instructions only where duplication is not authorized.

## Closure
Loss of Coffee, Work quota, a workspace, browser transport, or connector does not close work. Material terminal receipts close work.
