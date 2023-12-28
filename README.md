# About
This project has several API's for processing data in various formats (text, audio stream etc.). We generate responses using openAI based on the user's query. As for the API's response we send readable audio stream of the response generated by openAI which can played at the Frontend.

<img width="1320" alt="Screenshot 2023-12-28 at 7 11 43 PM" src="https://github.com/Conrad-X/chatbot-server/assets/6302514/5d1f61a8-1bb1-4aeb-b393-10864b910282">


# Getting Started

## Setting Up API Keys
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

## Running the Application
uvicorn server:app --host=127.0.0.1 --port=${PORT:-PortNumber} --reload (--reload is optional for hot reload)

## Running the Application (Heroku)
web uvicorn server:app --host=0.0.0.0 --port=${PORT:-5000}

# Happy Coding!
