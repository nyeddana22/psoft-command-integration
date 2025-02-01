import pickle
import os
import csv
from datetime import datetime, timedelta

# Get current time and calculate the threshold time (10 minutes ago)
current_time = datetime.now()
time_threshold = current_time - timedelta(minutes=10)


# Load the pickle file
def load_previous_set(PICKLE_FILE):
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, "rb") as f:
            return pickle.load(f)
    return set()


# Store student IDs from the CSV in the pickle file
def save_current_set(student_ids, PICKLE_FILE):
    with open(PICKLE_FILE, "wb") as f:
        pickle.dump(student_ids, f)


# Generates two lists - data updated 10 minutes ago, and student IDs to be deleted
def process_json(CSV_FILE, PICKLE_FILE):
    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    current_set = set()
    filtered_data = []

    for row in data:
        student_id = row["Student ID"]
        last_updated = datetime.fromisoformat(row["lastUpdated"])

        current_set.add(student_id)

        if last_updated >= time_threshold:
            filtered_data.append(row)

    # Load previous student ID set
    previous_set = load_previous_set(PICKLE_FILE)

    # Find deleted student IDs
    deleted_students = list(previous_set - current_set)

    # Save the current set for the next run
    save_current_set(current_set, PICKLE_FILE)

    return filtered_data, deleted_students
