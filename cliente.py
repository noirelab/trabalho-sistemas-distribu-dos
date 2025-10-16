# cliente.py (CORRIGIDO)
import Pyro5.api
import time
import os
import threading

# Uma variável global para sinalizar quando o jogo terminar
jogo_rodando = True

def limpar_tela():
    """Limpa o terminal para manter a exibição organizada."""
    os.system('cls' if os.name == 'nt' else 'clear')

def funcao_de_input(nome_jogador): # <-- MUDANÇA: Não recebe mais o jogo_remoto
    """Função que roda em uma thread separada para capturar o input do usuário."""
    global jogo_rodando

    # MUDANÇA: Cria um novo proxy ESPECIFICAMENTE para esta thread.
    jogo_remoto_thread = Pyro5.api.Proxy("PYRONAME:aventura.jogo")

    print("Digite suas mensagens no chat ou use '/votar <numero>' para votar.")
    print("Exemplo de voto: /votar 1")

    while jogo_rodando:
        try:
            texto = input()
            if not jogo_rodando:
                break

            if texto.startswith("/votar"):
                try:
                    _, id_opcao = texto.split()
                    # MUDANÇA: Usa o proxy desta thread
                    resposta = jogo_remoto_thread.votar(nome_jogador, id_opcao)
                    print(f"-> Servidor: {resposta}")
                except ValueError:
                    print("-> Comando de voto inválido. Use: /votar <numero>")
            else:
                # MUDANÇA: Usa o proxy desta thread
                jogo_remoto_thread.enviar_mensagem_chat(nome_jogador, texto)

        except (EOFError, KeyboardInterrupt):
            print("-> Desconectando...")
            jogo_rodando = False
            break

def main():
    global jogo_rodando

    try:
        # A thread principal ainda cria seu próprio proxy para exibir o jogo
        jogo_remoto = Pyro5.api.Proxy("PYRONAME:aventura.jogo")
    except Pyro5.errors.NamingError:
        print("Erro: Não foi possível encontrar o servidor do jogo. O servidor está rodando?")
        return

    nome_jogador = input("Digite seu nome de jogador: ")
    try:
        resposta_conexao = jogo_remoto.conectar(nome_jogador)
        print(resposta_conexao)
        if "Erro" in resposta_conexao:
            return
    except Exception as e:
        print(f"Não foi possível conectar ao servidor: {e}")
        return

    # MUDANÇA: Não passamos mais o 'jogo_remoto' para a thread.
    thread_input = threading.Thread(target=funcao_de_input, args=(nome_jogador,), daemon=True)
    thread_input.start()

    # Loop principal para atualizar a tela do jogo (usa o proxy da thread principal)
    ultimo_estado = {}
    try:
        while jogo_rodando:
            estado_atual = jogo_remoto.get_estado_jogo()

            if estado_atual != ultimo_estado:
                limpar_tela()
                print("================ Aventura Cooperativa ================\n")
                print("\n" + estado_atual["texto"] + "\n")

                opcoes = estado_atual.get("opcoes", {})
                aguardando = estado_atual.get("aguardando", False)
                
                if aguardando:
                    print("--- Aguardando início da história ---")
                    print("O jogo iniciará automaticamente quando houver jogadores suficientes.")
                elif opcoes:
                    print("--- Opções de Voto ---")
                    for id_opcao, detalhes in opcoes.items():
                        print(f"[{id_opcao}]: {detalhes['texto']}")
                    print("\nUse o comando '/votar <numero>' para votar.")
                else:
                    print("--- Fim da Aventura ---")
                    jogo_rodando = False

                print("\n--- Chat ---")
                for msg in estado_atual["chat"]:
                    print(msg)

                print("\n--------------------")
                print(f"Jogadores conectados: {', '.join(estado_atual['jogadores'])}")
                
                if not aguardando:
                    print("Digite sua mensagem ou comando de voto abaixo:")
                else:
                    print("Digite suas mensagens no chat enquanto aguarda:")

                ultimo_estado = estado_atual

            time.sleep(1)
    except Pyro5.errors.ConnectionClosedError:
        print("Conexão com o servidor foi perdida.")
    finally:
        jogo_rodando = False
        print("Saindo do jogo...")
        # Usamos o proxy da thread principal para desconectar
        jogo_remoto.desconectar(nome_jogador)

if __name__ == "__main__":
    main()
