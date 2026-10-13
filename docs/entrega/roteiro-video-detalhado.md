# Roteiro detalhado do vídeo — falas por trecho

> Para cada bloco: **🎬 Tela** (o que deixar na tela) e **🎙️ Fala** (o que dizer).
> As falas são sugestões — adaptem o tom, não leiam robotizado. Ensaiem uma vez
> para caber nos 15 min; cada integrante pode narrar um ou dois blocos.
> Deixe a API já rodando e o Swagger aberto antes de começar.

---

## 1. Abertura · 0:00–1:00

**🎬 Tela:** câmera/slide com os nomes, ou a página do repositório no GitHub.

**🎙️ Fala:**
> "Olá! Somos o grupo [número] da pós de Arquitetura de Software da FIAP.
> Integrantes: [nomes e RMs]. Nosso Tech Challenge é o MVP do back-end de uma
> oficina mecânica — um Sistema Integrado de Atendimento e Execução de Serviços.
> O problema que resolvemos: hoje a oficina controla tudo em planilha e anotação
> manual, o que gera erros de priorização, perda de histórico de clientes e
> veículos, e descontrole de peças. Nossa solução centraliza as ordens de
> serviço, os clientes e as peças, com acompanhamento do andamento em tempo real."

## 2. Arquitetura · 1:00–2:30

**🎬 Tela:** VSCode com a árvore de pastas `app/` aberta (domain, application, infrastructure, interfaces). Abra rapidamente `app/domain/ordem_servico.py`.

**🎙️ Fala:**
> "Aplicamos Domain-Driven Design com arquitetura em camadas, num monolito.
> Dentro de `app` temos quatro camadas: **domain**, o coração, com as entidades,
> objetos de valor, agregados e as regras de negócio; **application**, os casos de
> uso que orquestram o fluxo; **infrastructure**, os detalhes técnicos — banco,
> repositórios e autenticação; e **interfaces**, a borda HTTP com as rotas REST.
> A regra de ouro é que a dependência aponta sempre para dentro, para o domínio.
> Repare que o agregado OrdemServico, aqui no domínio, não importa FastAPI nem
> SQLAlchemy — é Python puro. Isso mantém a regra de negócio isolada da
> tecnologia e fácil de testar."

## 3. Banco de dados · 2:30–3:30

**🎬 Tela:** `docs/adr/0001-escolha-do-banco-de-dados.md`.

**🎙️ Fala:**
> "Escolhemos o SQLite e registramos essa decisão num ADR, um Architecture
> Decision Record. A justificativa: é zero-configuração, um arquivo único, sobe o
> ambiente inteiro com um comando, é suficiente para o volume do MVP e ótimo para
> rodar os testes. E, como o acesso a dados passa por uma porta de repositório
> definida no domínio, trocar para PostgreSQL no futuro é só mudar a variável de
> ambiente e a implementação na infraestrutura — sem tocar no domínio nem nos
> casos de uso. Essa é a vantagem concreta da arquitetura em camadas."

## 4. Event Storming + DDD · 3:30–5:00

**🎬 Tela:** o board do Event Storming no Miro. Se der, abra `app/domain/value_objects/` para amarrar com o código.

**🎙️ Fala:**
> "Modelamos o domínio com Event Storming. Partimos dos **eventos**, em laranja,
> sempre escritos no passado, como 'OS aberta' e 'Orçamento aprovado'. Os
> **comandos**, em azul, no imperativo, são o que gera cada evento. As
> **políticas**, em roxo, são automações do negócio — por exemplo, 'quando o
> orçamento é aprovado, baixar o estoque das peças'. A partir disso extraímos os
> **agregados**: a OrdemServico é a raiz, e os **objetos de valor** CpfCnpj, Placa
> e Dinheiro garantem que o dado nasce sempre válido. Identificamos três
> **bounded contexts**: Atendimento, Cadastros e Estoque. O evento 'Orçamento
> aprovado' é pivotal: marca a virada da negociação para a execução. Tudo isso
> está refletido no código, no pacote domain."

## 5. Demonstração funcional (Swagger) · 5:00–9:30

**🎬 Tela:** Swagger em `http://localhost:8000/docs`.

