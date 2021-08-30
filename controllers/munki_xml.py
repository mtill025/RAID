from raid import RaidAsset, RaidResponse
import os.path
import plistlib


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
        def __init__(self, assetinfo, serial=""):
            super().__init__(assetinfo)
            self.platform = "Munki"
            self.serial = serial
            if 'display_name' in self.dict:
                self.name = self.display_name

    def __init__(self, repo_path):
        """Wrapper for interacting with a Munki repository."""
        self.manifest_dir = f"{repo_path}/manifests"
        self.platform = "Munki"

    def search(self, name):
        """Searches Munki repository for manifest with name provided.
        Returns RaidAsset object."""
        manifest_path = self.manifest_dir + f"/{name}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, serial=name)
        return self.MunkiAsset(RaidResponse('302').json)

    def update_asset_name(self, serial, new_name):
        """Updates display_name in manifest with new_name."""
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            manifest['display_name'] = new_name
            write_manifest(manifest, manifest_path)
            manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, serial=serial)
        return self.MunkiAsset(RaidResponse('302').json)

    def add_asset_group(self, serial, group):
        """Adds group (included_manifest) to specified manifest."""
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            manifest['included_manifests'].append(group)
            write_manifest(manifest, manifest_path)
            manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, serial=serial)
        return self.MunkiAsset(RaidResponse('302').json)

    def remove_asset_group(self, serial, group):
        """Removes group (included_manifest) from specified manifest."""
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            if group in manifest['included_manifests']:
                manifest['included_manifests'].remove(group)
                write_manifest(manifest, manifest_path)
                manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, serial=serial)
        return self.MunkiAsset(RaidResponse('302').json)

    def clear_asset_groups(self, serial):
        """Removes all groups (included_manifests) from specified manifest."""
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            manifest['included_manifests'] = []
            write_manifest(manifest, manifest_path)
            manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, serial=serial)
        return self.MunkiAsset(RaidResponse('302').json)


