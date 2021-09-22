import sys
import os
root_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(root_dir)
from server import cli_sync

args = sys.argv

if len(args) < 2:
    print("Help page")
    sys.exit(0)

assets_to_sync = None
fields_to_sync = None
apply_sync = False
max_to_sync = None
start_index = 0

for arg in args:
    if arg == "--assets":
        assets_to_sync = args[args.index("--assets") + 1]
    elif arg == "--fields":
        fields_to_sync = args[args.index("--fields") + 1]
        fields_to_sync = fields_to_sync.split(",")
    elif arg == "--apply":
        apply_sync = True
    elif arg == "--max":
        max_to_sync = int(args[args.index("--max") + 1])
    elif arg == "--start_index":
        start_index = int(args[args.index("--start_index") + 1])

if not assets_to_sync or not fields_to_sync:
    print("Error: --assets and --fields must provide valid parameters.")
    sys.exit(0)

cli_sync(assets_to_sync, fields_to_sync, apply_sync, max_to_sync, start_index)


