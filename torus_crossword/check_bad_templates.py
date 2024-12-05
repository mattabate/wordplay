import json

with open("bad_templates.json") as f:
    bad_templates = json.load(f)

all_temps = bad_templates["38"] + bad_templates["40"] + bad_templates["42"]

new_38 = []
new_40 = []
new_42 = []
for t in all_temps:
    num_wall = t.count("█")
    if num_wall == 38 and t not in new_38:
        new_38.append(t)
    elif num_wall == 40 and t not in new_40:
        new_40.append(t)
    elif num_wall == 42 and t not in new_42:
        new_42.append(t)

with open("bad_templates.json", "w") as f:
    json.dump(
        {"38": new_38, "40": new_40, "42": new_42}, f, indent=4, ensure_ascii=False
    )
