
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response

import numpy as np

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def main():

    if request.method == "POST":

        req = request.form


        # missing
        missing = list()

        for k, v in req.items():

            if v=="":
                missing.append(k)

        if missing:
            feedback = f"Brak danych dla {', '.join(missing)}"
            return render_template("main.html", feedback=feedback)


        N = float(req["kapital"])
        r = float(req["procent"])/100
        n = int(req["liczba_rat"])


        print("--obliczenia--")

        # pożyczona kwota - kapitał
        #N = 460000

        # oprocentowanie w skali roku
        #r = (2.2 + 0 + 5.97)/100

        # liczba rat płatnych w ciągu roku
        k = 12

        # liczba rat ogółem
        #n = 360

        L = (N*r)
        M = k*(1-np.power(k/(k+r),n) )
        I = L/M

        I = round(I, 2)


        return render_template("main.html", feedback="rata równa : {}".format(I))

    return render_template("main.html")




if __name__ == "__main__":
    print("welcome to bank app")
    app.run(debug=True)
