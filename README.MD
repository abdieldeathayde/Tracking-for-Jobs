# JobApply Automation

<p align="center">
  <strong>Automação inteligente para organização e acompanhamento de candidaturas de emprego.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Selenium-Automation-green?logo=selenium" alt="Selenium">
  <img src="https://img.shields.io/badge/OpenPyXL-Excel-217346?logo=microsoftexcel" alt="OpenPyXL">
  <img src="https://img.shields.io/badge/Status-Em%20desenvolvimento-orange" alt="Status">
</p>

## Sobre o projeto

O **JobApply Automation** é uma aplicação desenvolvida em Python com o objetivo de auxiliar na busca, organização e acompanhamento de oportunidades de emprego.

A solução utiliza Selenium para automação de navegação web e OpenPyXL para gerenciamento de uma planilha Excel, centralizando informações sobre vagas e candidaturas.

O projeto foi pensado para profissionais que buscam oportunidades nas áreas de:

- Infraestrutura de TI;
- Suporte Técnico e Help Desk;
- Desenvolvimento Java;
- Desenvolvimento Full Stack.

A aplicação também considera oportunidades remotas e presenciais em Blumenau e região.

## Objetivos

- Organizar oportunidades de emprego em um único lugar.
- Facilitar a identificação de vagas compatíveis com o perfil profissional.
- Selecionar o currículo adequado para cada oportunidade.
- Auxiliar na navegação e no preenchimento de formulários de candidatura.
- Registrar o andamento dos processos seletivos.
- Manter um histórico atualizado das candidaturas.

## Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Linguagem principal |
| Selenium | Automação de navegador |
| OpenPyXL | Manipulação de planilhas Excel |
| PyPDF | Leitura de currículos PDF |
| Python-DOCX | Leitura de documentos Word |
| Python-Dotenv | Gerenciamento de variáveis de ambiente |
| Pytest | Testes automatizados |

## Plataformas consideradas

- LinkedIn
- Gupy
- Indeed

> **Observação:** a integração atual utiliza navegação assistida. A coleta automática de vagas e a integração completa com os formulários de cada plataforma ainda dependem de implementações específicas.

## Funcionalidades

### Implementadas na estrutura inicial

- [x] Organização modular do projeto.
- [x] Configuração do ambiente Python.
- [x] Inicialização da planilha de acompanhamento.
- [x] Cadastro manual de oportunidades.
- [x] Seleção de currículo por área profissional.
- [x] Navegação automatizada com Selenium.
- [x] Assistência no preenchimento de candidaturas.
- [x] Registro do status das candidaturas.
- [x] Testes iniciais com Pytest.

### Em desenvolvimento / planejadas

- [ ] Busca automatizada de oportunidades.
- [ ] Extração de informações das vagas.
- [ ] Análise de compatibilidade entre currículo e requisitos.
- [ ] Identificação automática de palavras-chave.
- [ ] Preenchimento de formulários específicos por plataforma.
- [ ] Dashboard com indicadores de candidaturas.
- [ ] Sistema de notificações sobre novas oportunidades.
- [ ] Prevenção de cadastro duplicado de vagas.

## Estrutura do projeto

```text
JobApply-Automation/
│
├── main.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
│
├── data/
│   ├── curriculo/
│   │   ├── Abdiel_CV_Infraestrutura.pdf
│   │   └── Abdiel_CV_Desenvolvimento.docx
│   │
│   └── vagas.xlsx
│
├── jobapply/
│   ├── applications/
│   │   └── application_manager.py
│   │
│   ├── browser/
│   │   └── selenium_manager.py
│   │
│   ├── collectors/
│   │   └── job_collector.py
│   │
│   ├── resume/
│   │   └── resume_manager.py
│   │
│   ├── spreadsheet/
│   │   └── excel_manager.py
│   │
│   └── utils/
│       └── logger.py
│
└── tests/
    └── test_job_collector.py
```

*Observação: a estrutura acima representa a organização prevista. Ajuste os caminhos caso seus diretórios estejam organizados de outra maneira.*

## Requisitos

