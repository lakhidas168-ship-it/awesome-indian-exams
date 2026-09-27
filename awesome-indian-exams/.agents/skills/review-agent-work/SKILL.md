---
name: review-agent-work
description: How the JEVX lane judges an agent's change to awesome-indian-exams (approve / request change / reject). Use when reviewing agent PRs or branches.
---

# Review agent work (JEVX)

Code has already checked format, lane scope, protected files and the evidence rule. You judge what code can't.

**Approve only if all of these hold:**
1. The diff does what the task's `accept` criteria say, visibly in the diff and not just in the notes.
2. Every exam fact is supported by an official source listed on the page. A page is `official` only where the
   receipt's "Sources fetched (code)" shows an HTTP 200 fetch of that URL.
3. It helps a student: clear, correct and specific, not padding.
4. No copied third-party text, no file-dump links, and no weakened checks or tests.

**Reject** (with a one-line reason) when any of these fails, or when the change is empty or off-task.
A rejected task goes back to the queue after a cool-down.

**Mac PR mode:** approve with `gh pr edit <n> --add-label hive:approved`. Reject with
`gh pr close <n> --delete-branch --comment "<reason>"`.
**Cloud mode:** `ops/judge.py` asks for a JSON verdict: `{"approve": true|false, "reason": "..."}`.
