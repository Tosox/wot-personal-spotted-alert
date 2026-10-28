import traceback

import BigWorld

from personal_spotted_alert import library
from personal_spotted_alert import tracking
from personal_spotted_alert.log import log

# Our wrapper around the vanilla target designator bulb (see src_flash), which
# lives in our markers root (library.py), so insertSymbol can find it
BULB_SYMBOL = library.BULB_CLASS

# Bottom of VehicleMarker.markerParts; the wrapper reports no height, so the
# marker's own stack stays exactly as it was
INSERT_INDEX = 0

# Where the bulb's centre sits relative to the health bar's left edge and
# vertical centre, and its size relative to the vanilla status icon. The
# vanilla bulb is drawn well below its own origin (~37px at full size), hence
# the upward shift, which shrinks along with the scale
BULB_SCALE = 0.8
BULB_OFFSET_X = -13
BULB_OFFSET_Y = -30

# Length of the bulb's hide animation; removing it sooner cuts the animation off
REMOVE_DELAY = 0.6

# Frame labels of the bulb's glow, as in gui_colors.xml (vm_stun_enemy_schema)
COLOR_DEFAULT = ('red', 0xFFDD9C)
COLOR_BLIND = ('purple', 0x9999FF)

_original_handle_battle_events = None
_original_set_vehicle_info = None
_original_plugin_stop = None
_original_update_marker_state = None

# vehicleID -> VehicleMarkerPlugin that owns its marker
_plugins = {}

# vehicleID -> (plugin, markerID) for markers that currently carry our bulb
_inserted = {}

# vehicleID -> pending BigWorld callback that removes the bulb
_removeCallbacks = {}


def _patched_handle_battle_events(self, events, additionalData=None):
    try:
        from BattleFeedbackCommon import BATTLE_EVENT_TYPE
        for data in events:
            if data['eventType'] == BATTLE_EVENT_TYPE.DETECTED:
                targetID = data['targetID']
                tracking.mark(targetID)
                _showBulb(targetID)
    except Exception:
        log('handleBattleEvents patch crashed:\n' + traceback.format_exc())
    return _original_handle_battle_events(self, events, additionalData)


def _patched_set_vehicle_info(self, marker, vInfo, guiProps, nameParts):
    result = _original_set_vehicle_info(self, marker, vInfo, guiProps, nameParts)
    try:
        if not _isKillCamPlugin(self):
            vehicleID = vInfo.vehicleID
            _plugins[vehicleID] = self
            # DETECTED can arrive before the enemy's marker exists, so catch up
            # once it does, as long as the detection is still fresh
            if tracking.isDetected(vehicleID) and _inserted.get(vehicleID) != (self, marker.getMarkerID()):
                _showBulb(vehicleID)
    except Exception:
        log('setVehicleInfo patch crashed:\n' + traceback.format_exc())
    return result


def _isKillCamPlugin(plugin):
    # Every battle page also runs a hidden markers manager for the kill cam,
    # whose plugin sets up the same vehicles; a bulb there is never seen
    from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import KillCamMarkersManager
    return isinstance(plugin._parentObj, KillCamMarkersManager)


def _patched_plugin_stop(self):
    # The plugin destroys all its markers here, so our bulbs go with them
    for vehicleID, plugin in _plugins.items():
        if plugin is self:
            _forget(vehicleID)
            del _plugins[vehicleID]
    return _original_plugin_stop(self)


def _patched_update_marker_state(self, handle, newState, *args, **kwargs):
    # Every death passes through here, so the bulb never lingers on a wreck
    if newState == 'dead':
        try:
            for vehicleID, ref in _inserted.items():
                if ref == (self, handle):
                    _removeBulb(vehicleID)
        except Exception:
            log('updateMarkerState patch crashed:\n' + traceback.format_exc())
    return _original_update_marker_state(self, handle, newState, *args, **kwargs)


def _effectColor(plugin):
    from account_helpers.settings_core.settings_constants import GRAPHICS
    return COLOR_BLIND if plugin.settingsCore.getSetting(GRAPHICS.COLOR_BLIND) else COLOR_DEFAULT


def _isVehicleAlive(plugin, vehicleID):
    # Not marker.isAlive(): that reads the vehicle entity, which is detached
    # while the enemy is out of sight, exactly when a re-spot comes in
    vInfo = plugin.sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
    return vInfo is not None and vInfo.isAlive()


def _callBulb(plugin, markerID, method, *args):
    plugin._invokeMarker(markerID, 'callInsertedSymbolMethod', BULB_SYMBOL, method, *args)


