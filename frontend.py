import os
import threading
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk

from utils import resource_path, aplicar_icone
from backend import ConfigManager, KumoController, DEFAULT_IP


def solicitar_ip_inicial() -> str:
    win = InitialIPWindow()
    win.mainloop()
    return win.ip_definido


class CustomIPDialog(tk.Toplevel):
    """Pop-up personalizado para alterar IP."""

    def __init__(self, parent, titulo, mensagem, valor_inicial=""):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("420x200")
        self.resizable(False, False)
        self.configure(bg="#1E1E1E")

        aplicar_icone(self)

        self.resultado = None
        self.transient(parent)
        self.grab_set()

        lbl_msg = tk.Label(
            self,
            text=mensagem,
            font=("Arial", 11, "bold"),
            bg="#1E1E1E",
            fg="#00E5FF",
            wraplength=380,
        )
        lbl_msg.pack(pady=(20, 10))

        self.ent_ip = tk.Entry(
            self,
            font=("Arial", 12),
            bg="#2B2B2B",
            fg="#FFFFFF",
            insertbackground="white",
            relief="flat",
            justify="center",
            bd=5,
        )
        self.ent_ip.pack(pady=10, ipadx=10, ipady=3)
        self.ent_ip.insert(0, valor_inicial)
        self.ent_ip.focus_set()
        self.ent_ip.bind("<Return>", lambda e: self.confirmar())

        btn_container = tk.Frame(self, bg="#1E1E1E")
        btn_container.pack(pady=15)

        btn_ok = tk.Button(
            btn_container,
            text="SALVAR",
            font=("Arial", 10, "bold"),
            bg="#00E5FF",
            fg="#000000",
            activebackground="#00B2CC",
            activeforeground="#000000",
            bd=0,
            padx=20,
            pady=5,
            cursor="hand2",
            command=self.confirmar,
        )
        btn_ok.pack(side="left", padx=10)

        btn_cancel = tk.Button(
            btn_container,
            text="CANCELAR",
            font=("Arial", 10, "bold"),
            bg="#444444",
            fg="#FFFFFF",
            activebackground="#555555",
            activeforeground="#FFFFFF",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.destroy,
        )
        btn_cancel.pack(side="left", padx=10)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        self.wait_window()

    def confirmar(self):
        self.resultado = self.ent_ip.get().strip()
        self.destroy()


class InitialIPWindow(tk.Tk):
    """Janela de captura inicial de IP."""

    def __init__(self):
        super().__init__()
        self.title("Configuração Inicial - Aja Remote")
        self.geometry("420x220")
        self.resizable(False, False)
        self.configure(bg="#1E1E1E")

        aplicar_icone(self)
        self.ip_definido = None

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        lbl_msg = tk.Label(
            self,
            text="Digite o IP da Matriz AJA KUMO:",
            font=("Arial", 11, "bold"),
            bg="#1E1E1E",
            fg="#00E5FF",
            wraplength=380,
        )
        lbl_msg.pack(pady=(25, 10))

        self.ent_ip = tk.Entry(
            self,
            font=("Arial", 12),
            bg="#2B2B2B",
            fg="#FFFFFF",
            insertbackground="white",
            relief="flat",
            justify="center",
            bd=5,
        )
        self.ent_ip.pack(pady=10, ipadx=10, ipady=3)
        self.ent_ip.insert(0, DEFAULT_IP)
        self.ent_ip.focus_set()
        self.ent_ip.bind("<Return>", lambda e: self.confirmar())

        btn_ok = tk.Button(
            self,
            text="SALVAR E CONTINUAR",
            font=("Arial", 10, "bold"),
            bg="#00E5FF",
            fg="#000000",
            activebackground="#00B2CC",
            activeforeground="#000000",
            bd=0,
            padx=20,
            pady=6,
            cursor="hand2",
            command=self.confirmar,
        )
        btn_ok.pack(pady=15)

    def confirmar(self):
        valor = self.ent_ip.get().strip()
        if valor:
            self.ip_definido = valor
            self.destroy()


