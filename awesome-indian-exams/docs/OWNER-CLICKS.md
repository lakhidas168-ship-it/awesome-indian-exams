# Owner clicks: every login and permission the hive needs, in one place

The owner's whole job is logins and payments. Everything else is automated. Steps marked **optional** add
capacity but nothing breaks without them.

## Already done

- This repository exists and is public: <https://github.com/lakhidas168-ship-it/awesome-indian-exams>.
- The hive runs on the owner's Mac (see [`ops/HIVE.md`](../ops/HIVE.md)). Its agents work against a local bare
  repository, `~/.hive/hub.git`, and `~/.hive/publish-github.sh` publishes **one gated, batched commit per hour**
  here. Commits that land on `main` here are merged back into the Mac hub by the same script.
- The cloud workflow `hive-cloud.yml` has **no schedule, on purpose**. Claim refs and per-task pushes every 20
  minutes look like git used as a message bus, which got the owner's previous GitHub account flagged as spam.

## A. The Mac: only when the doctor asks (`H-004`)

`python3 awesome-indian-exams/ops/doctor.py --mac` (also in `~/.hive/doctor.log`) names anything missing. The
usual fixes:

1. **Let the schedule read your folders:** open
   `x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles` (paste into Safari's address bar,
   or run `open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"`) → **+** →
   press ⌘⇧G → type `/usr/sbin/cron` → Open → switch it on.
2. **Keep the Mac awake on the charger:** paste `sudo pmset -c sleep 0` in Terminal, or System Settings →
   Battery → Options → "Prevent automatic sleeping on power adapter when the display is off".
3. **Sign in once in each agent** so it can run unattended: `opencode auth login` (choose OpenCode Go), `gemini`
   (sign in with Google), `agy` (sign in), `command-code login` (the account with the GOAT plan), and Hermes as you already set it up.

**Easiest:** in Terminal run `cd ~/code/awesome-indian-exams 2>/dev/null || cd ~ ; claude remote-control`,
open the new session in the Claude app, and say "Follow awesome-indian-exams/docs/MAC-HANDOFF.md".

## B. Your nine months of earlier work: the harvest (`H-005`)

4. **Google accounts:** for each account that holds exam material, either
   - sign it into **Google Drive for desktop** (it supports several accounts; each appears under
     `~/Library/CloudStorage/`), or
   - export it with **Google Takeout** <https://takeout.google.com> (choose Drive) and unzip the download into
     `~/Hive-Inbox`.

   The harvest scan runs every 6 hours, finds exam work in all of these places, removes duplicates, and keeps
   transcripts and coaching material out. The index stays private on the Mac.

## C. Optional extras

- **Switch on the website (one click, recommended):** open
  <https://github.com/lakhidas168-ship-it/awesome-indian-exams/settings/pages> → under "Build and deployment",
  Source: **GitHub Actions**. From the next update on, the list is live at
  <https://lakhidas168-ship-it.github.io/awesome-indian-exams/> with search, and the open data at `/data/exams.json`.
- **Exam AI accounts (Hugging Face and Kaggle):**
  1. Add two secrets at
     <https://github.com/lakhidas168-ship-it/awesome-indian-exams/settings/secrets/actions/new>:
     - `HF_TOKEN`: a Hugging Face **write** token from <https://huggingface.co/settings/tokens>;
     - `KAGGLE_API_TOKEN`: a Kaggle API token from <https://www.kaggle.com/settings> (API section).
     (The workflow also accepts the names `HUGGING_FACE` and `KAGGLE`.)
  2. Run <https://github.com/lakhidas168-ship-it/awesome-indian-exams/actions/workflows/ai-accounts.yml> →
     "Run workflow". It checks both logins and publishes the open data as the free Hugging Face dataset
     `<your account>/awesome-indian-exams`.
- **Run the cloud hive by hand** (for example while the Mac is off):
  1. Add the secret `OPENCODE_API_KEY` (key from <https://opencode.ai/auth>) at
     <https://github.com/lakhidas168-ship-it/awesome-indian-exams/settings/secrets/actions/new>.
  2. If wanted, add `GEMINI_API_KEY` too (key from <https://aistudio.google.com/apikey>), at the same link.
  3. Start it from the Actions tab:
     <https://github.com/lakhidas168-ship-it/awesome-indian-exams/actions/workflows/hive-cloud.yml> → "Run workflow".

  Never give it a schedule.
- **Student benefits** (if you have current student verification): <https://education.github.com/pack>.
- **Stop everything:**
  - On the Mac, run `bash awesome-indian-exams/ops/hive-loop.sh stop` from `~/code/awesome-indian-exams`.
  - To block manual cloud runs too, add a repository variable `HIVE_ENABLED` = `false` at
    <https://github.com/lakhidas168-ship-it/awesome-indian-exams/settings/variables/actions/new>.

## D. Growth accounts (optional, once: `H-007`)

These help the list spread; nothing breaks without them.

1. **Search:** add the website to Google Search Console
   (<https://search.google.com/search-console>) as a URL-prefix property
   `https://lakhidas168-ship-it.github.io/awesome-indian-exams/`, then submit `sitemap.xml`.
2. **Repository card:** on <https://github.com/lakhidas168-ship-it/awesome-indian-exams>:
   - click the gear next to "About" and add these topics: `india`, `competitive-exams`, `upsc`, `ssc`, `gate`,
     `jee`, `neet`, `exam-preparation`, `awesome-list`, `hindi`;
   - under Settings → General → Social preview, upload `awesome-indian-exams/assets/social-card.png`.
3. **Telegram channel** (for `T-318`):
   - create a public channel;
   - in Telegram, message @BotFather with `/newbot` and add the new bot to the channel as an admin;
   - give the bot token and the channel's `@name` to the Mac session, which saves them in `~/.hive/agents.env`
     as `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

## What runs where

| Where | Who | Model |
|---|---|---|
| Mac, continuous | Hermes lane: Hermes (`hermes -z`), plus Gemini CLI and Antigravity when signed in | Hermes on free models; each tool's own login |
| Mac, continuous | OpenCode lane: `opencode run` | OpenCode Go: DeepSeek V4.1 Flash |
| Mac, continuous | Command Code workers (`commandcode-1..6`, Hermes lane by default) | Command Code GOAT plan: open models, `HIVE_COMMANDCODE_MODEL` |
| Mac, continuous | Free-agent workers (HTTP) | Free tiers, with the owner's own proxy first when configured |
| Mac, recurring | JEVX judge (`ops/judge.py --publish`) against the local hub | OpenCode Go first, free tiers after |
| Mac, hourly | `~/.hive/publish-github.sh`: one gated commit to GitHub | none (validate, tests, secret and path checks) |
| Mac, every 6 h | Harvest scan of Mac folders, Drive for desktop, iCloud, `~/Hive-Inbox` | none (plain code) |
| GitHub, on every push and PR, hourly re-check, daily link check | `awesome-exams` workflow (read-only) | none |
| GitHub, by hand only | `hive-cloud` workflow | the free agent, OpenCode Go when its key is set |

All Mac workers claim from one local backlog, so no task is done twice.
