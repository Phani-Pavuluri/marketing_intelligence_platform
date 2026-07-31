# Repository Checkpoints

**Status:** verified remote-main inventory
**Owner:** MIP program owner; repository owners verify their own artifacts
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31
**Verified against:** MIP `631763cfb75fc42f8b1bf7025c5bce34c39097b5`; MMM `origin/main` `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`; GeoX `origin/main` `e0cef94c063b03b29e1e1760fb1c2320ce497b56`
**Update trigger:** `origin/main` changes relevant to P2 or a D6 release packet.

| Repository | Verified on main | Canonical commits and paths | Active/unresolved work | MIP runtime dependency and caveat |
|---|---|---|---|---|
| MIP | `631763c` observed / `4ddbe83` program checkpoint | P2 design plus authorized coordination-control-plane metadata. | Fixture-only P2 work remains separately unauthorized. | Consumer views are design only; no package call, persistence, or runtime adapter is canonical. |
| MMM | `1b75d1d` | `mmm/contracts/public_simulation.py`, `mmm/contracts/calibration_compatibility.py`, and five compatibility fixtures. | Protocol adoption, strict GeoX normalization, certified cross-repository fixtures, and D6 evidence remain proposed/open. | MMM owns compatibility truth; completion of a producer task still requires consumer verification. |
| GeoX | `e0cef94` | governed-readout contract and 12 certified fixtures. | Authorized builder/temporal/version task is producer-owned; full producer validation debt remains. | GeoX owns experiment truth and handoff eligibility; no consumer or runtime handoff is authorized. |

Sibling local worktrees were not used as evidence: MMM and GeoX had only local
`docs/tasks/` untracked content at verification. Local feature branches are not
canonical. Reported statements without the listed remote-main source remain
unverified until their owner supplies a committed path and pin.

The current coordination snapshot and dependency ledger are
[`CROSS_REPOSITORY_COORDINATION_STATE.json`](CROSS_REPOSITORY_COORDINATION_STATE.json).
