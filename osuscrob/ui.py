#!/usr/bin/env python3

from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    resp = """
        uwu
    """
    return resp


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
