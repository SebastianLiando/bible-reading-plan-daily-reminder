from google.cloud import firestore


class FirestoreRepository:
    """
    This class is a base class for repository that interacts with Firestore Database.
    This class is an abstract class, so instantiate one of the subclasses of this class instead.
    """

    def __init__(self, collection_name, client: firestore.Client = None) -> None:
        db = client if client is not None else firestore.Client()

        self.collection = db.collection(collection_name)

    def _data_class(self):
        """Returns the object type that the repository is dealing with."""
        raise NotImplementedError('Please pass in the entity data class.')

    def _create_from_doc(self, id: str, data: dict):
        """Creates the data object from the given id and data. 

        Args:
            id (str): The id of the object.
            data (dict): The data of the object.
        """
        json = {'id': id, **data}
        return self._data_class().from_json(json)

    def list(self) -> list:
        """Returns all the item in the database.

        Returns:
            list: All items in the database.
        """
        snapshots = self.collection.get()
        items = map(lambda doc: self._create_from_doc(doc.id, doc.to_dict()),
                    snapshots)
        return list(items)

    def save(self, data):
        """Persists the given data to the database. This operation can be insert or update.
        If the id of the data is empty, insert will be performed. Otherwise, update will be 
        performed.

        Args:
            data : The data to be saved.
        """

        # Make sure that the object is of the correct type.
        if not isinstance(data, self._data_class()):
            raise TypeError(f"Expected instance of type {self._object_type()}")

        firestore_data = data.to_json()
        doc_id = firestore_data.pop('id')

        if (doc_id == ''):
            # Insert
            inserted = self.collection.add(firestore_data)[1].get()
            return self._create_from_doc(inserted.id, inserted.to_dict())
        else:
            # Update
            self.collection.document(doc_id).set(firestore_data)
            return data

    def get(self, id: str):
        """Returns the object from the given id.

        Args:
            id (str): The id of the object.
        """
        doc = self.collection.document(id).get()
        return self._create_from_doc(doc.id, doc.to_dict())

    def delete(self, id: str):
        """Removes the object with the given id from the database.

        Args:
            id (str): The object id to be removed.
        """

        # Delete if the given id exists.
        self.collection.document(id).delete()
