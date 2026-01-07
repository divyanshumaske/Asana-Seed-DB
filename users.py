import random
import os
from datetime import datetime, timedelta

FIRST_NAME_FILE = r"C:\Users\divya\Downloads\archive (8)\first_name.txt"
LAST_NAME_FILE = r"C:\Users\divya\Downloads\archive (8)\last_name.txt"

TOTAL_USERS = 7000
ORG_ID = "01"
ORG_NAME = "Microsoft"
ORG_DOMAIN = "microsoft.in"

USER_ID_START = 100001
OUTPUT_SQL = "seedgen.sql"

random.seed(10)

with open(FIRST_NAME_FILE, encoding="utf-8") as f:
    first_names = [x.strip().lower() for x in f if x.strip()]

with open(LAST_NAME_FILE, encoding="utf-8") as f:
    last_names = [x.strip().lower() for x in f if x.strip()]

def join_date(min_years, max_years):
    days = random.randint(min_years * 365, max_years * 365)
    return datetime.now() - timedelta(days=days)

def fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

GENZ = lambda: join_date(1, 10)
MID = lambda: join_date(10, 20)
SENIOR = lambda: join_date(20, 35)

role_distribution = [
    ("engineer", 0.44),
    ("senior engineer", 0.01),
    ("product", 0.10),
    ("designer", 0.05),
    ("marketing", 0.15),
    ("operations", 0.10),
    ("management", 0.10),
    ("hr", 0.05),
]

roles = []
for role, pct in role_distribution:
    roles.extend([role] * int(TOTAL_USERS * pct))

assert len(roles) == TOTAL_USERS
random.shuffle(roles)

def assign_join_and_active(role):
    if role == "senior engineer":
        bucket = random.choices(
            [GENZ, MID, SENIOR], [10, 45, 45]
        )[0]
    elif role == "management":
        bucket = random.choices(
            [GENZ, MID, SENIOR], [15, 35, 50]
        )[0]
    else:
        bucket = random.choices(
            [GENZ, MID, SENIOR], [64, 26, 10]
        )[0]

    joined = bucket()
    years = (datetime.now() - joined).days / 365

    if years <= 10:
        active = random.random() < 0.95
    elif years <= 20:
        active = random.random() < 0.85
    else:
        active = random.random() < 0.70


    return joined, int(active)

sql = []
sql.append("START TRANSACTION;")

sql.append(f"""
INSERT INTO asana.organizations (
  organization_id,
  name,
  domain,
  created_at
) VALUES (
  '{ORG_ID}',
  '{ORG_NAME}',
  '{ORG_DOMAIN}',
  '{fmt(GENZ())}'
);
""".strip())

email_counter = {}

for i, role in enumerate(roles):
    fn = random.choice(first_names)
    ln = random.choice(last_names)

    user_id = f"{ORG_ID}{USER_ID_START + i}"
    name = f"{fn.capitalize()} {ln.capitalize()}"

    base_email = f"{fn}.{ln}"
    count = email_counter.get(base_email, 0) + 1
    email_counter[base_email] = count

    if count == 1:
        email = f"{base_email}@{ORG_DOMAIN}"
    else:
        email = f"{base_email}{count}@{ORG_DOMAIN}"

    joined_at, is_active = assign_join_and_active(role)

    sql.append(f"""
INSERT INTO asana.users (
  user_id,
  organization_id,
  name,
  email,
  role,
  is_active,
  created_at
) VALUES (
  '{user_id}',
  '{ORG_ID}',
  '{name}',
  '{email}',
  '{role}',
  {is_active},
  '{fmt(joined_at)}'
);
""".strip())


sql.append("COMMIT;")

with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
    f.write("\n".join(sql))

output_path = os.path.abspath(OUTPUT_SQL)
print("SQL generated successfully")
print("Output file path:", output_path)

