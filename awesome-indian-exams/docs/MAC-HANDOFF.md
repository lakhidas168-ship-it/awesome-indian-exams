# Mac handoff: instructions for a Claude session running on the owner's Mac

**Owner:** on the Mac, open Terminal and paste `cd ~/code/awesome-indian-exams 2>/dev/null || cd ~ ; claude remote-control`.
A session that runs on the Mac appears in the Claude app. Tell it: **"Follow awesome-indian-exams/docs/MAC-HANDOFF.md"**.
(If the repo is not on the Mac yet, the session clones it in step 1.)

---

**Claude on the Mac, this is for you.** The owner wants zero involvement beyond logins and payments. Do the steps
below in order, without asking unless a step needs the owner's password or a browser login. In that case, open
the exact page for them and wait. Report at the end what ran, what failed, and what the owner must click.

1. **Repository.** Work in `~/code/awesome-indian-exams`. On a Mac that is already set up it is a clone of the
   local hub `~/.hive/hub.git`: leave its remotes as they are and run `git pull --ff-only`. If the folder does not
   exist, clone <https://github.com/lakhidas168-ship-it/awesome-indian-exams> there
   (`mkdir -p ~/code && git clone https://github.com/lakhidas168-ship-it/awesome-indian-exams.git ~/code/awesome-indian-exams`).
   Read `CLAUDE.md` at the repository root before anything else.
2. **Health first.** `python3 awesome-indian-exams/ops/doctor.py --mac`. Fix what you can: install missing tools
   with Homebrew or npm. Collect what needs the owner (logins) for your report.
3. **Set up and start continuous mode.** `bash awesome-indian-exams/ops/mac-bootstrap.sh --loop`
   - It writes `~/.hive/agents.env`. Check that each command works as a one-shot on this Mac, and fix the file if
     not. Test each with a harmless prompt, e.g. `hermes -z "reply with OK"`,
     `opencode run -m opencode-go/deepseek-v4.1-flash "reply with OK"`, `gemini --yolo -p "reply with OK"`.
   - If the owner uses JEVX through its own CLI or MCP, put its one-shot command in `HIVE_CMD_JEVX`.
   - Size the parallelism to this Mac: about one worker per 2 GB of free RAM, at most 6 per lane
     (`HIVE_LOOP_HERMES`, `HIVE_LOOP_OPENCODE` in `agents.env`). Then
     `bash awesome-indian-exams/ops/hive-loop.sh stop && bash awesome-indian-exams/ops/hive-loop.sh start`.
4. **Harvest the owner's earlier work.** `python3 awesome-indian-exams/ops/harvest.py scan`, then `summary`.
   - Use the local filesystem MCP and any NotebookLM MCP available on this Mac to find exam material outside the
     default roots. Add those folders to `HIVE_HARVEST_ROOTS` in `agents.env` and scan again.
   - Never copy files into the repository yourself. The hive turns inventory items into verified pages through
     `where = "mac"` tasks, which the JEVX run adds.
5. **Watch the first hour.** Every ~10 minutes, `bash awesome-indian-exams/ops/hive-loop.sh status` and
   `python3 awesome-indian-exams/ops/doctor.py --mac`. If a worker keeps failing, read its log in `~/.hive/`,
   fix the cause (a login, a wrong command in `agents.env`, a missing tool) and restart the loop. Don't edit the
   protected hive files; propose changes in a PR instead.
6. **Report** to the owner, in Hinglish, short:
   - workers running;
   - tasks claimed and pushed in the first hour;
   - harvest item counts;
   - every owner action still needed, each with its exact link or command from `docs/OWNER-CLICKS.md`.

Rules that always apply: official sources only for exam facts; no copyrighted text (coaching material, books,
lecture transcripts); no personal data or local paths in the repository; never weaken a hive gate or test.
