import os

# Set the root RAID directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Set paths for template and system files
SETTINGS_FILE = f"{ROOT_DIR}/config/settings.cfg"
SETTINGS_TEMP_FILE = f"{ROOT_DIR}/system/settings_template.cfg"
ORG_MAP_FILE = f"{ROOT_DIR}/config/org_mapping.json"
ORG_MAP_TEMP_FILE = f"{ROOT_DIR}/system/org_mapping_template.json"
ERROR_LOG_FILE = f"{ROOT_DIR}/error.log"
DB_FILE = f"{ROOT_DIR}/config/raid.db"
GOOGLE_CREDS_DIR = f"{ROOT_DIR}/secrets"
LOG_DIR = f"{ROOT_DIR}"
SYNC_LOG_FILE = f"{LOG_DIR}/sync.log"
