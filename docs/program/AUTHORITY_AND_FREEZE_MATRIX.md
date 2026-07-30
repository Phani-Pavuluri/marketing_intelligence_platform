# Authority and Freeze Matrix

**Status:** current authority snapshot; unchanged by this packet
**Owner:** MIP program governance with named engine owners
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** MIP `89caf56`; MMM `origin/main` `9a3aa5c`; GeoX `origin/main` `8601823`
**Update trigger:** explicit authorization, gate completion, or capability retirement.

| Capability | Owner | Current state | Evidence or prerequisite | Next authority gate |
|---|---|---|---|---|
| Fixture-only MIP P2 implementation | MIP | approved; not authorized_for_execution | MIP P2 design and certified producer fixtures | explicit MIP task authorization |
| Live GeoX integration | GeoX/MIP | blocked | builder, D6, environment gate | R4/R5/R6 authorization |
| Live MMM integration | MMM/MIP | blocked | adapter, D6, environment gate | R4/R5/R6 authorization |
| GeoX analytical readout authority | GeoX | implemented/validated fixture evidence | governed-readout contract and fixtures | no MIP authority transfer |
| MMM compatibility authority | MMM | implemented/validated fixture evidence | compatibility contract and fixtures | no MIP authority transfer |
| MIP ExperimentEvidence export | MIP/GeoX | blocked | final contract and D6 packet | explicit export authorization |
| CalibrationSignal export | MMM/GeoX/MIP | blocked | normalized readout and compatibility evidence | explicit export authorization |
| TrustReport production assembly | MIP | blocked | artifact lifecycle, security, release evidence | R2/R5/R6 |
| Real customer data / uploads | MIP | blocked | security, tenancy, retention/deletion | R5 explicit authorization |
| Persistent customer artifacts | MIP | blocked | lifecycle, access, retention/deletion | R2/R5 explicit authorization |
| Scheduled jobs | MIP | blocked | jobs/recovery/SLO ownership | R5/R6 |
| Candidate generation / optimization | MMM/MIP | deferred | P6 authority and governed optimizer truth | separate capability authorization |
| Recommendation proposal/approval/execution | MIP/humans | deferred | RecommendationContract, human workflow, evidence gates | separate proposals and approval gates |
| Automatic MMM refit / model promotion | MMM | blocked | model governance and promotion evidence | explicit MMM/MIP authority |
| Treatment assignment | GeoX/humans | blocked | governed assignment and human approval | separate high-risk authorization |
| Pilot / production | program owners | blocked | R5/R6 and successful prior evidence | explicit pilot/production authorization |
| Package-side agents | engine owners | deferred | ownership, safety, and runtime authority | separate architecture/authority decision |
