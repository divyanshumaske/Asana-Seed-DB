import random
import os
from datetime import datetime, timedelta
USERS_SQL = "seedgen.sql"
TEAMS_SQL = "seedteams.sql"
OUTPUT_SQL = "seedprojects_tasks.sql"

ORG_ID = "01"
YEARS_BACK = 10

random.seed(42)
NOW = datetime.now()
def fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def random_date(year):
    return datetime(year, random.randint(1, 12), random.randint(1, 28))

#useres
users = {}
active_users_by_role = {}

with open(USERS_SQL, encoding="utf-8") as f:
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

                values = " ".join(buffer).split("VALUES")[1]
                vals = [v.strip().strip("'") for v in values.strip(" ();").split(",")]

                user_id = vals[0]
                role = vals[4]
                is_active = int(vals[5])

                users[user_id] = role
                if is_active == 1:
                    active_users_by_role.setdefault(role, []).append(user_id)

teams = {}
team_members = {}

with open(TEAMS_SQL, encoding="utf-8") as f:
    collecting = False
    buffer = []

    for line in f:
        line = line.strip()

        if line.startswith("INSERT INTO asana.teams"):
            collecting = True
            buffer = []
            continue

        if collecting:
            buffer.append(line)
            if line == ");":
                collecting = False

                values = " ".join(buffer).split("VALUES")[1]
                vals = [v.strip().strip("'") for v in values.strip(" ();").split(",")]

                team_id = int(vals[0])
                team_name = vals[2]

                teams[team_id] = team_name
                team_members[team_id] = []

with open(TEAMS_SQL, encoding="utf-8") as f:
    collecting = False
    buffer = []

    for line in f:
        line = line.strip()

        if line.startswith("INSERT INTO asana.team_memberships"):
            collecting = True
            buffer = []
            continue

        if collecting:
            buffer.append(line)
            if line == ");":
                collecting = False

                values = " ".join(buffer).split("VALUES")[1]
                vals = [v.strip().strip("'") for v in values.strip(" ();").split(",")]

                team_id = int(vals[0])
                user_id = vals[1]

                team_members.setdefault(team_id, []).append(user_id)

PROJECT_NAMES = [
    "Platform Revamp",
    "Customer Experience Upgrade",
    "Mobile App Redesign",
    "Analytics Modernization",
    "Security Hardening",
    "Workflow Automation",
    "Product Launch Initiative",
]

SECTION_TEMPLATES = [
    "Planning",
    "Backlog",
    "In Progress",
    "Review",
    "QA",
    "Launch",
    "Done",
]

TASK_TEMPLATES = {
    "engineer": [
        "Implement core workflow",
        "Fix integration issues",
        "Optimize system performance",
        "Add logging and monitoring",
    ],
    "product": [
        "Define requirements",
        "Review stakeholder feedback",
        "Update roadmap priorities",
    ],
    "designer": [
        "Create wireframes",
        "Design UI mockups",
        "Review design consistency",
    ],
    "marketing": [
        "Prepare launch messaging",
        "Coordinate campaign rollout",
        "Analyze engagement metrics",
    ],
}

sql = []
sql.append("START TRANSACTION;")

for team_id, members in team_members.items():

    if random.random() < 0.01:
        continue

    senior_engineers = [
        u for u in members
        if users.get(u) == "senior engineer"
        and u in active_users_by_role.get("senior engineer", [])
    ]

    if not senior_engineers:
        continue

    for year in range(NOW.year - YEARS_BACK, NOW.year + 1):
        project_count = random.randint(2, 3) * len(senior_engineers)

        for _ in range(project_count):
            created_at = random_date(year)
            duration = random.randint(180, 365)
            end_date = created_at + timedelta(days=duration)

            status = "active" if end_date > NOW or year == NOW.year else "completed"
            project_name = random.choice(PROJECT_NAMES)

            sql.append(f"""
INSERT INTO asana.projects (
  organization_id,
  team_id,
  owner_id,
  name,
  status,
  created_at
) VALUES (
  '{ORG_ID}',
  {team_id},
  '{random.choice(members)}',
  '{project_name}',
  '{status}',
  '{fmt(created_at)}'
);
""".strip())

            sql.append("SET @project_id = LAST_INSERT_ID();")

            sections = random.sample(SECTION_TEMPLATES, random.randint(4, 6))
            for pos, sec in enumerate(sections, start=1):
                sql.append(f"""
INSERT INTO asana.sections (
  project_id,
  name,
  position
) VALUES (
  @project_id,
  '{sec}',
  {pos}
);
""".strip())

            task_count = random.randint(30, 80)

            for _ in range(task_count):
                role = random.choice(list(TASK_TEMPLATES.keys()))
                task_name = random.choice(TASK_TEMPLATES[role])

                r = random.random()
                if r < 0.10:
                    desc = ""
                elif r < 0.90:
                    desc = f"{task_name} as part of project execution."
                else:
                    desc = (
                        f"{task_name}.\n"
                        "Ensure alignment with project goals.\n"
                        "Validate before completion."
                    )

                s = random.random()
                if s < 0.08:
                    status_t = "todo"
                elif s < 0.13:
                    status_t = "blocked"
                elif s < 0.28:
                    status_t = "done"
                else:
                    status_t = "in_progress"

                assignee = None
                if random.random() < 0.95 and active_users_by_role.get(role):
                    assignee = random.choice(active_users_by_role[role])

                sql.append(f"""
INSERT INTO asana.tasks (
  project_id,
  name,
  description,
  status,
  priority,
  assignee_id,
  created_at,
  completed_at
) VALUES (
  @project_id,
  '{task_name}',
  '{desc.replace("'", "''")}',
  '{status_t}',
  {random.randint(1,5)},
  {f"'{assignee}'" if assignee else "NULL"},
  '{fmt(created_at)}',
  {f"'{fmt(end_date)}'" if status_t == "done" else "NULL"}
);
""".strip())

sql.append("COMMIT;")

with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
    f.write("\n".join(sql))

print("Project, section, and task seed generated successfully")
print("Output file:", os.path.abspath(OUTPUT_SQL))
