import time
import boto3

# Only for local testing, make sure you comment this for Heroku
# from dotenv import load_dotenv
# load_dotenv()

polly = boto3.client('polly')

def polly_speak(text):
        start_time = time.time()
        audio_response = polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Joanna',      
        )
        audio_data = audio_response['AudioStream'].read()
        end_time = time.time()
        print(f"Polly Conversion: {end_time - start_time} sec")
        return audio_data