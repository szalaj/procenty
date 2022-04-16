
from flask import Flask, render_template, redirect, url_for, jsonify, request, make_response



app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def main():

    # tu po wypełnieniu i przesłaniu formularza
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


        # zmienne
        # pozyczony kapital
        N = float(req["kapital"])

        # oprocentowanie
        r = float(req["procent"])/100

        # liczba rat
        n = int(req["liczba_rat"])


        print("--obliczenia--")

        # liczba rat płatnych w ciągu roku
        k = 12

        # liczba rat ogółem
        #n = 360

        L = (N*r)
        M = k*(1-pow(k/(k+r),n) )
        I = L/M

        I = round(I, 2)


        return render_template("main.html", feedback="rata równa : {}".format(I))

    # tu zaczyna się aplikacja
    return render_template("main.html")




if __name__ == "__main__":
    print("welcome to bank app")
    app.run(debug=True)
