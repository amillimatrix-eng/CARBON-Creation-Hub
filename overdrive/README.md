# AMX OVERDRIVE

Durable commercial execution control for the AMilliMATRiX capability estate.

## Cadence
- Primary heartbeat: every 60 seconds on an AMX/self-hosted runner: `python3 overdrive/runner.py tick`
- GitHub recovery heartbeat: every 5 minutes.
- Each tick resumes the furthest evidenced state. It does not restart completed work.

## State chain
DISCOVERED -> QUALIFIED -> OFFERED -> RESPONDED -> NEGOTIATING -> CONTRACTED -> INVOICED -> PAID

## Manager lanes
DISCOVERY, CONVERSION, PRODUCTION, DISTRIBUTION, TECHNICAL, CRITIC, EVIDENCE.

Nothing is marked complete because research/build/activity occurred. Commercial terminal state is PAID; irreducible external gates are recorded explicitly.

## Safety
No secrets in repository. No bypass of OTP/CAPTCHA/KYC/provider controls. External actions require configured adapters. Dry/no-adapter ticks create auditable work receipts rather than fabricate execution.
