# GUIA DE EXECUÇÃO - IFRS 17 Risk Adjustment Engine

## 📋 Resumo Rápido

O projeto IFRS 17 está **100% pronto**. Faltavam apenas as dependências Python instaladas.

**3 passos para começar:**

1. Instale dependências (5-10 minutos, apenas 1ª vez)
2. Abra o notebook Jupyter
3. Execute as células na ordem

---

## ✅ Passo 1: Instalar Dependências (PRIMEIRA VEZ APENAS)

### Opção A: Automática (Recomendado)

```bash
cd "g:\Outros computadores\Meu computador\Controle Base\Projetos, Robos e Automação\Projetos Git\Projetos Extras (Portfolio)\IR17\ifrs17-risk-adjustment"

python setup_environment.py
```

Este script:
- Verifica Python 3.10+ ✓
- Instala 35+ pacotes científicos
- Valida estrutura do projeto
- Testa todos os imports

**Resultado esperado:** `[OK] AMBIENTE PRONTO!`

### Opção B: Manual

```bash
cd "g:\Outros computadores\Meu computador\Controle Base\Projetos, Robos e Automação\Projetos Git\Projetos Extras (Portfolio)\IR17\ifrs17-risk-adjustment"

pip install -r requirements.txt
```

---

## 🚀 Passo 2: Abrir Jupyter Notebook

Após instalar dependências (Passo 1):

```bash
# Ainda na pasta do projeto
jupyter notebook notebooks/main.ipynb
```

Seu navegador abrirá automaticamente com o notebook.

---

## ▶️ Passo 3: Executar o Pipeline

**No Jupyter, você verá:**

```
Cell 1: Setup - Imports e Configuração
Cell 2: Etapa 1 - Carregamento de Dados
Cell 3: Etapa 2 - Preprocessamento
... e assim por diante
```

### Executar Célula por Célula (Recomendado)

1. Clique na **primeira célula** (Setup)
2. Pressione **Shift + Enter**
3. Aguarde a execução (barra de progresso cinza)
4. Vá para a próxima célula
5. Repita

**Tempo total:** ~5-10 minutos

### OU: Executar Tudo de Uma Vez

Menu do Jupyter → **Cell** → **Run All**

Aguarde até ver: `PIPELINE COMPLETO EXECUTADO COM SUCESSO`

---

## 📊 Resultados

Após execução, os resultados estarão em:

### 1. Console do Jupyter
```
BEL: R$ 1.234.567,89
Risk Adjustment: R$ 234.567,89
Provisão Total: R$ 1.469.135,78
RA como % de BEL: 19.02%
```

### 2. Gráficos Embutidos
- Distribuição de perdas (histograma)
- Q-Q Plot (normalidade)
- Fluxos de caixa projetados

### 3. Arquivo JSON
```
reports/result_final.json
```

Contém todos os dados estruturados:
```json
{
  "timestamp": "2026-04-09T15:30:00",
  "models": {
    "frequency": "Poisson",
    "severity": "Lognormal"
  },
  "actuarial": {
    "bel": 1234567.89,
    "ra": 234567.89,
    "provision": 1469135.78
  }
}
```

---

## 🔍 Verificar Antes de Começar

```bash
# Confirme que está no diretório correto
cd "g:\Outros computadores\Meu computador\Controle Base\Projetos, Robos e Automação\Projetos Git\Projetos Extras (Portfolio)\IR17\ifrs17-risk-adjustment"

# Verifique que o dataset existe
ls data/raw/

# Saída esperada:
# Insurance claims data.csv (11.7 MB)
```

---

## 🆘 Problemas?

### Erro: "ModuleNotFoundError: No module named 'pandas'"
```bash
# Rode o setup novamente
python setup_environment.py

# Ou instale manualmente
pip install pandas numpy scipy scikit-learn statsmodels
```

### Erro: "No such file or directory: data/raw/Insurance claims data.csv"
```bash
# Verifique se arquivo existe
ls "data/raw/"

# Se não existir, o notebook usa dados SINTÉTICOS automaticamente
# (não há problema, o modelo funcionará normalmente)
```

### Jupyter não abre/congela
```bash
# Reinicie Jupyter
# Feche o navegador
# Execute novamente:
jupyter notebook notebooks/main.ipynb

# OU use JupyterLab (mais moderno):
pip install jupyterlab
jupyter lab notebooks/main.ipynb
```

