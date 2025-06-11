# Tweet Collector Web App

Esta aplicação web permite criar **listas de perfis** do Twitter e gerar relatórios em CSV, XML ou PDF com os tweets coletados em um intervalo de datas.

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
`python run_app.py`.

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

Abra o endereço exibido no terminal (por padrão `http://localhost:5000`; se a
porta estiver em uso será escolhida a próxima disponível). Primeiro crie uma ou
mais listas de perfis na tela **Listas**. Em seguida, em **Solicitar Relatório**,
escolha a lista desejada, defina o período (com data e hora) e o formato do
arquivo. O arquivo é oferecido para download automaticamente.
