from flask import Flask
from flask import request


app = Flask(__name__)


@app.route("/",  methods=['GET', 'POST', 'DELETE'])
def hello():
    if request.method == 'POST':
        print(request.get_data())
        return 'ok'


if __name__ == '__main__':
    app.run(debug=True, port=5000)
