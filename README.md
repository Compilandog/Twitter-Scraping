# Tweet Collector Web App

Esta aplicação web permite criar **listas de perfis** do Twitter e gerar relatórios em CSV, XML e PDF com os tweets coletados em um intervalo de datas. É possível escolher mais de um formato ao mesmo tempo.

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalação

```bash
pip install -r requirements.txt
```

Para iniciar rapidamente no macOS, basta **dar dois cliques** em `start.command`.
Ele cria um ambiente virtual, instala as dependências e abre o navegador
automaticamente. Em outros sistemas, execute `./run.sh` manualmente ou
`python run_app.py`. Esse script procura uma porta livre a partir da 5000 e abre
o navegador no endereço encontrado.

## Uso

Caso deseje iniciar manualmente, ative o ambiente virtual e execute `python app.py`.

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
lgt9id-codex/criar-execução-automática-e-relatórios-dinâmicos

4ibx2l-codex/criar-execução-automática-e-relatórios-dinâmicos
main
aberto automaticamente no endereço disponível. A página inicial exibe dois
botões: **Gerenciar Listas** e **Gerar Relatório**. Primeiro crie uma ou mais
listas de perfis acessando **Gerenciar Listas**. Em seguida, em **Gerar
Relatório**, escolha a lista desejada, defina o período (com data e hora) e
marque os formatos desejados. Se mais de um formato for selecionado, um arquivo
ZIP com todos eles será oferecido para download. Um resumo da coleta é exibido
na própria página.
lgt9id-codex/criar-execução-automática-e-relatórios-dinâmicos
aberto automaticamente no endereço disponível. Primeiro crie uma ou mais listas
de perfis na tela **Listas**. Em seguida, em **Solicitar Relatório**, escolha a
lista desejada, defina o período (com data e hora) e o formato do arquivo. O
relatório é oferecido para download automaticamente e um resumo da coleta é
exibido na própria página.
main
main
