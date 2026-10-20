# Writing harness options (19 Oct 2026)

**Later clarification:** Drew wants manual trials of hooks through saved approved narrations first. Hook-example research refreshes Saturday nights; pest-source research runs at writing start. Telegram and scheduling remain later work. The earlier subscription tests below passed, but the full harness is unbuilt. The session then hit its plan limit; subscription use consumes limited capacity. See the [current workflow](../video-workflow.md).

**Build a small Python script that runs `claude -p --model claude-sonnet-5-5` once per stage, saves batch state in one JSON file, and asks Drew through the plain Telegram Bot API; reuse no harness repo yet.**

Checked 19 Oct 2026 against Anthropic docs, local `claude` 2.1.289 (`--help` only, no model calls), and live GitHub. Nothing was installed or run.

## Short answer

- `claude -p` already does what we need: model choice, JSON-schema output, system prompt, no tools, session ids. It uses Drew's subscription login when no API key is set.
- The "wait for Drew" part is the only thing to build. A saved state file plus a Telegram message with buttons is simpler and more reliable than keeping a Claude session open.
- Do not use `--bare`. It skips the subscription login.
- Anthropic's docs support this for Drew's own use, with one unreconciled terms clause (section 2). They do not allow a product that runs other people's requests on Drew's login.

## 1. Running Claude Code without a person

