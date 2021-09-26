from typing import Set
from google.cloud import firestore


CHAT_ID = 'chat_id'


class SubscriberRepository:
    """
    This class is used to retrieve and persists subscriber data to the firestore database.
    """

    def __init__(self, db: firestore.Client) -> None:
        self.db = db
        self.collection = db.collection('subscribers')

    def _get_chat_id_from_doc(self, doc: firestore.DocumentSnapshot) -> str:
        """Returns the chat id from a firestore document.

        Args:
            doc (firestore.DocumentSnapshot): The firestore document.

        Returns:
            str: The chat id
        """
        data = doc.to_dict()
        return data[CHAT_ID]

    def get_subscribers(self) -> Set[str]:
        """Get all the subscribers' chat id.

        Returns:
            Set[str]: All chat ids of the subscriber.
        """
        subscribers_list = self.collection.get()
        chat_ids = map(self._get_chat_id_from_doc, subscribers_list)

        return set(chat_ids)

    def add_subscriber(self, chat_id: str):
        """Adds a subscriber to the database.

        Args:
            chat_id (str): The subscriber's chat id to add.
        """
        data = {
            CHAT_ID: chat_id
        }

        if not self.is_subscribed(chat_id):
            self.collection.add(data)

    def is_subscribed(self, chat_id: str) -> bool:
        documents = self.collection.where(CHAT_ID, '==', chat_id).get()

        doc = list(map(lambda x: x.exists), documents)

        if len(doc) == 0:
            return False
        else:
            return True

    def remove_subscriber(self, chat_id: str):
        """Removes a subscriber from the database. If the subscriber doesn't exist, this operation
        does nothing.

        Args:
            chat_id (str): The subscriber's chat id to remove.
        """
        documents = self.collection.where(CHAT_ID, '==', chat_id).get()

        for doc in documents:
            ref: firestore.DocumentReference = doc.reference
            ref.delete()
