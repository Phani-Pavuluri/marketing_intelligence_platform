# Repository Checkpoints

**Status:** verified remote-main inventory
**Owner:** MIP program owner; repository owners verify their own artifacts
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** MIP `89caf56e73e814b6f5e0d0584536f8705ac97803`; MMM `origin/main` `9a3aa5cb9a48c9a59d45e266685228835237f328`; GeoX `origin/main` `860182386c39f487747de5f43e67a31e9978e57c`
**Update trigger:** `origin/main` changes relevant to P2 or a D6 release packet.

| Repository | Verified on main | Canonical commits and paths | Active/unresolved work | MIP runtime dependency and caveat |
|---|---|---|---|---|
| MIP | `89caf56` | `c038178` roadmap consolidation; `fa4dfdf` and `89caf56` P2 design; `docs/roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md` | Fixture-only P2 implementation is only eligible for later separate authorization. | Consumer views are design only; no package call, persistence, or runtime adapter is canonical. |
| MMM | `9a3aa5c` | `20f22f7` `mmm/contracts/public_simulation.py`, `tests/fixtures/mip_export/simulation_v1/`; `9a3aa5c` `mmm/contracts/calibration_compatibility.py`, `tests/fixtures/mip_export/calibration_compatibility_v1/` | Strict GeoX-readout normalization adapter, certified cross-repository fixtures, and D6 pins/release evidence remain expected. | Public export and compatibility foundation are verified on main; the former public-simulation-handoff lane is superseded as a plan, not its verified artifacts. |
| GeoX | `8601823` | `fe2e97f` numerical-truth generator; `2fbfaf1` validation checkpoint; `9b74696` `panel_exp/contracts/geox_governed_experiment_readout.py`; `8601823` `tests/fixtures/geox_governed_readouts/` | Builder/package entrypoint, typed temporal boundaries, deterministic freshness/expiry, record-level envelope kind/schema, package-version semantics, and D6 checkpoint are unverified/pending. | Fixture contract/readouts are verified; no canonical main evidence establishes a production-ready builder or runtime handoff. |

Sibling local worktrees were not used as evidence: MMM and GeoX had only local
`docs/tasks/` untracked content at verification. Local feature branches are not
canonical. Reported statements without the listed remote-main source remain
unverified until their owner supplies a committed path and pin.
