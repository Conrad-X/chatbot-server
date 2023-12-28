import time
import os
#from dotenv import load_dotenv
from fastapi import FastAPI, File, Request
from fastapi.responses import StreamingResponse
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.aws.transcribe import *
from services.openai.response import *
from services.aws.polly import *
import time
from typing import Annotated
from pydub import AudioSegment

#load_dotenv()
key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)

tags_metadata = [
    {
        "name": "queryAssistant",
        "description": "Enables answering retrieval based queries",
    },
    {
        "name": "processAudioStream",
        "description": "Processes audio stream using AWS Stranscribe & OpenAI chat completion",
        "externalDocs": {
            "description": "Learn more about AWS Transcribe",
            "url": "https://aws.amazon.com/transcribe/",
        },
    },
        {
        "name": "processText",
        "description": "Processes plain text and respond with OpenAI chat completion",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

origins = [
    "http://localhost",
    "http://localhost:4200",
    "https://openai-chatbot-interface-9ab52001491e.herokuapp.com",
    "https://voice-chat-bot-client-18687526ee9a.herokuapp.com"
]
# Enable All External Links

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserText(BaseModel):
    text: str

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

@app.post("/queryAssistant/", tags=["queryAssistant"])
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

@app.post("/processAudioStream/", tags=["processAudioStream"])
async def process_audio(file: Annotated[bytes, File()]):
    start_time = time.time()
    user_text = await transcribe(file)
    response = StreamingResponse(process_stream_user_response_using_gpt(user_text), media_type="application/octet-stream")
    end_time = time.time()
    print(f"Total Time: {end_time - start_time}s")
    return response

@app.post("/processText/", tags=["processText"])
async def process_text(userText: UserText):
    start_time = time.time()
    response = StreamingResponse(process_stream_user_response_using_gpt(userText.text), media_type="application/octet-stream")
    end_time = time.time()
    print(f"Total Time: {end_time - start_time}s")
    return response

@app.get("/")
def read_root():
    return "Hello Human!"
