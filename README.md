# Tweet Collector Web App

Esta aplicação web permite criar **listas de perfis** do Twitter e gerar relatórios em CSV, XML e PDF com os tweets coletados em um intervalo de datas. É possível escolher mais de um formato ao mesmo tempo.

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalação

```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` já exige `snscrape >= 0.7.0.20230622`. Para contar com o
fallback via **Twint**, instale também:

```bash
pip install git+https://github.com/twintproject/twint.git@origin/master
```

Para iniciar rapidamente no macOS, basta **dar dois cliques** em `start.command`.
Ele cria um ambiente virtual, instala as dependências e abre o navegador
automaticamente. Em outros sistemas, execute `./run.sh` manualmente ou
`python run_app.py`. Esse script procura uma porta livre a partir da 5000 e abre
o navegador no endereço encontrado.

## Uso

Caso deseje iniciar manualmente, ative o ambiente virtual e execute `python app.py`.

### Coleta de Tweets resiliente

O Twitter costuma alterar com frequência os seus endpoints e isso pode
resultar em erros `404` ou bloqueios inesperados durante a coleta. A função
`collect_tweets` deste projeto tenta contornar esse problema de forma
automática. Ela executa duas estratégias em sequência:

1. **`snscrape` em modo HTML** – o aplicativo força `useScrapeApi = False`,
   ignorando o endpoint GraphQL que costuma retornar `404`.
2. **`twint` como último recurso** – caso a biblioteca esteja instalada, ela é
   usada para extrair os tweets diretamente do HTML.

Desse modo, se uma abordagem falhar, outra é tentada sem que o usuário
perceba, aumentando as chances de sucesso.

### Empacotamento

**macOS**

```bash
python setup_py2app.py py2app
```

O aplicativo `.app` será criado em `dist/`.

**Windows**

```bash
python setup_pyinstaller.py
```

O executável `.exe` será criado em `dist/`.

Ao executar o aplicativo, o servidor Flask será iniciado e o navegador será
aberto automaticamente no endereço disponível. A página inicial exibe dois
botões: **Gerenciar Listas** e **Gerar Relatório**. Primeiro crie uma ou mais
listas de perfis acessando **Gerenciar Listas**. Em seguida, em **Gerar
Relatório**, escolha a lista desejada, defina o período (com data e hora) e
marque os formatos desejados. Se mais de um formato for selecionado, um arquivo
ZIP com todos eles será oferecido para download. Um resumo da coleta é exibido
na própria página.
