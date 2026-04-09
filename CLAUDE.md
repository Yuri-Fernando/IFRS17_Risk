# CLAUDE.md — Template Universal de Projeto

> **Modo de uso:** Copie este arquivo para qualquer projeto.
> ⚠️ **IMPORTANTE:** Este arquivo AUTOMATICAMENTE carrega todos os arquivos centralizados.
> Não edite este arquivo — ele é um template que aponta para as fontes reais.

---

## 🎯 Identidade do Projeto

**Nome:** [IR17]
**Objetivo:** [PDesenvolver um motor de cálculo do Ajuste ao Risco conforme IFRS 17, integrando modelagem estatística (frequência e severidade), projeção de fluxos atuariais de previdência, simulação Monte Carlo e validação robusta, garantindo interpretabilidade, rastreabilidade e aderência a requisitos de auditoria.]
**Stack:** [Python (NumPy, Pandas, SciPy, Statsmodels), modelagem estatística (GLM, distribuições probabilísticas), simulação Monte Carlo, versionamento com Git, estruturação modular (pipeline orientado a produção), documentação técnica e atuarial.]
**Diretório:** [G:\Outros computadores\Meu computador\Controle Base\Projetos, Robos e Automação\Projetos Git\Projetos Extras (Portfolio)\IR17]

---

## 📚 Capacidades Carregadas (Automático)

✅ **Carrega de:** `G:\Outros computadores\Meu computador\Controle Base\Projetos, Robos e Automação\Claude\`

Este projeto tem acesso **automático** a:

### Skills (1534+)
📄 **Arquivo:** `G:\...\Claude\skills.md`
- Todas as 1534+ skills instaladas
- Ative com `/skill-name` ou mencione no prompt
- Quando nenhuma skill atender → use `/skill-forge` para criar

### Agentes (AIOX + GSD)
👥 **Arquivo:** `G:\...\Claude\agents.md`
- `@dev` `@qa` `@architect` `@pm` `@po` `@sm` `@analyst` `@data-engineer` `@ux-design-expert` `@devops`
- 17 agentes GSD especializados
- Ative com `@agent-name`

### Squads (12 coordenados)
🏢 **Arquivo:** `G:\...\Claude\squad.md`
- advisory-board, brand-squad, c-level-squad, copy-squad, cybersecurity, data-squad, design-squad, hormozi-squad, movement, storytelling, traffic-masters
- Use quando tarefas exigem múltiplos especialistas

### Memória Persistente
💾 **Arquivo:** `G:\...\Claude\memoria.md`
- Arquivo local: `G:\...\Claude\memory\`
- Supabase: tabelas conversas, fatos, perfil_usuario
- MongoDB: database `jarvis`

---

## 🧠 Sistema de Memória Automático

### Diretório Centralizado
```
G:\Outros computadores\Meu computador\Controle Base\Projetos, Robos e Automação\Claude\memory\
```
**Sincronizado entre dispositivos via G: (rede)**

### Arquivos de Memória (Sincronizados)
| Arquivo | Propósito | Sincronização |
|---------|-----------|----------------|
| `memory/user.md` | Perfil e preferências | Local → MongoDB |
| `memory/decisions.md` | Decisões técnicas | Local → MongoDB → Supabase |
| `memory/preferences.md` | Feedback e regras | Local → MongoDB |
| `memory/people.md` | Pessoas e referências | Local → MongoDB |
| `memory/decisions.csv` | Registro formal +30d | Local → MongoDB |

### Protocolo Automático de Memória
```
INÍCIO DA SESSÃO:
1. Leia G:\...\Claude\memory\user.md
2. Leia G:\...\Claude\memory\preferences.md
3. Leia últimas 10 linhas de memory/decisions.md
4. Confirme contexto

DURANTE A SESSÃO:
- Capture decisões em memory/decisions.md
- Atualize preferences.md se feedback recebido

