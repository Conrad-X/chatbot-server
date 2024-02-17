import json
import redis
import urllib.parse
import boto3
import requests
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
CHAT_BOT_SERVER_URL = os.getenv("CHAT_BOT_SERVER_URL")

REDIS_FILES_ENDPOINT = os.getenv("REDIS_FILES_ENDPOINT")
REDIS_FILES_PORT = os.getenv("REDIS_FILES_PORT")
REDIS_FILES_PASSWORD = os.getenv("REDIS_FILES_PASSWORD")

STATUS_PROCESSED = 'processed'

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        uploaded_file = s3.get_object(Bucket=bucket, Key=key)
        response = requests.post('https://api.openai.com/v1/files', files={'file': (key, uploaded_file['Body'])}, data={'purpose':'assistants'}, headers={"Authorization": f"Bearer {OPENAI_API_KEY}"})
        response = response.json()
        if response["status"] == STATUS_PROCESSED:
            file_id = response["id"]
            print(f"Uploaded File Id: {file_id}")
            
            # Overwrite the file id for the filename on Redis
            try:
                redis_client_files = redis.Redis(host=REDIS_FILES_ENDPOINT, port=REDIS_FILES_PORT, username="default", password=REDIS_FILES_PASSWORD, decode_responses=True, db=0)
            except Exception as e:
                print(f"Redis (Files) Initialization Error - {e}")
        
            print("Pinging Redis (Files)...")
            if redis_client_files.ping():
                print("Successfully connected with Redis (Files)!")
                
                # Retrieve Existing File Id (if any) Against File Key
                existing_file_id = redis_client_files.get(key)
                if existing_file_id is not None:
                    # Delete File Id On OpenAI
                    try:
                        response = requests.delete(f'https://api.openai.com/v1/files/{existing_file_id}', headers={"Authorization": f"Bearer {OPENAI_API_KEY}"})
                        response = response.json()
                        if response['deleted'] == True:
                            print(f"File {existing_file_id} Deleted On OpenAI Successfully.")
                    except Exception as e:
                        print("Deletion Error: File Might Not Exist On OpenAI")
                else:
                    print(f"No Existing File {key} Found On OpenAI.")
                    
                # Update The New File Id On Redis
                redis_client_files.set(key, file_id)
                print("File Id Updated On Redis Successfully.")
                
                # Get All File Ids From redis
                file_ids = []
                keys = redis_client_files.keys()
                for key in keys:
                    value = redis_client_files.get(key)
                    file_ids.append(value)
                    
                data = {
                    "file_ids": file_ids
                }
                
                # Update Assistant On OpenAI
                response = requests.post(f'https://api.openai.com/v1/assistants/{ASSISTANT_ID}', data=json.dumps(data), headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "OpenAI-Beta": "assistants=v1", "Content-Type": "application/json"})
                response = response.json()
                
                # Check if File Ids Sent And Recieved Are Same
                if response['file_ids'] == data['file_ids']:
                    print("Assistant Updated Successfully!")
                    
                    # Delete Threads From Redis & OpenAI
                    response = requests.post(f'{CHAT_BOT_SERVER_URL}/clearCache')
                    response = response.json()
                    
                    if response['status'] == True:
                        print("Threads Flushed Successfully!")
                    else:
                        print(f"Threads Flushing Failed. Please check the server logs for {CHAT_BOT_SERVER_URL}")    
                    
                    return {
                        'statusCode': 200,
                        'body': json.dumps('Assistant Updated Successfully!')
                    }
                else:
                    return {
                        'statusCode': 500,
                        'body': json.dumps('Assistant Files Not Updated Correctly.')
                    }
            else:
                return {
                    'statusCode': 500,
                    'body': json.dumps('Redis (Files) Connection Error.')
                }    
        else:
            return {
                'statusCode': 500,
                'body': json.dumps('OpenAI file Upload Error.')
            }    
    except Exception as exception:
        print(exception)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise exception
