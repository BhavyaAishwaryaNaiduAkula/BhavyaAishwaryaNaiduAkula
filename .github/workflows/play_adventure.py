import sys
import json
import re
import os

issue_title = os.environ.get("ISSUE_TITLE", "")
player_name = os.environ.get("PLAYER_NAME", "Adventurer")
issue_number = os.environ.get("ISSUE_NUMBER", "")

match = re.search(r"Adventure:\s*(.*)", issue_title, re.IGNORECASE)
if not match:
    sys.exit(0)

action = match.group(1).strip()

STATE_FILE = "adventure_state.json"
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
else:
    state = {"hp": 3, "xp": 0, "level": 1, "current_scene": "start", "last_player": "None"}

scenes = {
    "start": {
        "desc": "You stand at the edge of the Git Forest. The trees rustle with merge conflicts.",
        "choices": {"Walk into forest": "forest", "Set up camp": "camp"}
    },
    "forest": {
        "desc": "You walk deep and encounter a wild **Linter Monster**! It challenges your formatting.",
        "choices": {"Fight the monster": "fight_linter", "Flee to camp": "camp"}
    },
    "camp": {
        "desc": "You sit by the campfire and review pull requests. You recover 1 HP!",
        "choices": {"Walk into forest": "forest", "Rest more": "rest"}
    },
    "rest": {
        "desc": "You sleep peacefully. You wake up energized and ready to write code!",
        "choices": {"Walk into forest": "forest"}
    },
    "fight_linter": {
        "desc": "You formatted your code! The monster disappears, leaving a shiny green block. (+10 XP)",
        "choices": {"Walk deeper": "boss_fight", "Return to camp": "camp"}
    },
    "boss_fight": {
        "desc": "You encounter the **Merge Conflict Dragon**! It breathes merge conflicts everywhere.",
        "choices": {"Resolve conflicts": "victory", "Flee to camp": "camp"}
    },
    "victory": {
        "desc": "Victory! You merged the branch. You are now a Core Contributor. The adventure resets!",
        "choices": {"Start over": "start"}
    }
}

current_scene = state["current_scene"]
scene_data = scenes.get(current_scene, scenes["start"])
target_scene = "start"

for choice, target in scene_data["choices"].items():
    if action.lower() == choice.lower():
        target_scene = target
        break
else:
    target_scene = current_scene

if target_scene == "camp" and state["hp"] < 3:
    state["hp"] += 1
elif target_scene == "fight_linter":
    state["xp"] += 10
elif target_scene == "victory":
    state["xp"] += 50
    state["level"] += 1

if state["xp"] >= 20 * state["level"]:
    state["xp"] -= 20 * state["level"]
    state["level"] += 1

state["current_scene"] = target_scene

with open(STATE_FILE, "w") as f:
    json.dump(state, f, indent=4)

new_scene = scenes.get(target_scene, scenes["start"])
hp_hearts = "❤️" * state["hp"] + "🖤" * (3 - state["hp"])

game_markdown = f"""<!-- START_GAME_ZONE -->
### 🌲 The Git Contribution Adventure 🌲

**Current Scene:**
{new_scene["desc"]}

---

🛡️ **Stats:**
- **HP:** {hp_hearts}
- **XP:** {state["xp"]}
- **Level:** {state["level"]}
- **Last Action by:** @{player_name} (chose *"{action}"*)

What will you do next?
"""

repo_owner = os.environ.get("GITHUB_REPOSITORY", "yourusername/yourusername")
for choice in new_scene["choices"].keys():
    encoded_title = f"Adventure: {choice}".replace(" ", "+")
    encoded_body = f"Click+'Submit+new+issue'+to+make+your+choice!+Do+not+modify+the+title.".replace(" ", "+")
    link = f"https://github.com/{repo_owner}/issues/new?title={encoded_title}&body={encoded_body}"
    game_markdown += f"- [{choice}]({link})\n"

game_markdown += "<!-- END_GAME_ZONE -->"

with open("README.md", "r", encoding="utf-8") as f:
    readme_content = f.read()

pattern = r"<!-- START_GAME_ZONE -->.*?<!-- END_GAME_ZONE -->"
updated_readme = re.sub(pattern, game_markdown, readme_content, flags=re.DOTALL)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(updated_readme)
