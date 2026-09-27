# Owner clicks: every login and permission the hive needs, in one place

The owner's whole job is logins and payments. Everything else is automated. Do these once, in order; each is a link
to open or a line to paste. Steps marked **optional** add capacity but nothing breaks without them.

## A. Switch the hive on (2 minutes)

1. **Merge the pull request.** This starts the free hourly cloud hive.
   <https://github.com/lakhidas168-ship-it/lakhidas168-ship-it/pull/1> → "Ready for review" → "Merge pull request".
2. **OpenCode Go key → repository secret** (DeepSeek V4.1 Flash for the OpenCode lane and the judge).
   - Sign in with the account that has the Go plan and create an API key: <https://opencode.ai/auth>
   - Add it as a secret named `OPENCODE_API_KEY`:
     <https://github.com/lakhidas168-ship-it/lakhidas168-ship-it/settings/secrets/actions/new>
3. **Gemini API key (free) → repository secret** `GEMINI_API_KEY`. Create the key at
   <https://aistudio.google.com/apikey> and add it at the same secrets link as above.
4. **Optional, more free capacity:** OpenRouter key <https://openrouter.ai/settings/keys> → secret
   `OPENROUTER_API_KEY`. Groq key <https://console.groq.com/keys> → secret `GROQ_API_KEY`.

## B. The Mac: your own agents join the same hive (5 minutes)

5. **One paste in Terminal** (after step 1). It detects OpenCode, Hermes, Gemini CLI, Antigravity, JEVX and Ollama,
   writes `~/.hive/agents.env`, installs the hourly schedule, and starts the first scan of your earlier work.
   It opens the GitHub login in the browser if needed.
   ```bash
   mkdir -p ~/code && cd ~/code && { [ -d lakhidas168-ship-it ] || git clone https://github.com/lakhidas168-ship-it/lakhidas168-ship-it.git; } && cd lakhidas168-ship-it && git pull --ff-only && bash awesome-indian-exams/ops/mac-bootstrap.sh
   ```
6. **Let the schedule read your folders:** open
   `x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles` (paste into Safari's address bar,
   or run `open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"`) → **+** →
   press ⌘⇧G → type `/usr/sbin/cron` → Open → switch it on.
7. **Keep the Mac awake on the charger** (cron can't run while it sleeps): paste `sudo pmset -c sleep 0` in
   Terminal, or System Settings → Battery → Options → "Prevent automatic sleeping on power adapter when the display
   is off".
8. **Sign in once in each agent** so it can run unattended: `opencode auth login` (choose OpenCode Go), `gemini`
   (sign in with Google), `agy` (sign in), Hermes as you already set it up. If you use JEVX from its own
   command, put that command in `~/.hive/agents.env` as `HIVE_CMD_JEVX="..."`. The doctor (`~/.hive/doctor.log`)
   says which ones are missing.

## C. Your nine months of earlier work (the harvest)

9. **Google accounts:** for each account that holds exam material, either
   - sign it into **Google Drive for desktop** (it supports several accounts; each appears under
     `~/Library/CloudStorage/`), or
   - export it with **Google Takeout** <https://takeout.google.com> (choose Drive) and unzip the download into
     `~/Hive-Inbox`.
   The harvest scan runs every 6 hours, finds exam work in all of these places, removes duplicates, and keeps
   transcripts and coaching material out. The index stays private on the Mac.
10. **Optional:** let a Claude session work directly on the Mac: in Terminal, `cd ~/code/lakhidas168-ship-it`
    then run `claude remote-control`. It then shows up in the Claude Code app.

## D. Its own public repository (when you want it)

11. Create the empty repository (the form is pre-filled):
    <https://github.com/new?name=awesome-indian-exams&visibility=public&description=Free%20evidence-gated%20prep%20maps%20for%20India%27s%20competitive%20exams>
12. Give Claude access to it: <https://github.com/apps/claude/installations/select_target> → your account →
    Repository access → add `awesome-indian-exams`. A Claude session then moves this folder there (task `H-002`).

## E. Optional extras

- **Student benefits** (if you have current student verification): <https://education.github.com/pack>. Copilot
  Pro raises the free GitHub Models limits the hive uses.
- **Stop everything:** add a repository variable `HIVE_ENABLED` = `false` at
  <https://github.com/lakhidas168-ship-it/lakhidas168-ship-it/settings/variables/actions/new>. Delete it to
  resume.

## What runs where after these clicks

| Where | Who | Model |
|---|---|---|
| Cloud, hourly (free) | Hermes lane: built-in free agent | GitHub Models → Gemini → OpenRouter → Groq → OpenCode Go |
| Cloud, hourly | OpenCode lane: the real OpenCode CLI | OpenCode Go: DeepSeek V4.1 Flash (free agent as fallback) |
| Cloud, hourly | JEVX judge | OpenCode Go first, free tiers after |
| Mac, hourly | Hermes (`hermes -z`), Gemini CLI, Antigravity (`agy`): parallel workers in the Hermes lane | their own logins and models |
| Mac, hourly | OpenCode (`opencode run`, OpenCode Go), JEVX planner + PR reviewer | as configured |
| Mac, every 6 h | Harvest scan of Mac folders, Drive for desktop, iCloud, `~/Hive-Inbox` | none (plain code) |

All of them claim from one backlog on GitHub, so the Mac and the cloud never do the same task twice.
