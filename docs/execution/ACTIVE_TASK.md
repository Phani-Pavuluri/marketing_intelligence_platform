<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** merged

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_DELEGATED_ROUTINE_MERGE_PREFLIGHT_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `67c18c370e220cc4a7f84023f582b6c663aec947`
- **Authorization provenance:** `6874424383bbba1705fc2aaa4cd6d211637b9a8d`
- **Feature branch:** `feat/mip-delegated-routine-merge-preflight-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `a36822b8c41be5140cbda024963ef736fd2013d0`
- **Reviewed head:** `d69e0eb85425a471ccaef44caabfea35140bd701`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `merged`
- **Local feature-branch cleanup:** `observed_deleted`
- **Remote feature-branch cleanup:** `observed_deleted`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->


## Final task contract: `MIP_DELEGATED_ROUTINE_MERGE_PREFLIGHT_001` (self-contained)

**Primary mergeable outcome (one):** receipt schema, notes persistence/transport, and a read-only preflight verifier for delegated routine merge approvals. No executor, no authorizer, no policy edit, no canonical-state-schema change.

**Task frame:** MIP only, `branch_and_fast_forward`, branch `feat/mip-delegated-routine-merge-preflight-001`, base = synchronized main after the advisory-closure commit (exact SHAs recorded at authorization), Tier 3 (decision-authority surface), `merge_approval_mode: user_exact_head` for this task itself. Owned paths: `src/mip/execution/delegated_merge.py`, `tests/test_delegated_merge.py`, `docs/execution/DELEGATED_ROUTINE_MERGE_OPERATIONS.md`. Reuses: `taskctl`/state/views validation, observer `Ledger`/`Event`/`ReviewResult` models and `checkpoint()` read-only verification, atomic-write/lock patterns, coded-error style.

### (1) Strict receipt schema (JSON Schema, draft 2020-12 equivalent; model is strict, extra fields forbidden)

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "receipt_kind",
    "receipt_id",
    "repository",
    "task_id",
    "feature_branch",
    "merge_approval_mode",
    "authorization_sha",
    "implementation_sha",
    "reviewed_remote_head_sha",
    "main_baseline_sha",
    "reviewer",
    "decision",
    "issued_at",
    "delegation_provenance",
    "validation",
    "eligibility",
    "authority_impact",
    "limitations"
  ],
  "properties": {
    "schema_version": {
      "const": 1
    },
    "receipt_kind": {
      "const": "delegated_routine_merge_approval"
    },
    "receipt_id": {
      "type": "string",
      "format": "uuid"
    },
    "repository": {
      "const": "Phani-Pavuluri/marketing_intelligence_platform"
    },
    "task_id": {
      "type": "string",
      "minLength": 1
    },
    "feature_branch": {
      "type": "string",
      "minLength": 1
    },
    "merge_approval_mode": {
      "const": "delegated_routine"
    },
    "authorization_sha": {
      "$ref": "#/$defs/sha"
    },
    "implementation_sha": {
      "$ref": "#/$defs/sha"
    },
    "reviewed_remote_head_sha": {
      "$ref": "#/$defs/sha"
    },
    "main_baseline_sha": {
      "$ref": "#/$defs/sha"
    },
    "reviewer": {
      "$ref": "#/$defs/reviewer"
    },
    "decision": {
      "const": "approve_exact_reviewed_head"
    },
    "issued_at": {
      "type": "string",
      "format": "date-time"
    },
    "delegation_provenance": {
      "$ref": "#/$defs/provenance"
    },
    "validation": {
      "$ref": "#/$defs/validation"
    },
    "eligibility": {
      "$ref": "#/$defs/eligibility"
    },
    "authority_impact": {
      "$ref": "#/$defs/authority"
    },
    "limitations": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "minLength": 1
      }
    }
  },
  "$defs": {
    "sha": {
      "type": "string",
      "pattern": "^[0-9a-f]{40}$"
    },
    "reviewer": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "role",
        "session_id",
        "implementation_agent_session_id",
        "reviewer_authored_implementation",
        "observer_report_digest"
      ],
      "properties": {
        "role": {
          "enum": [
            "independent_codex_reviewer"
          ]
        },
        "session_id": {
          "type": "string",
          "format": "uuid"
        },
        "implementation_agent_session_id": {
          "type": "string",
          "pattern": "^ses_[A-Za-z0-9]+$"
        },
        "reviewer_authored_implementation": {
          "const": false
        },
        "observer_report_digest": {
          "type": "string",
          "pattern": "^[0-9a-f]{64}$"
        }
      }
    },
    "provenance": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "policy_version",
        "activation_receipt_id",
        "activation_notes_ref",
        "owner_decision_ref",
        "user_reserved_unchanged",
        "activation_head_sha",
        "policy_sha256"
      ],
      "properties": {
        "policy_version": {
          "type": "string",
          "minLength": 1
        },
        "activation_receipt_id": {
          "type": "string",
          "format": "uuid"
        },
        "activation_notes_ref": {
          "const": "refs/notes/mip-delegated-routine-receipts"
        },
        "owner_decision_ref": {
          "type": "string",
          "minLength": 1
        },
        "user_reserved_unchanged": {
          "const": true
        },
        "activation_head_sha": {
          "$ref": "#/$defs/sha"
        },
        "policy_sha256": {
          "type": "string",
          "pattern": "^[0-9a-f]{64}$"
        }
      }
    },
    "validation": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "tier_class",
        "categories"
      ],
      "properties": {
        "tier_class": {
          "enum": [
            1,
            2
          ]
        },
        "categories": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "focused_tests",
            "docker_make_validate",
            "taskctl_check",
            "git_diff_check",
            "ruff",
            "mypy"
          ],
          "properties": {
            "focused_tests": {
              "$ref": "#/$defs/category"
            },
            "docker_make_validate": {
              "$ref": "#/$defs/category"
            },
            "taskctl_check": {
              "$ref": "#/$defs/category"
            },
            "git_diff_check": {
              "$ref": "#/$defs/category"
            },
            "ruff": {
              "$ref": "#/$defs/category"
            },
            "mypy": {
              "$ref": "#/$defs/category"
            }
          }
        }
      }
    },
    "category": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "status",
        "detail",
        "tree_sha",
        "evidence"
      ],
      "properties": {
        "status": {
          "enum": [
            "pass",
            "not_required"
          ]
        },
        "detail": {
          "type": "string",
          "minLength": 1
        },
        "tree_sha": {
          "anyOf": [
            {
              "$ref": "#/$defs/sha"
            },
            {
              "type": "null"
            }
          ]
        },
        "evidence": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          }
        }
      }
    },
    "eligibility": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "tier_class",
        "routine_assertions",
        "quoted_state",
        "findings"
      ],
      "properties": {
        "tier_class": {
          "enum": [
            1,
            2
          ]
        },
        "routine_assertions": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "within_authorized_scope",
            "no_contract_meaning_change",
            "no_architecture_change",
            "no_authority_change",
            "no_sibling_impact"
          ],
          "properties": {
            "within_authorized_scope": {
              "const": true
            },
            "no_contract_meaning_change": {
              "const": true
            },
            "no_architecture_change": {
              "const": true
            },
            "no_authority_change": {
              "const": true
            },
            "no_sibling_impact": {
              "const": true
            }
          }
        },
        "quoted_state": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "risk_tier",
            "validation_scope",
            "owned_implementation_paths",
            "task_authoring_boundary",
            "merge_approval_mode",
            "capability_authorizations_changed",
            "all_protected_authority_false",
            "delegated_merge_required_validation",
            "full_suite_validation_required"
          ],
          "properties": {
            "risk_tier": {
              "type": "string",
              "minLength": 1
            },
            "validation_scope": {
              "type": "string",
              "minLength": 1
            },
            "owned_implementation_paths": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "task_authoring_boundary": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "merge_approval_mode": {
              "const": "delegated_routine"
            },
            "capability_authorizations_changed": {
              "const": false
            },
            "all_protected_authority_false": {
              "const": true
            },
            "delegated_merge_required_validation": {
              "type": "array",
              "minItems": 1,
              "uniqueItems": true,
              "items": {
                "enum": [
                  "focused_tests",
                  "docker_make_validate",
                  "taskctl_check",
                  "git_diff_check",
                  "ruff",
                  "mypy"
                ]
              }
            },
            "full_suite_validation_required": {
              "type": "boolean"
            }
          }
        },
        "findings": {
          "type": "array",
          "minItems": 8,
          "items": {
            "$ref": "#/$defs/finding"
          }
        }
      }
    },
    "finding": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "condition",
        "result",
        "evidence"
      ],
      "properties": {
        "condition": {
          "enum": [
            "definition_ready_opt_in",
            "tier_within_routine",
            "ownership_verified",
            "independent_review_exact_head",
            "no_open_findings",
            "validation_all_pass",
            "heads_and_baseline_stable",
            "activation_current"
          ]
        },
        "result": {
          "const": "pass"
        },
        "evidence": {
          "type": "string",
          "minLength": 1
        }
      }
    },
    "authority": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "capability_authority_added",
        "task_authorization_changed",
        "statement"
      ],
      "properties": {
        "capability_authority_added": {
          "const": false
        },
        "task_authorization_changed": {
          "const": false
        },
        "statement": {
          "type": "string",
          "minLength": 1
        }
      }
    }
  }
}
```

