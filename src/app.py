from flask import Flask, render_template

# start application
app = Flask(__name__)


# logger = logging.basicConfig(level=logging.DEBUG)


@app.route('/hello')
def hello_world():
    return render_template('hello.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8080)