def _cancelRemove(vehicleID):
    callbackID = _removeCallbacks.pop(vehicleID, None)
    if callbackID is not None:
        BigWorld.cancelCallback(callbackID)


def _forget(vehicleID):
    _cancelRemove(vehicleID)
    _inserted.pop(vehicleID, None)


def _showBulb(vehicleID):
    plugin = _plugins.get(vehicleID)
    if plugin is None:
        return
    marker = plugin._markers.get(vehicleID)
    if marker is None or not _isVehicleAlive(plugin, vehicleID):
        return
    markerID = marker.getMarkerID()

    _cancelRemove(vehicleID)
    if _inserted.get(vehicleID) != (plugin, markerID):
        # Only inserted for as long as it is shown, so idle markers stay vanilla
        plugin._invokeMarker(markerID, 'insertSymbol', BULB_SYMBOL, INSERT_INDEX, 0)
        _callBulb(plugin, markerID, 'setLayout', BULB_OFFSET_X, BULB_OFFSET_Y, BULB_SCALE)
        colorName, rgb = _effectColor(plugin)
        _callBulb(plugin, markerID, 'setColor', colorName, rgb)
        _inserted[vehicleID] = (plugin, markerID)

    _callBulb(plugin, markerID, 'show')


def _hideBulb(vehicleID):
    ref = _inserted.get(vehicleID)
    if ref is None:
        return
    plugin, markerID = ref
    _callBulb(plugin, markerID, 'hide')
    _cancelRemove(vehicleID)
    _removeCallbacks[vehicleID] = BigWorld.callback(REMOVE_DELAY, lambda: _removeBulb(vehicleID))


def _removeBulb(vehicleID):
    try:
        _cancelRemove(vehicleID)
        ref = _inserted.pop(vehicleID, None)
        if ref is None:
            return
        plugin, markerID = ref
        marker = plugin._markers.get(vehicleID)
        if marker is not None and marker.getMarkerID() == markerID:
            plugin._invokeMarker(markerID, 'removeSymbol', BULB_SYMBOL)
    except Exception:
        log('removing the bulb crashed:\n' + traceback.format_exc())


def _onExpire(vehicleID):
    _hideBulb(vehicleID)


def apply_patch():
    global _original_handle_battle_events, _original_set_vehicle_info, _original_plugin_stop, _original_update_marker_state

    from gui.battle_control.controllers import feedback_adaptor
    from gui.Scaleform.daapi.view.battle.shared.markers2d import vehicle_plugins

    if _original_handle_battle_events is None:
        _original_handle_battle_events = feedback_adaptor.BattleFeedbackAdaptor.handleBattleEvents
    feedback_adaptor.BattleFeedbackAdaptor.handleBattleEvents = _patched_handle_battle_events

    if _original_set_vehicle_info is None:
        _original_set_vehicle_info = vehicle_plugins.VehicleMarkerPlugin._setVehicleInfo
    vehicle_plugins.VehicleMarkerPlugin._setVehicleInfo = _patched_set_vehicle_info

    if _original_plugin_stop is None:
        _original_plugin_stop = vehicle_plugins.VehicleMarkerPlugin.stop
    vehicle_plugins.VehicleMarkerPlugin.stop = _patched_plugin_stop

    if _original_update_marker_state is None:
        _original_update_marker_state = vehicle_plugins.VehicleMarkerPlugin._updateMarkerState
    vehicle_plugins.VehicleMarkerPlugin._updateMarkerState = _patched_update_marker_state

    library.apply_patch()
    tracking.setOnExpire(_onExpire)


def remove_patch():
    global _original_handle_battle_events, _original_set_vehicle_info, _original_plugin_stop, _original_update_marker_state

    if _original_handle_battle_events is not None:
        from gui.battle_control.controllers import feedback_adaptor
        feedback_adaptor.BattleFeedbackAdaptor.handleBattleEvents = _original_handle_battle_events
        _original_handle_battle_events = None

    from gui.Scaleform.daapi.view.battle.shared.markers2d import vehicle_plugins
    if _original_set_vehicle_info is not None:
        vehicle_plugins.VehicleMarkerPlugin._setVehicleInfo = _original_set_vehicle_info
        _original_set_vehicle_info = None

    if _original_plugin_stop is not None:
        vehicle_plugins.VehicleMarkerPlugin.stop = _original_plugin_stop
        _original_plugin_stop = None

    if _original_update_marker_state is not None:
        vehicle_plugins.VehicleMarkerPlugin._updateMarkerState = _original_update_marker_state
        _original_update_marker_state = None

    for vehicleID in list(_inserted):
        _forget(vehicleID)
    _plugins.clear()
    library.remove_patch()
    tracking.clear()
