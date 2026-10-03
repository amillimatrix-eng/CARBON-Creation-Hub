# Minimal extension plan

Use the existing backend for continuity projection, the existing BLACK worker for
execution, the existing EvidenceStore for learned capability records, and existing
House/operator state for observability. No new daemon, worker or dashboard.

1. Add a validated source registry and encrypted content-addressed recovery store
   using cryptography Fernet (authenticated encryption), chunked bounded memory,
   atomic immutable manifests, locks, hashed reconstruction and retention.
2. Add local/Git-tracked-file, SQLite backup and configured rclone Drive adapters.
   Pin accepted source/config hashes. Provider loss uses verified recovery, never
   creates authority. Sync every source independently and record partial failure.
3. Extend BLACK with typed continuity adapters and exact-command scoped grants;
   separate queue fetch from code deployment, journal interruption, retain pending
   receipts, remove public raw output, provide one hardened systemd timer.
4. Extend EvidenceStore with attributable outcomes, typed lessons, tested candidates,
   versioned grants/capabilities and promotion compare-and-swap. Integrate the
   existing Reaper through a bounded filtering adapter and durable learning cycle.
5. Feed existing House/operator/API surfaces with safe health summaries. Fix
   private-version read leakage, workflow permissions and ignored secret/runtime
   files. Preserve original frontend and commercial behavior.
6. Exercise offline restore, corrupted chunks/manifests, failed/partial source,
   retries, duplicate jobs, unauthorized promotion, mandate drift, and real
   repository-derived Reaper filtering. Produce tests/security/commission receipts.
7. Reconcile touched files against latest main, push a review branch via the
   connected GitHub Git Data API, trigger existing CI and read back all changes.

Human involvement is bounded to unavailable machine/credential/key-custody gates.
Enrollment is one command on the existing BLACK installation; subsequent sync,
verification, restore tests and gate reassessment are periodic and idempotent.
