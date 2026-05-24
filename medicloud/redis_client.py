import os  
import redis

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    print("ERRO: Variável REDIS_URL não encontrada!")
    REDIS_URL = "redis://localhost:6379"

r = redis.from_url(REDIS_URL, decode_responses=True)

try:
    r.ping()
    print("Redis conectado com sucesso!")
except Exception as e:
    print(f"Redis não disponível. Erro: {e}")