FIM DA SESSÃO:
- Salve novos aprendizados em memory/user.md
- Registre decisões em decisions.csv (data_revisao = hoje + 30 dias)
- Sincronize com MongoDB via script
```

### Bancos de Dados Sincronizados
| Sistema | Status | Função |
|---------|--------|--------|
| **Arquivo Local** | ✅ Primário | Acesso rápido, portável |
| **MongoDB** | ✅ Longo prazo | Persistência cloud, histórico |
| **Supabase** | ✅ Estruturado | Tabelas relacionais, relatórios |

---

## Sistema AIOX (Synkra)

### Ativação de Agentes
Use `@agent-name` para ativar um agente especializado:

```
@dev          → Dex (implementação de código)
@qa           → Quinn (testes e qualidade)
@architect    → Aria (arquitetura e design técnico)
@pm           → Morgan (product management)
@po           → Pax (product owner, stories/epics)
@sm           → River (scrum master)
@analyst      → Alex (pesquisa e análise)
@data-engineer → Dara (banco de dados)
@ux-design-expert → Uma (UX/UI)
@devops       → Gage (CI/CD, git push — EXCLUSIVO)
@aiox-master  → Master (governança do framework)
```

### Comandos de Agentes (prefixo `*`)
```
*help             → Comandos disponíveis
*create-story     → Criar story de desenvolvimento
*task {nome}      → Executar task específica
*exit             → Sair do modo agente
```

---

## Skills Disponíveis

Ative skills com `/skill-name` ou referenciando no prompt. Ver lista completa em `skills.md`.

### Skills de Alta Prioridade para Projetos
```
/deep-research        → Pesquisa profunda sobre qualquer tema
/code-reviewer        → Revisão de código com feedback detalhado
/architect-review     → Revisão de arquitetura do sistema
/security-audit       → Auditoria de segurança
/database-designer    → Design de schema de banco de dados
/api-design           → Design de APIs RESTful/GraphQL
/tdd-guide            → Test-Driven Development
/skill-forge          → CRIAR NOVA SKILL (quando nenhuma existente atende)
/sub-agent-spawner    → CRIAR SUB-AGENTES para tarefas complexas
/agent-coordinator    → COORDENAR agentes e squads disponíveis
```

---

## Workflow de Desenvolvimento (Story-Driven)

### Fluxo Principal
```
@sm *create-story → @po *validate → @dev *develop → @qa *qa-gate → @devops *push
```

### Localização de Stories
```
docs/stories/{epicNum}.{storyNum}.story.md
```

### Regras
1. Todo desenvolvimento parte de uma story
2. Marque checkboxes conforme progresso: `[ ]` → `[x]`
3. Implemente EXATAMENTE o que os critérios de aceitação especificam
4. Execute testes antes de marcar como completo

---

## Padrões de Código

### Linguagens e Ferramentas
- **TypeScript/JavaScript:** Padrões ESM, async/await
- **Python:** 3.10+, type hints, `C:\Users\Yuri_\AppData\Local\Programs\Python\Python310\python.exe`
- **Testes:** Vitest/Jest, cobertura mínima 80%
- **Linting:** `npm run lint` antes de commit

### Commits (Conventional Commits)
```
feat: nova funcionalidade [Story X.Y]
fix: correção de bug [Story X.Y]
docs: documentação
chore: manutenção
refactor: refatoração
test: testes
```

---

## Configuração de Ambiente

### Python (Windows)
```bash
/c/Users/Yuri_/AppData/Local/Programs/Python/Python310/python.exe script.py
/c/Users/Yuri_/AppData/Local/Programs/Python/Python310/Scripts/pip.exe install pacote
```

### Node.js
```bash
npm run dev      # desenvolvimento
npm test         # testes
npm run lint     # linting
npm run build    # build
```

---

## Estrutura de Projeto Recomendada

```
projeto/
├── CLAUDE.md          ← este arquivo (copiado do template)
├── docs/
│   ├── stories/       ← stories de desenvolvimento
│   ├── prd/           ← product requirements
│   └── architecture/  ← decisões arquiteturais
├── src/               ← código fonte
├── tests/             ← testes
└── .claude/           ← configurações locais do projeto
```

---

## Referências Globais

| Arquivo | Localização |
|---------|-------------|
| Template CLAUDE.md | `G:\...\Claude\CLAUDE.md` |
| Lista de Skills | `G:\...\Claude\skills.md` |
| Lista de Agentes | `G:\...\Claude\agents.md` |
| Squads | `G:\...\Claude\squad.md` |
| Memória/Banco | `G:\...\Claude\memoria.md` |
| Skills instaladas | `C:\Users\Yuri_\.claude\skills\` |
| AIOX Core | `C:\Jarvis\aios-core\` |
| Repositórios | `C:\Jarvis\repos\` |

---

## Notas para Claude

- **Responda sempre em português** (exceto termos técnicos e código)
- **Seja conciso e direto** — evite repetições e resumos desnecessários
- **Consulte a memória** no início de cada sessão
- **Grave decisões** importantes imediatamente em `memory/decisions.md`
- **Use skills especializadas** para tarefas específicas
- **Prefira agentes** para tarefas complexas multi-etapas
- **Crie skills novas** com `/skill-forge` quando necessário
- **Delegar subtarefas** com `/sub-agent-spawner` para tarefas complexas

---

*Template v1.0 — Synkra AIOX / Jarvis | Atualizado: 2026-04-02*

---

## 📁 Estrutura de Arquivos Centralizados

| Tipo | Localização | Função |
|------|-------------|--------|
| **CLAUDE.md** | `G:\...\Claude\CLAUDE.md` | Este arquivo (template) |
| **skills.md** | `G:\...\Claude\skills.md` | 1534+ skills listadas |
| **agents.md** | `G:\...\Claude\agents.md` | Todos os agentes e comandos |
| **squad.md** | `G:\...\Claude\squad.md` | 12 squads coordenados |
| **memoria.md** | `G:\...\Claude\memoria.md` | Configuração completa de memória |
| **memory/** | `G:\...\Claude\memory\` | Arquivos de memória (sincronizados) |
| **Skills** | `C:\Users\Yuri_\.claude\skills\` | 1534+ skills instaladas |
| **Repos** | `C:\Jarvis\repos\` | ~35 repositórios clonados |
| **AIOX Core** | `C:\Jarvis\aios-core\` | Framework AIOX/Synkra |

---

## ✨ Novas Skills Criadas

| Skill | Comando | Função |
|-------|---------|--------|
| skill-forge | `/skill-forge` | Criar nova skill via prompt engineering |
| sub-agent-spawner | `/sub-agent-spawner` | Dividir tarefa em sub-agentes paralelos |
| agent-coordinator | `/agent-coordinator` | Delegar automaticamente para melhor agente |

---

## 🚀 Como Usar em Novo Projeto

**Copie este arquivo (CLAUDE.md) para qualquer projeto:**

```bash
cp G:\Outros\ computadores\Meu\ computador\Controle\ Base\Projetos,\ Robos\ e\ Automação\Claude\CLAUDE.md seu-projeto/CLAUDE.md
```

Pronto! Seu novo projeto agora tem:
- ✅ Acesso a todas as 1534+ skills
- ✅ Todos os agentes AIOX disponíveis
- ✅ Memória persistente sincronizada
- ✅ 12 squads coordenados
- ✅ ~35 repositórios clonados como referência

Não precisa configurar mais nada!

---

*CLAUDE.md v2.0 — Template Universal | Atualizado: 2026-04-02*
