from src.assets import get_asset
from src.bible.plan_manager import PlanManager
from src.data.plan_repository import PlanRepository
from google.cloud import firestore

import csv

# How to use:
# 1. Save the plan.csv file in src/assets/
# 2. Run this python file

# Read reading plan data.
rows = []
with open(get_asset('plan.csv')) as file:
    reader = csv.reader(file)

    # Exclude header
    rows = list(reader)[1:]

# Parse the tasks
plan_manager = PlanManager(rows)

# Get all the tasks
tasks = plan_manager.get_tasks()

# Create repo
db = firestore.Client()
repo = PlanRepository(db)

# Counter
i = 0
print(f'Uploading {len(tasks)} tasks.')

# Upload all tasks
for task in tasks:
    repo.upsert_plan(task)

    # Print progress
    i += 1
    print(f'\r{i} / {len(tasks)}', end='')

print()
print('Uploaded all tasks!')
