from controllers import snipe_api, google_api, airwatch_api, munki_xml
from raid import RaidSettings
import json
import os

SETTINGS_FILE = "config/settings.json"

# Import settings
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE) as file:
        settings = RaidSettings(json.load(file))

google = google_api.GoogleController()
snipe = snipe_api.SnipeController(settings.controller_urls['snipe'])
aw = airwatch_api.AirWatchController(settings.controller_urls['airwatch'])
munki = munki_xml.MunkiController(settings.controller_urls['munki'])


def get_platform(serial):
    cat = snipe.get_asset_category(serial)
    if cat:
        return cat.split(' ')[0]
    return None


def raid_search(serial):
    platform = get_platform(serial)
    results = {
        'snipe': snipe.search(serial),
        'google': None,
        'airwatch': None,
        'munki': None,
    }
    if platform == "Chrome":
        results['google'] = google.search(serial)
    elif platform is not None:
        results['airwatch'] = aw.search(serial)
        if platform == "Mac":
            results['munki'] = munki.search(serial)
    return results


def raid_update_asset_name(serial, new_name):
    platform = get_platform(serial)
    results = {
        'snipe': snipe.update_asset_name(serial, new_name),
        'google': None,
        'airwatch': None,
        'munki': None,
    }
    if platform == "Chrome":
        results['google'] = google.update_asset_name(serial, new_name)
    elif platform is not None:
        results['airwatch'] = aw.update_asset_name(serial, new_name)
        if platform == "Mac":
            results['munki'] = munki.update_asset_name(serial, new_name)
    return results


def raid_update_asset_org(serial, building, type):
    building = building.lower()
    type = type.lower()
    platform = get_platform(serial)
    with open('config/org_mapping.json') as file:
        org_map = json.load(file)
    results = {
        'snipe': snipe.update_asset_company(serial, org_map['snipe'][building][type]),
        'google': None,
        'airwatch': None,
        'munki': None,
    }
    if platform == "Chrome":
        results['google'] = google.update_asset_org(serial, org_map['google'][building][type])
    elif platform is not None:
        results['airwatch'] = aw.update_asset_org(serial, org_map['airwatch'][building][type])
        if platform == "Mac":
            munki.clear_asset_groups(serial)
            results['munki'] = munki.add_asset_group(serial, org_map['munki'][building][type])
    return results


def raid_update_asset_tag(serial, new_tag):
    platform = get_platform(serial)
    results = {
        'snipe': snipe.update_asset_tag(serial, new_tag),
        'google': None,
        'airwatch': None,
        'munki': None,
    }
    if platform == "Chrome":
        results['google'] = google.update_asset_tag(serial, new_tag)
    elif platform is not None:
        results['airwatch'] = aw.update_asset_tag(serial, new_tag)
        if platform == "Mac":
            pass
    return results

