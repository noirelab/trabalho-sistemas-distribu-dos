# Jogo de Aventura Cooperativo Distribuido

## Descricao

Este projeto implementa um jogo de aventura cooperativo utilizando sistemas distribuidos com a tecnologia Pyro5 (Python Remote Objects). Os jogadores se conectam a um servidor centralizado e tomam decisoes coletivas atraves de um sistema de votacao para progredir na historia.

## Arquitetura

### Servidor (servidor.py)
- Gerencia o estado global do jogo
- Controla conexoes de multiplos clientes simultaneos
- Implementa sistema de votacao cooperativa
- Gerencia chat em tempo real entre jogadores
- Garante thread safety com locks para evitar condicoes de corrida
- Controla inicio automatico da historia com minimo de jogadores
- Bloqueia novas conexoes apos inicio da partida

### Cliente (cliente.py)
- Interface de terminal interativa
- Conexao remota via Pyro5
- Atualizacao automatica da tela do jogo
- Sistema de comandos para votacao
- Chat integrado funcionando em paralelo
- Threading para input nao-bloqueante

### Historia (historia.json)
- Estrutura de dados em formato JSON
- Nos interconectados representando situacoes do jogo
- Opcoes de escolha com destinos especificados
- Multiplos finais possiveis baseados nas decisoes

## Funcionalidades

### Controle de Sessao
- Minimo de 2 jogadores necessarios para iniciar
- Historia inicia APENAS com comando manual do servidor
- Novas conexoes sao bloqueadas apos inicio da partida
- Interface interativa no servidor para controle administrativo

### Sistema de Votacao
- Todos os jogadores conectados devem votar para progredir
- Historia so avanca apos votacao completa
- Contador de votos restantes exibido em tempo real
- Opcao mais votada determina o proximo passo

### Chat Cooperativo
- Comunicacao em tempo real entre jogadores
- Funciona em paralelo ao sistema de votacao
- Historico das ultimas 15 mensagens
- Notificacoes automaticas de eventos do jogo

## Requisitos

### Dependencias
- Python 3.x
- Biblioteca Pyro5

### Instalacao
```bash
pip install Pyro5
```

## Execucao

### 1. Iniciar o Servidor de Nomes Pyro5
```bash
pyro5-ns
```

### 2. Executar o Servidor do Jogo
```bash
python servidor.py
```
O servidor ficara aguardando conexoes e exibira uma interface de comandos.

### 3. Conectar Clientes (minimo 2)
```bash
python cliente.py
```
Cada cliente deve executar em um terminal separado.

### 4. Iniciar a Historia (no servidor)
Quando tiver pelo menos 2 jogadores conectados, no terminal do servidor digite:
```
> iniciar
```

### Comandos do Servidor
- `iniciar` - Inicia a historia (requer minimo 2 jogadores)
- `status` - Mostra status atual dos jogadores
- `sair` - Encerra o servidor

## Fluxo do Jogo

1. Clientes se conectam ao servidor
2. Servidor aguarda minimo de 2 jogadores
3. Administrador executa comando 'iniciar' no servidor
4. Historia comeca e e apresentada a todos os jogadores
5. Jogadores podem conversar no chat durante toda a partida
6. Situacao atual da historia e exibida para todos
7. Jogadores votam nas opcoes disponiveis usando '/votar <numero>'
8. Historia progride APENAS apos todos os jogadores votarem
9. Processo se repete ate um final ser alcancado
10. Novas conexoes sao bloqueadas apos inicio da historia

## Conceitos de Sistemas Distribuidos

### RMI (Remote Method Invocation)
- Comunicacao transparente entre processos distribuidos
- Chamadas de metodos remotos via Pyro5
- Abstraindo complexidade da comunicacao de rede

### Consistencia de Estado
- Estado centralizado no servidor
- Sincronizacao automatica entre todos os clientes
- Garantia de visao consistente do jogo

### Concorrencia e Sincronizacao
- Threading para operacoes nao-bloqueantes
- Locks para proteger recursos compartilhados
- Gerenciamento seguro de multiplas conexoes simultaneas

### Tolerancia a Falhas
- Tratamento de desconexoes de clientes
- Recuperacao graceful de erros de rede
- Validacao de estados antes de operacoes criticas