from personal_spotted_alert.log import log
from personal_spotted_alert import patch
from personal_spotted_alert.util import safe


class PersonalSpottedAlertMod(object):

    @safe
    def init(self):
        patch.apply_patch()
        log('loaded')

    @safe
    def fini(self):
        patch.remove_patch()
        log('unloaded')


g_personalSpottedAlertMod = PersonalSpottedAlertMod()
