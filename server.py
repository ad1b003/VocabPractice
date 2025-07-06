from flask import Flask, redirect, render_template, request, session, url_for
from gspread import authorize
from google.oauth2.service_account import Credentials
from os import environ
# from pathlib import Path
# from dotenv import load_dotenv
# from os import getenv


app = Flask(__name__)

# env_file_path = Path('private/.env')
# load_dotenv(env_file_path)

app.secret_key = environ.get('FLASK_SECRET_KEY')

gsheets_scopes = [environ.get('GSHEETS_SCOPES')]
gsheets_credentials = Credentials.from_service_account_file(
    environ.get('GSHEETS_CREDENTIALS'), scopes=gsheets_scopes)

gsheets = authorize(gsheets_credentials)

WORKBOOK_IDS = (environ.get('GSHEETS_WORKBOOK_ID_EASY'), environ.get(
    'GSHEETS_WORKBOOK_ID_MEDIUM'), environ.get('GSHEETS_WORKBOOK_ID_HARD'))

workbooks = {}

for wb_id in WORKBOOK_IDS:
    wb = gsheets.open_by_key(wb_id)
    workbooks[wb_id.strip()] = {
        'object': wb,
        'title': wb.title
    }


def list_sheets(workbook):
    return [ws.title for ws in workbook.worksheets()]


def get_sheet(workbook, sheet_name):
    return workbook.worksheet(sheet_name)


def read_sheet_data(sheet):
    return sheet.get_all_records()


# --------- S E R V E R C O D E --------- #


@app.route("/sign-in", methods=["POST"])
def signIn():
    if session.get('user'):
        return redirect(url_for('home'))
    username = request.form.get('username')
    session['user'] = username
    print(session.get('user'))
    return redirect(url_for('home'))


@app.route("/sign-out")
def signOut():
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route("/")
def home():
    if session.get('user'):
        # return "welcome back"
        return render_template('index.html', workbooks=workbooks, list_sheets=list_sheets)
    return render_template('sign-in.html')


@app.route("/<workbook_id>/<sheet_name>")
def view_sheet(workbook_id, sheet_name):
    workbook_entry = workbooks.get(workbook_id)
    if not workbook_entry:
        return f"Workbook with ID {workbook_id} not found", 404

    workbook = workbook_entry['object']

    try:
        sheet = get_sheet(workbook, sheet_name)
        data = read_sheet_data(sheet)
    except Exception as e:
        return f"Error: {e}", 500

    return render_template('sheet.html', sheet_name=sheet_name, data=data)


# if __name__ == "__main__":
#     app.run()
