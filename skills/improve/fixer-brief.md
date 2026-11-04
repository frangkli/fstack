# Fixer brief

Send the fixer this brief with the verified records to fix, the scope globs, the base commit, the state folder and whether this is the final style pass. Use the `fixer` agent when one is defined, otherwise a general subagent.

---

Fix these verified findings. Each record gives the path, the line range, the problem, its trigger (a failing test or the exact input) and the evidence. The verifier already confirmed them: start from the record, never re-investigate whether the problem exists. You may try more than one fix. For each finding, return a verdict:
- **fixed:** with the pin, a test that fails without your fix;
- **rejected:** with the reason (needs a change outside the scope, blocked by a documented guarantee, or needs a decision);
- **deferred:** info findings only, outside the final style pass, with the reason.

Rules:
- Edit only files inside the scope. If a fix needs a file outside it, reject the finding and name the path.
- Save each fix as a local save point: `git add -- <the in-scope files you changed>`, then `git commit --fixup=<the commit that owns the code>`. Never push, and leave the rest of the tree and the history alone: no `checkout --`, `stash`, `reset` or `clean`.
- Every fix that changes behaviour gets a pin: a test that fails on the code before your fix. A heuristic fix gets a small table of cases covering each class of input, not one example. When the code imitates another system (a parser, a CLI, a file format), the pin's expected accepted and rejected inputs come from running that system, not from reading its docs.
- Fix the root cause the record points to, and leave unrelated code alone. When that fix is a design change and a smaller fix would only route around the design problem, reject the finding as "needs a decision" and give the options with their costs.
- When a documented guarantee makes the finding impossible to fix, reject it and say which guarantee. Keep the guarantee as written.
- Keep every behaviour the contract requires. If removing one is the only fix, reject the finding as "needs a decision" and name the requirement.
- In the final style pass, reject as "needs a decision" a fix that would change a public interface other modules or packages depend on.
- Write code and comments as if the loop didn't exist: nothing that mentions rounds, reviewers or earlier fixes.
- Run the cheapest check that covers each fix, as the commands table in AGENTS.md (or `GATES.md` where a repo has one) describes, under `timeout`. If two distinct fix attempts leave the same defect, stop and return "blocked" with both attempts. A test that fails as expected before its fix, or a fixture still being written, is not a failed attempt.
- Build anything you need from another commit in a `git worktree` under the state folder's `scratch/`, never in `/tmp`, and never set `CARGO_TARGET_DIR`.