- Python 3.10 ou superior.
- Microsoft Edge, Google Chrome ou Firefox instalado, conforme a opção `BROWSER`.
- Visual Studio Code (recomendado).
- Ambiente virtual Python.
- Conexão com a internet.

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/abdieldeathayde/Tracking-for-Jobs.git
```

### 2. Acesse a pasta

```bash
cd JobApply-Automation
```

### 3. Crie o ambiente virtual

```bash
python -m venv env
```

### 4. Ative o ambiente virtual

**Windows PowerShell:**

```powershell
.\env\Scripts\Activate.ps1
```

### 5. Instale as dependências

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 6. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
CV_INFRA_PATH=data/curriculo/Abdiel_CV_Infraestrutura .pdf
CV_DEV_PATH=data/curriculo/Abdiel_CV_Desenvolvimento.pdf

BROWSER=edge
HEADLESS=false
WAIT_TIMEOUT=15
```

Use `BROWSER=edge`, `BROWSER=chrome` ou `BROWSER=firefox` para escolher o navegador.
Certifique-se de que os arquivos dos currículos estejam nos caminhos configurados.

## Como utilizar

### Inicializar o sistema

```bash
python main.py init
```

Inicializa a estrutura da planilha de acompanhamento.

### Consultar oportunidades

```bash
python main.py search --area ambas --plataforma linkedin
```

O LinkedIn é a plataforma padrão. A busca percorre automaticamente as
consultas `Java Developer`, `Fullstack developer`, `Frontend Developer`,
`Mobile Developer`, `Analista de TI Júnior` e `Analista de Suporte Junior`,
nas cidades Blumenau e Gaspar, com os filtros de modalidade selecionados.
Os anúncios encontrados são registrados na planilha, sem duplicar links.
Para escolher áreas, cidades ou modalidades:

```bash
python main.py search --area infra --local "Blumenau SC" "Gaspar SC" --modalidade Remoto Híbrido Presencial
```

A busca coleta os anúncios exibidos publicamente pelo LinkedIn. O site pode
limitar resultados ou solicitar login; nesses casos, a busca informa que não
conseguiu carregar anúncios. A coleta não envia candidaturas.

### Cadastrar uma vaga

**Infraestrutura de TI:**

```bash
python main.py add --area infra
```

**Desenvolvimento:**

```bash
python main.py add --area dev
```

O sistema solicita os dados da oportunidade e registra as informações na planilha.

### Abrir uma candidatura

```bash
python main.py open --url "URL_DA_VAGA" --empresa "Empresa" --cargo "Analista de Cibersegurança"
```

O currículo é escolhido pelo cargo: programação/desenvolvimento usa o currículo
de desenvolvimento; infraestrutura, suporte e segurança da informação usam o
currículo de infraestrutura. Se o cargo não for reconhecido, informe
`--area infra` ou `--area dev`. O navegador prepara a candidatura para revisão;
o envio ainda é manual.

## Planilha de acompanhamento

O arquivo `data/vagas.xlsx` centraliza os registros das oportunidades.

Informações controladas:

- Empresa;
- Cargo;
- Modalidade;
- Localidade;
- Salário;
- Requisitos;
- Compatibilidade;
- Link da vaga;
- Plataforma;
- Data em que a vaga foi encontrada;
- Data da candidatura;
- Status da candidatura;
- Situação da vaga;
- Currículo utilizado;
- Observações.

## Fluxo de funcionamento

```text
Pesquisa de oportunidades
          |
          v
Identificação da vaga
          |
          v
Seleção do currículo
          |
          v
Análise das informações
          |
          v
Navegação com Selenium
          |
          v
Revisão humana
          |
          v
Envio manual da candidatura
          |
          v
Registro na planilha Excel
```

## Testes

Execute os testes automatizados com:

```bash
python -m pytest -v
```

## Segurança e boas práticas

- Não armazene senhas ou credenciais diretamente no código.
- Mantenha o arquivo `.env` fora do controle de versão.
- Respeite os termos de uso das plataformas de emprego.
- Não tente contornar CAPTCHA, autenticação ou mecanismos de segurança.
- Revise os dados antes de enviar qualquer candidatura.
- Mantenha os currículos atualizados.

## Próximas melhorias

1. Implementar coletores específicos para cada plataforma.
2. Desenvolver mecanismo de análise de compatibilidade com NLP.
3. Criar um dashboard de acompanhamento.
4. Implementar controle de duplicidade de vagas.
5. Melhorar a automação de formulários com revisão humana.
6. Desenvolver relatórios de desempenho das candidaturas.

## Autor

**Abdiel de Athayde**

Desenvolvido como projeto de estudo e aplicação prática de Python, automação web, organização de dados e desenvolvimento de soluções para produtividade profissional.

<p align="center">
  <strong>JobApply Automation</strong><br>
  <em>Menos trabalho manual. Mais organização na busca por oportunidades.</em>
</p>
