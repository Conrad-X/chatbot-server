import time
from services.aws.polly import polly_speak

async def process_text_stream_with_polly(client, user_response):
    system_prompt_template = "Given a user query, offer concise information about the user's query. \nIf there is any uncertainty, simply respond with 'Sorry,' and avoid providing unrelated information. \nDo not request additional details or clarifications."

    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        stream=True,
        messages=[
            {"role": "system", "content": system_prompt_template},
            {"role": "user", "content": user_response},
        ]
    )
    end_time = time.time()
    
    print(f"OpenAI Generating Response: {end_time - start_time}s")

    count = 0
    text = ""
    for chunk in response:
        if chunk.choices[0].delta.content != None:
            text += chunk.choices[0].delta.content + " "
            count += 1
            
            # print(chunk.choices[0].delta.content)
            if (text.__contains__('.')):
                print(text)
                yield polly_speak(text)
                count = 0
                text = ""
