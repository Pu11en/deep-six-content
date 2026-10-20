"""Subscription-only model calls. Raw model transcripts never enter project logs."""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile


class ModelError(Exception):
    def __init__(self, kind: str):
        self.kind = kind
        super().__init__(kind)


def clean_environment():
    return {
        k: v for k, v in os.environ.items()
        if not any(part in k.upper() for part in ("KEY", "TOKEN", "SECRET"))
        and not k.startswith(("OPENAI_", "ANTHROPIC_", "AZURE_", "CLAUDECODE",
                              "CLAUDE_CODE_USE_", "AWS_", "GOOGLE_", "CLOUD_ML_"))
    }


def invoke(args, *, cwd, prompt=None, timeout=240):
    try:
        p = subprocess.Popen(args, cwd=cwd, env=clean_environment(),
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, start_new_session=True)
    except FileNotFoundError:
        raise ModelError("cli_missing") from None
    try:
        out, err = p.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.communicate()
        raise ModelError("timeout") from None
    except KeyboardInterrupt:
        os.killpg(p.pid, signal.SIGKILL)
        p.communicate()
        raise
    return p.returncode, out, err


def failure_kind(text):
    text = text.lower()
    if any(x in text for x in ("usage limit", "rate_limit", "rate limit", "out of credits", "quota", "session limit")):
        return "subscription_limit"
    if any(x in text for x in ("not supported", "model_not_found", "does not exist", "unknown model")):
        return "model_unavailable"
    if any(x in text for x in ("log in", "login", "unauthorized", "authentication")):
        return "login_required"
    return "provider_failed"


class ModelRunner:
    def __init__(self, config, runtime):
        self.config = config
        self.runtime = Path(runtime)
        self.unavailable = set()

    def call(self, role, prompt, schema, *, research=False):
        routes = self.config.get("role_routes", {}).get(role)
        if routes is None:
            routes = []
            if self.config["active_provider"] == "auto":
                models = self.config["claude_models"]
                routes.append({"provider": "claude", "model": models.get(role, models["default"])})
            routes.extend({"provider": "codex", "model": model} for model in self.config["codex_models"])
        attempts = []
        for route in routes:
            provider, model = route["provider"], route["model"]
            effort = route.get("effort", "medium")
            if provider not in ("claude", "codex") or effort not in ("low", "medium", "high", "xhigh", "max"):
                raise ModelError("invalid_model_route")
            if (provider, model) in self.unavailable:
                continue
            try:
                result = self._call(provider, model, prompt, schema, research, effort=effort)
            except ModelError as error:
                attempts.append({"provider": provider, "model": model, "result": error.kind})
                # A broken response is a visible stage failure, not permission to
                # repeat the writing with every model and silently pick a result.
                if error.kind == "invalid_response":
                    raise ModelError("invalid_response") from None
                self.unavailable.add((provider, model))
                continue
            attempts.append({"provider": provider, "model": model, "result": "success"})
            return result, {"provider": provider, "model": model, "effort": effort, "attempts": attempts}
        raise ModelError("all_subscription_routes_unavailable:" + ",".join(a["result"] for a in attempts))

    def _call(self, provider, model, prompt, schema, research, *, effort="medium"):
        self.runtime.mkdir(parents=True, exist_ok=True)
        # All transient files are ours. TemporaryDirectory removes them on exit;
        # ephemeral CLI mode prevents rejected scripts becoming session archives.
        with tempfile.TemporaryDirectory(prefix="model-", dir=self.runtime) as tmp:
            tmp = Path(tmp)
            if provider == "codex":
                rc, out, err = invoke(["codex", "login", "status"], cwd=tmp, timeout=20)
                if rc or "chatgpt" not in (out + err).lower():
                    raise ModelError("chatgpt_login_required")
                schema_path = tmp / "schema.json"
                output_path = tmp / "answer.json"
                schema_path.write_text(json.dumps(schema))
                args = ["codex", "-a", "never", "exec", "--ignore-user-config", "--ignore-rules",
                        "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only",
                        "--model", model, "--color", "never", "--json",
                        "--output-schema", str(schema_path.resolve()),
                        "--output-last-message", str(output_path.resolve())]
                settings = {
                    "forced_login_method": "chatgpt", "model_provider": "openai",
                    "project_doc_max_bytes": 0, "web_search": "live" if research else "disabled",
                    "features.shell_tool": False, "features.shell_snapshot": False,
                    "features.multi_agent": False, "features.apps": False,
                    "features.plugins": False, "features.hooks": False,
                    "history.persistence": "none", "model_reasoning_effort": effort,
                }
                for key, value in settings.items():
                    args += ["-c", key + "=" + json.dumps(value)]
                args += ["-"]
                rc, out, err = invoke(args, cwd=tmp, prompt=prompt,
                                      timeout=self.config["timeout_seconds"])
                if rc:
                    raise ModelError(failure_kind(out + err))
                try:
                    result = json.loads(output_path.read_text())
                except (OSError, ValueError):
                    raise ModelError("invalid_response") from None
            else:
                rc, out, _ = invoke(["claude", "auth", "status", "--json"], cwd=tmp, timeout=20)
                try:
                    auth = json.loads(out)
                except ValueError:
                    raise ModelError("claude_login_required") from None
                if rc or not auth.get("loggedIn") or auth.get("authMethod") not in ("claude.ai", "oauth"):
                    raise ModelError("claude_subscription_required")
                args = ["claude", "-p", "--safe-mode", "--strict-mcp-config",
                        "--mcp-config", '{"mcpServers":{}}', "--model", model,
                        "--effort", effort,
                        "--no-session-persistence", "--output-format", "json",
                        "--tools", "WebSearch,WebFetch" if research else "",
                        "--json-schema", json.dumps(schema)]
                rc, out, err = invoke(args, cwd=tmp, prompt=prompt,
                                      timeout=self.config["timeout_seconds"])
                try:
                    payload = json.loads(out)
                except ValueError:
                    raise ModelError(failure_kind(out + err)) from None
                if rc or payload.get("is_error"):
                    raise ModelError(failure_kind(out + err))
                result = payload.get("structured_output")
            if not isinstance(result, dict):
                raise ModelError("invalid_response")
            return result
