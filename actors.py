# using python 3
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from gspread import CellNotFound
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from data import ACTORS

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

app = Flask(__name__)
# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'some?bamboozle#string-foobar'
# Flask-Bootstrap requires this line
Bootstrap(app)
# this turns file-serving to static, using Bootstrap files installed in env
# instead of using a CDN
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# with Flask-WTF, each web form is represented by a class
# "NameForm" can change; "(FlaskForm)" cannot
# see the route for "/" and "index.html" to see how this is used
class NameForm(FlaskForm):
    name = StringField('What is your Bigo VIP Token?', validators=[Required()])
    response = StringField('VIP Points')
    submit = SubmitField('Submit')

# define functions to be used by the routes (just one here)

# retrieve all the names from the dataset and put them into a list
def get_names(source):
    names = []
    for row in source:
        name = row["name"]
        names.append(name)
    return sorted(names)

# all Flask routes below

# two decorators using the same function
@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name('VIP Zone-dc966a6ff3a4.json', scope)

    client = gspread.authorize(creds)

    sheet = client.open('US/CA VIP POINTS CHECK UP').sheet1

    pp = pprint.PrettyPrinter()


    names = get_names(ACTORS)
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    message = ""
    if form.validate_on_submit():
        name = form.name.data

        try:
            x = sheet.find(name)

            form.name.data = name

            form.response.data = sheet.cell(x.row,11).value

        except CellNotFound:

            form.response.data = "We can't find your record here. " \
                             "Please send your ID to BIGOAMERICA@BIGO.TV, " \
                             "we will get you back within 3 business days."

        '''
        if name in names:
            message = "Yay! " + name + "!"
            # empty the form field
            form.name.data = ""
        else:
            message = "That actor is not in our database."
        '''
    # notice that we don't need to pass name or names to the template
    return render_template('index.html', form=form, message=message)

# keep this as is
if __name__ == '__main__':
    app.run(host='0.0.0.0')

