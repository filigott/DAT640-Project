from flask import Flask, render_template

ENABLE_DEBUG = True

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=ENABLE_DEBUG)
