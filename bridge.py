from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities     import MediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities     import ImageDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities     import VideoDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities  import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities      import OutgoingAckProtocolEntity
from yowsup.layers.protocol_presence.protocolentities  import PresenceProtocolEntity

import time, logging
from random import randint

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("bridge")

class BridgeLayer(YowInterfaceLayer):

  // These are the groups that need to be bridged
  groups = set([
    "groupId1", // eg: "912031212839-1243834430@g.us",
    "groupId2", // eg: "912031212838-9308343432@g.us",
    "groupId3"  // eg: "120812102912-2382342039@g.us"
  ])

  // bridge numbers, recommended to have at least 2
  selfParticipants = set([
    "082323092309", // bridge number 1
    "234023023233", // bridge number 2
    "213020923233"  // bridge number 3
  ])

  // List of participants
  participantMap = {}
  participantMap["SomeNumber1"] = "Some1 Name1"
  participantMap["SomeNumber2"] = "Some2 Name2"

  def getSV(self, value):
    return value if value is not None else "None"

  def logMsg(self, msg):
    try:
      msgStr = "type: " + self.getSV(msg.getType()) + ", from: " + self.getSV(msg.getFrom()) + ", participant: " + self.getSV(msg.getParticipant()) + ", timestamp: " + str(self.getSV(msg.getTimestamp()))

      if isinstance(msg, MediaMessageProtocolEntity):
        msgStr += ", mediaType: " + self.getSV(msg.getMediaType())

      if isinstance(msg, TextMessageProtocolEntity):
        msgStr += ", body: " + self.getSV(msg.getBody())

      logger.info(msgStr)
    except:
      logger.error("Exception in logMsg")

  def getParticipant(self, msg):
    if msg is None or msg.getParticipant() is None:
      return ""

    sender = msg.getParticipant().split("@")[0]
    return self.participantMap.get(sender, sender)

  def getCurrentTS(self):
    ts = 0

    try:
      with open("MESSAGE_TIMESTAMP", "r") as f:
        for line in f:
          ts = int(line)
    except Exception, e:
      logger.error("Ignored exception trying to read MESSAGE_TIMESTAMP")

    return ts

  @ProtocolEntityCallback("message")
  def onMessage(self, msg):

    self.logMsg(msg)

    #send receipt otherwise we keep receiving the same message over and over
    self.toLower(msg.ack())
    self.toLower(msg.ack(True))

    sender = msg.getFrom()
    msgTS = msg.getTimestamp()
    participant = self.getParticipant(msg)

    # Only do the processing if it's from "known" groups
    if not sender in self.groups:
      logger.info("Msg not from group, ignoring!")
      return

    # Only do the processing if it's NOT from self
    if participant in self.selfParticipants:
      logger.info("Msg from self participant, ignoring!")
      return

    # Only send msgs with a newer timestamp
    previousTS = self.getCurrentTS()
    if msgTS <= previousTS:
      logger.info("Msg is stale, ignoring! previousTS: " + str(previousTS))
      return

    # We only handle non-empty text and images
    if not (isinstance(msg, ImageDownloadableMediaMessageProtocolEntity) or (isinstance(msg, TextMessageProtocolEntity) and msg.getBody != None)):
      logger.info("Msg is not text or image, ignoring!")
      return

    with open("MESSAGE_TIMESTAMP", "w") as f:
      f.write(str(msgTS) + "\n")

    for toSendGroup in self.groups.difference([sender]):
      sendMsg = msg.forward(toSendGroup)

      if isinstance(msg, TextMessageProtocolEntity):
        sendMsg.setBody(self.getParticipant(msg) + "\n" + msg.getBody())
      elif isinstance(msg, ImageDownloadableMediaMessageProtocolEntity):
        caption = self.getParticipant(msg) + "\n" + (msg.getCaption() if msg.getCaption() != None else "")
        sendMsg.setCaption(caption)
      else:
        continue

      logger.info("Will send " + str(msgTS) + " to " + toSendGroup)
      time.sleep(randint(2,4))
      self.toLower(sendMsg)


  @ProtocolEntityCallback("receipt")
  def onReceipt(self, entity):
    #ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", "delivery", entity.getFrom())
    self.toLower(entity.ack())
