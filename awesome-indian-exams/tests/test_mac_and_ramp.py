"""Tests for the dynamic focus ramp, Mac-only tasks, multi-worker lanes with fallback, the cloud sandbox,
the harvest pipeline and the doctor."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from mock_llm import MockLLM, tool_call, tools_used
from test_agentctl import CONTENT, ENV, ctl, make_remote
from test_free_agent import KEY_ENVS

sys.path.insert(0, str(CONTENT / "ops"))
import agentctl  # noqa: E402
import harvest  # noqa: E402

RAMP = {"focus": {"ramp": {"start": 0.2, "step": 0.01, "per_published": 5, "min_acceptance": 0.8, "max": 0.6}},
        "lane_offset": {"hermes": 0}}


class Ramp(unittest.TestCase):
    def test_share_starts_at_20_and_grows_with_quality_work(self) -> None:
        self.assertAlmostEqual(agentctl.india_share(RAMP, 0, 0), 0.20)
        self.assertAlmostEqual(agentctl.india_share(RAMP, 5, 0), 0.21)
        self.assertAlmostEqual(agentctl.india_share(RAMP, 50, 5), 0.30)
        self.assertAlmostEqual(agentctl.india_share(RAMP, 10_000, 0), 0.60)  # capped

    def test_share_falls_back_when_quality_drops(self) -> None:
        self.assertAlmostEqual(agentctl.india_share(RAMP, 40, 20), 0.20)

    def test_rotation_matches_the_share(self) -> None:
        for share in (0.2, 0.21, 0.37):
            n = sum(agentctl.preferred_focus("hermes", RAMP, slot, share) == "india" for slot in range(2000))
            self.assertAlmostEqual(n / 2000, share, delta=0.01)

    def test_maturity_reads_receipts_and_judge_rejections(self) -> None:
        tasks = [{"id": "T-201", "focus": "india"}, {"id": "T-202", "focus": "india"}, {"id": "T-001"}]
        plan = "- 10:23 published `T-201`: ok\n- 11:23 rejected `T-202`: bad\n- 12:23 rejected `T-001`: core"
        self.assertEqual(agentctl.maturity(tasks, {"T-201", "T-001"}, plan), (1, 1))


BACKLOG = """[[task]]
id = "T-001"
lane = "hermes"
priority = 1
where = "mac"
title = "needs local files"
accept = ["a"]

