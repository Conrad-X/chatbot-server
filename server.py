import time
import os
from fastapi import FastAPI, File
from fastapi.responses import StreamingResponse
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from transcribe import *
# from processing import *
# from polly import *
import time
from typing import Annotated
from pydub import AudioSegment
import redis
import uuid
# from dotenv import load_dotenv
# load_dotenv()


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
    {
        "name": "clearCache",
        "description": "Cleares existing cache keys"
    }
]

app = FastAPI(openapi_tags=tags_metadata)

origins = [
    "http://localhost",
    "http://localhost:4200",
    "https://openai-chatbot-interface-9ab52001491e.herokuapp.com",
    "https://voice-chat-bot-client-18687526ee9a.herokuapp.com"
]
# Enable All External Links
# origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = None

class UserPromt(BaseModel):
    prompt: str

STATUS_COMPLETED = "completed"
THREAD_ID = os.getenv("THREAD_ID")

REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

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

def create_thread():
    thread = client.beta.threads.create()
    return thread.id

def get_mac_address():
    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
    mac = ':'.join(mac_num[i : i + 2] for i in range(0, 11, 2))
    return mac

def delete_threads(thread_id):
    response = client.beta.threads.delete(thread_id)
    return response["deleted"]

@app.post("/clearCache/", tags=["clearCache"])
async def clear_cache():
    try:
        redis_client = redis.Redis(host=REDIS_ENDPOINT, port=REDIS_PORT, username="default", password=REDIS_PASSWORD, decode_responses=True, db=0)
    except Exception as e:
        print("Redis Initialization Error")

    print("Pinging Redis...")
    if redis_client.ping():
        print("Successfully connected with Redis!")
    
    # Delete all threads (value stored against for mac address keys) 
    keys = redis_client.keys()
    for key in keys:
        value = redis_client.get(key)

        # Important - The OpenAI API always returns and error
        # upon retrieving and deleting a thread. 
        try:
            response = delete_threads(value)
        except Exception as e: 
            print(f"Exception - {e}")

        # (check the comment right above) if response: 
        redis_client.delete(key)

    #redis_client.flushdb()
    return { 'statusCode': 200, "status": True }

@app.post("/queryAssistant/", tags=["queryAssistant"])
async def query_text(userPrompt: UserPromt):
    # Check if a THREAD_ID exist within redis
    try:
        redis_client = redis.Redis(host=REDIS_ENDPOINT, port=REDIS_PORT, username="default", password=REDIS_PASSWORD, decode_responses=True, db=0)
    except Exception as e:
        print("Redis Initialization Error")

    print("Pinging Redis...")
    if redis_client.ping():
        print("Successfully connected with Redis!")

        mac_address = get_mac_address()
        print(f"The Mac Address value is {mac_address}")

        try:
            THREAD_ID = redis_client.get(mac_address)
        except Exception as e:
            print(e)
            return {'statusCode': 500}
        
        print(f"The THREAD_ID value is {THREAD_ID}")

        if(not(THREAD_ID)):
            THREAD_ID = create_thread()
            print(f"New Thread Id - {THREAD_ID}")
            redis_client.set(mac_address, THREAD_ID)

        print("Creating message...")

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
    else:
        return {'statusCode': 500}

# @app.post("/processAudioStream/", tags=["processAudioStream"])
# async def process_audio(file: Annotated[bytes, File()]):
#     start_time = time.time()
#     user_text = await transcribe(file)
#     response = StreamingResponse(process_stream_user_response(client, user_text), media_type="application/octet-stream")
#     end_time = time.time()
#     print(f"Total Time: {end_time - start_time}s")
#     return response

# @app.post("/processText/",tags=["processText"])
# async def process_text(text: str):
#     print(text)
#     start_time = time.time()
#     response = StreamingResponse(process_stream_user_response(client, text), media_type="application/octet-stream")
#     end_time = time.time()
#     print(f"Total Time: {end_time - start_time}s")
#     return response

@app.get("/")
def read_root():
    return "Hello Human!"
