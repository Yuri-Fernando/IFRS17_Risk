# Arquitetura AWS - IFRS 17 Risk Adjustment Engine

## Visão Geral

Proposta de arquitetura cloud para deployment de modelo em produção na AWS.

```
Dados Históricos
    ↓
[S3] Data Lake Raw
    ↓
[Glue] ETL (preprocess)
    ↓
[S3] Data Lake Processed
    ↓
[SageMaker] Model Training
    ↓
[SageMaker] Model Registry (versionamento)
    ↓
[Lambda] Inference (cálculo de RA)
    ↓
[RDS/Timestream] Results Storage
    ↓
[CloudWatch] Monitoramento
    ↓
[QuickSight/Tableau] Dashboards
```

## Componentes

### 1. Data Lake (S3)

**Função**: Armazenamento centralizado de dados

**Estrutura**:
```
s3://ifrs17-datalake/
├── raw/                    # Dados originais (nunca modifica)
│   ├── premios/
│   ├── sinistros/
│   ├── mortaldade/
│   └── cancelamentos/
├── processed/              # Dados pré-processados
│   ├── features/
│   └── validated/
├── models/                 # Artefatos de modelo
│   ├── v1.0.0/
│   ├── v1.1.0/
│   └── current/
└── results/                # Resultados de execução
    ├── monthly/
    └── quarterly/
```

**Lifecycle Policy**:
- Raw: Retenção indefinida
- Processed: 90 dias
- Results: 7 anos (compliance)

**Custo Estimado**: R$ 50-80/mês

### 2. ETL (AWS Glue)

**Função**: Preprocessamento e transformação de dados

**Jobs**:
```
Job 1: preprocess_raw
  - Carrega raw data de S3
  - Aplica transformações (vide src/data/preprocess.py)
  - Salva em processed/

Job 2: feature_engineering
  - Cria variáveis de interação
  - Normaliza
  - Salva em features/

Job 3: data_validation
  - Checa qualidade
  - Valida ranges
  - Rejeita se erros
```

**Configuração**:
- Runtime: Python 3.9
- Workers: G.2X (2 vCPU, 8GB RAM)
- Timeout: 1 hora

**Custo Estimado**: R$ 15-25/mês (para 2 jobs/dia)

### 3. Treinamento (SageMaker)

**Função**: Treinar e validar modelos

**Pipeline**:

#### Etapa 1: Prepare
- Carrega dados processados
- Split em train/test (80/20)

#### Etapa 2: Train
- Treina modelo de frequência
- Treina modelo de severidade
- Salva artefatos

#### Etapa 3: Evaluate
- Roda backtesting
- Testa stress scenarios
- Gera report de validação

#### Etapa 4: Register
- Versionamento automático
- Aprovação de modelo
- Deploy em staging

**Instância**:
- Type: ml.m5.xlarge
- Volume: 50GB
- Tempo estimado: 30 minutos

**Custo Estimado**: R$ 9-15/mês

### 4. Inference (AWS Lambda)

**Função**: Executar modelo em produção

**Configuração**:
```
Runtime: Python 3.9
Memory: 3008 MB
Timeout: 900 segundos (15 min)
Ephemeral Storage: 10GB
```

**Fluxo**:
1. Recebe evento (S3 novo arquivo)
2. Carrega modelo do Model Registry
3. Processa dados
4. Roda Monte Carlo (10k simulações)
5. Calcula RA
6. Salva em RDS
7. Dispara notificação

**Concorrência**: 100 simultâneas

**Custo Estimado**: R$ 5-10/mês

### 5. Armazenamento de Resultados (RDS)

**Função**: Persistência de resultados com histórico

**Configuração**:
```
Engine: PostgreSQL 13+
Instance: db.t3.micro (dev) ou db.t3.small (prod)
Storage: 100GB
Backup: Diário, retenção 7 anos
```

**Schema**:
```sql
CREATE TABLE executions (
    id SERIAL PRIMARY KEY,
    execution_date TIMESTAMP,
    model_version VARCHAR(10),
    n_simulations INT,
    bel NUMERIC,
    ra NUMERIC,
    total_provision NUMERIC,
    validation_status VARCHAR(50),
    audit_log JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE validation_metrics (
    id SERIAL PRIMARY KEY,
    execution_id INT REFERENCES executions,
    metric_name VARCHAR(50),
    metric_value NUMERIC,
    created_at TIMESTAMP
);
```

**Custo Estimado**: R$ 12-20/mês

### 6. Monitoramento (CloudWatch)

**Função**: Logs, métricas e alertas

**Métricas Rastreadas**:
- Duração de execução
- Taxa de sucesso/falha
- Número de simulações processadas
- Uso de memória Lambda
- Erros de conexão com BD

