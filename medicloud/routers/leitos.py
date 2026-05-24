from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services import (
    cadastrar_leito, atualizar_status_leito, ver_historico,
    obter_leito, listar_leito, deletar_leito, limpar_banco,
    atualizar_paciente, obter_stats
)

router = APIRouter(prefix="/leitos", tags=["leitos"])


class LeitoCreate(BaseModel):
    tipo: str
    status: str = "Disponivel"


class StatusUpdate(BaseModel):
    status: str


class PacienteUpdate(BaseModel):
    nome: str
    idade: Optional[int] = None
    diagnostico: Optional[str] = None


@router.get("/")
def listar(status: Optional[str] = None, tipo: Optional[str] = None):
    leitos = listar_leito(status=status)
    if tipo:
        leitos = [l for l in leitos if l.get("tipo") == tipo]
    # Ordenar por id numérico
    leitos.sort(key=lambda x: x.get("id", ""))
    return leitos


@router.get("/stats")
def stats():
    return obter_stats()


@router.post("/{leito_id}")
def criar(leito_id: str, body: LeitoCreate):
    cadastrar_leito(leito_id, body.tipo, body.status)
    return {"ok": True, "leito_id": leito_id}


@router.get("/{leito_id}")
def obter(leito_id: str):
    leito = obter_leito(leito_id)
    if not leito:
        raise HTTPException(status_code=404, detail="Leito não encontrado")
    return leito


@router.patch("/{leito_id}/status")
def atualizar_status(leito_id: str, body: StatusUpdate):
    ok, msg = atualizar_status_leito(leito_id, body.status)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"ok": True, "mensagem": msg}


@router.patch("/{leito_id}/paciente")
def atualizar_pac(leito_id: str, body: PacienteUpdate):
    ok, msg = atualizar_paciente(leito_id, body.nome, body.idade, body.diagnostico)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"ok": True}


@router.delete("/{leito_id}/paciente")
def remover_paciente(leito_id: str):
    from redis_client import r
    if not r.exists(f"leito:{leito_id}"):
        raise HTTPException(status_code=404, detail="Leito não encontrado")
    r.hdel(f"leito:{leito_id}", "paciente", "paciente_idade", "paciente_diagnostico")
    atualizar_status_leito(leito_id, "Disponivel")
    return {"ok": True}


@router.get("/{leito_id}/historico")
def historico(leito_id: str):
    return {"historico": ver_historico(leito_id)}


@router.delete("/{leito_id}")
def deletar(leito_id: str):
    deletar_leito(leito_id)
    return {"ok": True}
