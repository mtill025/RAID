import os
from shutil import copyfile
from controllers import google_api
from google.auth.exceptions import DefaultCredentialsError

ans = input("This script is for configuring RAID for first-time use. Would you like to continue? y/N: ")

if ans == "y":
    if not os.path.exists("config"):
        print("Creating config dir...")
        os.mkdir("config")

    if not os.path.exists("secrets"):
        print("Creating secrets dir...")
        os.mkdir("secrets")

    if not os.path.exists("config/org_mapping.json"):
        print("Creating org_mapping from template...")
        copyfile("system/org_mapping_template.json", "config/org_mapping.json")

    if not os.path.exists("config/settings.cfg"):
        print("Creating settings.cfg from template...")
        copyfile("system/settings_template.cfg", "config/settings.cfg")

    if not os.path.exists("secrets/token.json"):
        if os.path.exists("secrets/credentials.json"):
            print("Attempting to open Google OAUTH authorization portal in a browser...")
            try:
                google = google_api.GoogleController("secrets")
            except DefaultCredentialsError:
                pass
        else:
            print("secrets/credentials.json not found. Please follow the README directions and run the script again.")