| Need | How | Source |
| - | - | - |
| One-shot run | `claude -p "prompt"`; exit code 0 on success, non-zero on failure | [headless](https://code.claude.com/docs/en/headless) |
| Model | `--model claude-sonnet-5-5` (API ID, row "Claude API ID") or alias `sonnet` (= Sonnet 5.5 on the Anthropic API). Needs Claude Code 2.1.284+ | [models](https://platform.claude.com/docs/en/models/overview), [model-config](https://code.claude.com/docs/en/model-config) |
| Default model trap | On Pro/Max the default is Opus 5.5, so always pass `--model` | [model-config](https://code.claude.com/docs/en/model-config) |
| JSON result | `--output-format json` gives `result`, `session_id`, `total_cost_usd` | [headless](https://code.claude.com/docs/en/headless#get-structured-output) |
| Checked JSON | `--json-schema '<schema>'` fills `structured_output`; failure subtype `error_max_structured_output_retries`; schema is draft-07 | [structured outputs](https://code.claude.com/docs/en/agent-sdk/structured-outputs) |
| Our own instructions | `--system-prompt` / `--system-prompt-file` replace the default; `--append-system-prompt` adds | [cli-reference](https://code.claude.com/docs/en/cli-reference#system-prompt-flags) |
| No tools for writing stages | `--tools ""` | [cli-reference](https://code.claude.com/docs/en/cli-reference) |
| Ignore our CLAUDE.md files | `--safe-mode` drops CLAUDE.md, skills, hooks, MCP but keeps login and model choice ("differs from `--bare`") | [cli-reference](https://code.claude.com/docs/en/cli-reference) |
| Limits | `--max-turns` (documented; not in local `--help`), `--max-budget-usd`, `--fallback-model` | [cli-reference](https://code.claude.com/docs/en/cli-reference) |
| Resume | `--resume <id>`, `--session-id <uuid>`, `--no-session-persistence` | [headless](https://code.claude.com/docs/en/headless#continue-conversations) |
| Cron login | `claude setup-token` prints a 1-year token for `CLAUDE_CODE_OAUTH_TOKEN`; needs a Pro/Max/Team/Enterprise plan | [authentication](https://code.claude.com/docs/en/authentication#generate-a-long-lived-token) |

Why `--safe-mode`: Drew's global CLAUDE.md says to answer in caveman style, and this project's CLAUDE.md has board rules. Neither belongs in narration scripts. (Local `claude --help` confirms `--safe-mode`, `--json-schema`, `--tools`, `--bare`, `setup-token`.)

Why not `--bare`: "Set `ANTHROPIC_API_KEY` before running it, because bare mode doesn't use your subscription login." ([headless](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode))

**Agent SDK.** Python `claude-agent-sdk` v0.2.168 (2026-10-15, MIT) [repo](https://github.com/anthropics/claude-agent-sdk-python); it runs the bundled Claude Code binary ([overview](https://code.claude.com/docs/en/agent-sdk/overview)). The quickstart only shows API-key setup ([quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart)). I found no sentence that says "SDK + subscription is supported", but the legal page says plan limits "assume ordinary, individual usage of Claude Code and the Agent SDK" (section 2). Two repos below call the SDK on a CLI login. For this job `claude -p` is simpler than the SDK.

## 2. Subscription policy (what is allowed)

- Anthropic's own status for scripted use, verbatim: "Claude Agent SDK, `claude -p`, and third-party app usage still draw from your subscription limits." (update of 15 Jun 2026; 7 Oct 2026 note adds monthly API credits for Max and Team and says "You can still use the Claude Agent SDK, `claude -p`, and third-party apps with your subscription limits.") [support article](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
- Plan limits: "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and the Agent SDK." [legal-and-compliance](https://code.claude.com/docs/en/legal-and-compliance#acceptable-use)
- Limits themselves: "Both Pro and Max plans have a five-hour session limit and a weekly limit." They are "shared across Claude and Claude Code". [support](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- Products for others: "Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, or Max plan credentials on behalf of their users." [legal-and-compliance](https://code.claude.com/docs/en/legal-and-compliance#authentication-and-credential-use) Also: "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products" [SDK overview](https://code.claude.com/docs/en/agent-sdk/overview).
- Allowed for the person themself: the same page says it does not prevent "an end user from signing in to the unmodified Claude Code binary with their own Claude subscription". `setup-token` is documented "for CI and scripts" ([cli-reference](https://code.claude.com/docs/en/cli-reference)).
- Tension to know about: Consumer Terms section 3 bars access "through automated or non-human means, whether through a bot, script, or otherwise" except via an API key "or where we otherwise explicitly permit it" (effective 8 Oct 2025). [terms](https://www.anthropic.com/legal/consumer-terms) The docs above are the explicit permission for `claude -p`; I found no text that reconciles the two. Not legal advice.
- Third-party harnesses: news reports say subscriptions stopped covering tools like OpenClaw on 4 Apr 2026 ([report](https://aibusiness.com/agentic-ai/claude-subscribers-now-have-pay-use-openclaw)). Secondary source only; I found no Anthropic primary page. Our script runs Anthropic's unmodified binary, which is the safe side of that line.
- If Drew is on Max: monthly API credits ($100 Max 5x, $200 Max 20x) cover the Agent SDK and API but not interactive Claude Code; claiming needs a linked Console org and an API key. [support](https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans) Fallback only; his plan tier is unknown to me.

## 3. Built-in Claude Code features

| Feature | Exists? | Fit for us | Source |
| - | - | - | - |
| Scheduled: `/loop`, cron tools | Yes | No. Session-bound, needs open session, recurring tasks expire after 7 days | [scheduled-tasks](https://code.claude.com/docs/en/scheduled-tasks) |
| Scheduled: Routines (cloud) | Yes, research preview | No. Fresh GitHub clone, no local files, 1-hour minimum, subscription login | [routines](https://code.claude.com/docs/en/routines) |
| Scheduled: Desktop tasks | Yes | No. Desktop app is macOS / x64 Windows per `--desktop` flag text | [cli-reference](https://code.claude.com/docs/en/cli-reference) |
| GitHub Actions `schedule` | Yes | No. Repo and CI runner; `CLAUDE_CODE_OAUTH_TOKEN` secret works | [github-actions](https://code.claude.com/docs/en/github-actions) |
| Channels (Telegram, Discord, iMessage) | Yes, research preview | Later. Needs Bun and an open interactive session; flag hidden from `--help` | [channels](https://code.claude.com/docs/en/channels) |
| Hooks (`Notification`, `Stop`) | Yes | Possible alert hook; runs a shell command when Claude waits for input | [hooks-guide](https://code.claude.com/docs/en/hooks-guide) |
| Remote Control | Yes | No. Steers a session from the Claude phone app, not Telegram | [remote-control](https://code.claude.com/docs/en/remote-control) |
| Built-in cron for headless local runs | Not found | Use OS cron or a systemd / Windows Task Scheduler job | n/a |

Channels facts: Telegram plugin needs a BotFather token and `claude --channels plugin:telegram@claude-plugins-official`; "Events only arrive while the session is open"; sender allowlist by pairing; "When you run channels in non-interactive mode with `-p`, tools that need terminal input, such as multiple-choice questions and plan mode approval, are disabled". ([channels](https://code.claude.com/docs/en/channels))

## 4. Repos (live GitHub check, 19 Oct 2026)

Catalog (all-git) gave leads; every row below was re-checked with `gh api` and the code at the pinned SHA.

| Repo @ SHA | Stars / licence / last push | What the code does | Fit for 5-choice flow | Setup / risk |
| - | - | - | - | - |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/ea10b213686c90bb1984b2016937310e05336cf3/external_plugins/telegram) `ea10b21` (telegram plugin) | 43,110 / Apache-2.0 / 19 Oct 2026 | `server.ts` (1,045 lines): MCP server, grammY long polling, pairing + allowlist. Inline Allow/Deny buttons only for permission prompts (L441-447). `reply` tool is text + files, no buttons (L457-480) | Medium-low. Drew would type "3" and Claude must act on it. Good later as the "Telegram agent" | Bun (the `bun` here is a Windows shim under /mnt/c; WSL use unverified). Always-on interactive session. Research preview, flags may change |
| [overwirehq/claude-code-telegram](https://github.com/overwirehq/claude-code-telegram/tree/164afc1b9d3cb8cc37abd3c930cfb897257c4af9) `164afc1` | 2,814 / README says MIT but no LICENSE file (API 404) / 1 Oct 2026 | Python Telegram bot. Agent SDK first, CLI fallback; sets `ANTHROPIC_API_KEY` only if configured, else CLI login ([L385](https://github.com/overwirehq/claude-code-telegram/blob/164afc1b9d3cb8cc37abd3c930cfb897257c4af9/src/claude/sdk_integration.py#L385)). Whitelist auth, webhooks, cron scheduler, inline keyboards | Closest "Telegram agent + cron + Claude". Built as a remote coding chat, no staged pipeline or batch state | Large app with file and shell access. Unclear licence. Adopt later, not first |
| [easychen/ask4me](https://github.com/easychen/ask4me/tree/088ca312836d7baf4245d0b6b1c50661833ca966) `088ca31` | 113 / MIT / 14 May 2026 | Go server. `POST /v1/ask` with button markup; pushes a link via ServerChan or Apprise; you tap a button on a web page; the call returns the choice. SQLite; reconnect by `request_id` | Good "block until human picks" shape, but the choice happens on a web page, not inside Telegram | Needs a public URL (`ASK4ME_BASE_URL`) or tunnel. One maintainer |
| [VisionForge-OU/foreman](https://github.com/VisionForge-OU/foreman/tree/92d7f7971ca40442f95d552e167d214939a0390d) `92d7f79` | 443 / MIT per LICENSE file (GitHub shows NOASSERTION) / 29 Jun 2026 | Spawns local `claude` headless (stream-json) with turn, cost and time budgets; all state in files; hash-sealed human approval gates; terminal UI | Pattern only (software delivery, no Telegram) | Copy the idea: files as state, crash-safe, explicit gates |
| [context-machine-lab/sleepless-agent](https://github.com/context-machine-lab/sleepless-agent/tree/dbeb1c28699bfc7af48687203a2baa06c62cf7a1) `dbeb1c2` | 834 / MIT / 29 Mar 2026 | Python daemon, Agent SDK `query()` on CLI login ([executor.py L692](https://github.com/context-machine-lab/sleepless-agent/blob/dbeb1c28699bfc7af48687203a2baa06c62cf7a1/src/sleepless_agent/core/executor.py#L692)), SQLite task queue, Slack | Low. Slack, code tasks, git PRs | Proof that SDK on a subscription login works in practice |
| [hanxiao/claudecode-telegram](https://github.com/hanxiao/claudecode-telegram/tree/c925f90e0b5496e760e33140d3fd857d25b3edcd) `c925f90` | 610 / none / 25 Jan 2026 | Telegram webhook via Cloudflare Tunnel, then `tmux send-keys` into an interactive Claude; a Stop hook sends the reply back; resume uses `--dangerously-skip-permissions` ([bridge.py L148](https://github.com/hanxiao/claudecode-telegram/blob/c925f90e0b5496e760e33140d3fd857d25b3edcd/bridge.py#L148)) | Poor. Types keystrokes into the screen | No licence, skips permissions, stale |

Also checked, not a fit: [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) (9,576 stars, MIT, GitHub-only).

## 5. Recommendation

**Shape:** one script, `harness.py`, run by a timer. No long-running process, no open Claude session.

1. `start` (cron, later): run the research stage with `claude -p --model claude-sonnet-5-5 --tools "WebSearch,WebFetch" --json-schema <resource cards> --max-turns N`. Save cards to `batches/<id>/state.json`.
2. Hook stage: one `claude -p --model claude-sonnet-5-5 --safe-mode --tools "" --system-prompt-file prompts/hooks.txt --json-schema <5 hooks> --output-format json --no-session-persistence`. Input is the cards as text. Check count, duplicates and sources in the script. Save, set `status: waiting_for_drew`.
3. Ping: `sendMessage` with the 5 hooks and an inline keyboard (1-5, Skip) ([Bot API](https://core.telegram.org/bots/api#inlinekeyboardmarkup)).
4. `tick` (every minute): `getUpdates` long poll ([Bot API](https://core.telegram.org/bots/api#getupdates)); accept only Drew's chat id; `answerCallbackQuery`; write the choice to state; start the next stage. Skip re-runs the stage with feedback.
5. Narration stage: same pattern. Pass the exact chosen hook and its card explicitly instead of relying on `--resume`, so each stage can be re-run alone.
6. Failure: non-zero exit, `is_error`, or `error_max_structured_output_retries` sends Drew a short Telegram error. Expired login fails every call ("Login expired · Please run /login", [authentication](https://code.claude.com/docs/en/authentication#renew-an-expiring-login)); a ping on the first failure covers it.

**Reuse:** `claude -p` (nothing to install); Telegram Bot API through Python's standard library; cron or a systemd / Windows Task Scheduler timer; prompts already drafted in `01-content/writing-harness-prompts.md`.

**Write (about 150 lines, I can do it):** the state file, the stage runner, the Telegram sender and poller, JSON schemas for 5 hooks and 5 narrations.

**Drew's only steps:** make a bot in BotFather (2 minutes) and give the agent the token and Drew's chat id; run `claude setup-token` if cron cannot see Drew's login. Keep the token out of this folder.

**Later:** the Telegram agent calls the same entry point (`harness.py choose <batch> <n>`), so the script does not change. The official Telegram plugin or overwirehq/claude-code-telegram then become the front door.

**Cost:** zero dollars. Each stage uses plan limits (five-hour window and weekly cap, shared with Claude chat). A few calls per batch is small. `--tools ""` and `--system-prompt` keep prompts short.

## Unverified

- ~~Model ID accepted~~ **Verified October 19:** `claude -p --model claude-sonnet-5-5 --json-schema ... --tools ""` succeeded on Drew's Max subscription (claude.ai login, no API key). It returned the structured answer in 3.5 s. Claude Code also used Haiku 4.5 for a small background step.
- ~~Safe mode drops CLAUDE.md~~ **Verified October 19:** asked to quote the per-reply skill path from its instructions, the normal run quoted the caveman skill path. The `--safe-mode` run answered "none".
- How Anthropic classifies a Python script that shells out to `claude -p`. Docs call headless a supported surface; no direct statement on this case.
- Whether cron or Windows Task Scheduler can see Drew's login from WSL, and that WSL stays running when the timer fires.
- Bun working under WSL for the official Telegram plugin.
- Drew's plan tier (Pro or Max) and its real limits. No exact numbers are published on the pages I read.
- The April 2026 third-party harness change (news only).
