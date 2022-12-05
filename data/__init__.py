from google.cloud import firestore
from config.env import CREDENTIALS

db = firestore.Client(credentials=CREDENTIALS)
