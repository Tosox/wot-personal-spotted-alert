import traceback

from personal_spotted_alert import tracking
from personal_spotted_alert.log import log

_original_handle_battle_events = None
_original_set_vehicle_info = None
_lastMarkerRef = {}


def _patched_handle_battle_events(self, events, additionalData=None):
    try:
        from BattleFeedbackCommon import BATTLE_EVENT_TYPE
        for data in events:
            if data['eventType'] == BATTLE_EVENT_TYPE.DETECTED:
                targetID = data['targetID']
                tracking.mark(targetID)
                _showDetectedIcon(targetID, True)
    except Exception:
        log('handleBattleEvents patch crashed:\n' + traceback.format_exc())
    return _original_handle_battle_events(self, events, additionalData)


def _patched_set_vehicle_info(self, marker, vInfo, guiProps, nameParts):
    _lastMarkerRef[vInfo.vehicleID] = (self, marker)
    return _original_set_vehicle_info(self, marker, vInfo, guiProps, nameParts)


def _showDetectedIcon(vehicleID, isShown):
    ref = _lastMarkerRef.get(vehicleID)
    if ref is None:
        return
    from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
    plugin, marker = ref
    plugin._updateStatusMarkerState(vehicleID, isShown, marker.getMarkerID(), BATTLE_MARKER_STATES.TARGET_DESIGNATOR_SPOTTED_MARKER, 0, True, True)


def _onExpire(vehicleID):
    _showDetectedIcon(vehicleID, False)


def apply_patch():
    global _original_handle_battle_events, _original_set_vehicle_info

    from gui.battle_control.controllers import feedback_adaptor
    from gui.Scaleform.daapi.view.battle.shared.markers2d import vehicle_plugins

    if _original_handle_battle_events is None:
        _original_handle_battle_events = feedback_adaptor.BattleFeedbackAdaptor.handleBattleEvents
    feedback_adaptor.BattleFeedbackAdaptor.handleBattleEvents = _patched_handle_battle_events

    if _original_set_vehicle_info is None:
        _original_set_vehicle_info = vehicle_plugins.VehicleMarkerPlugin._setVehicleInfo
    vehicle_plugins.VehicleMarkerPlugin._setVehicleInfo = _patched_set_vehicle_info

    tracking.setOnExpire(_onExpire)


def remove_patch():
    global _original_handle_battle_events, _original_set_vehicle_info

    if _original_handle_battle_events is not None:
        from gui.battle_control.controllers import feedback_adaptor
        feedback_adaptor.BattleFeedbackAdaptor.handleBattleEvents = _original_handle_battle_events
        _original_handle_battle_events = None

    if _original_set_vehicle_info is not None:
        from gui.Scaleform.daapi.view.battle.shared.markers2d import vehicle_plugins
        vehicle_plugins.VehicleMarkerPlugin._setVehicleInfo = _original_set_vehicle_info
        _original_set_vehicle_info = None

    _lastMarkerRef.clear()
    tracking.clear()
