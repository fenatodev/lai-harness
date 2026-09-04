# LAI Harness

**Um harness de programação compacto e auditável para LLMs locais.**

Modelos locais pequenos se tornam muito mais úteis quando a arquitetura do agente é otimizada ao redor deles. O LAI Harness é um harness experimental para VS Code, construído para reduzir contexto desnecessário, schemas de ferramentas e rodadas repetidas de inferência.

Ele complementa agentes cloud de alto contexto: o LAI Harness atende ciclos locais rápidos e delimitados; outro agente pode assumir trabalhos amplos usando o handoff persistente.

## Destaques

- ferramentas compactas e específicas por modo;
- inspeção e patch em lote;
- guards de validação e aceitação;
- debug, review e security baseados em evidência;
- sanity check após patches;
- métricas, auditoria forense e contexto por workspace;
- cliente Python sem dependências externas;
- identidade pública padronizada como LAI Harness, mantendo o comando `lai`.

## Início rápido

Você precisa de Python 3.11+, Git, ripgrep, VS Code compatível e um servidor `llama.cpp` autenticado com API OpenAI-compatible.

```bash
git clone https://github.com/fenatodev/lai-local-agent.git
cd lai-local-agent
./scripts/install-local.sh
mkdir -p ~/.config/lai
umask 077
printf '%s' 'substitua-por-uma-chave-local-aleatoria' > ~/.config/lai/llama-api-key
```

Configure `LAI_HOST`, `LAI_PORT` e `LAI_MODEL`, instale a extensão a partir do código e use, por exemplo:

```text
@lai /plan planeje um teste de regressão focado
@lai /debug reproduza e rastreie o valor incorreto
@lai /implement implemente a mudança e valide
@lai /review revise minhas alterações Git atuais
@lai /handoff contexto para continuar no Codex
```

## Segurança

O LAI **não é uma sandbox**. As ferramentas de arquivo ficam confinadas à raiz do repositório e a ferramenta Git dedicada é somente leitura, mas `bash` executa com as permissões do usuário e usa uma denylist incompleta por natureza. Use uma conta de menor privilégio, mantenha backups e revise os diffs.

Chaves, modelos, logs, estados, métricas, auditoria e handoffs reais não devem ser publicados. Leia [SECURITY-MODEL.md](docs/SECURITY-MODEL.md).

## Resultados experimentais

As medições documentadas vieram de uma máquina e fixtures específicas. Elas mostram a evolução do experimento, não prometem desempenho universal. Consulte [BENCHMARKS.md](docs/BENCHMARKS.md).

O código original do LAI usa MIT. VS Code, llama.cpp, modelos, GGUF e templates permanecem sob termos próprios e não são redistribuídos. Consulte [THIRD_PARTY.md](THIRD_PARTY.md).

A documentação técnica principal está em inglês no diretório [`docs/`](docs/).
