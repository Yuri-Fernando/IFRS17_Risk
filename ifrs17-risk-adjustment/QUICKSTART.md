# QUICKSTART - IFRS 17 Risk Adjustment Engine

**Tempo estimado: 5-10 minutos**

## Passo 1: Instalar Dependências

```bash
# Navegue até a pasta do projeto
cd "g:\Outros computadores\Meu computador\Controle Base\Projetos, Robos e Automação\Projetos Git\Projetos Extras (Portfolio)\IR17\ifrs17-risk-adjustment"

# OPÇÃO A: Usar script automático de setup
python setup_environment.py

# OPÇÃO B: Instalar manualmente
C:\Users\Yuri_\AppData\Local\Programs\Python\Python310\python.exe -m pip install -r requirements.txt
```

## Passo 2: Abrir Jupyter Notebook

```bash
# Ainda na pasta do projeto, abra o notebook
jupyter notebook notebooks/main.ipynb
```

Seu navegador vai abrir automaticamente com o notebook.

## Passo 3: Executar o Pipeline Completo

**No Jupyter:**
1. Clique na primeira célula (setup)
2. Pressione **Shift + Enter** para executar
3. Vá para a próxima célula
4. Repita até a última célula

Ou execute tudo de uma vez:
- Menu → Cell → Run All

## Passo 4: Ver Resultados

Os resultados serão salvos em:
- `reports/result_final.json` - Dados estruturados
- Console do notebook - Visualizações e tabelas

## Alternativa: CLI (Sem Jupyter)

Se preferir executar tudo no terminal:

```bash
# Executa o pipeline completo
python run_pipeline.py

# Com customização
python run_pipeline.py --simulations 50000 --ra-method cte

# Ver opções
python run_pipeline.py --help
```

## Verificar Setup

Se encontrar erros, rode o diagnóstico:

```bash
python setup_environment.py
```

Este script verifica:
- ✅ Versão do Python
- ✅ pip e pip packages
- ✅ Estrutura do projeto
- ✅ Dataset
- ✅ Todos os imports

## Estrutura do Projeto

```
ifrs17-risk-adjustment/
├── notebooks/
│   ├── main.ipynb              ← EXECUTE ISTO
│   └── 00_quickstart.py
├── src/                        ← Código do modelo
│   ├── data/                   (carregamento)
│   ├── actuarial/              (BEL, projeção)
│   ├── modeling/               (frequência, severidade, RA)
│   ├── simulation/             (Monte Carlo)
│   ├── validation/             (testes estatísticos)
│   ├── governance/             (auditoria)
│   └── cloud/                  (pipeline, AWS)
├── data/
│   └── raw/
│       └── Insurance claims data.csv  (11.7 MB)
├── reports/                    ← Resultados
├── config/                     ← Parâmetros
├── requirements.txt            ← Dependências
├── setup_environment.py        ← Script de setup
├── run_pipeline.py             ← CLI alternativo
└── .claude/                    ← Configuração do projeto
```

## Requisitos Mínimos

- **Python:** 3.8+
- **Espaço disco:** 100 MB
- **RAM:** 4 GB
- **Dataset:** 11.7 MB (já incluído)

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'pandas'"
```bash
# Instale manualmente
pip install pandas numpy scipy scikit-learn statsmodels
```

### Erro: "ModuleNotFoundError: No module named 'src'"
```bash
# Execute do diretório correto:
cd ifrs17-risk-adjustment
jupyter notebook notebooks/main.ipynb
```

### Erro: "No such file or directory: 'data/raw/Insurance claims data.csv'"
```bash
# Verifique se o arquivo existe:
ls data/raw/
# Se não existir, o notebook usa dados sintéticos automaticamente
```

### Jupyter não abre
```bash
# Instale jupyter
pip install jupyter

# Ou use a versão JupyterLab
pip install jupyterlab
jupyter lab notebooks/main.ipynb
```

## Próximas Etapas

Após executar o notebook com sucesso:

1. **Revisar resultados:** Abra `reports/result_final.json`
2. **Entender a modelagem:** Leia `reports/methodology.md`
3. **Validação:** Confira `reports/validation_report.md`
4. **Explicação simplificada:** Veja `docs/business_explanation.md`

## Tempo de Execução

- Setup + Instalação: 5-10 min (primeira vez)
- Pipeline Jupyter: 5-10 min
- CLI (run_pipeline.py): 3-5 min

## Suporte

Se encontrar problemas:

1. Execute `python setup_environment.py` para diagnóstico
2. Verifique `requirements.txt` está completo
3. Confirme que Python 3.8+ está instalado
4. Veja a seção Troubleshooting acima

---

**Pronto? Execute:**
```bash
python setup_environment.py
jupyter notebook notebooks/main.ipynb
```