class GerenciadorEncoders(tk.Tk):

    def __init__(self, ip_matriz: str):
        super().__init__()
        self.title("Aja Remote - Painel 64x64")
        self.configure(bg="#1E1E1E")
        self.minsize(1100, 750)

        self.state("zoomed")
        aplicar_icone(self)

        self.ip_matriz = ip_matriz
        self.destino_selecionado = None
        self.matriz_estado = {}

        self.tally_destinos = {}
        self.tally_origens = {}

        self.img_logo = None
        self.carregar_imagens()
        self.criar_interface()
        self.criar_rodape()

        self.carregar_estado_inicial()

    def carregar_imagens(self):
        caminho_logo = resource_path("logo.png")
        if os.path.exists(caminho_logo):
            try:
                img_pil = Image.open(caminho_logo)
                img_pil.thumbnail((250, 50))
                self.img_logo = ImageTk.PhotoImage(img_pil)
            except Exception:
                self.img_logo = None

    def adicionar_log(self, mensagem: str, tipo: str = "INFO"):
        """Adiciona mensagens simplificadas e diretas ao painel de eventos."""

        def _log():
            import datetime

            hora = datetime.datetime.now().strftime("%H:%M:%S")
            tag = tipo.upper()

            self.txt_log.config(state="normal")
            self.txt_log.insert(tk.END, f"[{hora}] ", "TIME")
            self.txt_log.insert(tk.END, f"[{tag}] ", tag)
            self.txt_log.insert(tk.END, f"{mensagem}\n", "TEXTO")
            self.txt_log.see(tk.END)
            self.txt_log.config(state="disabled")

        self.after(0, _log)

    def criar_interface(self):
        # Cabeçalho da Aplicação (Altura fixa para permitir sobreposição perfeita)
        topo_frame = tk.Frame(self, bg="#1E1E1E", height=60)
        topo_frame.pack(fill="x", padx=15, pady=(10, 5))
        topo_frame.pack_propagate(False)  # Mantém a altura fixa

        # 1. Logo perfeitamente centralizada via posicionamento relativo (relx=0.5)
        center_header = tk.Frame(topo_frame, bg="#1E1E1E")
        center_header.place(relx=0.5, rely=0.5, anchor="center")

        if self.img_logo:
            lbl_logo = tk.Label(center_header, image=self.img_logo, bg="#1E1E1E")
            lbl_logo.pack()
        else:
            lbl_logo_txt = tk.Label(
                center_header,
                text="AJA REMOTE",
                font=("Arial", 16, "bold"),
                bg="#1E1E1E",
                fg="#00E5FF",
            )
            lbl_logo_txt.pack()

        # 2. Informações de IP e Botão ancorados estritamente à direita
        right_header = tk.Frame(topo_frame, bg="#1E1E1E")
        right_header.pack(side="right", fill="y")

        self.lbl_ip_info = tk.Label(
            right_header,
            text=f"IP Matriz: {self.ip_matriz}",
            font=("Arial", 10, "bold"),
            bg="#2B2B2B",
            fg="#00E5FF",
            padx=10,
            pady=5,
            bd=1,
            relief="solid",
        )
        self.lbl_ip_info.pack(side="left", padx=(0, 10), pady=12)

        btn_alterar_ip = tk.Button(
            right_header,
            text="⚙️ ALTERAR IP",
            font=("Arial", 9, "bold"),
            bg="#333333",
            fg="#FFFFFF",
            activebackground="#00E5FF",
            activeforeground="#000000",
            bd=0,
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.alterar_ip,
        )
        btn_alterar_ip.pack(side="left", pady=12)

        # Barra de Status de Seleção
        self.lbl_status_selecao = tk.Label(
            self,
            text="Nenhum Destino Selecionado — Selecione um Destino abaixo para operar",
            font=("Arial", 11, "bold"),
            bg="#2B2B2B",
            fg="#FFCC00",
            bd=1,
            relief="solid",
            padx=15,
            pady=5,
        )
        self.lbl_status_selecao.pack(fill="x", padx=15, pady=(5, 5))

        # Painel Central (Matriz de Botões)
        main_frame = tk.Frame(self, bg="#1E1E1E")
        main_frame.pack(expand=True, fill="both", padx=15, pady=0)

        cols = 16

        # Destinos (Saídas) - Tema Grafite Médio (#333333) com Texto Claro (#E0E0E0)
        box_destinos = tk.LabelFrame(
            main_frame,
            text=" 1. SELEÇÃO DE DESTINO (SAÍDAS 1-64) ",
            font=("Arial", 10, "bold"),
            fg="#00E5FF",
            bg="#2B2B2B",
            bd=1,
            relief="solid",
            padx=6,
            pady=6,
        )
        box_destinos.pack(expand=True, fill="both", pady=(0, 4))

        for c in range(cols):
            box_destinos.grid_columnconfigure(c, weight=1)

        for i in range(1, 65):
            r = (i - 1) // cols
            c = (i - 1) % cols
            box_destinos.grid_rowconfigure(r, weight=1)

            tally_frame = tk.Frame(
                box_destinos,
                highlightbackground="#444444",
                highlightthickness=2,
                bg="#2B2B2B",
            )
            tally_frame.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            self.tally_destinos[i] = tally_frame

            btn = tk.Button(
                tally_frame,
                text=f"Destino {i}",
                font=("Arial", 8, "bold"),
                bg="#333333",
                fg="#E0E0E0",
                activebackground="#00E5FF",
                activeforeground="#000000",
                bd=0,
                cursor="hand2",
                command=lambda d=i: self.selecionar_destino(d),
            )
            btn.pack(fill="both", expand=True)

        # Origens (Entradas) - Tema Grafite Escuro (#262626) com Texto Suave (#CCCCCC)
        box_origens = tk.LabelFrame(
            main_frame,
            text=" 2. SELEÇÃO DE ORIGEM (ENTRADAS 1-64) ",
            font=("Arial", 10, "bold"),
            fg="#00E5FF",
            bg="#2B2B2B",
            bd=1,
            relief="solid",
            padx=6,
            pady=6,
        )
        box_origens.pack(expand=True, fill="both", pady=(4, 4))

        for c in range(cols):
            box_origens.grid_columnconfigure(c, weight=1)

        for i in range(1, 65):
            r = (i - 1) // cols
            c = (i - 1) % cols
            box_origens.grid_rowconfigure(r, weight=1)

            tally_frame = tk.Frame(
                box_origens,
                highlightbackground="#444444",
                highlightthickness=2,
                bg="#2B2B2B",
            )
            tally_frame.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            self.tally_origens[i] = tally_frame

            btn = tk.Button(
                tally_frame,
                text=f"Origem {i}",
                font=("Arial", 8, "bold"),
                bg="#262626",
                fg="#CCCCCC",
                activebackground="#00FF66",
                activeforeground="#000000",
                bd=0,
                cursor="hand2",
                command=lambda o=i: self.comutar_origem(o),
            )
            btn.pack(fill="both", expand=True)

        # Painel Inferior de Log Integrado
        box_log = tk.LabelFrame(
            main_frame,
            text=" HISTÓRICO DE AÇÕES ",
            font=("Arial", 9, "bold"),
            fg="#888888",
            bg="#1E1E1E",
            bd=1,
            relief="solid",
        )
        box_log.pack(fill="x", pady=(2, 0))

        self.txt_log = scrolledtext.ScrolledText(
            box_log,
            height=4,
            bg="#121212",
            fg="#FFFFFF",
            font=("Consolas", 9),
            bd=0,
            state="disabled",
        )
        self.txt_log.pack(fill="both", expand=True, padx=4, pady=4)

        self.txt_log.tag_config("TIME", foreground="#666666")
        self.txt_log.tag_config(
            "INFO", foreground="#00E5FF", font=("Consolas", 9, "bold")
        )
        self.txt_log.tag_config(
            "OK", foreground="#00FF66", font=("Consolas", 9, "bold")
        )
        self.txt_log.tag_config(
            "ERRO", foreground="#FF4444", font=("Consolas", 9, "bold")
        )
        self.txt_log.tag_config("TEXTO", foreground="#CCCCCC")

    def criar_rodape(self):
        footer_label = tk.Label(
            self,
            text="Desenvolvido por Gabriel Menge",
            font=("Helvetica", 8),
            bg="#1E1E1E",
            fg="#555555",
        )
        footer_label.pack(side="bottom", fill="x", pady=(2, 2))

    def alterar_ip(self):
        dialog = CustomIPDialog(
            self,
            "Alterar IP da Matriz",
            "Digite o novo IP da Matriz AJA KUMO:",
            self.ip_matriz,
        )
        novo_ip = dialog.resultado
        if novo_ip:
            self.ip_matriz = novo_ip
            if ConfigManager.salvar_ip(self.ip_matriz):
                self.lbl_ip_info.config(text=f"IP Matriz: {self.ip_matriz}")
                self.adicionar_log(f"IP alterado para {self.ip_matriz}", "INFO")
                self.carregar_estado_inicial()
            else:
                self.adicionar_log("Erro ao salvar o novo IP.", "ERRO")

    def carregar_estado_inicial(self):
        self.lbl_status_selecao.config(
            text="Conectando à matriz AJA KUMO...",
            fg="#FFCC00",
        )
        self.adicionar_log(f"Conectando ao IP {self.ip_matriz}...", "INFO")

        def worker():
            sucesso, resultado = KumoController.obter_estado_matriz(self.ip_matriz)
            if sucesso:
                self.matriz_estado = resultado
                self.after(0, self.atualizar_interface_pos_leitura)
            else:
                self.after(
                    0,
                    lambda: self.lbl_status_selecao.config(
                        text="Sem conexão com a matriz — Modo manual ativo",
                        fg="#FF4444",
                    ),
                )
                self.adicionar_log("Falha ao conectar com a matriz.", "ERRO")

        threading.Thread(target=worker, daemon=True).start()

    def atualizar_interface_pos_leitura(self):
        self.lbl_status_selecao.config(
            text="Conectado com sucesso! Selecione um Destino abaixo.",
            fg="#00FF66",
        )
        self.adicionar_log("Matriz conectada e pronta para uso.", "OK")

    def selecionar_destino(self, num_destino: int):
        self.destino_selecionado = num_destino

        for d, frame in self.tally_destinos.items():
            if d == num_destino:
                frame.config(highlightbackground="#00E5FF", highlightthickness=3)
            else:
                frame.config(highlightbackground="#444444", highlightthickness=2)

        origem_atual = self.matriz_estado.get(num_destino, None)

        if origem_atual:
            self.lbl_status_selecao.config(
                text=f"DESTINO {num_destino} SELECIONADO  --->  ORIGEM ATIVA: ORIGEM {origem_atual}",
                fg="#00FF66",
            )
            self.adicionar_log(f"Destino {num_destino} selecionado (Origem atual: {origem_atual})", "INFO")
        else:
            self.lbl_status_selecao.config(
                text=f"DESTINO {num_destino} SELECIONADO",
                fg="#00E5FF",
            )
            self.adicionar_log(f"Destino {num_destino} selecionado", "INFO")

        self.atualizar_tally_origens(origem_atual)

    def comutar_origem(self, num_origem: int):
        if not self.destino_selecionado:
            self.adicionar_log("Selecione um Destino antes de escolher uma Origem.", "ERRO")
            self.lbl_status_selecao.config(
                text="ATENÇÃO: Selecione primeiro um Destino antes de escolher uma Origem!",
                fg="#FF4444",
            )
            return

        dest = self.destino_selecionado
        self.adicionar_log(f"Alterando: Destino {dest} para Origem {num_origem}...", "INFO")

        def worker():
            sucesso, msg = KumoController.comutar_destino(self.ip_matriz, dest, num_origem)

            if sucesso:
                self.matriz_estado[dest] = num_origem
                self.after(0, lambda: self.sucesso_comutacao(dest, num_origem))
            else:
                self.after(0, lambda: self.erro_comutacao(dest, num_origem))

        threading.Thread(target=worker, daemon=True).start()

    def sucesso_comutacao(self, destino: int, origem: int):
        self.lbl_status_selecao.config(
            text=f"COMUTAÇÃO OK: DESTINO {destino}  <===  ORIGEM {origem}",
            fg="#00FF66",
        )
        self.adicionar_log(f"Sucesso: Destino {destino} trocado para Origem {origem}", "OK")
        self.atualizar_tally_origens(origem)

    def erro_comutacao(self, destino: int, origem: int):
        self.lbl_status_selecao.config(
            text=f"FALHA AO ALTERAR DESTINO {destino}",
            fg="#FF4444",
        )
        self.adicionar_log(f"Não foi possível alterar o Destino {destino}", "ERRO")

    def atualizar_tally_origens(self, origem_ativa: int):
        for o, frame in self.tally_origens.items():
            if o == origem_ativa:
                frame.config(highlightbackground="#FF0000", highlightthickness=4)
            else:
                frame.config(highlightbackground="#444444", highlightthickness=2)