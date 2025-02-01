import requests
import json
import logging
import csvProcessing
import apiToken

# Define file paths for CSV data and previously student IDs
CSV_FILE = "venv/student_access.csv"
PICKLE_FILE = "venv/student_ids.pkl"

# Configure logging to store logs in a file
logging.basicConfig(
    filename="venv/logging.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("Logger")


# Function to fetch all access groups from Command to obtain group IDs
def get_all_groups():

    url = "https://api.verkada.com/access/v1/access_groups"
    headers = {"accept": "application/json", "x-verkada-auth": API_KEY["token"]}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to fetch groups: {response.status_code}, {response.text}")
    else:
        logger.info(f"Successfully fetched all groups!")
        groups = json.loads(response.content)
        name_to_group_id = {
            item["name"]: item["group_id"] for item in groups["access_groups"]
        }
        return name_to_group_id


# Function to create a new user in Command
def create_user(user):
    user_creation_url = "https://api.verkada.com/core/v1/user"
    payload = {
        "first_name": user["First Name"],
        "last_name": user["Last Name"],
        "external_id": user["Student ID"],
        "email": user["Email"],
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-verkada-auth": API_KEY["token"],
    }
    user_creation_response = requests.post(
        user_creation_url, json=payload, headers=headers
    )
    if user_creation_response.status_code != 200:
        logger.error(
            f"Error creating user: {user_creation_response.status_code}, {user_creation_response.text}"
        )
    else:
        logger.info(
            f"User has been successfully created: {user_creation_response.text}"
        )

    # Add user to corresponding access groups on Command if any
    if user["Access Groups"]:
        groups = user["Access Groups"].split(";") if user["Access Groups"] else []
        add_user_to_groups(user, groups)


# Function to delete users from Command if removed from PeopleSoft
def delete_users():
    for external in users_to_delete:
        user_deletion_url = (
            f"https://api.verkada.com/core/v1/user?external_id={external}"
        )
        headers = {
            "accept": "application/json",
            "x-verkada-auth": API_KEY["token"],
        }
        delete_response = requests.delete(user_deletion_url, headers=headers)
        if delete_response.status_code != 200:
            logger.error(
                f"Error deleting user: {delete_response.status_code}, {delete_response.text}"
            )
        else:
            logger.info(
                f"User with student ID {external} has been successfully deleted!"
            )


# Function to update user information with any field changes
def update_users():
    for user in data:
        external = user["Student ID"]
        # check if user with corresponding external ID exists
        get_user_url = f"https://api.verkada.com/core/v1/user?external_id={external}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-verkada-auth": API_KEY["token"],
        }
        get_user_response = requests.get(get_user_url, headers=headers)
        if get_user_response.status_code == 200:
            payload = {
                "first_name": user["First Name"],
                "last_name": user["Last Name"],
                "email": user["Email"],
            }
            update_response = requests.put(get_user_url, json=payload, headers=headers)
            if update_response.status_code != 200:
                logger.error(
                    f"Error updating user: {update_response.status_code}, {update_response.text}"
                )
            else:
                logger.info(
                    f"User has been successfully updated: {update_response.text}"
                )
            # Call function to update user access groups
            update_user_access_groups(user)

            # Call function to download corresponding user's profile photo from Command
            get_profile_photo(user)
        else:
            logger.info(
                f"User does not exist: {get_user_response.status_code}, {get_user_response.text}"
            )
            create_user(user)


# Function to update user access groups if there are any additions or removals
def update_user_access_groups(user):
    external = user["Student ID"]
    get_user_info_url = (
        f"https://api.verkada.com/access/v1/access_users/user?external_id={external}"
    )
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-verkada-auth": API_KEY["token"],
    }
    get_response = requests.get(get_user_info_url, json=external, headers=headers)
    user_obj = json.loads(get_response.text)
    user_groups_dict = user_obj["access_groups"] if user_obj["access_groups"] else []
    user_groups = [group["name"] for group in user_groups_dict]
    updated_groups = user["Access Groups"].split(";") if user["Access Groups"] else []

    groups_to_add = list(set(updated_groups) - set(user_groups))
    groups_to_remove = list(set(user_groups) - set(updated_groups))

    for group in groups_to_remove:
        group_id = group_id_mappings[group]
        delete_user_group_url = f"https://api.verkada.com/access/v1/access_groups/group/user?group_id={group_id}&external_id={external}"
        del_response = requests.delete(delete_user_group_url, headers=headers)
        if del_response.status_code != 200:
            logger.error(
                f"Error removing user from group: {del_response.status_code}, {del_response.text}"
            )
        else:
            logger.info(f"Removed user from group: {del_response.text}")
    add_user_to_groups(user, groups_to_add)


# Function to add a user to specified access groups
def add_user_to_groups(user, groups):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-verkada-auth": API_KEY["token"],
    }
    for group in groups:
        group_id = group_id_mappings[group]
        user_to_group_url = f"https://api.verkada.com/access/v1/access_groups/group/user?group_id={group_id}"
        payload = {"external_id": user["Student ID"]}
        add_response = requests.put(user_to_group_url, json=payload, headers=headers)
        if add_response.status_code != 200:
            logger.error(
                f"Error adding user to group: {add_response.status_code}, {add_response.text}"
            )
        else:
            logger.info(f"Added user to group: {add_response.text}")


# Function to download and save a user's profile photo
def get_profile_photo(user):
    external = user["Student ID"]
    url = f"https://api.verkada.com/access/v1/access_users/user/profile_photo?external_id={external}&original=true"
    headers = {"accept": "application/json", "x-verkada-auth": API_KEY["token"]}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logger.info(
            f"Successfully downloaded profile photo of user with student ID {external}."
        )
        file_path = f"venv/profiles/{external}.jpg"
        with open(file_path, "wb") as file:
            file.write(response.content)
    else:
        logger.error(
            f"Error downloading profile photo: {response.status_code}, {response.text}"
        )


# Main function to obtain processed CSVs, API key and access group mappings
if __name__ == "__main__":
    data, users_to_delete = csvProcessing.process_json(CSV_FILE, PICKLE_FILE)
    API_KEY = json.loads(apiToken.generate_api_token())
    group_id_mappings = get_all_groups()
    update_users()
    delete_users()
