import time
import os
import redis

from openai import OpenAI
from typing import Annotated
from pydub import AudioSegment

from fastapi import FastAPI, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from services.openai.assistant import run_thread, create_message, retrieve_run_instances, retrieve_message_list, create_thread, delete_threads
from interface.userprompt import UserPrompt
from services.aws.transcribe import transcribe
from services.openai.openai_response_with_polly import process_text_stream_with_polly
from services.utility.constants.meta_tags import tags_metadata

# Only for local testing, make sure you comment this for Heroku
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)

# Enable All External Links
# origins = ["*"]
origins = ["http://localhost","http://localhost:4200"]

app = FastAPI(openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

THREAD_ID = os.getenv("THREAD_ID")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
ASSISTANT_VOICE = "shimmer" # alloy | onyx | nova | shimmer
ASSISTANT_VOICE_MODEL = "tts-1" # tts-1 | tts-1-hd

@app.post("/queryAssistant/", tags=["queryAssistant"])
async def query_text(userPrompt: UserPrompt):
    print("Creating message...")        
    try:
        create_message(client, userPrompt.prompt, THREAD_ID)
        run_id = run_thread(client, THREAD_ID, ASSISTANT_ID)
        print(f"Your new run id is - {run_id}")

        start = time.time()
        status = None
        while status not in [STATUS_COMPLETED, STATUS_FAILED]:
            status = retrieve_run_instances(client, THREAD_ID, run_id)
            print(f"{status}\r", end="")
            status = status  
        
        print(f"The message status - {status}")
        if status == STATUS_COMPLETED: 
            end = time.time()
            print(f"Response Generation - {end - start}")
            messages = retrieve_message_list(client, THREAD_ID)
            # The top message at index 0 will always be from index after the run job is completed. 
            response = messages[0].content[0].text.value
        elif status == STATUS_FAILED:
            return { "content": "The message status failed. Please check your OpenAI account & Billing Status.", "statusCode": 500}
    except Exception as e:
        return { "content": e, "statusCode": 500}
    
    return { "content": response, "run_id": run_id, "thread_id": THREAD_ID, "statusCode": 200 }

@app.post("/processText/",tags=["processText"])
async def process_text(text: str):
    start_time = time.time()
    response = StreamingResponse(process_text_stream_with_polly(client, text), media_type="application/octet-stream")
    end_time = time.time()
    print(f"Total Time Elaspsed: {end_time - start_time} sec")
    return response

@app.post("/processAudioFile/", tags=["processAudioFile"])
async def process_audio(file: Annotated[bytes, File()]):
    start_time = time.time()
    user_text = await transcribe(file)
    response = StreamingResponse(process_text_stream_with_polly(client, user_text), media_type="application/octet-stream")
    end_time = time.time()
    print(f"Total Time Elaspsed: {end_time - start_time} sec")
    return response

@app.get("/")
def read_root():
    return "Hello Human!"