[[task]]
id = "T-002"
lane = "hermes"
priority = 2
title = "anywhere"
accept = ["a"]
"""


class MacOnlyTasks(unittest.TestCase):
    def test_cloud_skips_mac_tasks_and_mac_takes_them(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            repo = make_remote(tmp, ("r",), tasks_toml=BACKLOG)[0]
            cloud = json.loads(ctl(repo, "next", "hermes", env={**ENV, "HIVE_WHERE": "cloud"}).stdout)
            mac = json.loads(ctl(repo, "next", "hermes", env={**ENV, "HIVE_WHERE": "mac"}).stdout)
            self.assertEqual(cloud["id"], "T-002")
            self.assertEqual(mac["id"], "T-001")
        finally:
            shutil.rmtree(tmp)


@unittest.skipIf(os.environ.get("HIVE_IN_JUDGE"), "end-to-end runner tests are not repeated inside the judge")
class WorkersFallbackSandbox(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = make_remote(self.tmp, ("repo",))[0]
        steps = [("replace_in_file", {"path": "exams/engineering/gate-ee.md", "old": "## Free resources\n",
                                      "new": "## Free resources\n\n- Fallback worked.\n"}),
                 ("finish", {"notes": "fallback"})]
        self.mock = MockLLM(lambda body: tool_call(*steps[min(tools_used(body), 1)], tools_used(body)))

    def tearDown(self) -> None:
        self.mock.close()
        shutil.rmtree(self.tmp)

    def run_hive(self, *args: str, **env: str) -> subprocess.CompletedProcess:
        base = {k: v for k, v in ENV.items() if k not in KEY_ENVS}
        full = {**base, "HIVE_OPEN_PR": "0", "HIVE_HOME": str(self.tmp / "hive"), "HIVE_SLOT": "1",
                "HIVE_LLM_BASE_URL": self.mock.url, "OLLAMA_BASE_URL": "http://127.0.0.1:9/v1", **env}
        return subprocess.run(["bash", f"{CONTENT.name}/ops/run-hourly.sh", *args], cwd=self.repo, env=full,
                              text=True, capture_output=True, timeout=300)

    def test_named_worker_with_broken_agent_falls_back_to_free_agent(self) -> None:
        res = self.run_hive("hermes", "gemini", HIVE_CMD_GEMINI="false", HIVE_FALLBACK="free-agent")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("retrying once with free-agent", res.stdout)
        self.assertTrue((self.tmp / "hive" / "worktrees" / "gemini").is_dir())  # its own worktree
        refs = subprocess.run(["git", "ls-remote", "origin"], cwd=self.repo, capture_output=True, text=True).stdout
        self.assertIn("refs/heads/agent/hermes/", refs)

    def test_sandboxed_shell_agent_sees_no_git_and_no_token(self) -> None:
        agent = self.tmp / "shell-agent.sh"
        agent.write_text("#!/bin/bash\n"
                         "printf '\\n- Sandboxed edit.\\n' >> exams/engineering/gate-ee.md\n"
                         "{ echo \"token=${GITHUB_TOKEN:-none}\"; git rev-parse --git-dir >/dev/null 2>&1 "
                         "&& echo git=yes || echo git=no; } > ops/.notes.md\n", encoding="utf-8")
        agent.chmod(0o755)
        res = self.run_hive("hermes", HIVE_CMD_HERMES=str(agent), HIVE_SANDBOX="1", GITHUB_TOKEN="secret-token")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        subprocess.run(["git", "fetch", "-q", "origin"], cwd=self.repo, env=ENV)
        branch = next(line.split()[1] for line in subprocess.run(
            ["git", "ls-remote", "origin", "refs/heads/agent/hermes/*"], cwd=self.repo, capture_output=True,
            text=True).stdout.splitlines())
        subprocess.run(["git", "fetch", "-q", "origin", branch], cwd=self.repo, env=ENV)
        receipt_name = f"{CONTENT.name}/ops/done/{branch.rsplit('/', 1)[1]}.md"
        receipt = subprocess.run(["git", "show", f"FETCH_HEAD:{receipt_name}"], cwd=self.repo,
                                 capture_output=True, text=True).stdout
        page = subprocess.run(["git", "show", f"FETCH_HEAD:{CONTENT.name}/exams/engineering/gate-ee.md"],
                              cwd=self.repo, capture_output=True, text=True).stdout
        self.assertIn("Sandboxed edit.", page)
        self.assertIn("token=none", receipt)
        self.assertIn("git=no", receipt)


class Harvest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        root = self.tmp / "Documents"
        (root / "prep").mkdir(parents=True)
        (root / "prep" / "ssc_cgl_plan.md").write_text("SSC CGL tier 1 syllabus plan: quant daily, reasoning puzzles.\n" * 3)
        (root / "prep" / "copy_of_plan.md").write_text("SSC CGL tier 1 syllabus plan: quant daily, reasoning puzzles.\n" * 3)
        (root / "prep" / "gate_ee_lecture.srt").write_text("1\n00:00:01,000 --> 00:00:04,000\nGATE EE circuits\n")
        (root / "prep" / "neet_bio.md").write_text("Made Easy NEET UG biology syllabus notes\n")
        (root / "prep" / "upsc_cse_contacts.md").write_text("UPSC CSE syllabus group, call 9876543210\n")
        self.env = {**os.environ, "HIVE_HOME": str(self.tmp / "hive")}

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def h(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(CONTENT / "ops" / "harvest.py"), *args], env=self.env,
                              capture_output=True, text=True, timeout=120)

    def test_scan_dedupes_flags_risks_and_only_publishes_ids(self) -> None:
        self.assertEqual(self.h("scan", "--roots", str(self.tmp / "Documents")).returncode, 0)
        items = [json.loads(l) for l in (self.tmp / "hive" / "harvest" / "inventory.jsonl").read_text().splitlines()]
        risks = {Path(i["path"]).name: i["risk"] for i in items}
        self.assertEqual(len([i for i in items if i["exam"] == "ssc-cgl"]), 1)  # duplicate copy collapsed
        self.assertEqual(risks["gate_ee_lecture.srt"], "transcript")
        self.assertEqual(risks["neet_bio.md"], "third-party")
        self.assertEqual(risks["upsc_cse_contacts.md"], "personal")
        tasks = self.h("tasks", "--start", "501").stdout
        self.assertEqual(tasks.count("[[task]]"), 1)  # only the owner's own, non-personal work
        self.assertIn('where = "mac"', tasks)
        self.assertNotIn("Documents", tasks)
        self.assertNotIn("ssc_cgl_plan", tasks)
        transcript = next(i["id"] for i in items if i["risk"] == "transcript")
        self.assertNotEqual(self.h("show", transcript).returncode, 0)


class Doctor(unittest.TestCase):
    def test_doctor_reports_backlog_focus_and_mac_state(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            repo = make_remote(tmp, ("r",))[0]
            res = subprocess.run([sys.executable, str(repo / CONTENT.name / "ops" / "doctor.py"), "--mac", "--json"],
                                 cwd=repo, env={**ENV, "HIVE_HOME": str(tmp / "hive")}, capture_output=True,
                                 text=True, timeout=300)
            checks = {r["check"]: r for r in json.loads(res.stdout)}
            self.assertEqual(checks["content gate"]["level"], "OK")
            self.assertIn("india share 20%", checks["focus"]["detail"])  # fixed backlog: nothing published yet
            self.assertEqual(checks["agents.env"]["level"], "FAIL")  # nothing bootstrapped in this temp home
            self.assertIn("mac-bootstrap", checks["agents.env"]["fix"])
        finally:
            shutil.rmtree(tmp)


@unittest.skipIf(os.environ.get("HIVE_IN_JUDGE"), "the continuous-mode run is not repeated inside the judge")
class ContinuousMode(unittest.TestCase):
    def test_parallel_loops_take_distinct_tasks_and_stop_cleanly(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            backlog = "".join(f'[[task]]\nid = "T-{i:03d}"\nlane = "{"hermes" if i <= 5 else "opencode"}"\n'
                              f'priority = 1\ntitle = "task {i}"\naccept = ["a"]\n' for i in range(1, 8))
            repo = make_remote(tmp, ("repo",), tasks_toml=backlog)[0]
            agent = tmp / "agent.sh"
            agent.write_text('#!/bin/bash\nmkdir -p docs; echo "$$" > "docs/loop-$HIVE_TASK_ID.md"\n', encoding="utf-8")
            agent.chmod(0o755)
            env = {**{k: v for k, v in ENV.items() if k not in KEY_ENVS}, "HIVE_HOME": str(tmp / "hive"),
                   "HIVE_OPEN_PR": "0", "HIVE_CMD_HERMES": str(agent), "HIVE_CMD_OPENCODE": str(agent),
                   "HIVE_CMD_JEVX": "true", "HIVE_LOOP_HERMES": "2", "HIVE_LOOP_OPENCODE": "1",
                   "HIVE_LOOP_IDLE": "1", "HIVE_LOOP_JEVX_EVERY": "999"}
            loop = [f"{CONTENT.name}/ops/hive-loop.sh"]
            subprocess.run(["bash", *loop, "start"], cwd=repo, env=env, check=True, capture_output=True, timeout=60)
            deadline = time.time() + 120
            branches: list[str] = []
            while time.time() < deadline and len(branches) < 7:
                time.sleep(2)
                branches = subprocess.run(["git", "ls-remote", "origin", "refs/heads/agent/*"], cwd=repo,
                                          capture_output=True, text=True).stdout.split()[1::2]
            subprocess.run(["bash", *loop, "stop"], cwd=repo, env=env, capture_output=True, timeout=60)
            time.sleep(2)
            tasks = [b.rsplit("/", 1)[1] for b in branches]
            self.assertEqual(sorted(set(tasks)), [f"T-{i:03d}" for i in range(1, 8)])
            self.assertEqual(len(tasks), len(set(tasks)))
            left = subprocess.run(["pgrep", "-f", str(tmp / "hive")], capture_output=True, text=True).stdout.split()
            self.assertEqual(left, [], "stop left processes running")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class JEVXLocalMode(unittest.TestCase):
    """Test the JEVX lane when HIVE_OPEN_PR=0 (Mac local mode)."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = make_remote(self.tmp, ("repo",))[0]
        # Simple mock agent that appends a plan entry
        self.agent = self.tmp / "jevx-agent.sh"
        self.agent.write_text("""#!/bin/bash
# Mock JEVX agent: append a plan entry and update tasks.toml
cat >> ops/plan/$(date -u +%Y-%m-%d).md <<'EOF'

## $(date -u +%H:%M) UTC · local jevx run
- Added test task T-999
EOF
cat >> ops/tasks.toml <<'EOF'

[[task]]
id = "T-999"
lane = "opencode"
priority = 1
title = "test task from jevx"
accept = ["verify it appears"]
EOF
""", encoding="utf-8")
        self.agent.chmod(0o755)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def run_jevx_local(self, **extra_env: str) -> subprocess.CompletedProcess:
        base = {k: v for k, v in ENV.items() if k not in KEY_ENVS}
        full = {**base, "HIVE_OPEN_PR": "0", "HIVE_HOME": str(self.tmp / "hive"),
                "HIVE_SLOT": "1", "HIVE_CMD_JEVX": str(self.agent), **extra_env}
        return subprocess.run(
            ["bash", f"{CONTENT.name}/ops/run-hourly.sh", "jevx"],
            cwd=self.repo, env=full, text=True, capture_output=True, timeout=120
        )

    def test_jevx_local_pushes_branch_with_judge_trailer(self) -> None:
        """JEVX lane with HIVE_OPEN_PR=0 pushes agent/jevx/plan-* branch with Hive-Publish: judge trailer."""
        res = self.run_jevx_local()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("pushed agent/jevx/plan-", res.stdout)
        self.assertIn("for the local judge", res.stdout)

        # Verify branch exists on remote with correct commit message
        refs = subprocess.run(
            ["git", "ls-remote", "origin", "refs/heads/agent/jevx/plan-*"],
            cwd=self.repo, env=ENV, capture_output=True, text=True
        ).stdout
        self.assertTrue(refs.strip(), "no jevx plan branch pushed")
        branch = refs.split()[1]
        self.assertTrue(branch.startswith("refs/heads/agent/jevx/plan-"))

        # Verify commit has Hive-Publish: judge trailer
        sha = refs.split()[0]
        log = subprocess.run(
            ["git", "show", "-s", "--format=%B", sha],
            cwd=self.repo, env=ENV, capture_output=True, text=True
        ).stdout
        self.assertIn("Hive-Publish: judge", log)
        self.assertIn("hive(jevx): plan and backlog update", log)

    def test_jevx_local_branch_passes_hive_gate(self) -> None:
        """The JEVX local branch only touches allowed paths (ops/tasks.toml, ops/plan/, README, UPDATES.md)."""
        res = self.run_jevx_local()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

        refs = subprocess.run(
            ["git", "ls-remote", "origin", "refs/heads/agent/jevx/plan-*"],
            cwd=self.repo, env=ENV, capture_output=True, text=True
        ).stdout
        branch = refs.split()[1].replace("refs/heads/", "")
        sha = refs.split()[0]

        # Get changed files
        diff = subprocess.run(
            ["git", "diff", "--name-only", f"{sha}^..{sha}"],
            cwd=self.repo, env=ENV, capture_output=True, text=True
        ).stdout.strip().splitlines()

        # Run hive_gate.py on the branch
        gate_res = subprocess.run(
            [sys.executable, str(CONTENT / "scripts" / "hive_gate.py"), "--branch", branch],
            cwd=self.repo, env=ENV, input="\n".join(diff), text=True, capture_output=True
        )
        self.assertEqual(gate_res.returncode, 0, f"hive_gate failed: {gate_res.stdout} {gate_res.stderr}")
        self.assertIn("PASS", gate_res.stdout)

    def test_jevx_local_plan_is_landed_by_the_local_judge(self) -> None:
        """The local judge accepts a jevx plan branch (scope: ops/tasks.toml + ops/plan/) and lands it on main."""
        res = self.run_jevx_local()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

        judge = subprocess.run(
            [sys.executable, f"{CONTENT.name}/ops/judge.py", "--publish", "--no-llm"],
            cwd=self.repo, env=ENV, text=True, capture_output=True, timeout=600
        )
        self.assertEqual(judge.returncode, 0, judge.stdout + judge.stderr)
        self.assertIn("published", judge.stdout, judge.stdout)

        refs = subprocess.run(["git", "ls-remote", "origin", "refs/heads/agent/jevx/*"],
                              cwd=self.repo, env=ENV, capture_output=True, text=True).stdout
        self.assertEqual(refs.strip(), "", "the judged plan branch should be consumed")

        subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=self.repo, env=ENV, check=True)
        tasks = subprocess.run(["git", "show", f"origin/main:{CONTENT.name}/ops/tasks.toml"],
                               cwd=self.repo, env=ENV, capture_output=True, text=True).stdout
        self.assertIn("T-999", tasks, "the planner's new task did not reach main")

    def test_jevx_local_does_not_call_gh(self) -> None:
        """JEVX lane with HIVE_OPEN_PR=0 should not invoke gh CLI."""
        res = self.run_jevx_local()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        # gh pr list, gh pr create, gh pr close should not appear in output
        self.assertNotIn("gh pr", res.stdout)
        self.assertNotIn("gh pr", res.stderr)


if __name__ == "__main__":
    unittest.main()
