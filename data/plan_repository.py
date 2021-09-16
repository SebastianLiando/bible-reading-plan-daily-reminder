import datetime
from typing import List, Optional
from google.cloud import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.document import DocumentReference

from bible.plan_manager import ReadingTask, to_csv_date


class PlanRepository:
    def __init__(self, db: firestore.Client) -> None:
        self.db = db
        self.collection = db.collection('reading_plans')

    def upsert_plan(self, task: ReadingTask):
        # Try to get an existing plan for the date
        existing = self._get_plan(task.date)

        # Convert the object to dictionary
        data = task.to_dict()

        if existing is None:
            # If there is no plan for the given date, add to database
            self.collection.add(data)
        else:
            # If there is a plan for the given date, update the data
            ref: DocumentReference = existing.reference
            ref.set(data)

    def get_plans(self) -> List[ReadingTask]:
        docs = self.collection.get()

        return list(map(lambda x: ReadingTask.from_doc(x), docs))

    def _get_plan(self, date: datetime.date) -> Optional[DocumentSnapshot]:
        result = self.collection.where('date', '==', to_csv_date(date)).get()
        result = list(result)

        if len(result) == 0:
            return None
        else:
            return result[0]

    def get_plan_at(self, date: datetime.date) -> Optional[ReadingTask]:
        result = self._get_plan(date)

        if result is None:
            return None
        else:
            return ReadingTask.from_doc(result)
