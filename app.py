
from flask import Flask,render_template, request, redirect, url_for
from flask_alembic import Alembic

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
db.init_app(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    count = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __str__(self):
        return f'{self.name} / {self.count} / {self.price} PLN'



class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False)

    def __str__(self):
        return f' {self.balance} PLN'



class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    product = db.Column(db.String, nullable=True)
    count = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Float, nullable=True)

    def __str__(self):
        return f'{self.id} / {self.action} / {self.amount}PLN / {self.product} / {self.count}{self.price} PLN'


with app.app_context():
    db.create_all()



@app.route("/", methods=['POST', 'GET'])
def main_page():

    title = "System accountant - strona główna"
    products = db.session.query(Product).all()
    balance = db.session.query(Account).first()
    context = {"title": title,


               "products": products,
               "balance": balance}

    if  request.method == "POST":
        # kwota = float(request.form.get("kwota",0))

        k_produkt = request.form.get("zakup_produkt")
        k_ilosc = int(request.form.get("zakup_ilosc", 0))
        k_cena = float(request.form.get("zakup_cena", 0))

        action = db.Column(db.String, nullable=False)
        amount = db.Column(db.Float, nullable=False)
        product = db.Column(db.String, nullable=True)
        count = db.Column(db.Integer, nullable=True)
        price = db.Column(db.Float, nullable=True)


        p = db.session.query(Product).filter(Product.name == k_produkt).first()
        b = db.session.query(Account).first()
        h = History(action="kupno", amount=k_cena * k_ilosc, product=k_produkt, count=k_ilosc, price=k_cena)
        if not p:
            p = Product(name=k_produkt, count=0, price=0)
        p.count += k_ilosc
        p.price = k_cena
        b.balance -= k_cena * k_ilosc

        db.session.add(p)
        db.session.add(h)
        db.session.add(b)
        db.session.commit()


        context = {
           "title": title,
            "products": products
        }
        return redirect(url_for("main_page"))


    return render_template("main_page.html", context = context)

@app.route("/sale", methods=['POST', 'GET'])
def sale():

    title = "System accountant - strona główna"
    products = db.session.query(Product).all()
    context = {"title": title,


               "products": products}


    if  request.method == "POST":
        s_produkt = request.form.get("sprzedaz_produkt")
        s_ilosc = int(request.form.get("sprzedaz_ilosc", 0))
        s_cena = float(request.form.get("sprzedaz_cena", 0))


        p = db.session.query(Product).filter(Product.name == s_produkt).first()
        b = db.session.query(Account).first()
        h = History(action="sprzedaż", amount=s_cena * s_ilosc, product=s_produkt, count=s_ilosc, price=s_cena)

        if not p:
            return render_template("main_page_error.html", context=context)

        p.count -= s_ilosc
        b.balance += s_cena * s_ilosc

        db.session.add(h)
        db.session.add(p)
        db.session.add(b)
        db.session.commit()

        context = {

            "products": products
        }

    return redirect(url_for("main_page"))

@app.route("/balance", methods=['POST', 'GET'])
def balance():

    title = "System accountant - strona główna"
    balance = db.session.query(Account).first()
    products = db.session.query(Product).all()

    context = {"title": title,

                "products": products,
               "balance": balance
               }

    if  request.method == "POST":
        kwota = float(request.form.get("kwota",0))

        if kwota >0:
            akcja = "wpłata"

        else:
            akcja = "wypłata"


        h = History(action=akcja, amount=kwota, product=0, count=0, price=0)

        b = db.session.query(Account).first()
        if not b:
            b = Account(balance=0)

        b.balance += kwota
        db.session.add(h)
        db.session.add(b)
        db.session.commit()

        context = {
            "balance": balance
                   }

    return redirect(url_for("main_page"))

@app.route("/historia", methods=['POST', 'GET'])
def history():
    history = db.session.query(History).all()


    title = "System accountant - historia"
    okres_od = int(request.form.get("okres_od",0))
    okres_do = int(request.form.get("okres_do",0))
    context = {
        "title": title,


        "history": history
    }

    return render_template("history.html", context = context)


@app.route("/historia2", methods=['POST', 'GET'])
def history_date():
    history = db.session.query(History).all()

    title = "System accountant - historia"
    okres_od = int(request.form.get("okres_od",0))
    okres_do = int(request.form.get("okres_do",0))


    history_period = db.session.query(History).filter(History.id >= okres_od, History.id <= okres_do)

    context = {
        "title": title,


        "history": history,
        "history_period": history_period
    }


    return render_template("history.html", context = context)

alembic = Alembic()
alembic.init_app(app)

