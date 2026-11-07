from personal_spotted_alert.log import log
from personal_spotted_alert.util import safe

ROOT_SWF = 'personal_spotted_alert.swf'
BULB_CLASS = 'de.tosox.personal_spotted_alert.SpottedBulb'

_SETTINGS_ATTR = '_ExternalFlashComponent__settings'

_original_create = None
_original_populate = None


def isKillCam(manager):
    # Every battle page also runs a hidden markers manager for the kill cam,
    # which sets up the same vehicles but is never on screen during a battle
    from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import KillCamMarkersManager
    return isinstance(manager, KillCamMarkersManager)


@safe
def _load_app(manager, appSwf):
    # If this fails, the root falls back to the vanilla app on its first frame
    manager.movie.root.loadApp(appSwf)
    log('markers movie wraps %s' % appSwf)


def _patched_create(self):
    settings = getattr(self, _SETTINGS_ATTR, None)
    if isKillCam(self) or settings is None or settings.url == ROOT_SWF:
        return _original_create(self)

    # Read the swf only now, at battle start, so whatever another mod set it
    # to is what ends up wrapped by our root
    appSwf = settings.url
    setattr(self, _SETTINGS_ATTR, settings._replace(url=ROOT_SWF))
    try:
        _original_create(self)
    finally:
        setattr(self, _SETTINGS_ATTR, settings)
    _load_app(self, appSwf)


@safe
def _check_root(manager):
    if not isKillCam(manager) and not getattr(manager.movie.root, 'isPersonalSpottedAlertRoot', False):
        log('markers movie does NOT run through our root, the bulb will not show')


def _patched_populate(self):
    _original_populate(self)
    _check_root(self)


def apply_patch():
    global _original_create, _original_populate
    from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager

    if _original_create is None:
        _original_create = MarkersManager.createExternalComponent
    MarkersManager.createExternalComponent = _patched_create

    if _original_populate is None:
        _original_populate = MarkersManager._populate
    MarkersManager._populate = _patched_populate


def remove_patch():
    global _original_create, _original_populate
    from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager

    if _original_create is not None:
        MarkersManager.createExternalComponent = _original_create
        _original_create = None

    if _original_populate is not None:
        MarkersManager._populate = _original_populate
        _original_populate = None
