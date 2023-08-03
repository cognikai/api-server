from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from services.chatgpt import ChatGptService
from services.firebase import FirebaseService
from prompts import why5, inversion, first_principles,ten_framing,second_order_thinking
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create the FirebaseService singleton instance
firebase_service = FirebaseService("cognikai-firebase-adminsdk-b1rzk-e69e48ab75.json")
chatgpt_service = ChatGptService()

class Message(BaseModel):
	session_id: Optional[str]
	message: str
	method: Optional[str]

@app.get("/api/messages/{session_id}")
def get_messages(session_id: str):
	messages = firebase_service.get_messages(session_id)
	return messages

@app.post("/api/messages/last")
def get_last_session():
	session_id = firebase_service.get_last_session()
	return {"session_id": session_id}

@app.post("/api/messages")
async def create_message(message: Message):
	session_id = message.session_id
	message_content = message.message
	# If the session ID is not provided or the session doesn't exist,
	# generate a new session ID.
	if not session_id:
		session_id = firebase_service.create_session()
		if message.method:
			method = message.method
			if method == "5-whys":

				firebase_service.append_to_messages(session_id, {"content": why5.prompt, "role": "system"})
			elif method == "inversion":
				firebase_service.append_to_messages(session_id, {"content": inversion.prompt, "role": "system"})
			elif method == "second-order-thinking":
				firebase_service.append_to_messages(session_id, {"content": second_order_thinking.prompt, "role": "system"})
			elif method == "10-10-10-framing":
				firebase_service.append_to_messages(session_id, {"content": ten_framing.prompt, "role": "system"})
			elif method == "first-principles":
				firebase_service.append_to_messages(session_id, {"content": first_principles.prompt, "role": "system"})
			else:
				firebase_service.append_to_messages(session_id, {"content":why5.prompt, "role": "system"})


	messages = firebase_service.get_messages(session_id)
	messages.append({"content": message_content, "role": "user"})
	response = chatgpt_service.send_message(messages)
	firebase_service.append_to_messages(session_id, {"content": message_content, "role": "user"})
	firebase_service.append_to_messages(session_id, {"content": response, "role": "assistant"})

	return {"session_id": session_id, "message": response}


@app.get("/")
def read_root():
	return {"message": "Welcome to FastAPI server!"}
