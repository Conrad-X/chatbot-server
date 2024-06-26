def run_thread(client, thread_id, assistant_id):
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id, assistant_id=assistant_id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id))
    message_content = messages[0].content[0].text
    print(f"Assistant Response - {message_content.value}")
    return { "message": message_content.value, "run_id": run.id }

def create_message(client, prompt, thread_id):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt,
    )
    return message

def retrieve_run_instances(client, thread_id, run_id):
    run_list = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    ) 
    return run_list.status

def retrieve_message_list(client, thread_id):
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    return messages.data

def create_thread(client):
    thread = client.beta.threads.create()
    return thread.id

def delete_threads(client, thread_id):
    response = client.beta.threads.delete(thread_id)
    return response["deleted"]
