# Repository Checkpoints

**Status:** verified remote-main inventory
**Owner:** MIP program owner; repository owners verify their own artifacts
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31
**Verified against:** MIP `main` `18ab0d0c798dfcedd3f07034f4561320929477ea`; MMM `origin/main` `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`; GeoX `origin/main` `ee9673c13e69082367c1727568946ac4c1a01015`
**Update trigger:** `origin/main` changes relevant to P2 or a D6 release packet.

| Repository | Verified on main | Canonical commits and paths | Active/unresolved work | MIP runtime dependency and caveat |
|---|---|---|---|---|
| MIP | `18ab0d0` current main / `3520176` prior coordination closure | P2 design plus merged coordination-control-plane metadata; remote feature cleanup was observed. | Fixture-only P2 work and the context resolver remain separately unauthorized. | Consumer views are design only; no package call, persistence, or runtime adapter is canonical. |
| MMM | `1b75d1d` | `mmm/contracts/public_simulation.py`, `mmm/contracts/calibration_compatibility.py`, and five compatibility fixtures. | Protocol adoption, strict GeoX normalization, certified cross-repository fixtures, and D6 evidence remain proposed/open. | MMM owns compatibility truth; completion of a producer task still requires consumer verification. |
| GeoX | `ee9673c` observed / `e0cef94` prior closure | governed-readout contract and 12 certified fixtures; live authorized task `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001` at authorization `c4c9059`. | One producer-owned task covers temporal/version semantics and builder/package entrypoint; full producer validation debt remains. | GeoX owns experiment truth and handoff eligibility; no consumer or runtime handoff is authorized. |

Sibling local worktrees were not used as evidence: MMM and GeoX had only local
`docs/tasks/` untracked content at verification. Local feature branches are not
canonical. Reported statements without the listed remote-main source remain
unverified until their owner supplies a committed path and pin.

The current coordination snapshot and dependency ledger are
[`CROSS_REPOSITORY_COORDINATION_STATE.json`](CROSS_REPOSITORY_COORDINATION_STATE.json).
