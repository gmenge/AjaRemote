import json
import os
import requests

DEFAULT_IP = "192.168.1.100"
CONFIG_FILE = "config.json"


class ConfigManager:

    @staticmethod
    def carregar_ip():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    dados = json.load(f)
                    return dados.get("ip_matriz", None)
            except Exception:
                return None
        return None

    @staticmethod
    def salvar_ip(ip):
        try:
            dados = {}
            if os.path.exists(CONFIG_FILE):
                try:
                    with open(CONFIG_FILE, "r") as f:
                        dados = json.load(f)
                except Exception:
                    dados = {}
            dados["ip_matriz"] = ip
            with open(CONFIG_FILE, "w") as f:
                json.dump(dados, f, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar IP: {e}")
            return False


class KumoController:

    @staticmethod
    def comutar_destino(ip_matriz: str, destino: int, origem: int):
        """Comuta uma origem para um destino na matriz AJA KUMO via HTTP REST API."""
        url = f"http://{ip_matriz}/options"
        payload = {
            "paramName": f"eParamID_XKEY_Destination{destino}Source",
            "newValue": str(origem),
        }
        try:
            response = requests.post(url, json=payload, timeout=3)
            if response.status_code == 200:
                return True, "Comutação realizada com sucesso."
            else:
                return False, f"Status: {response.status_code}"
        except Exception as e:
            return False, f"Erro: {str(e)}"

    @staticmethod
    def obter_estado_matriz(ip_matriz: str):
        """Lê o estado atual de todas as 64 saídas/destinos da matriz."""
        url = f"http://{ip_matriz}/options"
        estado = {}
        try:
            response = requests.get(url, timeout=4)
            if response.status_code == 200:
                dados = response.json()
                for item in dados:
                    param = item.get("paramName", "")
                    if param.startswith(
                        "eParamID_XKEY_Destination"
                    ) and param.endswith("Source"):
                        try:
                            dest_num = int(
                                param.replace(
                                    "eParamID_XKEY_Destination", ""
                                ).replace("Source", "")
                            )
                            orig_num = int(item.get("value", 0))
                            estado[dest_num] = orig_num
                        except ValueError:
                            continue
                return True, estado
            return False, f"Status: {response.status_code}"
        except Exception as e:
            return False, str(e)