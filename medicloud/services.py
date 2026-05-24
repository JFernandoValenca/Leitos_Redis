from datetime import datetime
from redis_client import r

STATUS_VALIDOS = {"Disponivel", "Ocupado", "Manutencao", "Reservado"}


def cadastrar_leito(leito_id: str, tipo: str, status: str) -> None:
    r.hset(f"leito:{leito_id}", mapping={
        "id": leito_id,
        "tipo": tipo,
        "status": status
    })


def atualizar_status_leito(leito_id: str, novo_status: str) -> tuple:
    if novo_status not in STATUS_VALIDOS:
        return False, "Status invalido"
    if not r.exists(f"leito:{leito_id}"):
        return False, "Leito nao encontrado"

    r.hset(f"leito:{leito_id}", "status", novo_status)

    evento = f"{datetime.now().strftime('%d/%m/%Y %H:%M')} -> {novo_status}"
    r.rpush(f"historico:leito:{leito_id}", evento)
    r.ltrim(f"historico:leito:{leito_id}", -10, -1)

    return True, "Atualizado"


def atualizar_paciente(leito_id: str, nome: str, idade: int = None, diagnostico: str = None) -> tuple:
    if not r.exists(f"leito:{leito_id}"):
        return False, "Leito nao encontrado"

    mapping = {"paciente": nome}
    if idade is not None:
        mapping["paciente_idade"] = str(idade)
    if diagnostico:
        mapping["paciente_diagnostico"] = diagnostico

    r.hset(f"leito:{leito_id}", mapping=mapping)
    atualizar_status_leito(leito_id, "Ocupado")
    return True, "Paciente atualizado"


def ver_historico(leito_id: str) -> list:
    return r.lrange(f"historico:leito:{leito_id}", 0, -1)


def obter_leito(leito_id: str) -> dict | None:
    return r.hgetall(f"leito:{leito_id}") or None


def listar_leito(status: str = None) -> list:
    resultado = []
    for key in r.scan_iter("leito:*"):
        leito = r.hgetall(key)
        if status is None or leito.get("status") == status:
            resultado.append(leito)
    return resultado


def obter_stats() -> dict:
    leitos = listar_leito()
    total = len(leitos)
    ocupados = sum(1 for l in leitos if l.get("status") == "Ocupado")
    disponiveis = sum(1 for l in leitos if l.get("status") == "Disponivel")
    manutencao = sum(1 for l in leitos if l.get("status") == "Manutencao")
    reservados = sum(1 for l in leitos if l.get("status") == "Reservado")
    taxa = round((ocupados / total * 100) if total > 0 else 0, 1)
    return {
        "total": total,
        "ocupados": ocupados,
        "disponiveis": disponiveis,
        "manutencao": manutencao,
        "reservados": reservados,
        "taxa_ocupacao": taxa
    }


def deletar_leito(leito_id: str) -> None:
    r.delete(f"leito:{leito_id}")
    r.delete(f"historico:leito:{leito_id}")


def limpar_banco() -> None:
    r.flushdb()
