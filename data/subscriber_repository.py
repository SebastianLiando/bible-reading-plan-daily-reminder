from typing import Optional, Set
from google.cloud import firestore
from enum import Enum, auto, unique
from dataclasses import dataclass, asdict

from data.firestore_repository import FirestoreRepository


@unique
class SubscriptionItem(Enum):
    BIBLE_READING_PLAN = auto()
    SERVICE_REMINDER = auto()


@dataclass(frozen=True, eq=True)
class Subscriber:
    id: str
    chat_id: str
    sub_items: Set[SubscriptionItem]

    def is_subscribed_to(self, item: SubscriptionItem) -> bool:
        return item in self.sub_items

    def subscribe(self, item: SubscriptionItem):
        self.sub_items.add(item)

    def unsubscribe(self, item: SubscriptionItem):
        self.sub_items.remove(item)

    @staticmethod
    def from_json(json: dict):
        return Subscriber(
            id=json['id'],
            chat_id=json['chat_id'],
            sub_items=set(
                map(lambda value: SubscriptionItem(value), json['sub_items']))
        )

    def to_json(self):
        as_dict = asdict(self)
        # Convert enum to value
        as_dict['sub_items'] = list(
            map(lambda e: e.value, as_dict['sub_items']))

        return as_dict


class SubscriberRepository(FirestoreRepository):
    """
    This class is used to retrieve and persists subscriber data to the firestore database.
    """

    def __init__(self, db: Optional[firestore.Client] = None) -> None:
        client = db if db is not None else firestore.Client()
        super().__init__('subscribers', client)

    def _data_class(self):
        return Subscriber

    def list_by_subscription(self, item: SubscriptionItem):
        snapshots = self.collection.where(
            'sub_items', 'array_contains', item.value).get()
            
        items = map(lambda doc: self._create_from_doc(doc.id, doc.to_dict()),
                    snapshots)
        return list(items)

    def get(self, id: str):
        doc = self.collection.where('chat_id', '==', id).get()
        if len(doc) == 0:
            return None

        doc = doc[0]
        return super()._create_from_doc(doc.id, doc.to_dict())

    def is_subscribed(self, chat_id: str, item: SubscriptionItem) -> bool:
        doc = self.get(chat_id)
        return (doc is not None) and (item in doc.sub_items)

    def toggle_subscription(self, chat_id: str, item: SubscriptionItem):
        subscriber = self.get(chat_id)

        # Create a new subscriber if doesn't exist in database.
        if subscriber is None:
            subscriber = Subscriber(id='', chat_id=chat_id, sub_items=set())

        is_subbed = subscriber.is_subscribed_to(item)
        if is_subbed:
            subscriber.unsubscribe(item)
        else:
            subscriber.subscribe(item)

        return super().save(subscriber)
