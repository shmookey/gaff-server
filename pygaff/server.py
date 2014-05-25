from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/crop")
def crop_image ():
    return "not implemented yet!"

if __name__ == "__main__":
    app.run()

