import pushnotify


class NotificationManager(object):
    """
    class to abstract the notifications via pushnotify
    """
    def __init__(self, apikey, application, type="prowl"):
        self._client = pushnotify.get_client(
            self.type, application=self.application
        )
        self._client.add_key(self.apikey)

    def notify(self, event, description, split=True):
        """
        send a push notification
        """
        self._client.notify(description, event, split=split)
