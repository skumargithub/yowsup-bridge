from bridge import BridgeLayer
from yowsup.layers.auth                        import YowAuthenticationProtocolLayer
from yowsup.layers.protocol_messages           import YowMessagesProtocolLayer
from yowsup.layers.protocol_media              import YowMediaProtocolLayer
from yowsup.layers.protocol_receipts           import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks               import YowAckProtocolLayer
from yowsup.layers.protocol_iq                 import YowIqProtocolLayer
from yowsup.layers.network                     import YowNetworkLayer
from yowsup.layers.coder                       import YowCoderLayer
from yowsup.stacks import YowStack
from yowsup.common import YowConstants
from yowsup.layers import YowLayerEvent
from yowsup.stacks import YowStack, YOWSUP_CORE_LAYERS
from yowsup import env

import sys
import traceback
from random import randint
import logging

logger = logging.getLogger("main")

// Bridge numbers and their credentials
CREDENTIALS = [
  ("102480434343", "asldfasdfaASDFASFDAAdsfASDF="),
  ("230294340346", "asdf08asfdafdasdgf0uasdfadf="),
  ("340343094348", "05flasjfdlaskdfasdfasdfasdf=")
  ]

def NR_random(min, max):
  lastRandom = -1
  try:
    with open("LAST_RANDOM", "r") as f:
      for line in f:
        lastRandom = int(line)
  except:
    pass

  #print("LAST_RANDOM: " + str(lastRandom))

  credIndex = -1
  while True:
    credIndex = randint(min, max)
    #print("Generated credIndex: " + str(credIndex))
    if credIndex != lastRandom:
      break

  #print("credIndex: " + str(credIndex))
  with open("LAST_RANDOM", "w") as f:
    f.write(str(credIndex) + "\n")

  return credIndex

if __name__==  "__main__":
  try:
    credIndex = NR_random(0, len(CREDENTIALS) - 1)
    logger.info("Starting loop using: " + str(CREDENTIALS[credIndex]))

    layers = (
      BridgeLayer,
      (YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowMediaProtocolLayer, YowReceiptProtocolLayer, YowAckProtocolLayer, YowIqProtocolLayer)
    ) + YOWSUP_CORE_LAYERS

    stack = YowStack(layers)
    stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, CREDENTIALS[credIndex])         #setting credentials
    stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])    #whatsapp server address
    stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)              
    stack.setProp(YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource())          #info about us as WhatsApp client

    stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))   #sending the connect signal

    stack.loop() #this is the program mainloop
  except Exception, e:
    traceback.print_exc(limit=1, file=sys.stdout)
