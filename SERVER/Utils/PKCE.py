import base64
import hashlib
import json
import os
import string
import random

from DATABASE.redis_client import redis_client as redis
from dotenv import load_dotenv
from fastapi import APIRouter


load_dotenv()

def generate(verifier=None):
    if verifier is None:
        length = random.randint(43, 128)
        chars = string.ascii_letters + string.digits + '-._~'
        verifier = ''.join(random.choice(chars) for _ in range(length))

    code_verifier_bytes = verifier.encode('utf-8')
    code_challenge = hashlib.sha256(code_verifier_bytes).digest()
    challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip('=')
    state = os.urandom(16).hex()

    data = {
        'verifier': verifier,
        'challenge': challenge,
        'state': state
    }

    redis.set(f'pkce:{state}', json.dumps(data))

    return verifier, challenge, state


router = APIRouter(prefix='/pkce')

@router.get("")
async def pkce():
    verifier, challenge, state = generate()
    data = {
        'verifier': verifier,
        'challenge': challenge,
        'state': state,
        'app': os.getenv('VK_APP_ID'),
        'scope': 'phone community market'
    }
    return data





