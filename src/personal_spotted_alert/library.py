from personal_spotted_alert.log import log
from personal_spotted_alert.util import safe

# Our root for the markers movie (see src_flash); it loads the vanilla
# battleVehicleMarkersApp.swf itself, so our classes share its ApplicationDomain
ROOT_SWF = 'personal_spotted_alert.swf'
BULB_CLASS = 'de.tosox.personal_spotted_alert.SpottedBulb'

_original_swf = None
_original_populate = None


def _patched_populate(self):
    _original_populate(self)
    _check_root(self)


@safe
def _check_root(manager):
    if getattr(manager.movie.root, 'isPersonalSpottedAlertRoot', False):
        log('markers movie runs through our root')
    else:
        log('markers movie does NOT run through our root, the bulb will not show')


def apply_patch():
    global _original_swf, _original_populate
    from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager

    # Read by MarkersManager.__init__, so this takes effect from the next battle
    if _original_swf is None:
        _original_swf = MarkersManager.MARKERS_MANAGER_SWF
    MarkersManager.MARKERS_MANAGER_SWF = ROOT_SWF

    if _original_populate is None:
        _original_populate = MarkersManager._populate
    MarkersManager._populate = _patched_populate


def remove_patch():
    global _original_swf, _original_populate
    from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager

    if _original_swf is not None:
        MarkersManager.MARKERS_MANAGER_SWF = _original_swf
        _original_swf = None

    if _original_populate is not None:
        MarkersManager._populate = _original_populate
        _original_populate = None
