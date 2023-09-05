# file used for developing
from project import init_app

print(__name__)

app = init_app()

if __name__ == "__main__":
    app.run(port=80, debug=True)

    #app.run(host='0.0.0.0', port=5000)
