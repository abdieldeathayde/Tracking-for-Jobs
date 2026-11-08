# JobApply

**Organize vagas, acompanhe candidaturas e prepare cada aplicação com mais clareza.**

JobApply é uma ferramenta de linha de comando em Python para registrar oportunidades em uma planilha Excel, acompanhar o andamento dos processos seletivos e apoiar a pesquisa de vagas.

## O que já funciona

- Registra vagas manualmente e evita duplicatas pelo link.
- Mantém uma planilha Excel com filtros, listas de status e um painel resumido.
- Pesquisa anúncios públicos do LinkedIn e salva os resultados encontrados.
- Abre páginas de vagas no navegador e pode anexar o currículo selecionado ao primeiro campo de arquivo disponível.
- Escolhe um currículo de infraestrutura ou desenvolvimento a partir da área informada ou do cargo.

O envio de candidaturas é sempre manual. A pesquisa de Gupy e Indeed abre páginas para consulta; a extração automática está implementada apenas para anúncios públicos do LinkedIn.

## Requisitos

- Python 3.10 ou superior.
- Microsoft Edge, Google Chrome ou Firefox instalado para os comandos de navegador.
- Uma conexão com a internet para pesquisar ou abrir vagas.

## Instalação

```bash
git clone https://github.com/abdieldeathayde/Tracking-for-Jobs.git
cd Tracking-for-Jobs
python -m venv .venv
```

Ative o ambiente virtual:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Instale as dependências e prepare a configuração local:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copie `.env.example` para `.env` e ajuste os caminhos dos currículos se necessário:

```powershell
Copy-Item .env.example .env
```

```env
CV_INFRA_PATH=data/curriculo/Abdiel_CV_Infraestrutura.pdf
CV_DEV_PATH=data/curriculo/Abdiel_CV_Desenvolvimento.pdf
BROWSER=edge
HEADLESS=false
WAIT_SECONDS=15
```

`BROWSER` aceita `edge`, `chrome` ou `firefox`. `HEADLESS=true` executa o navegador sem janela visível. Os caminhos dos currículos podem apontar para outros arquivos PDF.

## Comandos

Execute os comandos a partir da pasta raiz do repositório.

### Criar a planilha

```bash
python main.py init
```

O arquivo será criado em `data/vagas.xlsx`, com abas de vagas e painel.

### Cadastrar uma vaga

Os campos de empresa, cargo, URL e área são obrigatórios:

```bash
python main.py add --empresa "Empresa Exemplo" --cargo "Analista de Suporte" --url "https://example.com/vaga" --area infra --modalidade Remoto --localidade "Blumenau SC" --plataforma LinkedIn
```

`--area` aceita `infra` ou `dev`. `--modalidade`, `--localidade` e `--plataforma` são opcionais.

### Listar e atualizar candidaturas

```bash
python main.py list
python main.py list --status "Em análise"
python main.py summary
python main.py update --id 3 --status "Em análise"
```

`summary` mostra o total de vagas e a contagem por status. Ao atualizar uma vaga para `Enviada`, a data da candidatura é preenchida automaticamente e preservada em atualizações futuras.

Os status aceitos são: `Não iniciada`, `Em progresso`, `Enviada`, `Em análise`, `Entrevista`, `Congelada`, `Desclassificado`, `Aprovado`, `Recusada` e `Encerrada`.

### Pesquisar oportunidades

```bash
python main.py search --area dev --local "Blumenau SC" "Gaspar SC" --modalidade Remoto Híbrido Presencial --plataforma linkedin
```

As áreas disponíveis são `infra`, `dev` e `ambas`. Sem opções adicionais, a pesquisa usa Blumenau e Gaspar (SC), todas as modalidades e LinkedIn. Os anúncios públicos encontrados são deduplicados pelo link antes de serem salvos.

Para abrir uma página de consulta do Indeed ou Gupy, use `--plataforma indeed` ou `--plataforma gupy`. Nessas plataformas a ferramenta não coleta nem registra anúncios automaticamente.

### Preparar uma candidatura para revisão

```bash
python main.py open --url "https://example.com/vaga" --empresa "Empresa Exemplo" --cargo "Desenvolvedor Java" --area dev
```

O navegador abre a página e tenta anexar o currículo. Revise os dados e faça o envio manualmente no site. A ferramenta não preenche todos os campos nem envia a candidatura em seu nome.

## Planilha

A planilha armazena empresa, cargo, modalidade, localidade, salário, requisitos, compatibilidade, URL, plataforma, datas, status, currículo utilizado e observações. O painel resume os status das candidaturas. Os dados ficam localmente em `data/vagas.xlsx`.

## Estrutura

```text
main.py                 Interface de linha de comando
jobapply/               Código da aplicação
  applications/         Apoio à candidatura assistida
  browser/              Inicialização do Selenium
  collectors/            Cadastro e coleta do LinkedIn
  resume/                Seleção do currículo
  spreadsheet/           Planilha e painel
  utils/                 Logs
  config.py              Configuração e caminhos
data/curriculo/          Currículos configurados localmente
tests/                   Testes automatizados
```

## Testes

```bash
python -m pytest -v
```

## Melhorias planejadas

- Coleta específica de vagas em outras plataformas, respeitando os limites de cada site.
- Busca e filtros pela interface, com critérios configuráveis pelo usuário.
- Relatórios mais detalhados sobre o andamento das candidaturas.
