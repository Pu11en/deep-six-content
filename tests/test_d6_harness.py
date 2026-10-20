"""Offline workflow tests. No subscriptions, network, real drafts or credentials."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from d6_harness import Harness, FlowError, BEGIN, END, check_shape, HOOKS
from d6_models import ModelRunner, ModelError, clean_environment
from d6_sources import validate_cards, source_url

ROOT = Path(__file__).resolve().parents[1]


def card(n):
    return {"url": f"https://citybugs.tamu.edu/fixture-{n}", "title": f"Fixture publication {n}",
            "publisher": "Fixture extension", "date": "2026-10-19", "lesson": f"Distinct fixture lesson {n}",
            "species": "fixture", "region": "Central Texas fixture", "limits": "Test content only",
            "facts": [{"statement": f"Fixture fact {n}.", "quote": f"Evidence for fixture {n} exists"}]}


def fetch(url, domains):
    n = url.rsplit("-", 1)[-1]
    return f"Evidence for fixture {n} exists on this unique test page {n}.", url


class FakeWriter:
    def __init__(self):
        self.calls = []
        self.prompts = []
        self.contexts = []
        self.fail_stage = None
        self.bad_hook = False
        self.foreign_source = False
        self.bad_narration = False
        self.research_round = 0
        self.narration_round = 0
        self.evidence_action = "reuse"
        self.shallow_source = False
        self.invalid_support = False
        self.research_flags = []
        self.editor_unresolved = []
        self.editor_transform = None

    def call(self, role, prompt, schema, research=False):
        self.calls.append(role)
        self.research_flags.append((role, research))
        self.prompts.append((role, prompt))
        if self.fail_stage == role:
            raise ModelError("subscription_limit")
        meta = {"provider": "fixture", "model": "fixture-writer", "attempts": []}
        if role == "research":
            self.research_round += 1
            return {"cards": [card(i + self.research_round * 10) for i in range(5)]}, meta
        context = json.loads(prompt.splitlines()[-1])
        self.contexts.append((role, context))
        if role == "depth_check":
            return {"ready": "no" if self.shallow_source else "yes", "assessment": "Fixture depth assessment", "questions": ["Why does it happen?"]}, meta
        if role == "evidence_plan":
            return {"action": self.evidence_action, "assessment": "Fixture evidence plan", "gaps": ["Explain mechanism"] if self.evidence_action == "research" else []}, meta
        if role == "support_research":
            support = card(900 + self.calls.count("support_research"))
            if self.invalid_support:
                support["facts"][0]["quote"] = "Not present in evidence"
            return {"cards": [support], "unresolved": []}, meta
        if role == "hooks":
            c = context["sources"][0]
            hooks = [{"source_id": c["source_id"], "text": f"Why does fixture {i} happen in {c['title']}?",
                      "fact_ids": [c["facts"][0]["id"]], "payoff": "A fixture answer"}
                     for i in range(1, 6)]
            if self.bad_hook:
                hooks[0]["fact_ids"] = ["unrelated-source-fact"]
            if self.foreign_source:
                hooks[0]["source_id"] = "different-source"
            return {"hooks": hooks}, meta
        if role == "narrations":
            self.narration_round += 1
            hook = context["selected_hook"]["text"]
            if self.bad_narration:
                hook += " Changed."
            outro = ("\n\n" + context["approved_outro"]) if context.get("approved_outro") else ""
            count = context.get("request", {}).get("count", 5)
            scripts = [{"text": hook + f"\n\nUnique fixture passage {self.narration_round}:{i}. "
                        "This complete explanation exists only in the temporary test project." + outro,
                        "fact_ids": [context["sources"][0]["facts"][0]["id"]]} for i in range(1, count + 1)]
            return {"scripts": scripts}, meta
        if role == "narration_edit":
            scripts = copy.deepcopy(context["drafts"])
            if self.editor_transform:
                self.editor_transform(scripts)
            return {"scripts": scripts, "changes": ["Fixture review completed."],
                    "unresolved": self.editor_unresolved}, meta
        raise AssertionError(role)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "01-content/harness").mkdir(parents=True)
        (self.root / "01-content/harness/config.json").write_text((ROOT / "01-content/harness/config.json").read_text())
        config_path = self.root / "01-content/harness/config.json"
        config = json.loads(config_path.read_text())
        config["research_backend"] = "subscription"
        config_path.write_text(json.dumps(config))
        (self.root / "01-content/writing-harness-prompts.md").write_text("Fixture writer instructions")
        (self.root / "01-content/narration-style.md").write_text(
            (ROOT / "01-content/narration-style.md").read_text())
        (self.root / "01-content/source-log.md").write_text("# Existing source history\n")
        (self.root / "BOARD.md").write_text("# Existing board\n\nKeep my earlier work.\n")
        self.writer = FakeWriter()
        self.flow = Harness(self.root, self.writer, fetch)
        # Tests exercise writing and board exports; production board updates are on hold.
        self.flow.config["writing_enabled"] = True
        self.flow.config["board_updates_enabled"] = True
        (self.root / "01-content/harness/config.json").write_text(json.dumps(self.flow.config))

    def start_hooks(self):
        self.flow.start()
        self.flow.choose(self.flow.state["current"]["review_id"], 2)

    def start_narrations(self, save_second=None):
        self.start_hooks()
        review = self.flow.state["current"]["review_id"]
        self.flow.choose(review, 2, save_second)
        return review

    def test_complete_flow_stops_at_sources_then_hooks_then_narrations(self):
        self.flow.start()
        current = self.flow.state["current"]
        self.assertEqual(current["status"], "waiting_sources")
        self.assertEqual(self.writer.calls, ["research"])
        self.assertNotIn("hooks", current)
        for c in current["cards"]:
            self.assertIn(c["title"], self.flow.display())
            self.assertIn(c["url"], self.flow.display())
            self.assertIn(c["lesson"], self.flow.display())
        source = current["cards"][1]
        self.flow.choose(current["review_id"], 2)
        current = self.flow.state["current"]
        visible = self.flow.display()
        self.assertEqual(len(visible.split("\n\n")), 5)
        self.assertNotIn("https", visible)
        self.assertNotIn("SRC-", visible)
        self.assertEqual({h["source_id"] for h in current["hooks"]}, {source["source_id"]})
        self.flow.choose(current["review_id"], 2)
        current = self.flow.state["current"]
        chosen = current["scripts"][2]["text"]
        rejected = current["scripts"][0]["text"]
        self.flow.choose(current["review_id"], 3)
        restored = Harness(self.root, self.writer, fetch)
        self.assertIsNone(restored.state["current"])
        self.assertEqual(restored.state["approved"][0]["text"], chosen)
        self.assertEqual(restored.state["approved"][0]["source"], source)
        exports = list((self.root / "01-content/approved-narrations").glob("*.md"))
        self.assertEqual(len(exports), 1)
        for path in self.root.rglob("*"):
            if path.is_file():
                self.assertNotIn(rejected, path.read_text())
        self.assertIn("Keep my earlier work", (self.root / "BOARD.md").read_text())

    def test_skip_failure_removes_rejections_and_retry_keeps_hook_source(self):
        self.start_narrations()
        current = self.flow.state["current"]
        hook, source = copy.deepcopy(current["selected_hook"]), copy.deepcopy(current["cards"])
        discarded = [s["text"] for s in current["scripts"]]
        self.writer.fail_stage = "narrations"
        with self.assertRaises(FlowError):
            self.flow.skip(current["review_id"], "Make the explanation less stiff.")
        for path in self.root.rglob("*"):
            if path.is_file():
                for script in discarded:
                    self.assertNotIn(script, path.read_text())
        self.writer.fail_stage = None
        restored = Harness(self.root, self.writer, fetch)
        restored.retry()
        self.assertEqual(restored.state["current"]["selected_hook"], hook)
        self.assertEqual(restored.state["current"]["cards"], source)
        self.assertEqual(self.writer.calls.count("research"), 1)
        preferences = self.flow.context()["hook_preferences"]
        self.assertEqual(len(preferences), 1)
        self.assertEqual(preferences[0]["action"], "choose")

    def test_hook_pick_and_comment_reach_next_batch_after_restart(self):
        self.start_hooks()
        current = self.flow.state["current"]
        openings = [h["text"] for h in current["hooks"]]
        self.flow.choose(current["review_id"], 2, save_second=4,
                         feedback="I like the direct question.")
        self.flow.choose(self.flow.state["current"]["review_id"], 1)
        restored = Harness(self.root, self.writer, fetch)
        restored.start()
        restored.choose(restored.state["current"]["review_id"], 1)
        role, context = self.writer.contexts[-1]
        self.assertEqual(role, "hooks")
        self.assertEqual(len(context["hook_preferences"]), 1)
        decision = context["hook_preferences"][0]
        self.assertEqual(decision["hooks"], openings)
        self.assertEqual(decision["number"], 2)
        self.assertEqual(decision["saved_number"], 4)
        self.assertEqual(decision["feedback"], "I like the direct question.")
        self.assertEqual(context["feedback"][0]["note"], decision["feedback"])

    def test_hook_skip_without_reason_survives_failed_generation_and_retry(self):
        self.start_hooks()
        current = self.flow.state["current"]
        openings = [h["text"] for h in current["hooks"]]
        source = copy.deepcopy(current["cards"])
        self.writer.fail_stage = "hooks"
        with self.assertRaises(FlowError):
            self.flow.skip(current["review_id"])
        restored = Harness(self.root, self.writer, fetch)
        self.writer.fail_stage = None
        restored.retry()
        context = self.writer.contexts[-1][1]
        self.assertEqual(len(context["hook_preferences"]), 1)
        decision = context["hook_preferences"][0]
        self.assertEqual(decision["action"], "skip")
        self.assertEqual(decision["hooks"], openings)
        self.assertEqual(decision["feedback"], "")
        self.assertEqual(context["feedback"], [])
        self.assertEqual(restored.state["current"]["cards"], source)
        self.assertEqual(self.writer.calls.count("research"), 1)

    def test_oversized_feedback_preserves_review_and_history(self):
        self.flow.start()
        before = copy.deepcopy(self.flow.state)
        calls = list(self.writer.calls)
        review = before["current"]["review_id"]
        for action in (lambda: self.flow.choose(review, 1, feedback="x" * 501),
                       lambda: self.flow.skip(review, "x" * 501)):
            with self.assertRaises(FlowError):
                action()
            self.assertEqual(self.flow.state, before)
            self.assertEqual(self.writer.calls, calls)

    def test_duplicate_or_stale_decision_does_not_repeat_model_work(self):
        old_review = self.start_narrations()
        before = copy.deepcopy(self.flow.state)
        calls = list(self.writer.calls)
        with self.assertRaises(FlowError):
            self.flow.choose(old_review, 2)
        with self.assertRaises(FlowError):
            self.flow.skip(old_review)
        self.assertEqual(self.flow.state, before)
        self.assertEqual(self.writer.calls, calls)

    def test_pending_review_blocks_new_start(self):
        self.flow.start()
        before = copy.deepcopy(self.flow.state)
        with self.assertRaises(FlowError):
            self.flow.start()
        self.assertEqual(before, self.flow.state)

    def premature_narrations(self):
        self.start_hooks()
        current = self.flow.state["current"]
        current.pop("hooks")
        current.update(stage="narrations", status="waiting_narrations", draft_openings=True,
                       scripts=[{"opening": "Unchosen opening", "text": "Premature script body", "fact_ids": ["F1"]}]*5)
        self.flow.save()
        return current

    def test_missing_hook_blocks_generation_and_approval_without_changes(self):
        current = self.premature_narrations()
        before = copy.deepcopy(self.flow.state)
        calls = self.writer.calls[:]
        with self.assertRaisesRegex(FlowError, "Choose a hook"):
            self.flow.narrations()
        with self.assertRaisesRegex(FlowError, "Choose a hook"):
            self.flow.choose(current["review_id"], 1)
        self.assertEqual(self.flow.state, before)
        self.assertEqual(self.writer.calls, calls)

    def test_restore_hook_review_removes_drafts_before_failure_and_preserves_choices(self):
        current = self.premature_narrations()
        before = copy.deepcopy(self.flow.state)
        self.writer.fail_stage = "hooks"
        with self.assertRaises(FlowError):
            self.flow.review_hooks()
        restored = Harness(self.root, self.writer, fetch)
        self.assertNotIn("scripts", restored.state["current"])
        self.assertNotIn("draft_openings", restored.state["current"])
        self.assertNotIn("review_id", restored.state["current"])
        for path in self.root.rglob("*"):
            if path.is_file():
                self.assertNotIn("Premature script body", path.read_text())
        self.writer.fail_stage = None
        restored.retry()
        self.assertEqual(restored.state["current"]["status"], "waiting_hooks")
        self.assertNotEqual(restored.state["current"]["review_id"], before["current"]["review_id"])
        self.assertEqual(restored.state["current"]["cards"], before["current"]["cards"])
        for key in ("source_queue", "used_sources", "decisions", "feedback", "approved"):
            self.assertEqual(restored.state[key], before[key])
        self.assertEqual(self.writer.calls.count("research"), 1)

    def test_every_full_narration_displays_the_same_chosen_hook(self):
        self.start_narrations()
        current = self.flow.state["current"]
        hook = current["selected_hook"]["text"]
        display = self.flow.display()
        self.assertEqual(display.count(hook), 5)
        for script in current["scripts"]:
            self.assertEqual(script["text"].split("\n\n", 1)[0], hook)
            self.assertIn(script["text"], display)
        with self.assertRaises(FlowError):
            self.flow.review_hooks()

    def test_editor_changes_reach_review_but_do_not_approve_the_script(self):
        def edit(scripts):
            scripts[0]["text"] = scripts[0]["text"].replace(
                "This complete explanation", "This edited explanation")
        self.writer.editor_transform = edit
        self.start_narrations()
        current = self.flow.state["current"]
        self.assertIn("This edited explanation", self.flow.display())
        self.assertEqual(current["narration_quality"]["status"], "ready_for_review")
        self.assertFalse(current["narration_quality"]["human_approved"])
        self.assertEqual(self.flow.state["approved"], [])
        self.assertEqual(self.writer.calls[-2:], ["narrations", "narration_edit"])
        self.flow.choose(current["review_id"], 1)
        approved = self.flow.state["approved"][0]
        self.assertTrue(approved["narration_quality"]["human_approved"])
        self.assertEqual([c["stage"] for c in approved["narration_quality"]["calls"]],
                         ["narrations", "narration_edit"])

    def test_unresolved_editor_problem_stops_after_one_pass_and_can_retry(self):
        self.writer.editor_unresolved = ["The evidence does not support the draft's claim."]
        with self.assertRaisesRegex(FlowError, "unresolved"):
            self.start_narrations()
        current = self.flow.state["current"]
        self.assertEqual(current["status"], "error")
        self.assertEqual(current["narration_quality"]["status"], "blocked")
        self.assertNotIn("scripts", current)
        self.assertNotIn("review_id", current)
        self.assertEqual(self.writer.calls.count("narration_edit"), 1)
        self.writer.editor_unresolved = []
        self.flow.retry()
        self.assertEqual(current["status"], "waiting_narrations")

    def test_editor_cannot_release_a_changed_outro_or_rejected_spoken_wording(self):
        self.start_narrations()
        for bad_text, error in (
            ("Changed ending.", "sign-off"),
            ("The University of Florida says so.", "source credits"),
            ("Use corrugated cardboard.", "wording Drew rejected"),
            ("Look\u2014an insect.", "em dash"),
        ):
            with self.subTest(bad_text=bad_text):
                def corrupt(scripts, value=bad_text):
                    text = scripts[0]["text"]
                    if value == "Changed ending.":
                        scripts[0]["text"] = text.rsplit("\n\n", 1)[0] + "\n\n" + value
                    else:
                        first, rest = text.split("\n\n", 1)
                        scripts[0]["text"] = first + "\n\n" + value + "\n\n" + rest
                self.writer.editor_transform = corrupt
                with self.assertRaisesRegex(FlowError, error):
                    self.flow.revise("narrations", "Keep the approved wording rules.")
                self.assertEqual(self.flow.state["current"]["narration_quality"]["status"], "blocked")
                self.assertNotIn("scripts", self.flow.state["current"])
                self.writer.editor_transform = None
                self.flow.retry()

    def test_focused_revision_has_one_selectable_script_and_keeps_hook(self):
        self.start_narrations()
        hook = copy.deepcopy(self.flow.state["current"]["selected_hook"])
        self.flow.revise("narrations", "Refine one focused explanation.", count=1)
        current = self.flow.state["current"]
        self.assertEqual(current["selected_hook"], hook)
        self.assertEqual(len(current["scripts"]), 1)
        before = copy.deepcopy(self.flow.state)
        with self.assertRaisesRegex(FlowError, "1 to 1"):
            self.flow.choose(current["review_id"], 2)
        self.assertEqual(self.flow.state, before)
        self.flow.choose(current["review_id"], 1)
        self.assertEqual(len(self.flow.state["approved"]), 1)

    def test_narrator_gets_current_brief_without_old_conflicting_instructions(self):
        self.start_hooks()
        self.flow.state["feedback"].extend([
            {"stage": "narrations", "note": "Old request: omit the branded outro."},
            {"stage": "narrations", "note": "Current request: use the approved outro."},
        ])
        self.flow.choose(self.flow.state["current"]["review_id"], 1)
        for role, prompt in self.writer.prompts:
            if role not in ("narrations", "narration_edit"):
                continue
            self.assertNotIn("Old request", prompt)
            self.assertNotIn("Fixture writer instructions", prompt)
            self.assertIn("Current request", prompt)
            self.assertIn("Helping you understand pests. Deep Six Pest Control.", prompt)
            self.assertIn("first listen", prompt)

    def test_shallow_source_stops_before_hook_generation(self):
        self.writer.shallow_source = True
        with self.assertRaisesRegex(FlowError, "Source needs more depth"):
            self.start_hooks()
        self.assertNotIn("hooks", self.writer.calls)
        self.assertEqual(self.flow.state["current"]["stage"], "hooks")

    def test_support_research_keeps_hook_queue_and_persists_evidence_on_approval(self):
        self.writer.evidence_action = "research"
        self.start_hooks()
        source_queue = copy.deepcopy(self.flow.state["source_queue"])
        hook = copy.deepcopy(self.flow.state["current"]["hooks"][1])
        self.flow.choose(self.flow.state["current"]["review_id"], 2)
        current = self.flow.state["current"]
        self.assertEqual(current["selected_hook"], hook)
        self.assertEqual(self.flow.state["source_queue"], source_queue)
        self.assertEqual(len(current["supporting_cards"]), 1)
        self.assertIn(("support_research", True), self.writer.research_flags)
        self.assertIn(("evidence_plan", False), self.writer.research_flags)
        context = self.writer.contexts[-1][1]
        support = current["supporting_cards"][0]
        self.assertIn(support["facts"][0]["id"], [f["id"] for f in context["sources"][0]["facts"]])
        self.assertNotIn(support["facts"][0]["id"], [f["id"] for f in self.flow.context(False)["sources"][0]["facts"]])
        self.flow.choose(current["review_id"], 1)
        self.assertEqual(self.flow.state["approved"][0]["supporting_sources"], [support])
        export = next((self.root / "01-content/approved-narrations").glob("*.md"))
        self.assertIn(support["url"], export.read_text())

    def test_failed_support_blocks_writing_and_retry_preserves_choices(self):
        self.writer.evidence_action = "research"
        self.writer.invalid_support = True
        self.start_hooks()
        with self.assertRaisesRegex(FlowError, "Supporting evidence"):
            self.flow.choose(self.flow.state["current"]["review_id"], 2)
        self.assertNotIn("narrations", self.writer.calls)
        hook = copy.deepcopy(self.flow.state["current"]["selected_hook"])
        self.writer.invalid_support = False
        restored = Harness(self.root, self.writer, fetch)
        restored.retry()
        self.assertEqual(restored.state["current"]["selected_hook"], hook)
        self.assertEqual(restored.state["current"]["status"], "waiting_narrations")

    def test_wording_skip_reuses_evidence_depth_skip_researches_without_archiving_scripts(self):
        self.writer.evidence_action = "research"
        self.start_narrations()
        current = self.flow.state["current"]
        discarded = [s["text"] for s in current["scripts"]]
        self.writer.evidence_action = "reuse"
        self.flow.skip(current["review_id"], "Make the wording natural")
        self.assertEqual(self.writer.calls.count("support_research"), 1)
        self.writer.evidence_action = "research"
        self.flow.skip(current["review_id"], "Needs more educational depth")
        self.assertEqual(self.writer.calls.count("support_research"), 2)
        self.assertEqual(len(current["supporting_cards"]), 2)
        for path in self.root.rglob("*"):
            if path.is_file():
                for script in discarded:
                    self.assertNotIn(script, path.read_text())

    def test_completed_support_is_not_repeated_after_writer_failure(self):
        self.writer.evidence_action = "research"
        self.writer.fail_stage = "narrations"
        with self.assertRaises(FlowError):
            self.start_narrations()
        self.writer.fail_stage = None
        restored = Harness(self.root, self.writer, fetch)
        restored.retry()
        self.assertEqual(self.writer.calls.count("support_research"), 1)
        self.assertEqual(self.writer.calls.count("evidence_plan"), 1)

    def test_conflicting_evidence_stops_without_changing_hook(self):
        self.writer.evidence_action = "blocked"
        self.start_hooks()
        hook = copy.deepcopy(self.flow.state["current"]["hooks"][1])
        with self.assertRaisesRegex(FlowError, "Evidence needs attention"):
            self.flow.choose(self.flow.state["current"]["review_id"], 2)
        self.assertNotIn("narrations", self.writer.calls)
        self.assertEqual(self.flow.state["current"]["selected_hook"], hook)
        self.assertNotIn("evidence_plan", self.flow.state["current"])

    def test_board_hold_keeps_display_file_unchanged_while_queue_saves(self):
        self.flow.config["board_updates_enabled"] = False
        before = (self.root / "BOARD.md").read_bytes()
        self.flow.start()
        self.flow.save_sources(self.flow.state["current"]["review_id"], [1, 2, 4, 5], first=1)
        self.assertEqual((self.root / "BOARD.md").read_bytes(), before)
        self.assertEqual(len(json.loads(self.flow.state_path.read_text())["source_queue"]), 4)
        self.assertTrue((self.root / "01-content/source-queue.md").exists())

    def test_multiple_liked_sources_keep_first_and_rotate_after_restart(self):
        self.flow.start()
        current = self.flow.state["current"]
        original = copy.deepcopy(current["cards"])
        review = current["review_id"]
        calls = list(self.writer.calls)
        self.flow.save_sources(review, [1, 2, 4, 5], first=1)
        restored = Harness(self.root, self.writer, fetch)
        queue = restored.state["source_queue"]
        self.assertEqual([s["source"] for s in queue], [original[i] for i in (0, 1, 3, 4)])
        self.assertEqual(restored.state["next_source_id"], original[0]["source_id"])
        self.assertEqual(restored.rotation()["counts"]["ants"], 4)
        self.assertEqual(restored.rotation()["next_pest"], "cockroaches")
        self.assertEqual(restored.state["decisions"][-1]["numbers"], [1, 2, 4, 5])
        self.assertEqual(self.writer.calls, calls)
        self.assertIsNone(restored.state["current"])
        self.assertIn(original[0]["url"], (self.root / "01-content/source-queue.md").read_text())
        before = copy.deepcopy(restored.state)
        with self.assertRaises(FlowError):
            restored.save_sources(review, [1, 2, 4, 5], first=1)
        self.assertEqual(restored.state, before)
        restored.start()
        self.assertEqual(restored.state["current"]["pest"], "cockroaches")
        self.assertIn("about cockroaches in Central Texas", self.writer.prompts[-1][1])
        self.assertEqual(restored.state["source_queue"], queue)

    def test_rotation_counts_liked_sources_not_merely_presented_sources(self):
        self.flow.start()
        self.assertEqual(self.flow.rotation()["counts"]["ants"], 0)
        self.flow.save_sources(self.flow.state["current"]["review_id"], [1, 2])
        self.assertEqual(self.flow.rotation()["next_pest"], "ants")
        self.flow.start()
        self.flow.save_sources(self.flow.state["current"]["review_id"], [3])
        self.assertEqual(self.flow.rotation()["counts"]["ants"], 3)
        self.assertEqual(self.flow.rotation()["next_pest"], "cockroaches")

    def test_full_rotation_waits_then_replenishes_finished_source(self):
        self.flow.config["pest_rotation"] = ["ants", "cockroaches"]
        for pest in ("ants", "cockroaches"):
            self.flow.start()
            self.assertEqual(self.flow.state["current"]["pest"], pest)
            self.flow.save_sources(self.flow.state["current"]["review_id"], [1, 2, 3])
        self.assertIsNone(self.flow.rotation()["next_pest"])
        calls = list(self.writer.calls)
        with self.assertRaises(FlowError):
            self.flow.start()
        self.assertEqual(self.writer.calls, calls)
        first = self.flow.state["next_source_id"]
        self.flow.start(source=first)
        self.assertEqual(self.flow.state["source_queue"][0]["status"], "in_use")
        self.assertIsNone(self.flow.rotation()["next_pest"])
        self.flow.choose(self.flow.state["current"]["review_id"], 1)
        self.flow.choose(self.flow.state["current"]["review_id"], 1)
        self.assertEqual(self.flow.state["source_queue"][0]["status"], "awaiting_video")
        self.assertIsNone(self.flow.rotation()["next_pest"])
        self.assertNotEqual(self.flow.state["next_source_id"], first)

    def test_writing_hold_saves_choice_without_generating_hooks(self):
        self.flow.config["writing_enabled"] = False
        self.flow.start()
        self.flow.choose(self.flow.state["current"]["review_id"], 1)
        self.assertEqual(self.writer.calls, ["research"])
        before = copy.deepcopy(self.flow.state)
        with self.assertRaises(FlowError):
            self.flow.start(source=self.flow.state["next_source_id"])
        self.assertEqual(self.flow.state, before)
        self.assertIn("Hooks are on hold", self.flow.display())

    def test_invalid_multi_selection_preserves_pending_review(self):
        self.flow.start()
        review = self.flow.state["current"]["review_id"]
        before = copy.deepcopy(self.flow.state)
        for numbers, first in (([], None), ([1, 1], None), ([1, 6], None), ([1, 2], 3)):
            with self.assertRaises(FlowError):
                self.flow.save_sources(review, numbers, first)
            self.assertEqual(self.flow.state, before)

    def test_research_failure_keeps_saved_source_queue_and_rotation(self):
        self.flow.start()
        self.flow.save_sources(self.flow.state["current"]["review_id"], [1, 2, 4, 5], first=1)
        queue = copy.deepcopy(self.flow.state["source_queue"])
        self.writer.fail_stage = "research"
        with self.assertRaises(FlowError):
            self.flow.start()
        restored = Harness(self.root, self.writer, fetch)
        self.assertEqual(restored.state["source_queue"], queue)
        self.assertEqual(restored.state["current"]["pest"], "cockroaches")
        self.writer.fail_stage = None
        restored.retry()
        self.assertEqual(restored.state["source_queue"], queue)
        self.assertEqual(restored.state["current"]["status"], "waiting_sources")

    def test_source_preference_reaches_research_after_restart_without_hook_feedback(self):
        self.flow.start()
        originals = copy.deepcopy(self.flow.state["current"]["cards"])
        self.flow.choose(self.flow.state["current"]["review_id"], 2,
                         feedback="More seasonal homeowner lessons.")
        self.assertEqual(self.writer.contexts[-1][1]["feedback"], [])
        self.flow.choose(self.flow.state["current"]["review_id"], 1,
                         feedback="I like short hook questions.")
        self.flow.choose(self.flow.state["current"]["review_id"], 1)
        restored = Harness(self.root, self.writer, fetch)
        restored.start()
        prompt = [p for role, p in self.writer.prompts if role == "research"][-1]
        context = json.loads(prompt.splitlines()[-1])
        self.assertEqual(len(context["source_preferences"]), 1)
        decision = context["source_preferences"][0]
        self.assertEqual(decision["number"], 2)
        self.assertEqual([s["url"] for s in decision["sources"]], [c["url"] for c in originals])
        self.assertEqual(context["source_feedback"][0]["note"], "More seasonal homeowner lessons.")
        self.assertNotIn("I like short hook questions", prompt)
        self.assertEqual(restored.state["current"]["status"], "waiting_sources")

    def test_source_skip_survives_failure_without_becoming_hook_feedback(self):
        self.flow.start()
        current = self.flow.state["current"]
        urls = [c["url"] for c in current["cards"]]
        self.writer.fail_stage = "research"
        with self.assertRaises(FlowError):
            self.flow.skip(current["review_id"], "These topics feel too narrow.")
        restored = Harness(self.root, self.writer, fetch)
        self.writer.fail_stage = None
        restored.retry()
        context = json.loads(self.writer.prompts[-1][1].splitlines()[-1])
        decision = context["source_preferences"][0]
        self.assertEqual(decision["action"], "skip")
        self.assertEqual([c["url"] for c in decision["sources"]], urls)
        self.assertEqual(decision["feedback"], "These topics feel too narrow.")
        restored.choose(restored.state["current"]["review_id"], 1)
        self.assertEqual(self.writer.contexts[-1][1]["hook_preferences"], [])
        self.assertEqual(self.writer.contexts[-1][1]["feedback"], [])

    def test_old_batch_moves_to_sources_with_backup_and_no_invented_rejection(self):
        self.flow.start()
        current = self.flow.state["current"]
        current.update(stage="hooks", status="waiting_hooks", hooks=[
            {"source_id": c["source_id"], "text": f"Old hook {i}"} for i, c in enumerate(current["cards"])])
        self.flow.save()
        old = copy.deepcopy(self.flow.state)
        old_review = current["review_id"]
        calls = list(self.writer.calls)
        self.flow.review_sources()
        backup = self.flow.runtime / "migrations" / (old_review + ".json")
        self.assertEqual(json.loads(backup.read_text()), old)
        self.assertEqual(current["status"], "waiting_sources")
        self.assertEqual(self.flow.state["decisions"], [])
        self.assertEqual(self.flow.state["used_sources"], old["used_sources"])
        self.assertEqual(self.writer.calls, calls)
        with self.assertRaises(FlowError):
            self.flow.choose(old_review, 2)
        self.flow.choose(current["review_id"], 3)
        self.assertEqual({h["source_id"] for h in current["hooks"]}, {old["current"]["cards"][2]["source_id"]})

    def test_hook_writer_cannot_switch_selected_source(self):
        self.flow.start()
        source = copy.deepcopy(self.flow.state["current"]["cards"][1])
        self.writer.foreign_source = True
        with self.assertRaises(FlowError):
            self.flow.choose(self.flow.state["current"]["review_id"], 2)
        self.assertEqual(self.flow.state["current"]["cards"], [source])
        self.assertNotIn("hooks", self.flow.state["current"])

    def test_overlong_source_summary_never_reaches_review(self):
        cards = [card(i) for i in range(5)]
        cards[0]["lesson"] = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        with patch.object(self.writer, "call", return_value=({"cards": cards}, {"model": "fixture"})):
            with self.assertRaises(FlowError):
                self.flow.start()
        self.assertEqual(self.flow.state["current"]["status"], "error")
        self.assertEqual(self.flow.state["used_sources"], [])
        self.assertNotIn("Fifth sentence", self.flow.display())

    def test_queued_hook_cannot_reuse_source_from_an_approved_episode(self):
        self.start_narrations(save_second=4)
        queued = copy.deepcopy(self.flow.state["queue"][0])
        self.flow.choose(self.flow.state["current"]["review_id"], 1)
        approved = copy.deepcopy(self.flow.state["approved"])
        with self.assertRaisesRegex(FlowError, "source reserved"):
            self.flow.start(queued["id"])
        self.assertIsNone(self.flow.state["current"])
        self.assertEqual(self.flow.state["queue"][0], queued)
        self.assertEqual(self.flow.state["approved"], approved)
        self.assertEqual(self.writer.calls.count("research"), 1)

    def test_skip_sources_consumes_fresh_sources_and_does_not_reuse_old_publications(self):
        self.flow.start()
        first = {c["source_id"] for c in self.flow.state["current"]["cards"]}
        self.flow.skip(self.flow.state["current"]["review_id"])
        second = {c["source_id"] for c in self.flow.state["current"]["cards"]}
        self.assertFalse(first & second)
        self.assertEqual(len(self.flow.state["used_sources"]), 10)

    def test_wrong_hook_in_narration_pauses_without_changing_selection(self):
        self.start_hooks()
        chosen = self.flow.state["current"]["hooks"][1]["text"]
        self.writer.bad_narration = True
        with self.assertRaises(FlowError):
            self.flow.choose(self.flow.state["current"]["review_id"], 2)
        self.assertEqual(self.flow.state["current"]["selected_hook"]["text"], chosen)
        self.assertNotIn("scripts", self.flow.state["current"])
        self.writer.bad_narration = False
        self.flow.retry()
        self.assertEqual(self.flow.state["current"]["status"], "waiting_narrations")

    def test_foreign_fact_ids_never_reach_the_board(self):
        self.writer.bad_hook = True
        with self.assertRaises(FlowError):
            self.start_hooks()
        self.assertNotIn("Why does fixture", (self.root / "BOARD.md").read_text())
        self.assertEqual(self.flow.state["current"]["status"], "error")

    def test_shortage_stops_before_hook_writing(self):
        self.flow.fetcher = lambda url, domains: ("This page does not contain the quote.", url)
        with self.assertRaises(FlowError):
            self.flow.start()
        self.assertEqual(self.writer.calls, ["research"])
        self.assertEqual(self.flow.state["used_sources"], [])

    def test_research_retry_receives_failed_source_urls(self):
        def unavailable_first(url, domains):
            if url.endswith("-10"):
                raise OSError("Fixture page unavailable")
            return fetch(url, domains)
        self.flow.fetcher = unavailable_first
        with self.assertRaises(FlowError):
            self.flow.start()
        self.flow.retry()
        research_prompts = [p for role, p in self.writer.prompts if role == "research"]
        self.assertNotIn("https://citybugs.tamu.edu/fixture-10", research_prompts[0])
        self.assertIn("https://citybugs.tamu.edu/fixture-10", research_prompts[1])
        self.assertIn("Use different publications instead", research_prompts[1])
        self.assertEqual(self.flow.state["current"]["status"], "waiting_sources")

    def test_lock_prevents_concurrent_writing(self):
        other = Harness(self.root, self.writer, fetch)
        with self.flow.locked():
            with self.assertRaises(FlowError):
                with other.locked():
                    pass

    def test_show_repairs_board_from_saved_state_without_a_model_call(self):
        self.flow.start()
        (self.root / "BOARD.md").write_text("# Existing board after interrupted display update\n")
        calls = list(self.writer.calls)
        Harness(self.root, self.writer, fetch).sync_outputs()
        self.assertIn("Fixture publication", (self.root / "BOARD.md").read_text())
        self.assertEqual(self.writer.calls, calls)

    def test_invalid_choice_preserves_state(self):
        self.flow.start()
        before = copy.deepcopy(self.flow.state)
        with self.assertRaises(FlowError):
            self.flow.choose(self.flow.state["current"]["review_id"], 1, 1)
        self.assertEqual(self.flow.state, before)

    def test_source_log_independently_reserves_used_urls(self):
        self.flow.start()
        url = self.flow.state["used_sources"][0]["urls"][0]
        self.assertIn(url, self.flow.legacy_log())
        accepted, _ = validate_cards([card(10)], ["tamu.edu"], [], self.flow.legacy_log(), fetch)
        self.assertEqual(accepted, [])

    def test_missing_state_never_overwrites_existing_source_history(self):
        self.flow.start()
        history = (self.root / "01-content/source-log.md").read_text()
        self.flow.state_path.unlink()
        with self.assertRaises(FlowError):
            Harness(self.root, self.writer, fetch)
        self.assertEqual((self.root / "01-content/source-log.md").read_text(), history)

    def test_interruption_saves_a_retryable_stage_without_selecting_anything(self):
        with patch.object(self.writer, "call", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.flow.start()
        restored = Harness(self.root, self.writer, fetch)
        self.assertEqual(restored.state["current"]["error"], "interrupted")
        self.assertEqual(restored.state["decisions"], [])
        restored.retry()
        self.assertEqual(restored.state["current"]["status"], "waiting_sources")


class SourceAndModelTests(unittest.TestCase):
    def test_quotes_duplicates_and_legacy_sources(self):
        cards = [card(i) for i in range(1, 7)]
        cards[1]["facts"][0]["quote"] = "Invented quote absent from page"
        cards[2] = copy.deepcopy(cards[0])
        accepted, _ = validate_cards(cards, ["tamu.edu"], [], "https://citybugs.tamu.edu/fixture-4", fetch)
        self.assertEqual([c["title"] for c in accepted], ["Fixture publication 1", "Fixture publication 5", "Fixture publication 6"])

    def test_query_tracking_and_fragments_do_not_create_a_new_source(self):
        self.assertEqual(source_url("https://citybugs.tamu.edu/a/?utm_source=x#section"), "https://citybugs.tamu.edu/a")

    def test_untrusted_domains_never_get_fetched(self):
        bad = card(1)
        bad["url"] = "https://citybugs.tamu.edu.example.com/private"
        def fail(*args):
            self.fail("Unexpected fetch")
        accepted, _ = validate_cards([bad], ["tamu.edu"], [], "", fail)
        self.assertEqual(accepted, [])

    def test_schema_rejects_null_or_wrong_count(self):
        for value in ({"hooks": None}, {"hooks": []}, {"hooks": "five"}):
            with self.assertRaises(FlowError):
                check_shape(value, HOOKS)

    def test_claude_limit_falls_back_for_any_role(self):
        config = {"active_provider": "auto", "claude_models": {"default": "sonnet", "scene_plan": "opus"},
                  "codex_models": ["gpt-6-astra", "gpt-6.1-sol"]}
        for role in ("hooks", "narrations", "research", "scene_plan"):
            runner = ModelRunner(config, ".")
            with patch.object(runner, "_call", side_effect=[ModelError("subscription_limit"), {"ok": True}]) as call:
                result, meta = runner.call(role, "fixture", {})
                self.assertTrue(result["ok"])
                self.assertEqual(meta["provider"], "codex")
                self.assertEqual(call.call_count, 2)
                self.assertEqual(meta["attempts"][0]["result"], "subscription_limit")

    def test_codex_mode_skips_claude_and_tries_second_backup(self):
        config = {"active_provider": "codex", "codex_models": ["gpt-6.1-sol", "gpt-6-astra"]}
        runner = ModelRunner(config, ".")
        with patch.object(runner, "_call", side_effect=[ModelError("model_unavailable"), {"ok": True}]):
            _, meta = runner.call("hooks", "fixture", {})
        self.assertEqual(meta["model"], "gpt-6-astra")
        self.assertTrue(all(x["provider"] == "codex" for x in meta["attempts"]))

    def test_writing_route_and_effort_do_not_change_other_stages(self):
        config = {
            "active_provider": "codex", "codex_models": ["gpt-6-astra"],
            "role_routes": {"narrations": [
                {"provider": "claude", "model": "claude-opus-5-5", "effort": "high"}]},
        }
        runner = ModelRunner(config, ".")
        with patch.object(runner, "_call", return_value={"ok": True}) as call:
            _, narration = runner.call("narrations", "fixture", {})
            self.assertEqual(call.call_args.args[:2], ("claude", "claude-opus-5-5"))
            self.assertEqual(call.call_args.kwargs["effort"], "high")
            _, hooks = runner.call("hooks", "fixture", {})
            self.assertEqual(call.call_args.args[:2], ("codex", "gpt-6-astra"))
        self.assertEqual(narration["effort"], "high")
        self.assertEqual(hooks["effort"], "medium")

    def test_api_credentials_are_not_inherited(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "fixture", "ANTHROPIC_API_KEY": "fixture", "OTHER_SECRET": "fixture", "CLAUDE_CODE_USE_BEDROCK": "1", "AWS_PROFILE": "fixture"}):
            env = clean_environment()
        self.assertFalse(any(k in env for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OTHER_SECRET", "CLAUDE_CODE_USE_BEDROCK", "AWS_PROFILE")))

    def test_invalid_model_response_does_not_trigger_more_generation(self):
        runner = ModelRunner({"active_provider": "codex", "codex_models": ["one", "two"]}, ".")
        with patch.object(runner, "_call", side_effect=ModelError("invalid_response")) as call:
            with self.assertRaises(ModelError):
                runner.call("hooks", "fixture", {})
            self.assertEqual(call.call_count, 1)


if __name__ == "__main__":
    unittest.main()
