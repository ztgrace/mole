from mole import build_all_payloads, load_plugins, get_plugin_dirs, token_server_health_check
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator
from burp import IBurpExtender
from burp import IContextMenuFactory
from burp import IContextMenuInvocation
from javax.swing import JMenuItem
from java.awt.event import ActionListener
#from java.awt.event import ActionEvent
#from java.awt.event import KeyEvent
#from java.util import List, ArrayList
import java.util.Arrays;
#import random
from lib.config import Config
from lib.trackingtoken import TrackingToken


class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory, IContextMenuFactory, ActionListener):
    def __init__(self):
        self.config = Config()
        self.menu_item = JMenuItem('Insert Mole payload')
        self.menu_item.addActionListener(self)

        # Check to see if we can reach the token server
        if not token_server_health_check(self.config):
            raise Exception('Token Server Unavailable: %s://%s' %(self.config.token_protocol, self.config.token_server))

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        callbacks.setExtensionName("Mole OOB Exploitation Framework")
        self._helpers = callbacks.getHelpers()
        callbacks.registerIntruderPayloadGeneratorFactory(self)
        callbacks.registerContextMenuFactory(self)
        print("Mole OOB Exploitation Framework Loaded")
        return

    @staticmethod
    def getGeneratorName():
        return "Mole Payload Generator"

    def createNewInstance(self, attack):
        return MoleBurpPayloadGenerator(self, attack)

    def createMenuItems(self, ctxMenuInvocation):
        self.ctxMenuInvocation = ctxMenuInvocation
        return [self.menu_item]

    def actionPerformed(self, actionEvent):
        t = TrackingToken(config=self.config, tags='MoleBurpInsertPayload')
        print('Inserted token: ' + t.full_token())

        # Code adapted from https://github.com/PortSwigger/handy-collaborator/blob/master/src/main/java/burp/BurpExtender.java
        selectedItems = self.ctxMenuInvocation.getSelectedMessages()
        selectedBounds = self.ctxMenuInvocation.getSelectionBounds()
        selectedInvocationContext = self.ctxMenuInvocation.getInvocationContext()

        if self._isRequest(selectedInvocationContext):
            selectedItem = selectedItems[0].getRequest()
        else:
            selectedItem = selectedItems[0].getResponse()

        before = self._helpers.bytesToString(selectedItem[0:selectedBounds[0]])
        after = self._helpers.bytesToString(selectedItem[selectedBounds[1]:])

        try:
            newItem = before + t.full_token() + after
            if self._isRequest(selectedInvocationContext):
                selectedItems[0].setRequest(newItem)
            else:
                selectedItems[0].setResponse(newItem)
        except:
            import traceback
            tb = traceback.format_exc()
            print(tb)

        return None

    def _isRequest(self, ctx):
        if ctx == IContextMenuInvocation.CONTEXT_MESSAGE_EDITOR_REQUEST:
            return True

        return False


class MoleBurpPayloadGenerator(IIntruderPayloadGenerator):
    def __init__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self._attack = attack
        self.max_payloads = 100
        self.num_payloads = 0
        self.config = Config()
        servers, payloads = load_plugins({}, {})

        print("MoleBurpPayloadGenerator Loaded")

        return

    def hasMorePayloads(self):
        print("hasMorePayloads called.")
        if self.num_payloads == self.max_payloads:
            print("No more payloads.")
            return False
        else:
            print("More payloads. Continuing.")
            return True

    def getNextPayload(self, current_payload):
        t = TrackingToken(self.config, tags='MoleBurpPayloadGenerator')
        return t.full_token()

    def reset(self):
        self.num_payloads = 0
        return

