from flask import Flask, render_template
from api import api


ENABLE_DEBUG = True

app = Flask(__name__)
app.register_blueprint(api)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=ENABLE_DEBUG, port=5001)
