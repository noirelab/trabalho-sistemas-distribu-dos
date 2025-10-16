import Pyro5.api
import json
import threading

# Garante que o servidor de nomes do Pyro5 esteja rodando.
# Em um terminal separado, execute: pyro5-ns
# Este comando deve ser executado antes de iniciar o servidor.

@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class JogoAventura:
    def __init__(self):
        # Carrega a estrutura da história a partir do arquivo JSON.
        with open("historia.json", "r", encoding="utf-8") as f:
            self.historia = json.load(f)

        self.posicao_atual = "inicio"
        self.jogadores = {}  # Ex: {"Alice": {"voto": None}, "Bob": {"voto": None}}
        self.mensagens_chat = []
        self.votos_atuais = {} # Ex: {"1": 1, "2": 0}
        self._lock = threading.Lock() # Para evitar condições de corrida
        
        # Novos atributos para controlar o estado do jogo
        self.historia_iniciada = False
        self.aguardando_jogadores = True
        self.minimo_jogadores = 2
        
        print("Servidor do Jogo iniciado.")
        print(f"Aguardando conexões de jogadores (mínimo: {self.minimo_jogadores})")
        print("A história será iniciada APENAS com comando manual do servidor.")

    def conectar(self, nome_jogador):
        with self._lock:
            # Verifica se a história já foi iniciada
            if self.historia_iniciada:
                return "Erro: A história já foi iniciada. Não é possível conectar novos jogadores."
                
            if nome_jogador in self.jogadores:
                return f"Erro: Jogador '{nome_jogador}' já existe."

            self.jogadores[nome_jogador] = {"voto": None}
            mensagem = f"--- {nome_jogador} entrou no jogo! ---"
            self.mensagens_chat.append(mensagem)
            print(mensagem)
            print(f"Jogadores conectados: {len(self.jogadores)} (mínimo: {self.minimo_jogadores})")
            
            if len(self.jogadores) >= self.minimo_jogadores:
                print("*** Mínimo de jogadores atingido! Digite 'iniciar' para começar a história ***")
            
            return f"Bem-vindo, {nome_jogador}!"

    def desconectar(self, nome_jogador):
        with self._lock:
            if nome_jogador in self.jogadores:
                del self.jogadores[nome_jogador]
                mensagem = f"--- {nome_jogador} saiu do jogo. ---"
                self.mensagens_chat.append(mensagem)
                print(mensagem)
                self._verificar_votos() # Re-avalia o estado de votação se alguém sair
                return True
        return False

    def get_estado_jogo(self):
        # Este método é o que os clientes chamarão em loop para atualizar suas telas.
        with self._lock:
            if not self.historia_iniciada:
                # Se ainda não iniciou, mostra sala de espera
                return {
                    "texto": f"Sala de espera... ({len(self.jogadores)}/{self.minimo_jogadores} jogadores mínimos)",
                    "opcoes": {},
                    "chat": self.mensagens_chat[-15:],
                    "jogadores": list(self.jogadores.keys()),
                    "aguardando": True
                }
            
            nodo_historia = self.historia[self.posicao_atual]
            return {
                "texto": nodo_historia["texto"],
                "opcoes": nodo_historia["opcoes"],
                "chat": self.mensagens_chat[-15:],  # Retorna apenas as últimas 15 mensagens
                "jogadores": list(self.jogadores.keys()),
                "aguardando": False
            }

    def enviar_mensagem_chat(self, nome_jogador, texto_mensagem):
        with self._lock:
            if nome_jogador in self.jogadores:
                mensagem = f"[{nome_jogador}]: {texto_mensagem}"
                self.mensagens_chat.append(mensagem)
                return True
        return False

    def votar(self, nome_jogador, id_opcao):
        with self._lock:
            if not self.historia_iniciada:
                return "A história ainda não foi iniciada. Aguarde..."
                
            if nome_jogador not in self.jogadores:
                return "Você não está conectado."

            # Verifica se a opção de voto é válida para a posição atual
            nodo_historia = self.historia[self.posicao_atual]
            if id_opcao not in nodo_historia["opcoes"]:
                return "Opção de voto inválida."

            if self.jogadores[nome_jogador]["voto"] is not None:
                return "Você já votou."

            self.jogadores[nome_jogador]["voto"] = id_opcao
            self.votos_atuais[id_opcao] = self.votos_atuais.get(id_opcao, 0) + 1
            
            votos_restantes = len(self.jogadores) - sum(1 for j in self.jogadores.values() if j["voto"] is not None)
            self.mensagens_chat.append(f"--- {nome_jogador} votou. Aguardando {votos_restantes} voto(s). ---")

            self._verificar_votos()
            return "Voto registrado."

    def _verificar_votos(self):
        # Função interna para processar o resultado quando todos votaram
        total_jogadores = len(self.jogadores)
        total_votos = sum(1 for jogador in self.jogadores.values() if jogador["voto"] is not None)

        if total_jogadores > 0 and total_votos == total_jogadores:
            if not self.votos_atuais: # Se não houver votos (ex: último jogador saiu)
                return

            # Determina a opção mais votada
            opcao_vencedora = max(self.votos_atuais, key=self.votos_atuais.get)

            # Avança na história
            nodo_atual = self.historia[self.posicao_atual]
            self.posicao_atual = nodo_atual["opcoes"][opcao_vencedora]["destino"]

            # Reseta os votos para a próxima decisão
            self.mensagens_chat.append(f"--- Votação encerrada! O grupo escolheu: '{nodo_atual['opcoes'][opcao_vencedora]['texto']}' ---")
            self.votos_atuais.clear()
            for jogador in self.jogadores.values():
                jogador["voto"] = None

    def _verificar_inicio_historia(self):
        # Método removido - agora é apenas manual
        pass

    def iniciar_historia_manualmente(self):
        # Método para o administrador iniciar manualmente
        with self._lock:
            if len(self.jogadores) < self.minimo_jogadores:
                print(f"ERRO: Mínimo de {self.minimo_jogadores} jogadores necessário. Conectados: {len(self.jogadores)}")
                return f"Erro: Mínimo de {self.minimo_jogadores} jogadores necessário."
            
            if self.historia_iniciada:
                print("ERRO: História já foi iniciada.")
                return "Erro: História já foi iniciada."
            
            self.historia_iniciada = True
            self.aguardando_jogadores = False
            mensagem = "--- História iniciada pelo servidor! A aventura começa agora! ---"
            self.mensagens_chat.append(mensagem)
            print(f"*** HISTÓRIA INICIADA! {len(self.jogadores)} jogadores participando ***")
            return "História iniciada com sucesso."


