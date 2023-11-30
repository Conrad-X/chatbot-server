import os
from openai import OpenAI
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

file_1 = client.files.create(
  file=open("files/conrad-labs-policies.pdf", "rb"),
  purpose='assistants'
)

file_2 = client.files.create(
  file=open("files/employees-handbook.pdf", "rb"),
  purpose='assistants'
)

file_3 = client.files.create(
  file=open("files/more-conrad-labs-policies.txt", "rb"),
  purpose='assistants'
)

assistant = client.beta.assistants.create(
  name="The Rad Assistant",
  description=description,
  model="gpt-3.5-turbo-1106",
  tools=[{
      "type": "retrieval",
    },
  ],
  instructions=instructions,
  file_ids=[file_1.id, file_2.id, file_3.id]
)
print(f"Your Assistant id is - {assistant.id}")

thread = client.beta.threads.create()
print(f"Your thread id is - {thread.id}")

