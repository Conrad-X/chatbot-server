from pydub.playback import play
import time
import boto3
from pydub import AudioSegment
import io

polly = boto3.client('polly')

def polly_speak(text):
        start_time_1 = time.time()
        audio_response = polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Joanna',
                
        )
        audio_data = audio_response['AudioStream'].read()
        end_time_1 = time.time()
        print(f"Polly Conversion: {end_time_1 - start_time_1}s")
        return audio_data