Global invariants: SHA values are lowercase 40 hex; receipt IDs are UUID4, session IDs are real UUIDs; strings must be nonempty after strip; booleans and integers remain strict. Auth→implementation→reviewed ancestry must hold. The quoted state matches the exact reviewed canonical blob, including task-authored `delegated_merge_required_validation` and `full_suite_validation_required`; unknown/missing classification or required-category declarations fail closed. Tier classes agree and the canonical risk tier has a tier_1 or tier_2 prefix; Tier 3 never qualifies. Exactly the eight named findings appear once each. Issued-at is timezone-aware and not before the completed observer event timestamp.

Required validation comes from the Git-authored `delegated_merge_required_validation`, never from receipt prose. It must include taskctl_check and git_diff_check; Tier 2 also requires focused_tests; full_suite_validation_required also requires docker_make_validate, ruff and mypy. Every declared required category must have status pass, exact reviewed Git tree SHA, and nonempty references to actual validation artifacts in the observer-owned report bundle. References are relative, bounded to that bundle, and may not escape through traversal or symlinks. Test counts and actual commands/results must be in detail; they are independent-review evidence, not a claim that parsing a string reruns tests. A not_required category is allowed only outside the Git-required set, has null tree_sha, empty evidence and a reason in detail. No required gate is waived.

