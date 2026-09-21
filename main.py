import backend
import frontend


def main():
    # Tenta carregar o IP via backend
    ip_configurado = backend.ConfigManager.carregar_ip()

    # Se não houver IP salvo, solicita a captura ao frontend
    if not ip_configurado:
        ip_configurado = frontend.solicitar_ip_inicial()
        if ip_configurado:
            backend.ConfigManager.salvar_ip(ip_configurado)

    # Inicia a aplicação principal se o IP estiver definido
    if ip_configurado:
        app = frontend.GerenciadorEncoders(ip_matriz=ip_configurado)
        app.mainloop()


if __name__ == "__main__":
    main()