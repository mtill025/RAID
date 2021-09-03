from controllers import snipe_api, google_api, airwatch_api, munki_xml
from system import forms
from raid import RaidSettings
from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import json
import configparser
import os
import datetime

# TODO: Automatic updates
# TODO: Clean up/comment/get ready for deployment

SETTINGS_FILE = "config/settings.cfg"
SETTINGS_TEMP_FILE = "system/settings_template.cfg"
ORG_MAP_FILE = "config/org_mapping.json"
ORG_MAP_TEMP_FILE = "system/org_mapping_template.json"

# Import settings
settings = configparser.ConfigParser()
if not os.path.exists(SETTINGS_FILE):
    settings.read(SETTINGS_TEMP_FILE)
    with open(SETTINGS_FILE, 'w') as file:
        settings.write(file)
settings.read(SETTINGS_FILE)

# Import org mapping
if not os.path.exists(ORG_MAP_FILE):
    with open(ORG_MAP_TEMP_FILE) as file:
        org_map = json.load(file)
    with open(ORG_MAP_FILE, 'w') as file:
        json.dump(org_map, file)
with open(ORG_MAP_FILE) as file:
    org_map = RaidSettings(json.load(file))

google = google_api.GoogleController()
snipe = snipe_api.SnipeController(settings['urls']['snipe'])
aw = airwatch_api.AirWatchController(settings['urls']['airwatch'])
munki = munki_xml.MunkiController(settings['urls']['munki'])

# Web server
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = settings['web_server']['key']

# Connect to database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///config/raid.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Database tables


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    role = db.Column(db.Integer, nullable=False)
    commands = relationship("Command", back_populates="submitter")


class Command(db.Model):
    __tablename__ = "commands"
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.String(30), nullable=False)
    serial = db.Column(db.String(250), nullable=False)
    asset_tag = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    building = db.Column(db.String(250), nullable=False)
    group = db.Column(db.String(250), nullable=False)
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    submitter = relationship("User", back_populates="commands")


if not os.path.exists("config/raid.db"):
    db.create_all()

# Decorator for requiring admin to access pages


def admin_only(function):
    @wraps(function)
    def wrap_fn(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 1:
            return abort(403)
        return function(*args, **kwargs)
    return wrap_fn


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# ### ROUTES ### #


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = forms.LoginForm()
    if request.method == 'POST':
        username = login_form.username.data
        password = login_form.password.data
        users = User.query.all()
        # If no users exist, register first user as an admin
        if not users:
            first_admin = User(
                username=username,
                password=generate_password_hash(
                    password=password,
                    method='pbkdf2:sha256',
                    salt_length=8
                ),
                role=1,
            )
            db.session.add(first_admin)
            db.session.commit()
            login_user(first_admin)
            return redirect(url_for('index'))
        else:
            user = User.query.filter(User.username == username).first()
            if user and check_password_hash(pwhash=user.password, password=password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid credentials", category="flash-error")
                return redirect(url_for('login'))
    return render_template('login.html', form=login_form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/', methods=['POST', 'GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    search_form = forms.SearchForm()
    edit_form = forms.EditForm()
    building_choices = org_map.org_choices['buildings']
    group_choices = org_map.org_choices['groups']
    edit_form.building.choices = building_choices
    edit_form.group.choices = group_choices
    if request.method == 'POST':
        search_by = search_form.type.data
        search_num = search_form.identifier.data
        if search_by == "Asset Tag":
            asset = snipe.search_by_asset_tag(search_num)
            if 'serial' in asset.dict:
                search_num = asset.serial
        results = raid_search(search_num)
        edit_form.serial.data = results['snipe'].serial
        edit_form.name.data = results['snipe'].name
        edit_form.asset_tag.data = results['snipe'].asset_tag
        if results['snipe'].org_unit == "LS":
            edit_form.building.data = "ES"
        else:
            edit_form.building.data = results['snipe'].org_unit
        if results['airwatch'] and results['airwatch'].org_unit.find("Student") != -1:
            edit_form.group.data = "Student"
        elif results['google'] and results['google'].org_unit.find("Student") != -1:
            edit_form.group.data = "Student"
        return render_template('index.html', search_form=search_form, edit_form=edit_form, results=results,
                               logged_in=current_user.is_authenticated)
    return render_template('index.html', search_form=search_form, edit_form=edit_form,
                           logged_in=current_user.is_authenticated)


@app.route('/edit', methods=['POST'])
@login_required
def edit():
    serial = request.form['serial']
    if serial != "":
        new_name = request.form['name']
        new_asset_tag = request.form['asset_tag']
        new_building = request.form['building']
        new_group = request.form['group']
        results = [raid_update_asset_name(serial, new_name),
                   raid_update_asset_tag(serial, new_asset_tag),
                   raid_update_asset_org(serial, new_building, new_group)]
        safe_return_codes = ['101', '200']
        for result in results:
            for item in result:
                asset = result[item]
                if asset:
                    if asset.raid_code['code'] in safe_return_codes:
                        pass
                    else:
                        flash(f"{asset.platform} Error {asset.raid_code['code']}: {asset.raid_code['message']}",
                              "flash-error")
        new_command = Command(
            datetime=datetime.datetime.now().strftime("%Y-%m-%d %-I:%M %p"),
            serial=serial,
            name=new_name,
            asset_tag=new_asset_tag,
            building=new_building,
            group=new_group,
            submitter_id=current_user.id
        )
        db.session.add(new_command)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<userid>')
@admin_only
def delete(userid):
    if current_user.id != int(userid):
        db.session.delete(User.query.get(userid))
        db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin', methods=['GET', 'POST'])
@admin_only
def admin():
    register_form = forms.RegisterUserForm()
    if request.method == 'POST':
        username = register_form.username.data
        password = register_form.password.data
        role = register_form.role.data
        user = User.query.filter(User.username == username).first()
        if not user:
            new_user = User(
                username=username,
                password=generate_password_hash(
                    password=password,
                    method='pbkdf2:sha256',
                    salt_length=8
                ),
                role=role,
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('admin'))
        else:
            user.password = generate_password_hash(
                password=password,
                method='pbkdf2:sha256',
                salt_length=8
            )
            user.role = role
            db.session.commit()
    commands = Command.query.order_by(Command.id.desc()).limit(10)
    users = User.query.all()
    return render_template('admin.html', form=register_form, logged_in=current_user.is_authenticated,
                           commands=commands, users=users)


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
        results['google'] = google.search(serial, level="FULL")
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
    results = {
        'snipe': snipe.update_asset_company(serial, org_map.snipe[building][type]),
        'google': None,
        'airwatch': None,
        'munki': None,
    }
    if platform == "Chrome":
        results['google'] = google.update_asset_org(serial, org_map.google[building][type])
    elif platform is not None:
        results['airwatch'] = aw.update_asset_org(serial, org_map.airwatch[building][type])
        if platform == "Mac":
            results['munki'] = munki.update_asset_main_group(serial, org_map.munki[building][type])
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
    # app.run(host='0.0.0.0', port=5000, debug=True)
    from waitress import serve
    serve(app, host='0.0.0.0')
