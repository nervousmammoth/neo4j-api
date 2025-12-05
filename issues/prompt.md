## Starting Work on an Issue

DONT WORK IN MAIN

### Before You Code

1. **Read the full issue** — understand the problem, acceptance criteria, and any linked discussions or prior attempts
2. **Clarify ambiguity first** — if something's unclear, ask before you build the wrong thing
3. **Check for related issues or PRs** — someone may have started this, or there may be dependencies
4. **Understand the relevant codebase area** — read the code you'll be touching, trace the data flow

### Setup

1. **Pull the latest from main** — don't start from stale code
2. **Create a feature branch** — use a descriptive name like `fix/issue-123-user-auth-bug` or `feat/add-export-csv`
3. **Reproduce the bug or understand the current behavior** — confirm you can see what you're fixing or extending

### Development

1. **Follow TDD with high-quality, real-world tests**
   - Write a failing test first, then make it pass, then refactor
   - **100% test coverage is required** — every line, branch, and edge case must be tested
   - Write tests that reflect actual usage, not just happy paths
   - Test edge cases: empty inputs, nulls, boundary values, malformed data, concurrent access
   - Test error handling: ensure failures are caught, logged, and handled gracefully
   - Avoid trivial tests that just confirm the code runs — tests should validate behavior and catch regressions
   - If a bug prompted the issue, write a test that reproduces it before fixing
   - Tests are documentation — someone reading them should understand what the code does and why

2. **Make atomic commits** — each commit should be a single logical change that compiles and passes tests
3. **Write meaningful commit messages** — explain *what* and *why*, not just *how*
4. **Keep the PR small and focused** — if scope creeps, split it into separate PRs
5. **Don't refactor unrelated code** — stay focused on the issue at hand

### Before Opening a PR

1. **Run the full test suite locally** — don't rely on CI to catch obvious failures
2. **Verify test coverage meets 100%** — use coverage tools and review uncovered lines
3. **Self-review your diff** — read it as if you're the reviewer
4. **Update or add documentation** if behavior changes
5. **Check for leftover debug code, TODOs, or commented-out blocks**

### Communication

1. **Comment on the issue** that you're working on it — avoid duplicate effort
2. **Ask for help early** if you're stuck longer than 30 minutes on the same problem
3. **Link the issue in your PR** — use keywords like `Fixes #123` for automatic closing
