from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

import os

@app.route('/')
def index():
    scripts = [f for f in os.listdir('scripts') if f.endswith('.py')]
    return render_template('index.html', scripts=scripts)

@app.route('/run_script', methods=['POST'])
def run_script():
    script_name = request.form['script_name']
    try:
        output = subprocess.check_output(['python', script_name], stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    return render_template('index.html', output=output)

if __name__ == '__main__':
    app.run(debug=True)
