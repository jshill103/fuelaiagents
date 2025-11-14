# app/cli/discover_accounts.py

from typing import Dict, List
from app.agents.discovery_agent import suggest_accounts_for_brand


def main():
    # You can make these configurable later; hard-coded for FuelAI for now
    brand_name = "FuelAI"
    brand_description = (
        "AI that runs outbound and follow-ups for sales teams, acting like a human SDR "
        "that never gets tired. It plugs into existing workflows and keeps reps in more "
        "conversations instead of admin hell."
    )
    target_audience = (
        "B2B SaaS founders, sales leaders, SDR/BDR managers, and RevOps leaders who care "
        "about pipeline, outbound efficiency, and scaling without just hiring more headcount."
    )

    existing_handles: Dict[str, List[str]] = {
        "instagram": ["getfuelai"],
        "facebook": ["Fuel AI"],
        "linkedin": ["fuelAI"],
    }

    suggestions = suggest_accounts_for_brand(
        brand_name=brand_name,
        brand_description=brand_description,
        target_audience=target_audience,
        existing_handles=existing_handles,
        max_suggestions=15,
    )

    if not suggestions:
        print("No suggestions returned.")
        return

    print("\n=== Suggested Accounts ===\n")
    for i, s in enumerate(suggestions, start=1):
        print(f"{i:2d}. [{s['platform']}] {s['handle']}  ({s['display_name']})")
        print(f"    type: {s['type']}  fit_score: {s['fit_score']:.2f}")
        if s.get("reason"):
            print(f"    reason: {s['reason']}")
        print()

    print("You can add any of these into the `sources` table, e.g.:")
    print("""
insert into sources (platform, handle, is_competitor, fetch_schedule)
values ('instagram', 'some_handle', true, 'daily');
""")


if __name__ == "__main__":
    main()