def main():
    # Configuração do servidor Pyro5
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns() # Encontra o servidor de nomes
    
    jogo = JogoAventura()
    uri = daemon.register(jogo)
    ns.register("aventura.jogo", uri) # Registra o objeto com um nome lógico

    print("Servidor pronto. Aguardando conexões.")
    print("Comandos disponíveis:")
    print("  'iniciar' - Inicia a história (mínimo 2 jogadores)")
    print("  'status' - Mostra status atual")
    print("  'sair' - Encerra o servidor")
    
    # Thread para aceitar comandos do administrador
    def comandos_admin():
        while True:
            try:
                comando = input("> ").strip().lower()
                if comando == "iniciar":
                    resultado = jogo.iniciar_historia_manualmente()
                    if "sucesso" in resultado:
                        print("Comando executado com sucesso!")
                elif comando == "status":
                    with jogo._lock:
                        print(f"Jogadores conectados: {len(jogo.jogadores)}")
                        print(f"Jogadores: {list(jogo.jogadores.keys())}")
                        print(f"História iniciada: {'Sim' if jogo.historia_iniciada else 'Não'}")
                elif comando == "sair":
                    print("Encerrando servidor...")
                    daemon.shutdown()
                    break
                else:
                    print("Comando inválido. Use: iniciar, status, ou sair")
            except (KeyboardInterrupt, EOFError):
                print("\nEncerrando servidor...")
                daemon.shutdown()
                break
    
    thread_admin = threading.Thread(target=comandos_admin, daemon=True)
    thread_admin.start()
    
    try:
        daemon.requestLoop() # Inicia o loop do servidor
    except KeyboardInterrupt:
        print("\nServidor encerrado.")

if __name__ == "__main__":
    main()