Activation record: strict version-1 Git note of kind delegation_activation on the exact prerequisite reviewed implementation head, not a merge commit (this repository uses fast-forward). Exact keys: schema_version (integer 1), receipt_kind (delegation_activation), receipt_id (UUID4), policy_version (nonempty string), policy_sha256 (64 lowercase hex), prerequisite_head_sha (40 lowercase hex), decision (activate), scope_tier_classes (exact [1,2]), owner_decision_ref (nonempty immutable Git evidence reference), issued_at (timezone-aware RFC3339), limitations (nonempty list of nonempty strings). Receipt provenance activation_head_sha identifies that annotated target; prerequisite_head_sha must equal it and be an ancestor of live synchronized origin/main. Receipt version/ID/owner decision reference must match the activation note, and both policy hashes must equal the actual current main policy document hash. Missing activation fails E_DELEGATED_NOT_ACTIVATED. This prerequisite task does not create an activation note or approve itself; activation uses the owner's separate explicit authority decision only after the prerequisite is reviewed and merged. The owner has already directed removal of the routine approval conflict; do not ask again for the activation intent or technical storage location.

### (2) Actual reviewer identity and independent evidence

Use the existing observer Ledger/Event/ReviewResult models and its event-key/report resolution; do not invent a different key formula or an arbitrary report directory. Require a completed non-stale completion event for this exact repository/task/head and a strict result.json with pass verdict and no unresolved findings or pending owner decisions. Reports and validation artifacts are read only from the deterministic observer-owned report directory in this review checkout. The result digest is SHA256 of sorted compact UTF-8 canonical JSON. The observer directory is `.codex/review-observer` under --repository, with the existing observer layout.

The events.jsonl bundle must contain a real Codex thread.started event whose thread_id is a valid UUID equal to receipt reviewer.session_id, plus a completed model turn. Require valid JSONL and matching result/task/head identity; a different or absent actual run UUID fails even if receipt role text is correct. Require the configured implementation binding/session record for this task to match implementation_agent_session_id, the Muse/OpenCode namespace, and never attribute that UUID to the reviewer; contradictory attribution fails closed. Reuse the existing recipient-binding identity conventions and reject missing/ambiguous implementation identity instead of guessing. A different UUID alone is not independence. Git note author names are not a role-identity proof: both agents legitimately use the owner's Git identity. This is procedural independent-review evidence, not a claim of adversarial isolation between same-user processes.

### (3) Note/file/ref consistency, no fetch/write in preflight

Preflight takes `--receipt PATH` and requires canonical-JSON equality between the file and the note attached to `reviewed_remote_head_sha`. Live checks use read-only `git ls-remote origin <ref>` for both the notes ref and `refs/heads/<feature_branch>`: local notes-ref value must equal the live remote value (missing ⇒ `E_DELEGATED_NOTE_MISSING`, locally-present-but-unequal ⇒ stale/unpushed `E_DELEGATED_NOTE_STALE`, unparseable ⇒ `E_DELEGATED_NOTE_CORRUPT`), and the live branch head must still equal `reviewed_remote_head_sha` and live `origin/main` must equal `main_baseline_sha`. Preflight performs zero fetches and zero writes; it never repairs state.

### (4) Serialized attach

