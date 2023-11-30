import time
import os
#from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

#load_dotenv()
key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
    "https://openai-chatbot-interface-9ab52001491e.herokuapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserPromt(BaseModel):
    prompt: str

STATUS_COMPLETED = "completed"
THREAD_ID = os.getenv("THREAD_ID")

ASSISTANT_ID = os.getenv("ASSISTANT_ID")
ASSISTANT_VOICE = "shimmer" # alloy | onyx | nova | shimmer
ASSISTANT_VOICE_MODEL = "tts-1" # tts-1 | tts-1-hd

def run_thread(thread_id, assistant_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    return run.id

def create_message(prompt, thread_id):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt,
    )
    return message

def retrieve_run_instances(thread_id, run_id):
    run_list = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    ) 
    return run_list.status

def retrieve_message_list(thread_id):
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    return messages.data

@app.post("/query/")
async def query_text(userPrompt: UserPromt):
    create_message(userPrompt.prompt, THREAD_ID)
    run_id = run_thread(THREAD_ID, ASSISTANT_ID)
    print(f"Your new run id is - {run_id}")

    start = time.time()
    status = None
    while status != STATUS_COMPLETED:
        status = retrieve_run_instances(THREAD_ID, run_id)
        print(f"{status}\r", end="")
        status = status  
    
    end = time.time()
    print(f"Response Generation - {end - start}")
    messages = retrieve_message_list(THREAD_ID)

    # The top message at index 0 will always be from index after the run job is completed. 
    response = messages[0].content[0].text.value
    return { "content": response, "run_id": run_id, "thread_id": THREAD_ID }

@app.get("/")
def read_root():
    return "Hello Human!"
