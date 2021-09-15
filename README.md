# RAID
Raider Asset Information Distributor is a web application designed to help with reducing the workload involved with managing IT assets in a mixed management environmment.
IT departments, especially those with smaller budgets, tend to find themselves having to utilize many different management platforms. RAID uses the APIs of many of these platforms in order to provide one portal for management.

Currently, RAID supports the following platforms:
* AirWatch/Workspace ONE
* Snipe-IT
* Google Admin Console
* Munki

RAID can manage the following asset data on said platforms:
* Asset name
* Asset tag
* Asset organiztion unit
* ...with many more features planned


## Installation
```
git clone https://github.com/mtill025/RAID.git --branch v1.0.0
```
Substitute version numbers as needed.

## Setup
* Install Python 3.9.
* Install the latest version of RAID from this repository. Ensure the user you want to run the RAID process as has ownership of the RAID directory. Ensure you run the rest of the setup as said user.
* [Recommended] Create a Python venv in your RAID directory and activate it.
```
# MacOS commands
python3 -m venv raid-venv
source raid-venv/bin/activate
```
* Install the RAID python requirements.
```
pip install -r requirements.txt
```
* Setup Google API access for the Google account which should be used by RAID to interact with Google. [More info](https://developers.google.com/workspace/guides/create-project)
* Download the Google credentials.json file and store it in RAID/secrets. [More info](https://developers.google.com/workspace/guides/create-credentials)
* Setup AirWatch/Workspace ONE API access and then add the following info to your keychain using the keyring library in your Python venv.
```
keying set aw_auth authcode
# Enter authcode when prompted i.e. username:password
keyring set aw_key key
# Enter API key when prompted
```
* Setup Snipe-IT API access and then add the following info to your keychain using the keyring library in your Python venv.
```
keyring set snipe_key key
# Enter Snipe API key when prompted
```
* Run the raid-setup.py script found in the RAID directory to complete Google OAUTH setup and initialize system files.
* Configure RAID settings in the config/settings.cfg file. Set the URLs/paths for your management platforms and change the web server key to a random string of characters.
```
# URLs for RAID platform API controllers
[urls]
munki = /path/to/munki/repo
airwatch = https://airwatchapi.example
snipe = https://snipeapi.exmaple


# Web server secret key - DO NOT LEAVE DEFAULT
[web_server]
key = template_key
```
* Configre the organization unit mapping file found at config/org_mapping.json. Buildings are layer 1 options and groups are layer 2 options. This file determines how RAID will organize assets in each system. See section at the bottom for more info on org_mappings. Example:
```
{
  "org_choices": {
    "buildings": [
      "NYC Office",
      "CHI Office"
    ],
    "groups": [
      "HR",
      "IT"
    ]
  },
  "google": {
    "nyc office": {
      "hr": "/Offices/NYC/HR",
      "it": "/Offices/NYC/IT"
    },
    "chi office": {
      "hr": "/Offices/CHI/HR",
      "it": "/Offices/CHI/IT"
    }
  },
  "airwatch": {
    "nyc office": {
      "hr": "NYC_HR",
      "it": "NYC_IT"
    },
    "chi office": {
      "hr": "CHI_HR",
      "it": "CHI_IT"
    }
  },
  "snipe": {
    etc..
  },
  "munki": {
    etc..
  }
}
```
* You're ready to fire up the RAID server! Run the server.py file to do so. Make sure you run it from the root RAID directory or it will not work! (This should be fixed in the future.)
## Organization Unit Mapping
The org_choices dictionary lists exactly what options will show up in the RAID GUI, and thus can be capitalized as desired. The actual platform mapping dictionary options must be all lowercase! More info to come..
