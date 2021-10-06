from raid import RaidAsset, RaidResponse
import os.path
import plistlib
import re


def read_manifest(path):
    """Opens manifest file (plist) and returns it as plistlib object."""
    with open(path, 'rb') as plist:
        manifest = plistlib.load(plist)
    return manifest


def write_manifest(manifest, path):
    """Writes plist to file path"""
    with open(path, 'wb') as file:
        plistlib.dump(manifest, file)


class MunkiController:

    class MunkiAsset(RaidAsset):
        def __init__(self, assetinfo, ou_regex, serial=""):
            super().__init__(assetinfo)
            self.platform = "Munki"
            self.serial = serial
            if 'display_name' in self.dict:
                self.name = self.display_name
            if 'included_manifests' in self.dict:
                self.org_unit = []
                munki_groups = self.included_manifests
                regex = re.compile(ou_regex)
                for group in munki_groups:
                    if regex.match(group):
                        self.org_unit.append(group)

    def __init__(self, repo_path, ou_regex):
        """Wrapper for interacting with a Munki repository."""
        self.repo_root_dir = repo_path
        self.manifest_dir = f"{repo_path}/manifests"
        self.platform = "Munki"
        self.ou_regex = ou_regex

    def search(self, name):
        """Searches Munki repository for manifest with name provided.
        Returns RaidAsset object."""
        manifest_path = self.manifest_dir + f"/{name}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, self.ou_regex, serial=name.upper())
        return self.MunkiAsset(RaidResponse('302').json, self.ou_regex)

    def update_asset_name(self, serial, new_name):
        """Updates display_name in manifest with new_name."""
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            manifest['display_name'] = new_name
            write_manifest(manifest, manifest_path)
            manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, self.ou_regex, serial=serial)
        return self.MunkiAsset(RaidResponse('302').json, self.ou_regex)

    def add_asset_group(self, serial, group):
        """Adds group (included_manifest) to specified manifest."""
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            if group not in manifest['included_manifests']:
                manifest['included_manifests'].append(group)
                write_manifest(manifest, manifest_path)
                manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, self.ou_regex, serial=serial)
        return self.MunkiAsset(RaidResponse('302').json, self.ou_regex)

    def update_asset_main_group(self, serial, group):
        """Adds group (included_manifest) to specified manifest."""
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            regex = re.compile(self.ou_regex)
            current_main_groups = []
            for grp in manifest['included_manifests']:
                if regex.match(grp):
                    current_main_groups.append(grp)
            for grp in current_main_groups:
                manifest['included_manifests'].remove(grp)
            manifest['included_manifests'].append(group)
            write_manifest(manifest, manifest_path)
            manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, self.ou_regex, serial=serial)
        return self.MunkiAsset(RaidResponse('302').json, self.ou_regex)

    def remove_asset_group(self, serial, group):
        """Removes group (included_manifest) from specified manifest."""
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            if group in manifest['included_manifests']:
                manifest['included_manifests'].remove(group)
                write_manifest(manifest, manifest_path)
                manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, self.ou_regex, serial=serial)
        return self.MunkiAsset(RaidResponse('302').json, self.ou_regex)

    def clear_asset_groups(self, serial):
        """Removes all groups (included_manifests) from specified manifest."""
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            manifest['included_manifests'] = []
            write_manifest(manifest, manifest_path)
            manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, self.ou_regex, serial=serial)
        return self.MunkiAsset(RaidResponse('302').json, self.ou_regex)

    def new_manifest(self, serial, name, group):
        """Creates new manifest using the template manifest in the Munki repository."""
        template_path = self.repo_root_dir + "/template"
        if os.path.exists(template_path):
            new_manifest = read_manifest(template_path)
            new_manifest['display_name'] = name
            if group:
                new_manifest['included_manifests'] = [f"groups/{group}"]
            write_manifest(new_manifest, f"{self.manifest_dir}/{serial}")
            return self.MunkiAsset(new_manifest, self.ou_regex, serial=serial)
        return self.MunkiAsset(RaidResponse('100').json, self.ou_regex)


