---
name: improve
description: Review, verify and fix loop with a fixed round budget. Use to improve, clean up or harden a module, system or repo, to fix the findings of a review, or as the fix step of adversarial-review and pr.
---

# Improve

Fresh reviewers find defects, a fresh verifier confirms them and a fresh fixer fixes them, over one scope. A run has one full review round and one confirming round, and a third round only when the confirming round confirms a new critical or major finding. A low-risk, low-impact change gets no confirming review, and neither does a round 1 that fixed no critical or major finding and touched no high-risk file: the verifier alone checks its fixes. Either way, no unchecked fix counts as done. Before a PR is marked ready, one more run reviews the whole branch for style: the [final style pass](#final-style-pass).

## Inputs

- **Target:** the branch's change by default, or the paths you were given.
- **Scope:** path globs the fixer may touch. Default: the target's directories, wide enough to put tests next to the code.
- **Reviewer:** `adversarial-review`. When it hands you its review, that review was round 1 of this run, already verified and recorded in the state folder: continue from its `next.md` at step 4. Findings handed over from anywhere else (a PR's bots, a person, a maintenance pass with [lens.md](lens.md)) are round 1's candidates: write them as `round-1/handed.json`, build round 1's packet with `adversarial-review`'s packet command, pick risk and impact with its table, and start at step 3.
- **Contract:** what the change must achieve and must not break, when the caller has one. Fixes keep every requirement in it.
- **Base:** the commit to diff against.
- **State folder:** the run's `state/<ticket>/` when an orchestrator passes one, otherwise `$(git rev-parse --path-format=absolute --git-common-dir)/improve/<slug>/`. It lives outside the worktree, so an agent resumed in any worktree of the repo finds it. Layout, formats and the `ledger.py` commands: [ledger.md](ledger.md).

## Steps

1. **Baseline.** If the state folder holds an unfinished run ([ledger.md](ledger.md) says when), continue from its `next.md`, never from round 1, under the [final style pass](#final-style-pass)'s changes when `next.md` names that pass. Otherwise, if a finished ledger ended `done` and its `head` is an ancestor of `HEAD` (`git merge-base --is-ancestor`), the change only grew since that run: round 1's base is that head. After a rebase, or a run that ended any other way, round 1 uses the target's base. Move the finished ledger aside, keeping its `decisions` and its refuted and deferred findings, and run `ledger.py init`. Commit the target's uncommitted in-scope changes as a `wip:` save point, so every round reviews a commit; running `improve` is the request to commit. Add the contract and the hashes of the untracked files outside the scope to the ledger.
2. **Review.** Every round calls `adversarial-review` in findings mode, unless it already ran round 1 itself. For round 1, pass the target's base; it picks the lanes from its risk and impact table. Later rounds call it with its base set to the last reviewed head, so the packet, `ocr` and every lane see only the fix diff, plus the round number and the ids the fixes claim to close. The lanes: one combined reviewer, plus the bug-pass lanes scoped to the same diff when it touches high-risk code, plus design-and-style when the run uses the lens. Skip the lanes and go to step 3 with no candidates when round 1 picked no confirming round (low risk, low impact), or when round 1's fixes closed no critical or major finding and changed no file it marked high risk.
3. **Verify.** `ledger.py candidates <state> <n> <shards>`, with one shard per 10 candidates, at most 4 (1 up to 12 candidates). Then one fresh verifier per shard, all in parallel, under [the verifier brief](../adversarial-review/verifier-brief.md), gets the round's packets, the lane results, its candidates file (`candidates.json`, or `candidates-<k>.json` when split) and the closing ids whose path is in its file. Each confirms or refutes its candidates, checks its closing fixes, and writes `verified-<n>.json` or `verified-<n>-<k>.json`. Then `ledger.py apply <state> <n> <head>`, which reads them all. Read only the verifiers' summaries. These are the round's only verifiers.
4. **Decide.**
   - A confirmed finding whose only fix drops or narrows a contract requirement: escalate it, and send the rest on.
   - After round 1: fix the open criticals and majors and the minors whose fix changes one line of code (its pin test aside). With none, go to step 7.
   - After the confirming round: a new critical or major, or a critical or major fix that didn't hold, means fix, then the third and last round. Any other critical or major still open stops the run. With none open, go to step 7.
   - After the third round: anything critical or major still open stops the run; otherwise go to step 7.
5. **Fix.** One fresh fixer gets the records step 4 picked, under [fixer-brief.md](fixer-brief.md). It never re-identifies a problem, may try more than one fix, and commits each fix as a local `fixup!` save point; nothing is pushed. Record each rejection and deferral with `ledger.py verdict`, and write the ids it claims fixed into `next.md` as the next round's closing list.
6. **Scope guard.** Compare `git diff --name-only <base>` and the untracked files against the scope globs, and re-hash the guarded files. A change outside the scope halts the run; leave it in place and report it. Otherwise back to step 2.
7. **Finish.** Spot-check one pinned fix: in a scratch worktree under the state folder's `scratch/`, put that file back to its base version and confirm its test fails. Remove any comment or name that narrates the loop. Fold the save points with `git -c sequence.editor=: rebase --interactive --autosquash <base>`, and give a remaining `wip:` commit a real message (`fix: …`, or the repo's convention), drafted by the `writer` agent when one is defined. Record each minor or info still open, unless the fixer rejected it, with `ledger.py verdict <state> <id> deferred Noted`. Run `ledger.py outcome`, remove the scratch worktrees, and report.

After each step, rewrite `next.md`: whether the run is the final style pass, the step just finished, the next one, the last reviewed head, the high-risk files, the closing ids, and any lane still running. Run every long command under `timeout`. The same check failing twice with the same error halts the run as blocked, with both attempts.

Run the repo's cheapest relevant checks while fixing, and its full readiness check once at the end, as `GATES.md` describes.

## Final style pass

The caller (`pr`) starts this run after the last bug-fix round and before it marks the PR ready, and skips it when it already ran on this change: the ledger's `style_pass` is set, its `outcome` is `done`, and `git diff --quiet <its head> HEAD` passes. It reviews only design and style, once, and its last verifier confirms that each fix keeps behaviour, so no bug round follows it. The steps above run with these changes:

1. **Baseline.** An unfinished final style pass ([ledger.md](ledger.md) says when) continues from its `next.md`. Otherwise the base is the branch's merge base with the default branch, and the state folder is the branch's, as the review left it. The round number n is one past the highest round in the ledger or in the state folder's `round-<k>/` folders. Keep the ledger in place and run `ledger.py init` on it, which keeps the findings. Then write `next.md` naming the pass and round n. Then `ledger.py style <state> <n>` writes the findings the `design-style` lane raised that are still deferred or open, except Dismissed ones, to the round's lane file `deferred.json` for a re-check. It changes no status, so a pass cut off before its round is applied starts over and picks the same findings.
2. **Review.** `adversarial-review` in findings mode with the `design-style` lane alone, on the full branch diff.
3. **Verify** as usual, when the round has candidates. The verifier re-checks each finding marked `recheck` against the current code.
4. **Decide.** Fix every finding confirmed in round n, whatever its severity; the one-line rule for minors doesn't apply. With no candidates or none confirmed, the pass changed no code: go to step 7, without the end-of-run readiness check.
5. **Fix** as usual. A rejection doesn't stop the pass: report each one as a design question for the owner, with the fixer's options.
6. **Check.** After the scope guard, one fresh verifier under [the verifier brief](../adversarial-review/verifier-brief.md) gets the fix diff (`git diff <round n's head> HEAD`), no candidates, the ids the fixer claims fixed and word that this is the final style pass, and writes `verified-<n+1>.json`. Skip `ledger.py candidates` and run `ledger.py apply <state> <n+1> <head>`. No review round follows. A fix that didn't hold stays open, and goes to the report. Then step 7, whose end-of-run readiness check is the pass's test run, and which ends the pass `done`.

## When to stop

| Outcome | When | Report |
|---|---|---|
| **Done** | A review round left no critical or major open, or the final style pass reached step 7, rejections included | Rounds, open minor findings, state folder path |
| **Escalated: still open** | A critical or major is open when step 4 stops the run, including one the fixer rejected as outside the scope | Each finding by title and id, and the decision that's needed |
| **Escalated: impossible** | The fixer says a finding is real but blocked by a documented guarantee | The guarantee and the finding |
| **Escalated: contract** | The only fix for a finding drops or narrows a contract requirement | The requirement, the finding, and the options |
| **Escalated: design** | In a bug round, the fixer rejects a finding as "needs a decision": its root cause is a design problem a local fix would only route around | The finding, the design problem, and the fixer's options with a recommended default |
| **Halted** | A change outside the scope, a reviewer, verifier or fixer that died or couldn't run (including a usage limit), or a check that failed twice with the same error | What happened, from the ledger; nothing reverted. Running `improve` again continues from `next.md` once the cause is cleared |

An escalation is never reported as success. To continue after one, start a fresh run with the user's ruling added to the new ledger's `decisions` as binding.

## Report

Follow [the review report format](../adversarial-review/report.md), including its writing rules: outcome first, then what was fixed (each with its pin), what's left and why, and decisions that need the user. Name every finding by its title, with its id beside it.
