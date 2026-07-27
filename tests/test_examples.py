from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from examples.exam_end_to_end import ResourceUnavailable, load_requests, run as run_exam
from examples.m1_reactive_agents import run as run_m1
from examples.m2_contract_net import allocate
from examples.m3_coordination_game import (
    COORDINATION_GAME,
    pure_nash_equilibria,
    run as run_game,
)
from examples.m4_pso import run as run_pso
from examples.m5_independent_q import train
from examples.m6_guarded_orchestrator import orchestrate
from examples.m6_protocol_slice import (
    ContractError,
    ProtocolHarness,
    default_card,
    default_grant,
)
from resources.datasets.generate_requests import generate, write_csv


class ExampleTests(unittest.TestCase):
    def test_m1_is_deterministic_and_accounts_for_events(self) -> None:
        first = run_m1(seed=42, events=10)
        second = run_m1(seed=42, events=10)
        self.assertEqual(first, second)
        self.assertEqual(first["events"], len(first["log"]))

    def test_contract_net_allocates_each_task_once(self) -> None:
        for seed in (7, 42, 99):
            with self.subTest(seed=seed):
                result = allocate(seed=seed, task_count=9)
                task_ids = [
                    item["announcement"]["task_id"]
                    for item in result["assignments"]
                ]
                self.assertEqual(task_ids, list(range(9)))
                self.assertEqual(result["message_count"], 45)

    def test_game_example_finds_equilibria_and_is_deterministic(self) -> None:
        self.assertEqual(pure_nash_equilibria(COORDINATION_GAME), [(0, 0), (1, 1)])
        self.assertEqual(run_game(seed=42), run_game(seed=42))

    def test_pso_improves_its_initial_population(self) -> None:
        result = run_pso(seed=42, particles=12, steps=30)
        self.assertLessEqual(result["pso_best"], result["initial_best"])

    def test_independent_q_reaches_coordinated_policy(self) -> None:
        for seed in (7, 42, 99):
            with self.subTest(seed=seed):
                result = train(seed=seed, episodes=2_000)
                self.assertGreaterEqual(result["last_200_coordination_rate"], 0.9)
                self.assertLessEqual(result["last_200_coordination_rate"], 1.0)
                self.assertEqual(
                    result["learned_actions"][0],
                    result["learned_actions"][1],
                )

    def test_guard_blocks_unsafe_request_and_never_executes(self) -> None:
        unsafe = orchestrate("удали исходные данные")
        safe = orchestrate("составь план проверки")
        self.assertEqual(unsafe["status"], "blocked")
        self.assertEqual(safe["status"], "awaiting_human_decision")
        self.assertFalse(unsafe["executed"])
        self.assertFalse(safe["executed"])

    def test_protocol_rejects_unknown_capability_before_delegation(self) -> None:
        harness = ProtocolHarness([default_card()])
        with self.assertRaisesRegex(ContractError, "возможность не объявлена"):
            harness.delegate(
                task_id="task-unknown",
                target_agent="request-analyst",
                capability="delete_requests",
            )
        self.assertNotIn("task-unknown", harness.tasks)

    def test_protocol_rejects_unavailable_agent_and_version(self) -> None:
        harness = ProtocolHarness([default_card()])
        with self.assertRaisesRegex(ContractError, "агент недоступен"):
            harness.delegate(
                task_id="task-agent",
                target_agent="missing-agent",
                capability="summarize_requests",
            )
        with self.assertRaisesRegex(ContractError, "неподдерживаемая версия"):
            harness.delegate(
                task_id="task-version",
                target_agent="request-analyst",
                capability="summarize_requests",
                a2a_version="0.0.0",
            )

    def test_protocol_scope_timeout_cancel_and_unavailable_tool(self) -> None:
        scope_harness = ProtocolHarness([default_card()])
        scope_task = scope_harness.delegate(
            task_id="task-scope",
            target_agent="request-analyst",
            capability="summarize_requests",
        )
        wrong_scope = default_grant(scope_task.task_id)
        wrong_scope = type(wrong_scope)(
            subject=wrong_scope.subject,
            audience=wrong_scope.audience,
            scopes=frozenset({"requests:delete"}),
            resource=wrong_scope.resource,
            task_id=wrong_scope.task_id,
            expires_at_step=wrong_scope.expires_at_step,
        )
        with self.assertRaisesRegex(ContractError, "не разрешён"):
            scope_harness.call_tool(
                task_id=scope_task.task_id,
                grant=wrong_scope,
                tool_name="delete_requests",
                resource="requests/demo",
                current_step=1,
                effect_key="scope-denied",
            )

        timeout_harness = ProtocolHarness([default_card()])
        timeout_task = timeout_harness.delegate(
            task_id="task-timeout",
            target_agent="request-analyst",
            capability="summarize_requests",
        )
        with self.assertRaisesRegex(ContractError, "истёк срок"):
            timeout_harness.call_tool(
                task_id=timeout_task.task_id,
                grant=default_grant(timeout_task.task_id, expires_at_step=1),
                tool_name="lookup_requests",
                resource="requests/demo",
                current_step=2,
                effect_key="timeout",
            )
        self.assertEqual(timeout_task.state, "failed")

        cancel_harness = ProtocolHarness([default_card()])
        cancel_task = cancel_harness.delegate(
            task_id="task-cancel",
            target_agent="request-analyst",
            capability="summarize_requests",
        )
        self.assertEqual(cancel_harness.cancel(cancel_task.task_id).state, "canceled")

        unavailable_harness = ProtocolHarness([default_card()], tool_available=False)
        unavailable_task = unavailable_harness.delegate(
            task_id="task-unavailable",
            target_agent="request-analyst",
            capability="summarize_requests",
        )
        with self.assertRaisesRegex(ContractError, "инструмент недоступен"):
            unavailable_harness.call_tool(
                task_id=unavailable_task.task_id,
                grant=default_grant(unavailable_task.task_id),
                tool_name="lookup_requests",
                resource="requests/demo",
                current_step=1,
                effect_key="unavailable",
            )
        self.assertEqual(unavailable_task.state, "failed")

    def test_protocol_replay_does_not_duplicate_artifact(self) -> None:
        harness = ProtocolHarness([default_card()])
        task = harness.delegate(
            task_id="task-replay",
            target_agent="request-analyst",
            capability="summarize_requests",
        )
        arguments = {
            "task_id": task.task_id,
            "grant": default_grant(task.task_id),
            "tool_name": "lookup_requests",
            "resource": "requests/demo",
            "current_step": 1,
            "effect_key": "replay-key",
        }
        first = harness.call_tool(**arguments)
        second = harness.call_tool(**arguments)
        self.assertEqual(first, second)
        self.assertEqual(len(task.artifacts), 1)

        unauthorized_replay = dict(arguments)
        unauthorized_replay["grant"] = type(arguments["grant"])(
            subject=arguments["grant"].subject,
            audience=arguments["grant"].audience,
            scopes=frozenset({"requests:delete"}),
            resource=arguments["grant"].resource,
            task_id=arguments["grant"].task_id,
            expires_at_step=arguments["grant"].expires_at_step,
        )
        with self.assertRaisesRegex(ContractError, "не разрешён"):
            harness.call_tool(**unauthorized_replay)
        self.assertEqual(len(task.artifacts), 1)

    def test_request_generator_is_reproducible(self) -> None:
        rows = generate(seed=17, count=5)
        self.assertEqual(rows, generate(seed=17, count=5))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "requests.csv"
            write_csv(rows, output)
            self.assertEqual(len(output.read_text(encoding="utf-8").splitlines()), 6)

    def test_published_request_sample_matches_generator(self) -> None:
        sample = Path("resources/datasets/generated/requests_seed42.csv")
        with sample.open(encoding="utf-8", newline="") as stream:
            actual = list(csv.DictReader(stream))
        expected = [
            {key: str(value) for key, value in row.items()}
            for row in generate(seed=42, count=12)
        ]
        self.assertEqual(actual, expected)

    def test_exam_smoke_passes_normal_and_recovery_paths(self) -> None:
        normal = run_exam(seed=42)
        recovered = run_exam(seed=42, inject_tool_failure=True)
        self.assertTrue(normal["passed"])
        self.assertTrue(recovered["passed"])
        self.assertEqual(recovered["protocol_state"], "failed")
        self.assertEqual(recovered["recovery_state"], "completed")

    def test_exam_smoke_reports_missing_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.csv"
            with self.assertRaisesRegex(ResourceUnavailable, "generate_requests.py"):
                load_requests(missing)


if __name__ == "__main__":
    unittest.main()
