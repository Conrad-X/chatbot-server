import os
import redis
from openai import OpenAI

# Only for local testing, make sure you comment this for Heroku
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=key)

description = """
    You are a bot for a tech company named `Conrad Labs` who responds to the employees of conrad labs efficiently with precise response
    regarding the company policies and employee handbook information.
""" 

instructions = """
    Follow the instructions listed below: 
    
    1. You are a bot for a tech company named `Conrad Labs` who responds to the employees of conrad labs efficiently with precise response
    regarding the company policies and employee handbook information. Most of the time, the employees would be interested in the policy information that
    you can retrieve from the files attached. Here are a few examples:
    a. Hey, what is the policy around annual leaves?
    b. What is the policy around working at home?
    c. Can I reimburse my travel expense? 
    d. How much medical coverage does a company offer? 

    2. If you dont find a match or an answer within the file then refrain from answering the question and just respond 
    `I'm sorry, I couldn't find the information for your question. Can you please elaborate further?`

    4. Do not engage in any other conversation that isn't related to the policies of conrad labs or information regarding the company, 
    in case the user is asking questions outside of it then excuse yourself from the conversation by responding 'I apologize but as Conrad's bot I can only 
    guide you regarding the policies and company specific information.'

    5. Keep your answers concise and short, avoid adding details and be to the point.  
"""

REDIS_ENDPOINT_FILES_DB = os.getenv("REDIS_ENDPOINT_FILES_DB")
REDIS_PORT_FILES_DB = os.getenv("REDIS_PORT_FILES_DB")
REDIS_PASSWORD_FILES_DB = os.getenv("REDIS_PASSWORD_FILES_DB")

REDIS_ENDPOINT_THREADS_DB = os.getenv("REDIS_ENDPOINT")
REDIS_PORT_THREADS_DB = os.getenv("REDIS_PORT")
REDIS_PASSWORD_THREADS_DB = os.getenv("REDIS_PASSWORD")

redis_client = None
# Flush Redis Files List
print("Initializing Redis")
try:
  redis_client = redis.Redis(host=REDIS_ENDPOINT_FILES_DB, port=REDIS_PORT_FILES_DB, username="default", password=REDIS_PASSWORD_FILES_DB, decode_responses=True, db=0)
except Exception as e:
  print(f"Redis Files DB Initialization Error - {e}")

print("Pinging Redis...")
if redis_client.ping():
    print("Successfully connected with Redis Files DB!")
    # Flush all the file since you will be creating new ones with a new assistant
    redis_client.flushdb()

    # Get the list of all files in the asset directory
    path = "../../assets/files"
    directory_list = os.listdir(path)
    print("Files within assets folder :'", path, "' :")
    print(directory_list)

    file_ids = []
    ignore_file_list =[".DS_Store"]

    for file_name in directory_list:
      if file_name not in ignore_file_list:
        uploaded_file = client.files.create(
          file=open(f"{path}/{file_name}", "rb"),
          purpose='assistants'
        )
        file_ids.append(uploaded_file.id)
        # Update the file Id with the name on Redis
        redis_client.set(file_name, uploaded_file.id)

    assistant = client.beta.assistants.create(
      name="The Conrad Policy Assistant",
      description=description,
      model="gpt-3.5-turbo-1106",
      tools=[{
          "type": "retrieval",
        },
      ],
      instructions=instructions,
      file_ids=file_ids
    )
    print(f"Your Assistant id is - {assistant.id}")

    thread = client.beta.threads.create()
    print(f"Your thread id is - {thread.id}")

    # Flush All Threads In Redis
    try:
      redis_client = redis.Redis(host=REDIS_ENDPOINT_THREADS_DB, port=REDIS_PORT_THREADS_DB, username="default", password=REDIS_PASSWORD_THREADS_DB, decode_responses=True, db=0)
    except Exception as e:
      print("Redis Threads DB Initialization Error")

    print("Pinging Redis...")
    if redis_client.ping():
      print("Successfully connected with Redis Threads DB!")
      redis_client.flushdb()

    print("New Policy Assistant Created Successfully!")
