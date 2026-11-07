# Demo video script (target 2:30–3:00)

Record with **Cmd+Shift+5 → Record Entire Screen** (or a selected portion). Upload to
YouTube (Unlisted) or Loom, then paste the link into README.md where it says `TODO: add link`.

Before you record:
- Mattermost open in a browser at `localhost:61559`, logged in as `shikhar`. Have the `desk-submissions` and `desk-judging` tabs ready.
- The **sandbox runner** terminal is visible (`python3 tools/runner.py`).
- `shortlist.template.yaml` is open in an editor, or GitHub is open at the repo.

---

### 0:00–0:20 · The problem (show the GitHub README top)
> "Every hackathon ends with a few judges and hundreds of repos. Most of judging
> time goes to cloning repos, finding out the README doesn't run, and hunting
> for the demo link. Shortlist hands that grunt work to Switch agents, and
> humans make every call, right in team chat."

### 0:20–0:45 · One Switch template builds the whole desk (show shortlist.template.yaml, scroll)
> "One Switch template creates three agents, two linked rooms (a public intake
> room and a private judging room), three roles (clerk is exclusive, reproducer
> and scorer are shared), and the rubric and house rules as room documents.
> Import it in Switch Console, click Use, and the desk is open."

Show the Switch Console Rooms list for a second (desk-submissions, desk-judging).

### 0:45–1:15 · A participant submits (desk-submissions)
Post: `Submitting Standup Relay v2: https://github.com/sgoel2be24-cyber/shortlist/tree/main/demo/submissions/standup-relay @desk-clerk`
> "A participant drops a link. The clerk gives it a case id, runs a static
> preflight check, and answers in the thread with a checklist of what they can
> still fix. No scores ever appear in this public room."

### 1:15–1:55 · Evidence in the private room (desk-judging + runner terminal)
> "In the private room the clerk opens the case and addresses the reproducer
> and scorer roles. The reproducer never runs submission code itself. It files a
> job, and a human-started **sandbox runner** runs the README's commands in a
> locked-down Docker container." *(point at the terminal: ▶ S-n … ■ PASS)*
> "The scorer grades against the rubric document, citing a file and line for
> every score, and argues against its own score."

Scroll to an earlier scorecard (S-2 18/100: MODULE_NOT_FOUND, plus the dead Loom link with its 404).
> "It caught a broken build and a demo link that returns a 404, things a
> checklist would miss."

### 1:55–2:25 · Humans decide (desk-judging)
Post: `@desk-clerk shortlist S-n`
> "Only a human can decide. The clerk updates the scoreboard document and tells
> the participant their status, kindly, in their thread." *(switch to the public room to show it)*

### 2:25–2:50 · The safety moments (scroll the judging room)
> "Three times Switch's guardrails stopped the wrong thing:
> - The reproducer refused to fake a result when its permissions blocked it.
> - Owner-only commands were refused from an unlinked account, even when another
>   agent tried to pass them along.
> - The scorer flagged a commit pushed *after* scoring, and the clerk flagged that
>   the submitter was also judging."

### 2:50–3:00 · Close
> "Rooms, roles, documents, access rules, linked rooms and one template:
> Shortlist works only because it's built on Switch. Swap the rubric, and it
> reviews grants, take-homes or pull requests."
