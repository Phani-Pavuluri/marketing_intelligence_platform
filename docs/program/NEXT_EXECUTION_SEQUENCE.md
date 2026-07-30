# Next Execution Sequence

**Status:** proposed sequencing; no step is authorized by this file
**Owner:** MIP program owner with MMM and GeoX owners
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** MIP `89caf56`; MMM `origin/main` `9a3aa5c`; GeoX `origin/main` `8601823`
**Update trigger:** a prerequisite merge, D6 packet, or explicit task authorization.

1. **GeoX:** resolve typed temporal boundaries, deterministic freshness/expiry,
   record envelope kind/schema, and producer package-version semantics.
2. **GeoX:** complete or verify the governed-readout builder/package entrypoint.
3. **MMM:** implement strict GeoX-readout normalization and certified
   cross-repository compatibility fixtures.
4. **MIP — Fixture-only P2 consumer and planning-evidence journey implementation:** after separate authorization, begin work from the merged design.
5. **All owners:** reconcile final producer/consumer contracts and exact pins.
6. **All owners:** complete D6 version, compatibility, release, rollback,
   migration, last-known-good, failure, and owner evidence.
7. **All owners:** after separate authorization, run a fixture-only
   cross-repository integration dry run.
8. **Program governance:** seek separate authorization before any live package
   integration.

Steps 1 and 3 may proceed in parallel where their own repository gates permit;
step 4 depends on its MIP authorization and certified compatible fixtures; steps
5–7 depend on all prior producer and consumer evidence. Live engines, real
data, P6 decision workflows, pilot, and production remain blocked future phases.
