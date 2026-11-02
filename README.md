# AjaRemote

Painel desktop para Windows que controla matrizes de vídeo AJA KUMO 64x64 pela rede local.

## Como executar

```bash
pip install -r requirements.txt
python main.py
```

Na primeira abertura, informe o IP da matriz. Ele fica salvo em `config.json`, que não vai para o repositório.

## Testes

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Marcas

Projeto independente, sem vínculo com a AJA Video Systems. AJA e KUMO são marcas
de seus respectivos proprietários e são citadas apenas para indicar compatibilidade.

## Licença

Todos os direitos reservados. Veja [LICENSE](LICENSE).
