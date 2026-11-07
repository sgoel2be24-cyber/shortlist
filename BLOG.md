# I turned a Mattermost channel into a hackathon judging desk with three AI agents

*Built for the Flip the Switch Hackathon with [Switch](https://github.com/sandbox-quantum/switch).*

Every hackathon ends the same way. A few judges face a pile of repos, and most
of their time goes to work that isn't judging: cloning repos, finding out the
README steps don't run, and hunting for the demo link. **Shortlist** hands that
work to agents and leaves the decisions with people. It all happens in the
team chat the judges already use.

## The setup: one template, about 10 minutes

Switch puts AI coding agents (I used Claude Code) into team chat as teammates.
The part that sold me is **templates**. One YAML file creates:

- **3 agents**, each with its own brief and access rules
- **2 linked rooms**: a public `#shortlist-submissions` and a private `#shortlist-judging`
- **3 roles**: `clerk` (exclusive), `reproducer` (shared) and `scorer` (shared)
- **2 room documents**: the rubric and the house rules, which every agent reads on joining
- **the kickoff messages** that wake the agents up

Import it in Switch Console, click **Use**, and the desk is open.

## The flow

1. A participant posts a repo link in the public room.
2. The **clerk** runs a static preflight check (README, run steps, video,
   license, actual platform use) and replies with a ✅/❌ checklist.
3. The clerk opens case `S-1` in the private room and addresses
   `@reproducer` and `@scorer`. These are *roles*, not agent names, so adding
   a second reproducer agent to clear a backlog takes no configuration.
4. The **reproducer** pulls the README's run commands and runs them in a
   locked-down Docker container. It posts PASS or FAIL with the real output.
5. The **scorer** grades against the rubric document, with evidence for every
   line and a devil's-advocate note against its own score.
6. A **human judge** types `@clerk shortlist S-1`. The clerk updates the
   `scoreboard` document and posts a status update to the participant.

## What surprised me about Switch

- **Roles beat agent names.** `@reproducer` reaches whoever holds the role, so
  the workflow doesn't break when the agent behind it changes.
- **Access rules are the security model.** Only the clerk is addressable by
  anyone. The agents that run code and assign scores answer only their owner
  and their owner's agents. A participant can't talk their way to a better
  score.
- **Room documents are shared memory.** The rubric lives in the room, so
  every agent that joins reads the same rules.
- **Presence isn't availability.** If an agent is idle, Switch says so in the
  channel instead of leaving you waiting.

## Try it

Repo: https://github.com/sgoel2be24-cyber/shortlist. It includes three demo
submissions: one that passes, one with a broken build, and one that's mostly
buzzwords.

The same desk works for grant reviews, take-home interviews and open-source PR
triage. Swap the rubric document and keep the rooms, roles and template.

#HowISwitch
