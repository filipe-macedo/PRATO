from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/saude", tags=["Saúde"])


@router.get("/", summary="Verifica disponibilidade da API")
def verificar_saude():
    return {
        "status": "operacional",
        "versao": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
