## About 
This project comprises of a chatbot server comprising of multiple API's for processing user input prompt in various text and audio formats. The responses is generated using openAI and multiple apporaches are accomodated to send the response back to the user. Here are a few details that will come in handy while navigating this repository.

    .
    ├── assets                  # Domain specific files provided to OpenAI Assistant
    ├── interface               # Utility classes used within the server code
    ├── legacy                  # Generalized version of the chat bot server
    ├── server.py               # Chatbot server file
    ├── requirements.txt        # List of dependency used for deploying 
    ├── Procfile                # Procfile (equired by Heroku only)
    └── README.md


## Getting Started
There are two forms of servers available under this repository
- the first one is a basic one found under the ```legacy``` folder, this can be re-used for multiple scenarios depending on your application domain and is built upon OpenAI Assistants and depicts the workflow. Follow the steps below to make the legacy server work
    - Create a ```.env``` file comprising of the folling details
      ```
      ASSISTANT_ID=XXXXXXXXXXXX
      OPENAI_API_KEY=XXXXXXXXXX
      THREAD_ID=XXXXXXXXXXXXXXX

      AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXX
      AWS_DEFAULT_REGION=XXXXXXXXXXXXXXX
      AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXX
      ```
    - use ```pip install``` to install all dependencies. 
    - Copy the ```server-default.py``` under the ```legacy``` folder to the main directory and run the following command. you can rename the file to 'server.py' if you prefer but make sure you make the appropriate changes to 
      the command below  
      ```
      uvicorn server-default:app --host=0.0.0.0 --port=8000
      ```
    - Once you're server is running you can visit the API doc file here ```http://localhost:8000/docs``` where you can test it
    - To understand how an assistant works, we recommend that you go through the official doc from OpenAI https://platform.openai.com/docs/assistants/how-it-works .
    - Here's the interaction diagram of the workflow

      <img src="https://github.com/Conrad-X/chatbot-server/assets/6302514/965f06fa-be6a-4b38-a75e-05af1f3e7ebc" width="500" />

- The second one is found the main directory by the name of ```server.py``` and is an example of a specialized bot for the any domian's policy documents. This bot is built on Conrad Lab's policy documents which are maintained by the human rescources. Follow the steps below to make the server work
  - Create a ```.env``` file comprising of the folling details
      ```
      ASSISTANT_ID=XXXXXXXXXXXX
      OPENAI_API_KEY=XXXXXXXXXX
      THREAD_ID=XXXXXXXXXXXXXXX

      AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXX
      AWS_DEFAULT_REGION=XXXXXXXXXXXXXXX
      AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXX

      REDIS_ENDPOINT=XXXXXXXXXXXXXXXX
      REDIS_PORT=XXXXXXXXXXXXXXXXXXXX
      REDIS_PASSWORD=XXXXXXXXXXXXXXXX
      ```
    - use ```pip install``` to install all dependencies.
    - use the following command to run the server
      ```
      uvicorn server:app --host=127.0.0.1 --port=${PORT:-PortNumber} --reload (--reload is optional for hot reload)
      ```
    - The Redis instance 
    - Here's the interaction diagram of the workflow
   
      <img src="https://github.com/Conrad-X/chatbot-server/assets/6302514/d51430bc-7d9e-4ca7-ba4a-0a01dd39c3b0" width="850" />

