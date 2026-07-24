import unittest

from cyber_lab import (
    AuthorizationScopeType,
    CyberAuthorization,
    CyberLab,
    CyberLabActionRequest,
    CyberLabDecisionType,
    CyberLabTarget,
    build_local_fuzz_cases,
)


class CyberLabTests(unittest.TestCase):
    def test_localhost_target_can_be_approved_as_dry_run(self) -> None:
        lab = CyberLab()
        target = "http://localhost:3000"
        lab.add_target(
            CyberLabTarget(
                identifier=target,
                scope_type=AuthorizationScopeType.LOCAL_LAB,
                owner="eden",
                proof="local dev server",
            )
        )
        authorization = CyberAuthorization(
            owner="eden",
            scope_type=AuthorizationScopeType.LOCAL_LAB,
            targets=(target,),
            allowed_actions=("run_local_fuzzing",),
        )

        decision = lab.evaluate(
            CyberLabActionRequest(
                action="run_local_fuzzing",
                target=target,
                authorization=authorization,
                approved=True,
                dry_run=True,
            )
        )

        self.assertEqual(decision.decision, CyberLabDecisionType.DRY_RUN_ONLY)
        self.assertTrue(decision.allowed)
        self.assertEqual(len(lab.audit_log()), 1)

    def test_public_url_is_denied(self) -> None:
        lab = CyberLab()
        target = "https://example.com"
        lab.add_target(
            CyberLabTarget(
                identifier=target,
                scope_type=AuthorizationScopeType.OWNED_ASSET,
                owner="eden",
                proof="declared ownership",
            )
        )
        authorization = CyberAuthorization(
            owner="eden",
            scope_type=AuthorizationScopeType.OWNED_ASSET,
            targets=(target,),
            allowed_actions=("scan_lab_target",),
        )

        decision = lab.evaluate(
            CyberLabActionRequest(
                action="scan_lab_target",
                target=target,
                authorization=authorization,
                approved=True,
            )
        )

        self.assertEqual(decision.decision, CyberLabDecisionType.DENIED)
        self.assertIn("External targets", decision.reason)

    def test_forbidden_actions_are_never_approved(self) -> None:
        lab = CyberLab()
        target = "http://localhost:3000"
        lab.add_target(
            CyberLabTarget(
                identifier=target,
                scope_type=AuthorizationScopeType.LOCAL_LAB,
                owner="eden",
                proof="local dev server",
            )
        )
        authorization = CyberAuthorization(
            owner="eden",
            scope_type=AuthorizationScopeType.LOCAL_LAB,
            targets=(target,),
            allowed_actions=("credential_theft",),
        )

        decision = lab.evaluate(
            CyberLabActionRequest(
                action="credential_theft",
                target=target,
                authorization=authorization,
                approved=True,
            )
        )

        self.assertEqual(decision.decision, CyberLabDecisionType.DENIED)

    def test_local_fuzz_cases_are_deterministic(self) -> None:
        cases = build_local_fuzz_cases(("empty", "boundary_number"))

        self.assertEqual(cases, ("", str(2**63 - 1)))


if __name__ == "__main__":
    unittest.main()
