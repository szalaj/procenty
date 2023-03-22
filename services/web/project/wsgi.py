# file used for developing
from project import init_app


app = init_app()

if __name__ == "__main__":
    print('---start---')
    app.run(port=5000, debug=True)

    #app.run(host='0.0.0.0', port=5000)
