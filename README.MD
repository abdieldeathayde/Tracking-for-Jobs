# JobApply Automation

<p align="center">
  <strong>Automação assistida para busca, registro e acompanhamento de candidaturas de emprego.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Selenium-Automation-green?logo=selenium" alt="Selenium">
  <img src="https://img.shields.io/badge/OpenPyXL-Excel-217346?logo=microsoftexcel" alt="OpenPyXL">
  <img src="https://img.shields.io/badge/Status-Em%20desenvolvimento-orange" alt="Status">
</p>

## Sobre o projeto

O **JobApply Automation** é uma aplicação em Python (CLI) para apoiar a organização e o acompanhamento de oportunidades de emprego. Ela utiliza **Selenium** para navegação/coleta assistida no navegador e **OpenPyXL** para criar e manter uma planilha Excel com o histórico das vagas e candidaturas.

O projeto é voltado principalmente para oportunidades nas áreas de:

- Infraestrutura de TI, suporte técnico e segurança da informação;
- Desenvolvimento de software (Java, full stack, frontend, mobile etc.).

As buscas e o fluxo foram pensados para vagas remotas, híbridas e presenciais (por padrão, Blumenau e Gaspar/SC), mas os parâmetros podem ser ajustados via linha de comando.

## Funcionalidades

### Implementadas

- **CLI com subcomandos** (`init`, `list`, `summary`, `update`, `search`, `add`, `open`, `export`).
- **Planilha de acompanhamento** (`vagas.xlsx`) com:
  - abas `Vagas` e `Dashboard`;
  - cabeçalho fixo, filtro automático, largura de colunas, tabela formatada;
  - validação de dados (status da candidatura, situação da vaga, modalidade);
  - formatação condicional por status e métricas no dashboard.
- **Cadastro manual de vagas** com validação de URL, normalização de dados e seleção de currículo por área.
- **Acompanhamento de candidaturas**: listagem (com filtro por status), resumo por status e atualização de status por ID.
- **Busca assistida de vagas**:
  - geração de URLs de pesquisa por plataforma;
  - no **LinkedIn**, coleta de anúncios públicos exibidos na página, extração de dados básicos (título, empresa, localidade, modalidade inferida, link canônico), deduplicação e registro na planilha;
  - filtros por área, localidade(s), modalidade(s) e opção de **Candidatura Simplificada** (`--easy-apply`, LinkedIn);
  - detecção de `authwall`/login no LinkedIn e interrupção segura da busca;
  - delays configuráveis entre consultas.
  - em **Gupy/Indeed**, abertura das páginas de pesquisa para revisão manual no navegador.
- **Abertura assistida de candidatura** (`open`): abre a vaga no navegador, valida o currículo (PDF), tenta localizar e anexar campo de upload, tenta abrir modal de *Easy Apply* (seletores LinkedIn) e registra/atualiza a vaga como `Em progresso` após confirmação do usuário (envio permanece manual).
- **Seleção automática de currículo** por área/cargo (infraestrutura/suporte/segurança x desenvolvimento), com possibilidade de override manual (`--area`).
- **Deduplicação de vagas** pelo link (normalização de URL; para LinkedIn, uso de URL canônica do anúncio).
- **Registro de data de envio**: ao atualizar status para `Enviada`, a data da candidatura é preenchida automaticamente se estiver vazia.
- **Exportação de candidaturas em PDF** (`export`): gera relatório com filtros por status e opção `--applied-only` (exclui "Não iniciada"), útil para arquivar candidaturas aplicadas.
- **Logs** em arquivo rotativo (`logs/jobapply.log`).
- **Configuração flexível de ambiente**: carrega variáveis do `.env` na raiz do workspace com fallback para `jobapply/.env`.
- **Testes automatizados** com Pytest (`jobapply/tests/`).

### Em desenvolvimento / planejadas

- Coletores automatizados específicos para Gupy e Indeed (além da abertura assistida).
- Extração/análise de compatibilidade entre currículo e requisitos (ex.: palavras-chave/NLP).
- Preenchimento mais completo de formulários específicos por plataforma (sempre com revisão humana).
- Relatórios/indicadores adicionais de desempenho das candidaturas.
- Melhorias de detecção de duplicidades e enriquecimento de dados das vagas.

## Tecnologias utilizadas

| Tecnologia | Uso no projeto |
|---|---|
| Python | Linguagem principal e CLI (`argparse`) |
| Selenium | Automação/navegação no navegador e coleta de anúncios no LinkedIn |
| OpenPyXL | Criação e manipulação da planilha Excel (`.xlsx`) |
| python-dotenv | Carregamento de variáveis de ambiente (`.env`) |
| fpdf2 | Geração de relatórios de candidaturas em PDF |
| Pytest / pytest-cov | Testes automatizados (dependências em `requirements.txt`) |

