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
import os
import json
from fpdf import FPDF
import logging
import traceback
import io
import zipfile

app = Flask(__name__)
app.secret_key = 'change-this-secret'
LISTS_FILE = 'lists.json'

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
    records = []
    for user in profiles:
        query = f"from:{user} since:{since} until:{until}"
        for t in snt.TwitterSearchScraper(query).get_items():
            records.append(
                {
                    "hora": t.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "usuario": f"@{user}",
                    "link": f"https://twitter.com/{user}/status/{t.id}",
                }
            )
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
    profiles = data.get(selected, [])
    return render_template("lists.html", lists=sorted(data.keys()), selected=selected, profiles=profiles)


@app.route('/collect', methods=['GET', 'POST'])
def collect():
    data = load_lists()
    if not data:
        flash('Crie uma lista antes de coletar.', 'error')
        return redirect(url_for('lists_view'))
    selected = request.args.get('list') or request.form.get('list') or next(iter(data.keys()))
    if request.method == 'POST':
        list_name = request.form.get('list')
        start_date = request.form.get('start')
        start_time = request.form.get('start_time') or '00:00'
        end_date = request.form.get('end')
        end_time = request.form.get('end_time') or '23:59'
        formats = request.form.getlist('format')
        output_filename = request.form.get('output') or 'tweets'

        since = f"{start_date}_{start_time}"
        until = f"{end_date}_{end_time}"

        try:
            dt.datetime.fromisoformat(f"{start_date}T{start_time}")
            end_dt = dt.datetime.fromisoformat(f"{end_date}T{end_time}")
        except ValueError:
            flash('Datas em formato invalido.', 'error')
            return render_template('collect.html', lists=sorted(data.keys()), selected=list_name,
                                   start_date=start_date, end_date=end_date, start_time=start_time,
                                   end_time=end_time, fmt_list=formats, output=output_filename)
        if end_dt < dt.datetime.fromisoformat(f"{start_date}T{start_time}"):
            flash('A data de fim nao pode ser menor que a de inicio.', 'error')
            return render_template('collect.html', lists=sorted(data.keys()), selected=list_name,
                                   start_date=start_date, end_date=end_date, start_time=start_time,
                                   end_time=end_time, fmt_list=formats, output=output_filename)

        try:
            df = collect_tweets(data[list_name], since, until)
        except snt.base.ScraperException:
            logging.error("ScraperException\n%s", traceback.format_exc())
            return render_template('error.html', message='Não foi possível coletar tweets neste momento. Tente novamente mais tarde.')

        if df.empty:
            return render_template('error.html', message='Nenhum tweet encontrado para o período selecionado.')

        summary_lines = []
        for user, count in df['usuario'].value_counts().items():
            summary_lines.append(f"{user}: {count} links")
        summary_lines.append(f"Total: {len(df)} tweets")
        flash("; ".join(summary_lines), "success")

        lgt9id-codex/criar-execução-automática-e-relatórios-dinâmicos
        if not formats:
            flash('Selecione ao menos um formato.', 'error')
            
 4ibx2l-codex/criar-execução-automática-e-relatórios-dinâmicos
        if not formats:
            flash('Selecione ao menos um formato.', 'error')

        if fmt == 'csv':
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            buf.seek(0)
            return send_file(io.BytesIO(buf.getvalue().encode('utf-8')),
                             mimetype='text/csv',
                             as_attachment=True,
                             download_name=f"{output_filename}.csv")
        elif fmt == 'xml':
            buf = io.StringIO()
            df.to_xml(buf, index=False, root_name='tweets', row_name='tweet')
            buf.seek(0)
            return send_file(io.BytesIO(buf.getvalue().encode('utf-8')),
                             mimetype='application/xml',
                             as_attachment=True,
                             download_name=f"{output_filename}.xml")
        elif fmt == 'pdf':
            pdf_bytes = df_to_pdf_bytes(df)
            return send_file(io.BytesIO(pdf_bytes),
                             mimetype='application/pdf',
                             as_attachment=True,
                             download_name=f"{output_filename}.pdf")
        else:
            flash('Formato desconhecido.', 'error')
main
main
            return render_template('collect.html', lists=sorted(data.keys()), selected=list_name,
                                   start_date=start_date, end_date=end_date, start_time=start_time,
                                   end_time=end_time, fmt_list=formats, output=output_filename)

        if len(formats) == 1:
            fmt = formats[0]
            if fmt == 'csv':
                buf = io.StringIO()
                df.to_csv(buf, index=False)
                buf.seek(0)
                return send_file(io.BytesIO(buf.getvalue().encode('utf-8')),
                                 mimetype='text/csv',
                                 as_attachment=True,
                                 download_name=f"{output_filename}.csv")
            elif fmt == 'xml':
                buf = io.StringIO()
                df.to_xml(buf, index=False, root_name='tweets', row_name='tweet')
                buf.seek(0)
                return send_file(io.BytesIO(buf.getvalue().encode('utf-8')),
                                 mimetype='application/xml',
                                 as_attachment=True,
                                 download_name=f"{output_filename}.xml")
            elif fmt == 'pdf':
                pdf_bytes = df_to_pdf_bytes(df)
                return send_file(io.BytesIO(pdf_bytes),
                                 mimetype='application/pdf',
                                 as_attachment=True,
                                 download_name=f"{output_filename}.pdf")
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
            return send_file(zip_buf,
                             mimetype='application/zip',
                             as_attachment=True,
                             download_name=f"{output_filename}.zip")
    return render_template('collect.html', lists=sorted(data.keys()), selected=selected, fmt_list=[])


if __name__ == '__main__':
    app.run()
