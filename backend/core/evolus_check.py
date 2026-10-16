"""One live analysis to check that the corrective-action draft comes from the Evolus agent.

Reads .env like the API does. Calls Token Factory twice (second opinion + Evolus agent's model), so it costs
the same as one analysis in the UI. See docs/DEVIR-NOTU.md for how to read the result.

Usage: python -m backend.core.evolus_check            # sample "press"
       python -m backend.core.evolus_check forklift   # press | forklift | conveyor | fryer
"""
import sys

from backend.core.analyze import Analyzer
from backend.core.samples import SAMPLES


def main() -> None:
    sample_id = sys.argv[1] if len(sys.argv) > 1 else "press"
    sample = next(s for s in SAMPLES if s["id"] == sample_id)
    analyzer = Analyzer()
    agent = analyzer.evolus
    missing = [name for name, value in (("EVOLUS_API_KEY", agent.api_key), ("EVOLUS_APP_ID", agent.app_id),
                                        ("EVOLUS_AGENT_ID", agent.agent_id)) if not value]
    print(f"Evolus configured: {agent.configured}" + (f" (missing in .env: {', '.join(missing)})" if missing else ""))
    print(f"Agent: {agent.agent_id} | endpoint '{agent.endpoint}': {agent.url} | timeout {agent.timeout:.0f} s")
    print(f"Analyzing sample '{sample_id}' (about 1-3 minutes)...")

    result = analyzer.analyze(sample["text"])
    second, draft = result["amd"]["calls"]
    plan = result["action_plan"]
    print(f"Second opinion: {second['model']} | {second['seconds']} s | error: {second['error']}")
    print(f"Draft:          {draft['model']} | {draft['seconds']} s | via: {draft['via']} | error: {draft['error']}")
    if draft["evolus_error"]:
        print(f"Evolus error:   {draft['evolus_error']}")
    print(f"Actions kept: {len(plan['actions'])} | rejected: {len(plan['rejected'])} | total {result['seconds_total']} s")
    for action in plan["rejected"]:
        print(f"  rejected {action.get('standard')}: {'; '.join(action['problems'])}")

    if draft["via"] == "evolus":
        print("RESULT: OK, the draft came from the Evolus agent.")
    elif agent.configured:
        print("RESULT: FALLBACK, Evolus failed and Token Factory wrote the draft (see 'Evolus error').")
    else:
        print("RESULT: Evolus is not configured, Token Factory wrote the draft (fill the missing .env values).")


if __name__ == "__main__":
    main()
