# AMX INTAKE — OPPORTUNITY DEPLOYMENT BRIEF ARTIFACT SKILL

Status: COMPLETE_FOR_GOVERNANCE_REVIEW — NOT YET PROMOTED/ACCEPTED
Date: 2026-10-04
Origin: Owner upload

## Submitted package
The complete submitted skill package is now durably preserved in the AMX Library intake estate:

`/AMX/ROOT/INTAKE/ARTIFACT_SKILLS/AMX_OPPORTUNITY_DEPLOYMENT_BRIEF_2026-10-04/`

Files:
- `SKILL.md`
- `artifact-template.json`
- `openai.yaml`
- `assets/reference.docx`
- `assets/preview.png`

## Exact integrity
- SKILL.md SHA-256: `cfee83bafa50903907cfde51ac508a6697ea7cd164cdb6ca35717c5b713327ac`
- artifact-template.json SHA-256: `54586c722449d873eb16ed211e8591a179f31da5e245dcc82800df649380b127`
- openai.yaml SHA-256: `e7b7ca733ed8d950efc8e046e56a209f6c4beb618ac8381f201ee089ddf97ff6`
- assets/reference.docx SHA-256: `12b888b577e78a9f14998d279e762991ff184ff1c3f454b01995be55fa7142cd`
- assets/preview.png SHA-256: `8f05842ea441973ab651714c5d1dccf9621bdb32e63a743771aed38a09ac81fc`

## Durable Library references
- SKILL.md: `libfile_789736cb77d88191a4502522b2273a0b`
- artifact-template.json: `libfile_5cdd487bde4081918366cc84ae9fbc55`
- openai.yaml: `libfile_18135bffb0e881919101c9cff594cedf`
- assets/reference.docx: `libfile_28db2bf5017c81919bd22fe4d215aaed`
- assets/preview.png: `libfile_7a15fd95a7b081918076061d3e0a89d7`

## Intended capability
Artifact template: AMX Opportunity Deployment Brief.

The package defines a reusable document-generation workflow for evaluating and governing high-upside opportunities using fixed scoring, ownership boundaries, cloud-launch gates, evidence requirements, and human approvals.

The retained reference itself states that a score of 70 or more can justify a capped, time-boxed trial, but does not represent a 70% probability of revenue/payment, and financial planning assumes the first trial returns zero until benchmark evidence exists.

## Package relationship
`artifact-template.json` resolves:
- reference: `assets/reference.docx`
- preview: `assets/preview.png`

`openai.yaml` uses the same preview asset for small/large icons and declares the default prompt for this template.

The retained reference assets are now present in the durable intake package. The earlier INCOMPLETE_FOR_EXECUTION condition caused by missing assets is therefore CLOSED.

## Governance / implementation request
1. Preserve the submitted package exactly as provenance.
2. Reconcile against existing AMX opportunity/intake/governance machinery.
3. Avoid duplicate workflow creation if capability is already covered.
4. Preserve ownership/identity separation, scoring semantics, launch gates, evidence requirements, and human-approval boundaries from the retained reference.
5. Preserve template fidelity: the retained reference controls layout/formatting unless Owner explicitly overrides.
6. Do not invent facts merely to fill template fields.
7. Do not promote to operational/accepted skill merely because the files are complete; require normal governance disposition and one rendered fidelity/acceptance test.
8. Disposition through normal intake: ACCEPT / MERGE / AMEND / REJECT / HOLD.

## T10
Supposed outcome: intake the complete AMX Opportunity Deployment Brief skill/template package.
Actual outcome: all five package files are durably preserved with exact hashes and retained asset paths resolved.
Proof: Library upload receipts plus exact SHA-256 values above.
Changed: prior missing-asset blocker is closed; package is COMPLETE_FOR_GOVERNANCE_REVIEW.
Still unproven: governance acceptance, activation, invocation behavior, and rendered document fidelity under the installed skill runtime.
