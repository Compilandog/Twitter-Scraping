from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)
import datetime as dt
import pandas as pd
import snscrape.modules.twitter as snt
from snscrape.base import ScraperException
import os
import json
from fpdf import FPDF
import logging
import traceback
import io
import zipfile
import uuid

app = Flask(__name__)
app.secret_key = 'change-this-secret'
LISTS_FILE = 'lists.json'
DOWNLOADS = {}

logging.basicConfig(level=logging.INFO)


def load_lists():
    if not os.path.exists(LISTS_FILE):
        return {}
    with open(LISTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_lists(data):
    with open(LISTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def collect_tweets(profiles, since, until):
    """Collect tweets handling Twitter API changes gracefully.

    This function first tries the default ``snscrape`` GraphQL endpoint. If it
    fails (for example returning HTTP 404 when GraphQL is blocked), it falls
    back to the legacy HTML scraping mode. As a last resort it attempts to use
    ``twint`` when that package is available. Only the successfully retrieved
    tweets are returned in a DataFrame.
    """

    records = []
    for user in profiles:
        query = f"from:{user} since:{since} until:{until}"
        scraper = snt.TwitterSearchScraper(query)

        def _append(tweet):
            records.append(
                {
                    "hora": tweet.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "usuario": f"@{user}",
                    "link": f"https://twitter.com/{user}/status/{tweet.id}",
                }
            )

        try:
            for t in scraper.get_items():
                _append(t)
            continue
        except ScraperException as e:
            logging.warning("snscrape default mode failed for %s: %s", user, e)

        # Second attempt: disable GraphQL usage and parse HTML instead
        try:
            scraper.useScrapeApi = False  # type: ignore[attr-defined]
            for t in scraper.get_items():
                _append(t)
            continue
        except ScraperException as e:
            logging.warning("snscrape HTML mode failed for %s: %s", user, e)

        # Final attempt using twint if installed
        try:
            import nest_asyncio
            import twint

            nest_asyncio.apply()
            c = twint.Config()
            c.Username = user
            c.Since = since.replace("_", " ")
            c.Until = until.replace("_", " ")
            c.Pandas = True
            twint.run.Search(c)
            df_twint = twint.storage.panda.Tweets_df
            if df_twint is not None:
                for _, row in df_twint.iterrows():
                    records.append(
                        {
                            "hora": row["date"],
                            "usuario": f"@{user}",
                            "link": row["link"],
                        }
                    )
            # cleanup global dataframe for the next run
            twint.storage.panda.clean()
        except Exception as e:  # noqa: BLE001
            logging.error("twint fallback failed for %s: %s", user, e)

    return pd.DataFrame(records)


def df_to_pdf_bytes(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    col_width = pdf.w / 3 - 2
    row_height = pdf.font_size * 1.5
    headers = ["hora", "usuario", "link"]
    for h in headers:
        pdf.cell(col_width, row_height, h, border=1)
    pdf.ln(row_height)
    for _, row in df.iterrows():
        pdf.cell(col_width, row_height, str(row["hora"]), border=1)
        pdf.cell(col_width, row_height, str(row["usuario"]), border=1)
        pdf.cell(col_width, row_height, str(row["link"]), border=1)
        pdf.ln(row_height)
    return pdf.output(dest="S").encode("latin-1")


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/lists', methods=['GET', 'POST'])
def lists_view():
    data = load_lists()
    selected = request.args.get("list")
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_list":
            name = request.form["new_list"].strip()
            if name and name not in data:
                data[name] = []
                selected = name
                flash("Lista criada.", "success")
            else:
                flash("Nome inválido ou já existe.", "error")
        elif action == "delete_list":
            name = request.form["listname"]
            if name in data:
                del data[name]
                selected = None
                flash("Lista removida.", "success")
        elif action == "add_profile":
            name = request.form["listname"]
            profile = request.form["profile"].strip().lstrip("@")
            if profile and profile not in data.get(name, []):
                data[name].append(profile)
                flash("Perfil adicionado.", "success")
            selected = name
        elif action == "remove_profile":
            name = request.form["listname"]
            profile = request.form["profile"]
            if profile in data.get(name, []):
                data[name].remove(profile)
                flash("Perfil removido.", "success")
            selected = name
        save_lists(data)
        return redirect(url_for("lists_view", list=selected))
    if not selected and data:
        selected = next(iter(data.keys()))
    return render_template("lists.html", lists=data, selected=selected)


@app.route('/collect', methods=['GET', 'POST'])
def collect():
    data = load_lists()
    if not data:
        flash('Crie uma lista antes de coletar.', 'error')
        return redirect(url_for('lists_view'))
    selected = request.args.get('list') or request.form.get('list') or next(iter(data.keys()))
    if request.method == 'POST':
        list_name = request.form.get('list')
        start_raw = request.form.get('start')
        end_raw = request.form.get('end')
        formats = request.form.getlist('format')
        output_filename = request.form.get('output') or 'tweets'

        try:
            start_dt = dt.datetime.fromisoformat(start_raw)
            end_dt = dt.datetime.fromisoformat(end_raw)
        except (ValueError, TypeError):
            flash('Datas em formato invalido.', 'error')
            return render_template('collect.html', lists=sorted(data.keys()), selected=list_name,
                                   start=start_raw, end=end_raw, fmt_list=formats, output=output_filename)
        if end_dt < start_dt:
            flash('A data de fim nao pode ser menor que a de inicio.', 'error')
            return render_template('collect.html', lists=sorted(data.keys()), selected=list_name,
                                   start=start_raw, end=end_raw, fmt_list=formats, output=output_filename)

        since = start_raw.replace('T', '_')
        until = end_raw.replace('T', '_')

        try:
            df = collect_tweets(data[list_name], since, until)
        except ScraperException as e:
            app.logger.error(f"Erro no snscrape: {e}")
            return render_template('error.html', message='Não foi possível coletar tweets neste momento. Tente novamente mais tarde.')

        if df.empty:
            return render_template('error.html', message='Nenhum tweet encontrado para o período selecionado.')

        summary_lines = []
        for user, count in df['usuario'].value_counts().items():
            summary_lines.append(f"{user}: {count} links")
        summary_lines.append(f"Total: {len(df)} tweets")

        if not formats:
            flash('Selecione ao menos um formato.', 'error')
            return render_template('collect.html', lists=sorted(data.keys()), selected=list_name,
                                   start=start_raw, end=end_raw, fmt_list=formats, output=output_filename)

        if len(formats) == 1:
            fmt = formats[0]
            if fmt == 'csv':
                buf = io.StringIO()
                df.to_csv(buf, index=False)
                buf.seek(0)
                data_bytes = buf.getvalue().encode('utf-8')
                mime = 'text/csv'
                name = f"{output_filename}.csv"
            elif fmt == 'xml':
                buf = io.StringIO()
                df.to_xml(buf, index=False, root_name='tweets', row_name='tweet')
                buf.seek(0)
                data_bytes = buf.getvalue().encode('utf-8')
                mime = 'application/xml'
                name = f"{output_filename}.xml"
            elif fmt == 'pdf':
                data_bytes = df_to_pdf_bytes(df)
                mime = 'application/pdf'
                name = f"{output_filename}.pdf"
        else:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, 'w') as zf:
                for fmt in formats:
                    if fmt == 'csv':
                        tmp = io.StringIO()
                        df.to_csv(tmp, index=False)
                        tmp.seek(0)
                        zf.writestr(f"{output_filename}.csv", tmp.getvalue())
                    elif fmt == 'xml':
                        tmp = io.StringIO()
                        df.to_xml(tmp, index=False, root_name='tweets', row_name='tweet')
                        tmp.seek(0)
                        zf.writestr(f"{output_filename}.xml", tmp.getvalue())
                    elif fmt == 'pdf':
                        zf.writestr(f"{output_filename}.pdf", df_to_pdf_bytes(df))
            zip_buf.seek(0)
            data_bytes = zip_buf.getvalue()
            mime = 'application/zip'
            name = f"{output_filename}.zip"

        file_id = str(uuid.uuid4())
        DOWNLOADS[file_id] = (data_bytes, mime, name)
        return render_template('success.html', url=url_for('download', file_id=file_id), summary=summary_lines)
    return render_template('collect.html', lists=sorted(data.keys()), selected=selected, fmt_list=[], start=None, end=None)


@app.route('/download/<file_id>')
def download(file_id):
    entry = DOWNLOADS.pop(file_id, None)
    if not entry:
        return render_template('error.html', message='Arquivo não encontrado.')
    data, mime, name = entry
    return send_file(io.BytesIO(data), mimetype=mime, as_attachment=True, download_name=name)


if __name__ == '__main__':
    app.run()
