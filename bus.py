

class DV01Events:
    DV01_UPDATED = 'dv01_updated'


class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, callback):
        self._subscribers.setdefault(event_type, []).append(callback)

    def publish(self, event_type, *args, **kwargs):
        for callback in self._subscribers.get(event_type, []):
            callback(*args, **kwargs)
