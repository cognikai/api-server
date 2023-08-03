import uuid
import firebase_admin
from firebase_admin import firestore, credentials


class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class FirebaseService(metaclass=Singleton):
	def __init__(self, credential_path):
		cred = credentials.Certificate(credential_path)
		firebase_admin.initialize_app(cred)
		self.db = firestore.client()

	def get_session(self, session_id):
		return self.db.collection(u'sessions').document(session_id).get()


	def create_session(self):
		session_id = str(uuid.uuid4())
		self.db.collection(u'sessions').document(session_id).set({'messages': []})
		return session_id

	def does_session_exist(self, session_id):
		session_data = self.get_session(session_id).to_dict()
		return session_data is not None

	def append_to_messages(self, session_id, message):
		session = self.get_session(session_id)
		if session.exists:
			messages = session.to_dict().get('messages', [])
			messages.append(message)
			self.update_session(session_id, messages)
			return True
		else:
			return False

	def get_messages(self, session_id):
		session = self.get_session(session_id)
		if session.exists:
			return session.to_dict().get('messages', [])
		else:
			return []

	def update_session(self, session_id, messages):
		return self.db.collection(u'sessions').document(session_id).update({'messages': messages})

	def get_last_session(self):
		sessions = self.db.collection(u'sessions').order_by(u'created_at', direction=firestore.Query.DESCENDING).limit(1).get()

		if len(sessions) > 0:
			return sessions[0].id
		else:
			return None