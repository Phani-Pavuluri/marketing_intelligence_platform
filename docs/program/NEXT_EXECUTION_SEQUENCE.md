# Next Execution Sequence

**Status:** proposed sequencing; no step is authorized by this file
**Owner:** MIP program owner with MMM and GeoX owners
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31
**Verified against:** MIP `3520176`; MMM `origin/main` `1b75d1d`; GeoX `origin/main` `ee9673c`
**Update trigger:** a prerequisite merge, D6 packet, or explicit task authorization.

1. **GeoX and MMM:** adopt the coordination protocol in parallel (proposed only).
2. **GeoX:** complete its single authorized governed-readout builder/package
   entrypoint task, which includes temporal, freshness, record-kind, schema,
   and producer-version semantics.
3. **MMM:** implement strict GeoX-readout normalization and certified
   cross-repository compatibility fixtures.
4. **MIP:** after separate authorization, implement the fixture-only P2
   planning-evidence journey.
5. **All owners:** reconcile D6 and consider a separately authorized
   fixture-only cross-repository dry run.
6. **Program governance:** seek separate authorization before any live package
   integration.

The merged coordination control plane is a completed prerequisite. Steps 1 and
2 may proceed in parallel where their own repository gates permit.
GeoX authorizes its own builder task; MIP coordination cannot add a dependency
or authorize that task. Step 4 depends on live merged GeoX producer evidence
and declared consumer verification; steps 5–7 depend on all prior producer and
consumer evidence. Live engines, real
data, P6 decision workflows, pilot, and production remain blocked future phases.
