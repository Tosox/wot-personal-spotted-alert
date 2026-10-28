from personal_spotted_alert.log import log
from personal_spotted_alert.util import safe

# Our root for the markers movie (see src_flash). It loads the markers app the
# battle was about to start, so our classes share that app's ApplicationDomain
ROOT_SWF = 'personal_spotted_alert.swf'
BULB_CLASS = 'de.tosox.personal_spotted_alert.SpottedBulb'

# ExternalFlashComponent keeps the swf it creates in this private field
_SETTINGS_ATTR = '_ExternalFlashComponent__settings'

_original_create = None
_original_populate = None


def _patched_create(self):
    from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import KillCamMarkersManager

    settings = getattr(self, _SETTINGS_ATTR, None)
    # The kill cam markers are never on screen during a battle, so leave them be
    if isinstance(self, KillCamMarkersManager) or settings is None or settings.url == ROOT_SWF:
        return _original_create(self)

    # Read the swf only now, at battle start, so whatever another mod set it
    # to, and whenever it did, is what ends up wrapped by our root
    appSwf = settings.url
    setattr(self, _SETTINGS_ATTR, settings._replace(url=ROOT_SWF))
    try:
        _original_create(self)
    finally:
        setattr(self, _SETTINGS_ATTR, settings)
    _load_app(self, appSwf)


@safe
def _load_app(manager, appSwf):
    # If this fails, the root falls back to the vanilla app on its first frame
    manager.movie.root.loadApp(appSwf)
    log('markers movie wraps %s' % appSwf)


def _patched_populate(self):
    _original_populate(self)
    _check_root(self)


@safe
def _check_root(manager):
    from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import KillCamMarkersManager
    if isinstance(manager, KillCamMarkersManager):
        return
    if not getattr(manager.movie.root, 'isPersonalSpottedAlertRoot', False):
        log('markers movie does NOT run through our root, the bulb will not show')


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
