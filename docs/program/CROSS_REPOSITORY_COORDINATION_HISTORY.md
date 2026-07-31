# Cross-Repository Coordination History

**Status:** append-only program event ledger
**Coordinator:** MIP program governance

| Date | Event | Evidence | Cross-repository impact |
|---|---|---|---|
| 2026-07-30 | MIP V2 workflow recovery closed | MIP `38f88467f55d5bc4cc64e5a58b0f08f1639a40d0` | Established the conforming MIP V2 closure; no product authority changed. |
| 2026-07-30 | MMM V2 workflow reconciliation closed | MMM `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421` | Preserved MMM compatibility/public-simulation evidence and closed workflow governance; no new engine authority. |
| 2026-07-30 | GeoX import-health recovery and V2 adoption closure | GeoX `e0cef94c063b03b29e1e1760fb1c2320ce497b56` | Preserved governed-readout fixtures and import health; builder work remains separately authorized in GeoX. |
| 2026-07-31 | P2 readiness reconciliation superseded before execution | MIP `631763cfb75fc42f8b1bf7025c5bce34c39097b5` | Replaced a one-time checkpoint refresh with durable coordination control-plane work. |
| 2026-07-31 | Coordination-control-plane task authorized | MIP `631763cfb75fc42f8b1bf7025c5bce34c39097b5` | Creates the pinned coordination snapshot and blocker lifecycle; no capability authority. |
| 2026-07-31 | GeoX governed-readout builder authorized | GeoX `ee9673c13e69082367c1727568946ac4c1a01015`; authorization `c4c9059a6a6e882a10a356350376d8a64fb14057` | Separate from the V2 closure: one GeoX-owned task advances temporal/version semantics and the builder/package entrypoint; no MIP integration authority. |
| 2026-07-31 | Coordination snapshot reconciliation recorded | MIP correction branch `b0a9a9c1812b1ae1740d85fbb29827d60d338ebe`; MMM `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`; GeoX `ee9673c13e69082367c1727568946ac4c1a01015` | Corrects stale sibling pins and duplicate GeoX planning identities, adds live-overlay dependency resolution, and preserves all authority freezes. |

Historical nonconforming external workflow merges remain recorded in each
repository's execution history where relevant. They are governance evidence,
not approval, runtime, or capability authority.
