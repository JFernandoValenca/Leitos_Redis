from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import leitos
from redis_client import r

LEITOS_PADRAO = [
    ("101", "UTI"),       ("102", "UTI"),       ("103", "UTI"),
    ("104", "UTI"),       ("105", "UTI"),       ("106", "UTI"),
    ("107", "UTI"),       ("108", "UTI"),       ("109", "UTI"),
    ("110", "UTI"),
    ("201", "Enfermaria"), ("202", "Enfermaria"), ("203", "Enfermaria"),
    ("204", "Enfermaria"), ("205", "Enfermaria"), ("206", "Enfermaria"),
    ("207", "Enfermaria"), ("208", "Enfermaria"), ("209", "Enfermaria"),
    ("210", "Enfermaria"),
    ("301", "Emergencia"), ("302", "Emergencia"), ("303", "Emergencia"),
    ("304", "Emergencia"), ("305", "Emergencia"),
    ("401", "Pediatria"),  ("402", "Pediatria"),  ("403", "Pediatria"),
    ("404", "Pediatria"),  ("405", "Pediatria"),
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    cadastrados = 0
    for leito_id, tipo in LEITOS_PADRAO:
        chave = f"leito:{leito_id}"
        if not r.exists(chave):
            r.hset(chave, mapping={"id": leito_id, "tipo": tipo, "status": "Disponivel"})
            cadastrados += 1
    if cadastrados > 0:
        print(f" {cadastrados} leito(s) cadastrado(s) no Banco de dados")
    else:
        print("Leitos ja existem no Redis — nenhuma alteracao feita")
    yield
    print("Servidor encerrado")

app = FastAPI(title="Medi CLOUD", version="2.0.0", lifespan=lifespan)
app.include_router(leitos.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")
