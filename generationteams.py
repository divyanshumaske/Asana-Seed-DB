import random
import os

OUTPUT_SQL = "seedteams.sql"
ORG_ID = "01"

START_TEAM_ID = 5001
ENGINEERING_TEAMS = 50

random.seed(42)


USERS_SQL_FILE = "seedgen.sql"

roles = {
    "engineer": [],
    "senior engineer": [],
    "product": [],
    "designer": [],
    "marketing": [],
    "operations": [],
    "management": [],
    "hr": []
}

with open(USERS_SQL_FILE, encoding="utf-8") as f:
    collecting = False
    buffer = []

    for line in f:
        line = line.strip()

        if line.startswith("INSERT INTO asana.users"):
            collecting = True
            buffer = []
            continue

        if collecting:
            buffer.append(line)

            if line == ");":
                collecting = False

                values_block = " ".join(buffer)
                values_part = values_block.split("VALUES")[1]
                values = values_part.strip(" ();").split(",")

                user_id = values[0].strip().strip("'")
                role = values[4].strip().strip("'")

                roles[role].append(user_id)


sql = []
sql.append("START TRANSACTION;")

team_id = START_TEAM_ID

def create_team(team_name):
    global team_id
    sql.append(f"""
INSERT INTO asana.teams (
  team_id,
  organization_id,
  name,
  created_at
) VALUES (
  {team_id},
  '{ORG_ID}',
  '{team_name}',
  NOW()
);
""".strip())
    current_team = team_id
    team_id += 1
    return current_team

def add_member(team_id, user_id):
    sql.append(f"""
INSERT INTO asana.team_memberships (
  team_id,
  user_id
) VALUES (
  {team_id},
  '{user_id}'
);
""".strip())

random.shuffle(roles["senior engineer"])
random.shuffle(roles["engineer"])

for i in range(ENGINEERING_TEAMS):
    t_id = create_team(f"Engineering Team {i+1}")

    senior = roles["senior engineer"].pop()
    add_member(t_id, senior)

    engineers = random.randint(6, 12)
    for _ in range(engineers):
        add_member(t_id, roles["engineer"].pop())

def build_functional_teams(role, prefix):
    random.shuffle(roles[role])
    team_num = 1
    while roles[role]:
        t_id = create_team(f"{prefix} Team {team_num}")
        members = random.randint(5, 15)
        for _ in range(min(members, len(roles[role]))):
            add_member(t_id, roles[role].pop())
        team_num += 1

build_functional_teams("product", "Product")
build_functional_teams("designer", "Design")
build_functional_teams("marketing", "Marketing")
build_functional_teams("operations", "Operations")
build_functional_teams("management", "Management")
build_functional_teams("hr", "HR")

sql.append("COMMIT;")

with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
    f.write("\n".join(sql))

print("Team seed SQL generated")
print("Output file:", os.path.abspath(OUTPUT_SQL))
