import json

import backend


class Resposta:
    def __init__(self, status_code, dados=None):
        self.status_code = status_code
        self._dados = dados

    def json(self):
        return self._dados


def test_salvar_ip_preserva_outras_configuracoes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.json").write_text(json.dumps({"tema": "escuro"}), encoding="utf-8")

    assert backend.ConfigManager.salvar_ip("10.0.0.5")

    assert backend.ConfigManager.carregar_ip() == "10.0.0.5"
    assert json.loads((tmp_path / "config.json").read_text(encoding="utf-8"))["tema"] == "escuro"


def test_sem_arquivo_nao_ha_ip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert backend.ConfigManager.carregar_ip() is None


def test_comutacao_informa_falha_http(monkeypatch):
    monkeypatch.setattr(backend.requests, "post", lambda *a, **k: Resposta(500))

    sucesso, mensagem = backend.KumoController.comutar_destino("10.0.0.5", 1, 2)

    assert not sucesso
    assert "500" in mensagem


def test_le_estado_da_matriz(monkeypatch):
    dados = [
        {"paramName": "eParamID_XKEY_Destination3Source", "value": "7"},
        {"paramName": "outro_parametro", "value": "1"},
    ]
    monkeypatch.setattr(backend.requests, "get", lambda *a, **k: Resposta(200, dados))

    assert backend.KumoController.obter_estado_matriz("10.0.0.5") == (True, {3: 7})