`attach` runs under the existing file-lock pattern. Outcomes: byte-identical receipt already on the head ⇒ `already-attached`, exit 0, no mutation; different bytes on the same head ⇒ `E_DELEGATED_NOTE_CONFLICT`, exit 2, never force-overwrite; unparseable existing note ⇒ fail closed, preserved; lock contention ⇒ exit 3. Attach writes only the notes ref. Only the dedicated refs/notes/mip-delegated-routine-receipts ref is accepted. It accepts normal approval receipts only, never activation records; no force overwrite or implicit push. Semantic canonical-JSON equality defines identical duplicates, so formatting alone is not a conflict.

### (5) No semantic guessing (by construction)

All policy semantics enter as explicit inputs: reviewer-attested `routine_assertions` booleans, reviewer-recorded `findings` with fixed condition keys, task-authored `quoted_state` re-verified against the committed blob, tier-gated fixed category sets, and the activation record's pinned version/scope/identity. The verifier performs only equality, ancestry, liveness, and presence checks.

**Named acceptance tests:** happy-path approval; rejections for missing receipt, non-routine tier/semantics, self-approval (same-session and same-namespace variants), stale head, replaced head, absent observer bundle, digest mismatch, failed validation category, moved main, policy-version drift, missing/stale/corrupt/unpushed note, file↔note mismatch, attach conflict/duplicate/corruption, lock contention, bounded-output/secrets checks. Tier 3 gate applies (focused pytest, full Docker `make validate`, `taskctl check`, JSON parsing, `git diff --check`, exact owned-path/ancestry/authority checks, independent Codex exact-head review). Deferred: executor, activation decision, bidirectional channel, sibling adoption. Unresolved execution-blocking design questions: none.

## Owner authorization, delivery and preserved boundaries

Owner instruction: “approve merging MIP head 917c432dbffc49bc9189713c19346fd1a7f82cd9, remve the conflict so you dont need approval”. The delivery merge is closed at 67c18c370e220cc4a7f84023f582b6c663aec947; this separately authorized prerequisite is part of removing that conflict. The storage/transport choice reuses existing pushed review notes and is resolved, not an additional owner question. Major decisions remain reserved exactly as the policy defines. This task is not eligible for its own delegated approval; its merge uses the existing external approval path. Activation follows only after actual prerequisite merge and Git-recorded owner authority; no untracked report activates anything.

Read AGENTS, stable execution files/context index, lean delivery standard, delegated policy and observer/adapter evidence. One primary outcome: verifiable independent receipt/preflight. These schema, transport and verifier pieces are necessary together for the one eligibility gate. Unresolved execution-blocking design questions: none. Compatibility: additive new receipt/note format, no existing state/observer/adapter schema migration. Owned implementation paths are the three named new files; also own only the three stable execution files, with ACTIVE_TASK generated block only after authorization. Existing policy, AGENTS, standards, observer/schema, taskctl, product/analytical files and sibling repositories are read-only. All protected authority remains false. Muse owns implementation approach; Codex independently reviews, does not author implementation.

Dependencies: the observer checkpoint cf0ac9feafc65c3f35266b550cf33f5a4183203a and delivery closure 67c18c370e220cc4a7f84023f582b6c663aec947 are merged ancestors. Affected/modified MIP only, workstream WS-MIP-DELEGATED-ROUTINE-MERGE-PREFLIGHT-001, owner mip_execution_governance. GeoX and MMM remain independent read-only context, not prerequisites; no coordination snapshot refresh, consumer/product eligibility or sibling authority follows.

Validation for execution, independent exact-head review and post-fast-forward: focused tests/test_delegated_merge.py plus existing tests/test_review_observer.py and tests/test_opencode_advisory.py; full native Docker make validate; native taskctl check; JSON parsing; diff, ancestry, authorization/owned paths and authority checks. Every required category passes. Test isolated Git fixtures and synthetic run artifacts, never production sessions. Named cases additionally prove real reviewer UUID mismatch, duplicate/missing condition findings, changed policy content without version bump, missing/mismatched required validation declarations, optional not_required handling, out-of-bundle/symlink evidence rejection, missing/nonancestor activation target, forged implementation attribution, note-target and notes-ref mismatch, idempotent attach and no branch/worktree mutation. Fixtures must preserve normal schema/lifecycle semantics, not weaken validators for convenience.

Publish through native taskctl transitions with actual implementation SHA/evidence; human completion evidence outside generated block records behavior, actual counts, limits, exact Git identity/ancestry, impact and unchanged authority. Freeze the task-owned tree, run its exact gate, publish the validation-receipt commit naming implementation parent, gate/results, evidence source, tree/worktree state and authority. No post-receipt file edits. Push exact feature head, verify local/remote equality and stop ready_for_review; no merge, self-approval, activation or successor authorization.
