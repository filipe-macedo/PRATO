from pydantic_settings import BaseSettings


class Configuracoes(BaseSettings):
    database_url: str = "sqlite:///./prato.db"
    caminho_modelo: str = "models/modelo_final.pkl"
    debug: bool = True
    allowed_origins: str = "http://localhost:8501"

    @property
    def origens_permitidas(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


configuracoes = Configuracoes()
