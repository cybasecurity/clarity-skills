#!/bin/sh
# Prints one line of session context in a Clarity/Stacks project; prints nothing otherwise.
# Signals: Clarinet.toml or .clar files (three levels, node_modules skipped), an @stacks/ or Clarinet
# dependency in package.json, or sBTC/Clarinet named in the top-level task or readme files.
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
found=""
if [ -f "$dir/Clarinet.toml" ] || find "$dir" -maxdepth 3 -name node_modules -prune -o -name '*.clar' -print 2>/dev/null | grep -q .; then
  found=1
elif [ -f "$dir/package.json" ] && grep -Eq '"@stacks/|"@hirosystems/clarinet|"clarinet' "$dir/package.json" 2>/dev/null; then
  found=1
elif cat "$dir/TASK.md" "$dir/README.md" "$dir/AGENTS.md" 2>/dev/null | grep -Ewq 'sBTC|Clarinet'; then
  found=1
fi
if [ -n "$found" ]; then
  echo "This is a Clarity/Stacks project. Once you know the task, and before writing contracts, tests, chain-data scripts or reviews, or answering how Clarity code behaves, load clarity:start and the skills for the task: audit or review -> clarity:auditor and clarity:security; write or change a contract, or a question about what Clarity code returns, aborts, rolls back or checks -> clarity:scholar and clarity:security; upgrades or replacing logic -> clarity:upgrades; tests -> clarity:testing; deployment -> clarity:deployment; protocol integration -> clarity:protocols and clarity:ecosystem; chain data or APIs -> clarity:apis. The router summarizes; the rules are in those skills. Before calling a build or contract change done, go through clarity:start's \"Before calling a contract done\" list and fix each failing item instead of reporting it as unmet."
fi
exit 0
