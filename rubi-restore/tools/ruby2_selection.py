"""Selection of the frozen, installed final sidecars, without old research trees."""
from release_contract import checked_owner,contract
from package_paths import resource
def selected(unit,editorial_path,overlay_path=None):
 row=checked_owner(unit);selection=row['selection']
 if resource(selection['editorial']['path'])!=editorial_path.resolve():raise ValueError('Wrong canonical editorial')
 if overlay_path is not None and resource(selection['sidecar']['path'])!=overlay_path.resolve():raise ValueError('Wrong selected sidecar')
 return contract()['release_id'],selection
