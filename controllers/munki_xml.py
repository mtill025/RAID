from raid import RaidAsset, RaidResponse
import os.path
import plistlib


def read_manifest(path):
    """Opens manifest file (plist) and returns it as plistlib object."""
    with open(path, 'rb') as plist:
        manifest = plistlib.load(plist)
    return manifest


def write_manifest(manifest, path):
    with open(path, 'wb') as file:
        plistlib.dump(manifest, file)


class MunkiController:

    class MunkiAsset(RaidAsset):
        def __init__(self, assetinfo, pkginfo=None):
            super().__init__(assetinfo)
            self.platform = "Munki"
            self.pkginfo = pkginfo

    def __init__(self, repo_path):
        self.manifest_dir = f"{repo_path}/manifests"

    def search(self, serial):
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest, pkginfo=manifest)
        return self.MunkiAsset(RaidResponse('302').json)

    def update_asset_name(self, serial, new_name):
        manifest_path = self.manifest_dir + f"/{serial}"
        if os.path.exists(manifest_path):
            manifest = read_manifest(manifest_path)
            manifest['display_name'] = new_name
            write_manifest(manifest, manifest_path)
            manifest = read_manifest(manifest_path)
            return self.MunkiAsset(manifest)
        return self.MunkiAsset(RaidResponse('302').json)

