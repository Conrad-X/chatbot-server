import time
import os
import redis
import re
from interface.usertext import UserText

from openai import OpenAI
from typing import Annotated
from pydub import AudioSegment

from fastapi import FastAPI, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from services.openai.assistant import run_thread, create_message, retrieve_run_instances, retrieve_message_list, create_thread, delete_threads
from interface.userprompt import UserPrompt
from services.redis.init import redis_init
from services.aws.polly import polly_speak
from services.aws.transcribe import transcribe
from services.openai.openai_response_with_polly import process_text_stream_with_polly
from services.utility.constants.meta_tags import tags_metadata
import sentry_sdk

# Only for local testing, make sure you comment this for Heroku
# from dotenv import load_dotenv
# load_dotenv()

key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)

sentry_sdk.init(
    dsn="https://7ad05bc294c3dc529d53452d14a46f5b@o4507509440970752.ingest.de.sentry.io/4507509452243024",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

# Enable All External Links
# origins = ["*"]
origins = ["http://localhost", "http://localhost:3000", "http://localhost:4200","https://openai-chatbot-interface-9ab52001491e.herokuapp.com","https://voice-chat-bot-client-18687526ee9a.herokuapp.com", "https://test.simplisti.cc", "https://www.simplisti.cc"]

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

REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

ASSISTANT_ID = os.getenv("ASSISTANT_ID")
ASSISTANT_VOICE = "shimmer" # alloy | onyx | nova | shimmer
ASSISTANT_VOICE_MODEL = "tts-1" # tts-1 | tts-1-hd

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

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

        # Important - The OpenAI API always returns an error
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
async def query_text(userPrompt: UserPrompt):
    # Initialize Redis
    redis_client = redis_init(REDIS_ENDPOINT, REDIS_PORT, REDIS_PASSWORD)
    if redis_client is not None:
        address = userPrompt.address
        # For testing purposes - get_mac_address() fetches your machine's MAC
        print(f"The Mac Address value is {address}")

        # Fetch the THREAD_ID against the unique address
        try:
            THREAD_ID = redis_client.get(address)
        except Exception as e:
            print(e)
            return {'statusCode': 500}
        print(f"The THREAD_ID value is {THREAD_ID}")

        # If THREAD_ID doesn't exist, create a new one
        if(not(THREAD_ID)):
            THREAD_ID = create_thread(client)
            print(f"New Thread Id - {THREAD_ID}")
            redis_client.set(address, THREAD_ID)

        # Once THREAD_ID is created of fetches, create your message
        print("Creating message...")        
        try:
            create_message(client, userPrompt.prompt, THREAD_ID)
            start = time.time()
            print("Running Thread ...")
            run_instace = run_thread(client, THREAD_ID, ASSISTANT_ID)
            run_id = run_instace["run_id"]
            message = run_instace["message"].replace("**")
            message = re.sub(r"【.*?】", "", message)
            print(f"Your new run id is - {run_id}")
            print("Run Complete!")

            # status = None
            # while status not in [STATUS_COMPLETED, STATUS_FAILED]:
            #     status = retrieve_run_instances(client, THREAD_ID, run_id)
            #     print(f"{status}\r", end="")
            #     status = status
                
            status = retrieve_run_instances(client, THREAD_ID, run_id)
            print(f"The message status - {status}")

            if status == STATUS_COMPLETED: 
                end = time.time()
                print(f"Response Generation - {end - start}")
                # messages = retrieve_message_list(client, THREAD_ID) 
                # response = messages[0].content[0].text.value
            elif status == STATUS_FAILED:
                return { "content": "The message status failed. Please check your OpenAI account & Billing Status.", "statusCode": 500}
        
        except Exception as e:
            return { "content": str(e), "statusCode": 500}
        
        return { "content": message, "run_id": run_id, "thread_id": THREAD_ID, "statusCode": 200 }
    else:
        return {'statusCode': 500}

@app.post("/processText/", tags=["processText"])
async def process_text(userText: UserText):
    start_time = time.time()
    response = StreamingResponse(process_text_stream_with_polly(client, userText.text), media_type="application/octet-stream")
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