**🎙️ Fala (vá executando enquanto narra):**
> "Agora a demonstração. Primeiro a **autenticação**: as rotas administrativas são
> protegidas por JWT. Clico em **Authorize**, faço login com o usuário de
> demonstração admin / admin123.
>
> Começo pelos **cadastros**: crio um **cliente** — e repare que o sistema valida
> o CPF; um **veículo** com placa, marca, modelo e ano; um **serviço**; e uma
> **peça** já com estoque inicial.
>
> Agora **abro a Ordem de Serviço**, referenciando o cliente e o veículo pelos
> ids que acabei de cadastrar. A OS nasce no status **Recebida**.
>
> **Incluo o serviço e a peça** na OS, informando os ids do catálogo — e o
> **orçamento é calculado automaticamente**, somando a mão de obra e as peças.
>
> Agora o **fluxo de status**: inicio o diagnóstico, envio para aprovação e
> aprovo. Repare que, **ao aprovar, o estoque da peça baixou automaticamente** —
> e, se faltasse saldo, a aprovação seria recusada sem alterar nada. Concluo a
> execução e entrego.
>
> A **consulta de andamento é pública**: o cliente acompanha a OS sem precisar de
> token. E temos também o **relatório de tempo médio de execução**.
>
> Por fim, uma prova das **regras de negócio**: se eu tentar pular uma etapa,
> aprovando uma OS recém-criada, o sistema recusa com 400 e a mensagem de
> transição inválida — porque a regra vive no domínio."

## 6. Execução e segurança · 9:30–10:30

**🎬 Tela:** terminal + Swagger.

**🎙️ Fala:**
> "A aplicação sobe com um comando: localmente com `uvicorn`, ou tudo
> containerizado com `docker compose up`, usando o Dockerfile e o
> docker-compose que entregamos. A documentação da API é o próprio Swagger,
> gerado automaticamente pelo FastAPI. E, reforçando a segurança: se eu chamar
> uma rota administrativa **sem token**, recebo **401 Unauthorized**."

## 7. Testes automatizados · 10:30–12:30

**🎬 Tela:** terminal rodando `pytest`; depois `docs/qualidade/cobertura.md`.

**🎙️ Fala:**
> "Rodo a suíte de testes: **78 testes passando, com 94% de cobertura**, bem acima
> dos 80% exigidos. Temos testes **unitários** do domínio — validações de CPF e
> placa, a máquina de status, o cálculo de orçamento — e testes de **integração**
> que sobem a API e exercitam os endpoints de ponta a ponta, incluindo o fluxo
> completo da OS e a baixa de estoque na aprovação. A evidência fica no relatório
> de cobertura no repositório."

## 8. Análise de vulnerabilidade · 12:30–13:30

**🎬 Tela:** `docs/qualidade/relatorio-seguranca.md`.

**🎙️ Fala:**
> "Para a segurança, rodamos duas ferramentas: o **bandit**, análise estática do
> código, que não apontou nenhum problema; e o **pip-audit**, que verifica
> vulnerabilidades conhecidas nas dependências, também sem apontamentos. Inclusive
> trocamos a biblioteca de JWT de python-jose para **PyJWT**, porque a primeira
> arrastava uma dependência vulnerável sem correção disponível. O relatório
> completo está versionado no repositório."

## 9. Fechamento · 13:30–15:00

**🎬 Tela:** o repositório no GitHub (mostrar a main protegida e os PRs).

**🎙️ Fala:**
> "Encerrando: entregamos um monolito em camadas com DDD, o banco justificado por
> ADR, uma API REST documentada no Swagger, autenticação JWT, testes com 94% de
> cobertura e análise de segurança limpa, tudo containerizado com Docker. No
> GitHub, a branch main é protegida e todo o código entrou por Pull Request.
> Esse foi o nosso Tech Challenge da Fase 1. Obrigado!"

---

## Checklist antes de gravar
- [ ] API rodando e Swagger aberto; login (Authorize) testado.
- [ ] Board do Miro aberto numa aba.
- [ ] Terminal pronto para rodar `pytest`.
- [ ] Microfone testado (áudio compreensível é requisito).
- [ ] Gravar **depois** de fixar o commit da entrega (o vídeo deve corresponder a ele).
- [ ] Publicar no YouTube como **público** e conferir numa aba anônima.
