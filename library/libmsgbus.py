
class MsgBus(object):
    callerList = {}

    def __init__(self):
        test =0


    def subscribe(self, channel, callback):

        if channel not in MsgBus.callerList.keys():
   #         print ('Create Channel new')
            MsgBus.callerList[channel] = []
        MsgBus.callerList[channel].append(callback)

   #     print('callerList',MsgBus.callerList)

        return True

    def unsubscribe(self, channel, callback):

        if channel in MsgBus.callerList.keys():
            MsgBus.callerList[channel].remove(callback)

        return True

    def unsubscribe_all(self, channel):

        if channel in MsgBus.callerList.keys():
            MsgBus.callerList[channel] = []

        return True

    def has_subscriber(self,channel):

        result = 0

        if channel in MsgBus.callerList.keys():
            result = len(MsgBus.callerList[channel])

        return result

    def MsgBusPublish(self, channel, *args, **kwargs):

        result = False

    #   print('Hier',channel)
        if channel in MsgBus.callerList.keys():
            result = True
     #       print('Channel',channel)
            for item in MsgBus.callerList[channel]:
      #          print('Item',item)
                item(*args, **kwargs)
        else:
            print('Channel not found')

        return result

    def debug(self):

        print ('DEBUG',MsgBus.callerList)

        return

