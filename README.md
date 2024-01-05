## About 
This project is based on `FastAPI` and represents a chatbot server comprising of multiple API's for processing user input prompt in various text and audio formats. The responses is generated using openAI and multiple apporaches are accomodated to send the response back to the user. Here are a few details that will come in handy while navigating this repository.

    .
    ├── assets                  # Domain specific files provided to OpenAI Assistant
    ├── interface               # Utility classes used within the server code
    ├── legacy                  # Generalized version of the chat bot server
    ├── services                # Services used within the server files
        ├── aws
        ├── openai
        ├── redis
        ├── utility
            ├── constants
    ├── server.py               # Chatbot main server file
    ├── server-test.py          # Chatbot test server file
    ├── requirements.txt        # List of dependency used for deploying 
    ├── Procfile                # Procfile (equired by Heroku only)
    └── README.md


## Getting Started

### Text Based Conversational Bot Server
There are two forms of servers available under this repository
- The first one is a basic one found under the `legacy` folder, this can be re-used for multiple scenarios depending on your application domain and is built upon OpenAI Assistants and depicts the workflow. Follow the steps below to make the legacy server work
    - Create a `.env` file comprising of the folling details
      ```
      ASSISTANT_ID=XXXXXXXXXXXX
      OPENAI_API_KEY=XXXXXXXXXX
      THREAD_ID=XXXXXXXXXXXXXXX

      AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXX
      AWS_DEFAULT_REGION=XXXXXXXXXXXXXXX
      AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXX
      ```
    - use ```pip install``` to install all dependencies. 
    - You can test by using using a `server-test.py` within the root directory by running the following command on your terminal given that the aforementioned keys are provided in the `.env` file
      ```
      uvicorn server-test:app --host=127.0.0.1 --port=8000
      ```
    - Once you're server is running you can visit the API doc file here `http://localhost:8000/docs` where you can test it
    - To understand how an assistant works, we recommend that you go through the official doc from OpenAI https://platform.openai.com/docs/assistants/how-it-works .
    - Here's the interaction diagram of the workflow

      <img src="https://github.com/Conrad-X/chatbot-server/assets/6302514/965f06fa-be6a-4b38-a75e-05af1f3e7ebc" width="500" />

- The second one is found the main directory by the name of `server.py` and is an example of a specialized bot for the any domian's policy documents. This bot is built on Conrad Lab's policy documents which are maintained by the human rescources. Follow the steps below to make the server work
  - Create a `.env` file comprising of the folling details
    
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
      
    - use `pip install` to install all dependencies.
    - use the following command to run the server
      ```
      uvicorn server:app --host=127.0.0.1 --port=8000 --reload (--reload is optional for hot reload)
      ```
    - The introduction of redis instace is the only difference between the aforementioned `legacy` server, in this use-case we need it to traclk and persist the thread Ids of the OpenAI assistants, which saves the context of the conversation. These thread Ids will be saved against a unique identifier which refers to an individual user, whenever we need to update the assistant we have to flush these thread Ids to impose a new context and hence new threads will be created in order to achieve that and will be saved. We also keep track of the file Ids for each uploaded file to the assistant, these come in handy whenver we are updating the OpenAI assistant. In order to achieve that the new file needs to be uploaded first on the OpenAI platform, the file Id against the new file would be replaced with the previous and store in the redis. The files not provided to the OpenAI will be deleted from the context, which means we have to keep track of all files that exist in a particular context while replacing old files with the new ones in the process and refreshing the threads along the way. 
    - Here's the interaction diagram of the workflow
   
      <img src="https://github.com/Conrad-X/chatbot-server/assets/6302514/d51430bc-7d9e-4ca7-ba4a-0a01dd39c3b0" width="850" />

### Voice Based Response Server Endpoints
The voice based endpoints are common between both ```legacy``` and main directory server files but are subject to changes in the future. The two tools `AWS Transcribe` and `AWS Polly` are used in these endpoints to transcribe the audio file send by the user, the generated text is used to generate a response throgh OpenAI with a `stream=True` parameter within the completion API. The stream parameters helps in generating stream based response which are received in forms of chunks and can be immediately processed by `Polly` to be spoken out to the user. Make sure you have the following keys present within your `.env` file

 ```
 AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXX
 AWS_DEFAULT_REGION=XXXXXXXXXXXXXXX
 AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXX
 ```

- `For Testing only` [/processText]() <br/>
  This endpoint can be used for testing purposes, you can provide a test prompt which will not require transcribing and just be sent to OpenAI completion API to generate the response and be spoken out by Polly.
- `For Official Use` [/processAudioFile]() <br/>
   This endpoint follows the complete workflow as stated within the aforementioned paragraph and is depicted in the diagram below

   <img src="https://github.com/Conrad-X/chatbot-server/assets/6302514/f13474b3-8c8d-47f8-8e03-ec4983509168" width="750" />


### Creating the Policy Assistant
You can create your own assistant following the example within `services/openai/create_policy_assistant.py` which is a functional example for creating the assistant as per the example stated above. 
If you want to run this code locally, make sure you have the following environment variables intact, you can observe an addition of three set of new `redis` variables which correspond to the files Db shown in the diagram above. The files db stores the filenames along with their `OpenAI` file Id
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

REDIS_ENDPOINT_FILES_DB=XXXXXXXXXXXXXXXXXXXXXXX
REDIS_PORT_FILES_DB=XXXXXXXXXXXXXXXXXXXXXXXXXXX
REDIS_PASSWORD_FILES_DB=XXXXXXXXXXXXXXXXXXXXXXX
 ```
