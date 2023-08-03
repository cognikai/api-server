import openai
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

class ChatGptService:

	def __init__(self,api_key = None):
		if api_key is None:
			api_key = os.getenv("OPENAI_API_KEY")
		openai.api_key = api_key


	def send_message(self,messages:[str],model="gpt-4") :

		response = openai.ChatCompletion.create(
			model=model,
			messages = messages,
			temperature=0,
			max_tokens=250,
			presence_penalty=0.6,
			timeout=60
		)
		message = response["choices"][0]["message"]["content"]
		return message

if __name__ == "__main__":

	from prompts import inversion
	messages = [
		{
			"content":inversion.prompt,
			"role":"system"
		},
		{
			"content":"I want to make love with my friend's sister.",
			"role":"user"
		}
	]
	client = ChatGptService()
	response = client .send_message(messages)

	print(response)