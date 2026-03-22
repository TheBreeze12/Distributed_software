import os
import redis
from dotenv import load_dotenv

BASE_URL=os.path.dirname(os.path.dirname(__file__))
print(BASE_URL)

load_dotenv(BASE_URL + "\.env")

REDIS_HOST=os.getenv("REDIS_HOST","127.0.0.1")
REDIS_PORT=os.getenv("REDIS_PORT","6379")
REDIS_DB=os.getenv("REDIS_DB","0")

print(REDIS_PORT)
redis_client=redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True)