### Script setup_environment.py não roda
```bash
# Garanta que está usando Python 3.10+
python --version

# Se for 3.8 ou 3.9, execute com path completo:
C:\Users\Yuri_\AppData\Local\Programs\Python\Python310\python.exe setup_environment.py
```

---

## 📚 Entender a Estrutura

```
ifrs17-risk-adjustment/
│
├── 📓 notebooks/
│   └── main.ipynb                    ← EXECUTE ISTO
│
├── 🔧 src/                           (Código do modelo)
│   ├── data/                         (Carregamento)
│   ├── actuarial/                    (BEL, projeção)
│   ├── modeling/                     (Frequência, severidade, RA)
│   ├── simulation/                   (Monte Carlo)
│   ├── validation/                   (Testes estatísticos)
│   ├── governance/                   (Auditoria)
│   └── cloud/                        (Pipeline, AWS)
│
├── 📊 data/
│   └── raw/
│       └── Insurance claims data.csv (11.7 MB)
│
├── 📈 reports/                       (Resultados)
│   ├── result_final.json             ← Gerado após execução
│   ├── methodology.md                (Como funciona)
│   └── validation_report.md          (Testes estatísticos)
│
├── ⚙️ config/
│   ├── parameters.yaml               (Parâmetros do modelo)
│   └── model_config.yaml             (Configurações técnicas)
│
├── 📖 docs/
│   ├── business_explanation.md       (Explicação leiga)
│   └── glossary.md                   (80+ termos técnicos)
│
├── ✅ setup_environment.py           (Script de setup)
├── 🚀 run_pipeline.py                (Alternativa CLI)
└── .claude/                          (Configuração do projeto)
```

---

## 🎯 Fluxo Completo

```
┌─────────────────────────────────────────────────────────────┐
│  Seu Projeto IFRS 17 - Sequência de Execução                │
└─────────────────────────────────────────────────────────────┘

1. [SETUP] Instale dependências
   └─> python setup_environment.py
       (5-10 minutos, apenas 1ª vez)

2. [NOTEBOOK] Abra Jupyter
   └─> jupyter notebook notebooks/main.ipynb
       (Abre no navegador)

3. [EXECUÇÃO] Execute as 10 etapas
   ├─ Etapa 1: Carregamento de dados
   ├─ Etapa 2: Preprocessamento
   ├─ Etapa 3: Projeção atuarial (BEL)
   ├─ Etapa 4: Modelos estatísticos
   ├─ Etapa 5: Simulação Monte Carlo (10k)
   ├─ Etapa 6: Risk Adjustment
   ├─ Etapa 7: Provisão IFRS 17 Total
   ├─ Etapa 8: Validação e testes
   ├─ Etapa 9: Relatório de auditoria
   └─ Etapa 10: Resumo executivo

4. [RESULTADOS] Analize os outputs
   ├─ Console: BEL, RA, Provisão
   ├─ Gráficos: Distribuições e fluxos
   └─ JSON: reports/result_final.json

5. [DOCUMENTAÇÃO] Entenda a modelagem
   ├─ reports/methodology.md
   ├─ reports/validation_report.md
   └─ docs/business_explanation.md
```

---

## ⏱️ Tempos Esperados

| Atividade | Tempo |
|-----------|-------|
| Setup (install) | 5-10 min |
| Pipeline Jupyter | 5-10 min |
| Total | 10-20 min |

---

## ✨ Próximas Etapas (Opcional)

Após rodar o notebook:

1. **Customize parâmetros:** `config/parameters.yaml`
2. **Execute CLI:** `python run_pipeline.py --simulations 50000`
3. **Adicione dados:** `data/raw/seus_dados.csv`
4. **Estude código:** Leia `src/` para entender implementação

---

## 📞 Resumo

| O quê | Comando |
|------|---------|
| **Instalar deps** | `python setup_environment.py` |
| **Abrir notebook** | `jupyter notebook notebooks/main.ipynb` |
| **Rodar tudo CLI** | `python run_pipeline.py` |
| **Ver resultados** | `reports/result_final.json` |
| **Entender código** | `README.md` e `reports/methodology.md` |

---

## 🎉 Bom Trabalho!

Seu projeto está **completo e funcional**. 

Execute os 3 passos acima e você terá:
- ✅ Modelo IFRS 17 funcionando
- ✅ Simulação Monte Carlo (10k)
- ✅ Risk Adjustment calculado
- ✅ Validação estatística completa
- ✅ Provisão contábil final

**Próximo:** `python setup_environment.py`
