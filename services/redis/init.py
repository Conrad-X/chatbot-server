import redis

def redis_init(REDIS_ENDPOINT, REDIS_PORT, REDIS_PASSWORD):
    try:
        redis_client = redis.Redis(host=REDIS_ENDPOINT, port=REDIS_PORT, username="default", password=REDIS_PASSWORD, decode_responses=True, db=0)
    except Exception as e:
        print(f"Redis Initialization Error - {e}")

    print("Pinging Redis...")
    if redis_client.ping():
        print("Successfully connected with Redis!")
        return redis_client
    else: 
        return None