> As dependências efetivas do projeto estão em [`requirements.txt`](requirements.txt).

## Plataformas

- **LinkedIn**: busca com filtros e coleta de anúncios públicos para registro na planilha (pode exigir login ou limitar resultados).
- **Gupy** e **Indeed**: abertura das páginas de pesquisa para análise manual (sem coletor automatizado dedicado).

A automação **não** contorna CAPTCHA, autenticação ou mecanismos de proteção das plataformas. A coleta não envia candidaturas.

## Estrutura do projeto (neste workspace)

```text
tracking-jobs/                  # raiz do workspace
├── env/                        # ambiente virtual (opcional, se já criado)
└── jobapply/                   # pacote/aplicação
    ├── main.py                 # ponto de entrada da CLI
    ├── config.py               # configuração e variáveis de ambiente
    ├── requirements.txt
    ├── .env                    # variáveis locais (não versionar)
    ├── .env.example
    ├── applications/
    │   └── application_manager.py
    ├── browser/
    │   └── selenium_manager.py
    ├── collectors/
    │   ├── job_collector.py
    │   └── linkedin_collector.py
    ├── reporting/
    │   └── pdf_report.py
    ├── resume/
    │   └── resume_manager.py
    ├── spreadsheet/
    │   └── excel_manager.py
    ├── utils/
    │   ├── logger.py
    │   └── urls.py
    ├── tests/
    └── data/                   # dados locais (podem existir conforme uso)
```

**Observação sobre caminhos:** [`config.py`](config.py) define `ROOT_DIR` como o diretório pai de `jobapply/` (ou seja, a raiz do workspace). Por padrão, carrega variáveis de `ROOT_DIR/.env` e usa `jobapply/.env` como fallback (sem sobrescrever valores já definidos). A planilha, logs e exportações são gravados por padrão em `data/vagas.xlsx`, `logs/jobapply.log` e `data/candidaturas_aplicadas.pdf` relativos à raiz do workspace; os caminhos dos currículos também são resolvidos a partir desse contexto. Ajuste o `.env` e os arquivos conforme a sua organização local.

## Requisitos

- Python 3.10 ou superior.
- Navegador instalado: Microsoft Edge, Google Chrome ou Firefox (conforme `BROWSER`).
- Driver compatível com o navegador/Selenium, quando necessário no seu ambiente.
- Conexão com a internet para buscas e abertura de páginas.

## Instalação e configuração

### 1. Ambiente virtual e dependências

Na raiz do workspace (onde está a pasta `jobapply/`):

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\jobapply\requirements.txt
```

> Se já existir um ambiente virtual em `env/`, você pode usá-lo diretamente.

### 2. Variáveis de ambiente

Crie um arquivo `.env` na **raiz do workspace** (mesmo nível de `jobapply/`), com base em [`jobapply/.env.example`](.env.example). Exemplo:

```env
CV_INFRA_PATH=data/curriculo/Abdiel_CV_Infraestrutura.pdf
CV_DEV_PATH=data/curriculo/Abdiel_CV_Desenvolvimento.pdf

BROWSER=edge
HEADLESS=false
WAIT_SECONDS=15
REQUEST_DELAY_MIN=2.0
REQUEST_DELAY_MAX=5.0

# Opcional: perfil dedicado do navegador
BROWSER_PROFILE_DIR=
```

- `BROWSER`: `edge`, `chrome` ou `firefox`.
- `WAIT_SECONDS`: tempo de espera usado em operações com Selenium (ex.: carregamento de resultados).
- `REQUEST_DELAY_MIN` / `REQUEST_DELAY_MAX`: intervalo (segundos) entre consultas na busca do LinkedIn.
- Certifique-se de que os arquivos de currículo existam nos caminhos configurados (a seleção exige que o arquivo exista).

## Como utilizar

Execute os comandos **a partir da raiz do workspace** usando o módulo `jobapply.main`:

```powershell
# com o venv ativado
python -m jobapply.main --help

# ou chamando o Python do venv diretamente
.\env\Scripts\python.exe -m jobapply.main --help
```

### `init` — inicializar planilha

```powershell
python -m jobapply.main init
```

Cria a estrutura inicial da planilha (abas, validações, formatação e dashboard).

### `list` — listar vagas

```powershell
python -m jobapply.main list
python -m jobapply.main list --status "Em análise"
```

Exibe ID, status, cargo, empresa, localidade e link. `--status` aceita os mesmos valores usados na planilha.

### `summary` — resumo por status

```powershell
python -m jobapply.main summary
```

Mostra o total de vagas e a contagem por status.

### `update` — atualizar status da candidatura

```powershell
python -m jobapply.main update --id 3 --status "Em análise"
```

Status aceitos: `Não iniciada`, `Em progresso`, `Enviada`, `Em análise`, `Entrevista`, `Congelada`, `Desclassificado`, `Aprovado`, `Recusada`, `Encerrada`.

### `search` — buscar oportunidades

```powershell
# LinkedIn (padrão), áreas dev + infra, locais e modalidades padrão
python -m jobapply.main search

