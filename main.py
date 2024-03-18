from flask import Flask, request, jsonify, session, redirect, url_for, render_template, flash

app = Flask(__name__)
@app.route('/', methods=['get'])
def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run(debug=True)
