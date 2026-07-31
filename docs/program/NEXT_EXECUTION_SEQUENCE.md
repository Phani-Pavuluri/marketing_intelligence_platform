# Next Execution Sequence

**Status:** proposed sequencing; no step is authorized by this file
**Owner:** MIP program owner with MMM and GeoX owners
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31
**Verified against:** MIP `631763c`; MMM `origin/main` `1b75d1d`; GeoX `origin/main` `e0cef94`
**Update trigger:** a prerequisite merge, D6 packet, or explicit task authorization.

1. **MIP:** complete the coordination-control-plane task.
2. **GeoX and MMM:** adopt the coordination protocol in parallel (proposed only).
3. **GeoX:** resolve governed-readout temporal, version, and envelope semantics.
4. **GeoX:** complete the governed-readout builder/package entrypoint.
5. **MMM:** implement strict GeoX-readout normalization and certified
   cross-repository compatibility fixtures.
6. **MIP:** after separate authorization, implement the fixture-only P2
   planning-evidence journey.
7. **All owners:** reconcile D6 and consider a separately authorized
   fixture-only cross-repository dry run.
8. **Program governance:** seek separate authorization before any live package
   integration.

Steps 1 and 3 may proceed in parallel where their own repository gates permit;
step 4 depends on its MIP authorization and certified compatible fixtures; steps
5–7 depend on all prior producer and consumer evidence. Live engines, real
data, P6 decision workflows, pilot, and production remain blocked future phases.
