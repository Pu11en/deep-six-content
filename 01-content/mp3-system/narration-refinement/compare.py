"""Bounded subscription comparison. Leaves the live review and approvals untouched."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from d6_harness import Harness, atomic_text
from d6_models import ModelRunner

FOLDER = Path(__file__).resolve().parent
REQUEST = {
    "count": 1,
    "focus": (
        "Refine one strong narration in the recognition direction Drew liked in option 2. "
        "Use this sequence: answer the hook with the mother placing one egg and her young "
        "feeding on the cockroach eggs; explain how to recognize the adult by its small "
        "size and flag-like body movement; finish with what this means for a homeowner "
        "who sees it, including that this wasp does not sting or bite people. "
        "Connect the thoughts naturally. Do not diagnose an infestation. This recognition "
        "lesson does not need a closing infestation disclaimer, a trap-placement lesson, "
        "jaws, an egg-laying time measurement, or a full life-cycle and exit-hole sequence. "
        "Do not first say the eggs are food and then explain the same feeding point again. "
        "A single connected sequence from her egg to her young feeding supplies the payoff. "
        "Give the visible features directly, without announcing how to recognize it first. "
        "Extra host-species examples are optional facts, not a required caveat: saying this "
        "wasp feeds on cockroach eggs does not claim that every cockroach species is a host. "
        "The viewer should understand what it is and what it is doing, not hear a fact list."
    ),
}
FEEDBACK = (
    "Drew wants one carefully refined narration and fewer repeated corrections. "
    "He liked option 2's recognition direction, not its wording. Use connected, "
    "natural speech, no filler or obvious conclusions, no spoken source credits "
    "or unexplained terms, exact hook 4C and the approved outro. The narration is "
    "not approved. Compare models on the same brief before choosing a writing route."
)


class RecordedRunner:
    def __init__(self, config, runtime):
        self.runner = ModelRunner(config, runtime)
        self.records = []

    def call(self, role, prompt, schema, research=False):
        started = time.monotonic()
        output, meta = self.runner.call(role, prompt, schema, research=research)
        self.records.append({
            "stage": role, **meta,
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "elapsed_seconds": round(time.monotonic() - started, 1),
            "output": output,
        })
        return output, meta


def compare(label, provider, model, baseline):
    flow = Harness(ROOT)
    flow.state = copy.deepcopy(baseline)
    flow.state["current"]["narration_request"] = REQUEST
    flow.state["feedback"].append({"stage": "narrations", "note": FEEDBACK})
    config = copy.deepcopy(flow.config)
    route = [{"provider": provider, "model": model, "effort": "high"}]
    config["role_routes"] = {"narrations": route, "narration_edit": route}
    runner = RecordedRunner(config, flow.runtime)
    flow.runner = runner
    flow.save = lambda: None
    receipt = {
        "requested_model": model, "effort": "high",
        "subscription_only": True, "fallback_enabled": False,
        "live_state_written": False, "human_approved": False,
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    try:
        flow.narrations()
        receipt.update(status="complete", scripts=flow.state["current"]["scripts"],
                       quality=flow.state["current"]["narration_quality"])
    except Exception as error:
        receipt.update(status="failed", error_type=type(error).__name__, error=str(error))
    receipt["calls"] = runner.records
    receipt["finished_utc"] = datetime.now(timezone.utc).isoformat()
    atomic_text(FOLDER / (label + ".json"), json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return {"model": model, "status": receipt["status"], "calls": len(runner.records)}


if __name__ == "__main__":
    baseline = json.loads((ROOT / "01-content/harness/runtime/state.json").read_text())
    assert baseline["current"]["run_id"] == "D6-01096ba333e3"
    assert baseline["current"].get("evidence_ready")
    flow = Harness(ROOT)
    flow.state["current"]["narration_request"] = REQUEST
    flow.state["feedback"].append({"stage": "narrations", "note": FEEDBACK})
    atomic_text(FOLDER / "brief.json", json.dumps(flow.narration_context(), ensure_ascii=False, indent=2) + "\n")
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [
            pool.submit(compare, "astra", "codex", "gpt-6-astra", baseline),
            pool.submit(compare, "opus", "claude", "claude-opus-5-5", baseline),
        ]
        for job in as_completed(jobs):
            print(json.dumps(job.result()), flush=True)