**Logs**:
- CloudWatch Logs (automático)
- Retenção: 30 dias
- Log group: `/aws/lambda/ifrs17-inference`

**Alarmes**:
- Falha de execução
- Execução > 900s
- Erro no acesso a RDS
- Desvio inesperado em RA

**Custo Estimado**: R$ 5-10/mês

### 7. CI/CD (CodePipeline + CodeBuild)

**Função**: Deploy automático

**Pipeline**:
```
1. Source (GitHub/CodeCommit)
   ↓
2. Build (CodeBuild)
   - Executa testes (pytest)
   - Lint (pylint, black)
   - Coverage > 80%
   ↓
3. Staging (Lambda em staging)
   - Deploy em função de teste
   - Roda smoke tests
   ↓
4. Production (Lambda em prod)
   - Deploy automático se staging OK
```

**Custo Estimado**: R$ 3-7/mês

### 8. Versioning (S3 + DynamoDB)

**Função**: Histórico de versões de modelo

**DynamoDB Table**:
```
PK: model_version (v1.0.0)
SK: timestamp
Attributes:
  - s3_location
  - parameters
  - validation_score
  - deployed_date
```

**Custo Estimado**: R$ 1-2/mês

### 9. Segurança

#### Autenticação
- IAM Roles para cada serviço
- Nenhuma API Key em código

#### Criptografia
- S3: SSE-S3 ou KMS
- RDS: Encrypted volumes
- Transit: TLS 1.2+

#### Auditoria
- CloudTrail para todas as APIs
- VPC Flow Logs (opcional)
- S3 Access Logs
- RDS audit plugin

#### Conformidade
- VPC isolada (sem internet direto)
- Endpoint de S3/RDS em VPC
- Security groups restritivos

### 10. Disaster Recovery

**RTO** (Recovery Time Objective): 4 horas
**RPO** (Recovery Point Objective): 1 hora

**Estratégia**:
1. Backup diário RDS (retenção 35 dias)
2. S3 replicação cross-region
3. Infrastructure as Code (CloudFormation/Terraform)
4. Runbook de recuperação documentado

## Fluxo de Execução

### Diário (Cálculo de RA)

```
1. 08:00 - Glue Job: preprocess_raw
   Carrega dados do dia anterior
   Preprocessa e valida
   Salva em S3 processed/

2. 09:00 - Lambda: inference
   Carrega último modelo
   Processa dados processados
   Roda Monte Carlo (10k sim)
   Salva resultados em RDS
   Envia email para análistas

3. 10:00 - CloudWatch
   Monitora sucesso/falha
   Gera logs
   Atualiza dashboards
```

### Mensal (Retreinamento)

```
1. SageMaker Training Pipeline
   Carrega dados do mês
   Treina novo modelo
   Executa validação
   Registra versão

2. Aprovação Manual
   Analista revisa resultados
   Aprova ou rejeita

3. Deploy (se aprovado)
   Atualiza Model Registry
   Lambda começa usar novo modelo
   Notifica stakeholders
```

## Custo Estimado (Mensal)

| Serviço | Estimativa |
|---------|-----------|
| S3 (Data Lake) | R$ 50-80 |
| Glue (ETL) | R$ 15-25 |
| SageMaker (Training) | R$ 9-15 |
| Lambda (Inference) | R$ 5-10 |
| RDS (Database) | R$ 12-20 |
| CloudWatch | R$ 5-10 |
| CodePipeline/Build | R$ 3-7 |
| DynamoDB (Versioning) | R$ 1-2 |
| **Total** | **R$ 100-170/mês** |

## Benefícios

1. **Escalabilidade**: Auto-scaling automático
2. **Confiabilidade**: 99.99% uptime SLA
3. **Segurança**: Compliance com reguladores
4. **Auditoria**: Trilha completa de execução
5. **Custo-efetivo**: Pay-as-you-go
6. **DevOps**: Deploy automático

## Alternativas Consideradas

### Opção 1: Batch em EC2
- Mais controle
- Custo maior
- Mais complexidade operacional

### Opção 2: Fargate (Containers)
- Mais flexível
- Custo similar Lambda
- Melhor para pipelines complexos

### Opção 3: On-Premise
- Custo CAPEX alto
- Menos escalável
- Compliance mais complexo

**Recomendação**: Lambda + Glue (serverless) é ideal para este caso.

## Próximos Passos

1. Criar conta AWS
2. Setup VPC isolada
3. Criar S3 buckets
4. Deploy Glue jobs
5. Criar SageMaker notebooks
6. Desenvolver Lambda function
7. Setup RDS
8. Configurar CloudWatch
9. Documentar runbooks
10. Treinamento de team

---

*Arquitetura AWS - IFRS 17 Risk Adjustment v1.0*
