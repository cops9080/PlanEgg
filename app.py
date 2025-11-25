from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/quest')
def quest():
    return render_template("quest_preview.html")

@app.route('/questlist')
def questlist():
    pass
    # return render_template()

@app.route('/market')
def market():
    return render_template("market.html")

if __name__ == '__main__':
    app.run()
