import BigWorld

from personal_spotted_alert.util import safe

EXPIRE_SECONDS = 7.0
TICK_INTERVAL = 0.5

_lastSeen = {}
_tickCallbackID = None
_onExpire = None


def isDetected(vehicleID):
    lastSeen = _lastSeen.get(vehicleID)
    return lastSeen is not None and BigWorld.time() - lastSeen <= EXPIRE_SECONDS


def setOnExpire(callback):
    global _onExpire
    _onExpire = callback


@safe
def mark(vehicleID):
    _lastSeen[vehicleID] = BigWorld.time()
    _ensureTicking()


def _ensureTicking():
    global _tickCallbackID
    if _tickCallbackID is None:
        _tickCallbackID = BigWorld.callback(TICK_INTERVAL, _tick)


@safe
def _tick():
    global _tickCallbackID
    _tickCallbackID = None
    now = BigWorld.time()
    for vehicleID in list(_lastSeen):
        if now - _lastSeen[vehicleID] > EXPIRE_SECONDS:
            del _lastSeen[vehicleID]
            if _onExpire is not None:
                _onExpire(vehicleID)

    if _lastSeen:
        _tickCallbackID = BigWorld.callback(TICK_INTERVAL, _tick)


def clear():
    global _tickCallbackID, _onExpire
    if _tickCallbackID is not None:
        BigWorld.cancelCallback(_tickCallbackID)
        _tickCallbackID = None
    _lastSeen.clear()
    _onExpire = None
