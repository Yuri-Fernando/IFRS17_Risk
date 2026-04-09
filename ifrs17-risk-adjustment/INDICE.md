# 📚 ÍNDICE COMPLETO - Projeto IFRS 17

## 🎯 Para Começar AGORA

1. **[GUIA_EXECUCAO.md](GUIA_EXECUCAO.md)** ← LEIA ISTO PRIMEIRO
   - 3 passos para rodar o projeto
   - Instruções completas e detalhadas
   - Troubleshooting

2. **[QUICKSTART.md](QUICKSTART.md)** ← Se preferir resumido
   - Versão rápida do guia de execução

3. **[setup_environment.py](setup_environment.py)** ← Execute isto
   ```bash
   python setup_environment.py
   ```

4. **[notebooks/main.ipynb](notebooks/main.ipynb)** ← Abra depois
   ```bash
   jupyter notebook notebooks/main.ipynb
   ```

---

## 📖 Documentação Essencial

### Para Entender o Projeto

| Arquivo | Leia Quando | Objetivo |
|---------|-----------|----------|
| [README.md](README.md) | Sempre | Visão geral |
| [CHECKLIST_PROJETO.md](CHECKLIST_PROJETO.md) | Verificar Status | Tudo que foi implementado |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Contexto | Resumo executivo |

### Para Entender a Modelagem

| Arquivo | Para Quem | Objetivo |
|---------|----------|----------|
| [docs/business_explanation.md](docs/business_explanation.md) | Não-técnicos | O que o modelo faz (linguagem simples) |
| [docs/glossary.md](docs/glossary.md) | Todos | 80+ termos técnicos explicados |
| [reports/methodology.md](reports/methodology.md) | Técnicos | Como o modelo funciona (8K palavras) |
| [reports/assumptions.md](reports/assumptions.md) | Auditores | Todas as hipóteses do modelo |

### Para Conformidade

| Arquivo | Para Quem | Objetivo |
|---------|----------|----------|
| [reports/ifrs17_alignment.md](reports/ifrs17_alignment.md) | Compliance | Conformidade com IFRS 17 |
| [reports/validation_report.md](reports/validation_report.md) | Auditores | Protocolo completo de validação |
| [reports/model_comparison.md](reports/model_comparison.md) | Especialistas | Comparação VaR vs CTE vs CoC |

### Para Arquitetura

| Arquivo | Para Quem | Objetivo |
|---------|----------|----------|
| [docs/architecture_diagram.md](docs/architecture_diagram.md) | Arquitetos | Diagramas do sistema |
| [src/cloud/aws_architecture.md](src/cloud/aws_architecture.md) | DevOps | Arquitetura AWS proposta |

---

## 💻 Código Fonte (src/)

### Estrutura Modular

```
src/
├── data/               (Carregamento e preprocessamento)
├── actuarial/          (BEL, projeção, lapse, mortalidade)
├── modeling/           (Frequência, severidade, RA)
├── simulation/         (Monte Carlo)
├── validation/         (Testes estatísticos)
├── governance/         (Auditoria, versionamento)
└── cloud/              (Pipeline, AWS)
```

---

## 📓 Notebooks

| Arquivo | Objetivo | Quando Usar |
|---------|----------|-----------|
| [notebooks/main.ipynb](notebooks/main.ipynb) | **Pipeline completo 10 etapas** | Execute isto sempre |
| [notebooks/00_quickstart.py](notebooks/00_quickstart.py) | Validação rápida | Se tiver dúvida no setup |

---

## 📈 Relatórios Finais (Pós-Execução)

Estes arquivos são **gerados** após rodar o notebook:

| Arquivo | Contém | Criado Por |
|---------|--------|-----------|
| [reports/result_final.json](reports/result_final.json) | Dados estruturados (BEL, RA, Provisão) | `notebooks/main.ipynb` |
| [reports/audit_trail.md](reports/audit_trail.md) | Log de auditoria | Automático |
| [CHECKLIST_PROJETO.md](CHECKLIST_PROJETO.md) | Verificação de funcionalidades | Verificação manual |

---

## 🚀 Scripts de Execução

| Script | Uso | Comando |
|--------|-----|---------|
| [setup_environment.py](setup_environment.py) | Setup automático (EXECUTE PRIMEIRO) | `python setup_environment.py` |
| [run_pipeline.py](run_pipeline.py) | Pipeline via CLI | `python run_pipeline.py` |
| [notebooks/main.ipynb](notebooks/main.ipynb) | Pipeline via Jupyter | `jupyter notebook notebooks/main.ipynb` |

---

## 🔗 Links Rápidos

### Para Começar
- [GUIA_EXECUCAO.md](GUIA_EXECUCAO.md) ← **COMECE AQUI**
- [setup_environment.py](setup_environment.py)
- [notebooks/main.ipynb](notebooks/main.ipynb)

### Para Aprender
- [docs/business_explanation.md](docs/business_explanation.md)
- [reports/methodology.md](reports/methodology.md)
- [docs/glossary.md](docs/glossary.md)

### Relatórios e Status
- [reports/result_final.json](reports/result_final.json)
- [reports/validation_report.md](reports/validation_report.md)
- [CHECKLIST_PROJETO.md](CHECKLIST_PROJETO.md)

---

## 🆘 Suporte

1. **Erro de setup?** → [GUIA_EXECUCAO.md - Troubleshooting](GUIA_EXECUCAO.md#problemas)
2. **Erro de imports?** → `python setup_environment.py` novamente
3. **Notebook não executa?** → Confirme que está no diretório correto
4. **Resultados estranhos?** → Verifique [reports/assumptions.md](reports/assumptions.md)

---

## 📄 Versão

**Projeto:** IFRS 17 Risk Adjustment Engine v1.0.0  
**Data:** 9 de Abril de 2026  
**Status:** ✅ Operacional
