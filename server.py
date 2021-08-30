from controllers import snipe_api, google_api, airwatch_api, munki_xml
from system import forms
from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
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

# Web server
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = settings.web_server['key']

# ### ROUTES ### #


@app.route('/', methods=['POST', 'GET'])
def index():
    search_form = forms.SearchForm()
    if request.method == 'POST':
        search_by = search_form.type.data
        search_num = search_form.identifier.data
        if search_by == "Asset Tag":
            asset = snipe.search_by_asset_tag(search_num)
            if 'serial' in asset.dict:
                search_num = asset.serial
        results = raid_search(search_num)
        # for item in results:
        #     if results[item] is not None:
        #         print(results[item].name)
        return render_template('index.html', form=search_form, results=results)
    return render_template('index.html', form=search_form)


@app.route('/results', methods=['POST', 'GET'])
def show_results():
    pass

# ### RAID FUNCTIONS ### #


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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)