# exemplos de filtros
python -m jobapply.main search --area infra --local "Blumenau SC" "Gaspar SC" --modalidade Remoto Híbrido Presencial
python -m jobapply.main search --plataforma linkedin --easy-apply
python -m jobapply.main search --plataforma gupy
```

- `--area`: `infra`, `dev` ou `ambas` (padrão: `ambas`).
- `--local`: uma ou mais cidades/localidades (padrão: `Blumenau SC`, `Gaspar SC`).
- `--modalidade`: `Remoto`, `Híbrido`, `Presencial` (padrão: todas).
- `--plataforma`: `linkedin` (padrão), `gupy`, `indeed`.
- `--easy-apply`: filtra vagas com Candidatura Simplificada no LinkedIn.

**Comportamento:** no LinkedIn, o sistema percorre combinações de consultas/localidades, aguarda resultados, coleta anúncios e registra vagas novas na planilha (sem duplicar links). Em Gupy/Indeed, as páginas são abertas para revisão manual durante a execução.

### `add` — cadastrar vaga manualmente

```powershell
python -m jobapply.main add --empresa "Empresa" --cargo "Analista de Suporte" --url "https://..." --area infra
```

Argumentos principais:
- obrigatórios: `--empresa`, `--cargo`, `--url`, `--area` (`infra` ou `dev`);
- opcionais: `--modalidade` (`Remoto|Híbrido|Presencial|Não informado`), `--localidade`, `--plataforma` (`LinkedIn|Gupy|Indeed|Outra`).

Se o link já estiver cadastrado, a vaga não é duplicada.

### `open` — abrir candidatura assistida

```powershell
python -m jobapply.main open --url "https://..." --empresa "Empresa" --cargo "Desenvolvedor Java" --area dev
```

- `--area` é opcional; se omitida, o currículo é inferido pelo cargo. Se não for possível inferir, informe `--area infra` ou `--area dev`.
- O assistente tenta preparar a página (ex.: anexar currículo PDF quando houver campo de upload e, quando aplicável, abrir fluxo de candidatura simplificada). **O envio da candidatura é sempre manual** e deve ser revisado por você.
- Ao final, a vaga é registrada/atualizada como `Em progresso` na planilha.

### `export` — exportar candidaturas para PDF

```powershell
# exporta todas as candidaturas
python -m jobapply.main export

# exporta apenas candidaturas aplicadas (status diferente de "Não iniciada")
python -m jobapply.main export --applied-only

# filtra por status e define caminho de saída
python -m jobapply.main export --status Enviada "Em análise" Entrevista --output .\data\candidaturas_aplicadas.pdf
```

- `--output`: caminho do PDF gerado (padrão: `data/candidaturas_aplicadas.pdf`).
- `--status`: um ou mais status para incluir no relatório.
- `--applied-only`: exclui candidaturas com status `Não iniciada`.

## Planilha de acompanhamento

A planilha `data/vagas.xlsx` (na raiz do workspace, por padrão) contém:

- **Aba `Vagas`**: colunas como ID, Empresa, Cargo, Modalidade, Localidade, Salário, Requisitos, Compatibilidade (%), Link da vaga, Plataforma, Data encontrada, Data da candidatura, Status da candidatura, Situação da vaga, Currículo utilizado e Observações.
- **Aba `Dashboard`**: indicadores consolidados (total, enviadas/em análise/entrevista/aprovado/desclassificado, em progresso, congeladas, aprovadas, desclassificadas).

Os registros são deduplicados pelo link da vaga. Logs da aplicação ficam em `logs/jobapply.log`.

## Fluxo de funcionamento

```text
Busca ou identificação da oportunidade
                |
                v
Coleta/registro na planilha (quando aplicável)
                |
                v
Seleção do currículo (por área/cargo)
                |
                v
Abertura assistida da vaga no navegador
                |
                v
Revisão humana e envio manual
                |
                v
Atualização de status e acompanhamento na planilha
```

## Testes

Execute a partir da raiz do workspace:

```powershell
python -m pytest jobapply\tests -v
```

(ou `python -m pytest -v`, conforme a sua preferência de descoberta de testes.)

## Segurança e boas práticas

- Não armazene senhas ou credenciais no código.
- Mantenha o arquivo `.env` fora do controle de versão.
- Respeite os termos de uso das plataformas de emprego.
- Não tente contornar CAPTCHA, autenticação ou mecanismos de segurança.
- Revise os dados antes de enviar qualquer candidatura.
- Mantenha os currículos atualizados e confira os caminhos configurados.

## Autor

**Abdiel de Athayde**

Projeto de estudo e aplicação prática em Python, automação web e organização de dados para acompanhamento de candidaturas.
