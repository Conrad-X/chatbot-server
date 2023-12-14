import asyncio
import time
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from amazon_transcribe.utils import apply_realtime_delay

# Sample Rate should be same as rate at which we are recording the audio otherwise transcribing won't work
SAMPLE_RATE = 41000
REGION = "us-east-1"

class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream):
        super().__init__(output_stream)        
        self.last_transcript = ""

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                print("IN")
                if result.is_partial == False:
                    self.last_transcript += alt.transcript + ' '

    def get_last_transcript(self):
        return self.last_transcript


async def basic_transcribe(audio_stream):
    # Setup up our client with our chosen AWS region
    client = TranscribeStreamingClient(region=REGION)

    # Start transcription to generate our async stream
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=SAMPLE_RATE,
        media_encoding="pcm",
    )

    async def write_chunks():
        chunk_size_bytes = 31 * 1024
        for i in range(0, len(audio_stream), chunk_size_bytes):
            chunk = audio_stream[i:i + chunk_size_bytes]
            await stream.input_stream.send_audio_event(audio_chunk=chunk)
        await stream.input_stream.end_stream()

    start_time = time.time()
    print("Transcribing started")
    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(), handler.handle_events())
    end_time = time.time()
    print(f"Transcribing: {end_time - start_time}s")
    print(handler.get_last_transcript())
    return handler.get_last_transcript()

async def transcribe(audio):
    text = await basic_transcribe(audio)
    return text