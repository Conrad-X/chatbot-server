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
    - Copy the ```server-default.py``` under the ```legacy``` folder to the main directory and run the following command. you can rename the file to 'server.py' if you prefer but make sure you make the appropriate changes to 
      the command below  
      ```
      uvicorn server-default:app --host=0.0.0.0 --port=8000
      ```
    - Once you're server is running you can visit the API doc file here ```http://localhost:8000/docs``` where you can test it
    - To understand how an assistant works, we recommend that you go through the official doc from OpenAI https://platform.openai.com/docs/assistants/how-it-works .
    - Here's the interaction diagram of the workflow: 

      <img src="https://github.com/Conrad-X/chatbot-server/assets/6302514/965f06fa-be6a-4b38-a75e-05af1f3e7ebc" width="500" />

- The second one is found the main directory by the name of ```server.py``` and is the 
### Setting Up API Keys
We will need a couple of keys for this app's configuration. So you'll need to add the key/value pairs as enviroment variables.

### OPENAI Key
Add your openAI key as OPENAI_API_KEY="Your-Api-Key" (Don't forgot to throw some $ into your account)

### AWS Keys
You will need to configure AWS by adding three keys as enviroment variables. 
    1. AWS_ACCESS_KEY_ID="Your-Key"
    2. AWS_SECRET_ACCESS_KEY="Your-Key"
    3. REGION_NAME="Your-Region"

## Installing Dependencies

### Use "pip install" for installing dependencies

### Running the Application
uvicorn server:app --host=127.0.0.1 --port=${PORT:-PortNumber} --reload (--reload is optional for hot reload)

### Running the Application (Heroku)
web uvicorn server:app --host=0.0.0.0 --port=${PORT:-5000}
