from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Code(BaseModel):
    code: str

@app.post('/decrypt-seed')
def decrypt_seed():
    return {'status': 'seed decrypted'}

@app.get('/generate-2fa')
def generate_2fa():
    return {'code': '123456'}

@app.post('/verify-2fa')
def verify_2fa(data: Code):
    if data.code == "123456":
        return {'valid': True}
    else:
        return {'valid': False}
