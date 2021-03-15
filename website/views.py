from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Review
from flask_login import login_required, current_user, login_user, logout_user


views = Blueprint("views",__name__)

@views.route("/",methods=["GET","POST"])
@login_required
def home():
    if request.method=="POST":
        firstname = request.form.get("fname")
        lastname = request.form.get("lname")
        if firstname != "" and lastname != "":

            with open("user.txt","a") as f:
                f.write(firstname+" "+lastname+"\n")
                flash("zarejstrowano uzytkownika","success")
        else:
            flash("nie podano uzytkownika", "error")
    return render_template("home.html",user=current_user)

@views.route("/test")
def test():
    with open("user.txt", "r") as f:
        data = f.readlines()
    return render_template("test.html",users = data)

@views.route("/add-file", methods=["GET","POST"])
def add_file():
    if request.method == "POST":
        file_name = request.form.get("file_name")
        with open(file_name, "w") as f:
            f.write("test")

    return render_template("add_file.html")

@views.route("/sign-up",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        plec = request.form.get("plec")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        print(email,plec,password1,password2)
        if len(email)<3:
            flash("zbyt krotki adres email", "error")
        elif len(password1)<6:
            flash("haslo zbyt krotkie", "error")
        elif len(password1) > 18:
            flash("hasło powinno byc max 18 znakow", "error")
        elif password1 != password2:
            flash("podane hasła są różne","error")
        else:
            flash("zarejestrowano pomyślnie","success")
            user = User(email=email, password=generate_password_hash(password1,method="sha256"), plec=plec, admin=False)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("views.home"))

    return render_template("signup.html",user=current_user)

@views.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password):

                flash("Zalogowano do serwisu ", "success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Nieporawne hasło ", "error")
        else:
            flash("Użytkownik nie istnieje", "error")
    return render_template("login.html",user=current_user)

@views.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.login"))

@views.route("/review", methods=["POST","GET"])
@login_required
def review():
    if request.method == "POST":
        review_note = request.form.get("review_note")
        print(review_note)
        uwaga = Review(text=review_note,id_user=current_user.id, status="w toku")
        db.session.add(uwaga)
        db.session.commit()
        flash("Twoja opinia zostala dodana", "success")
    return render_template("review.html", user=current_user)

@views.route("/settings", methods=["POST","GET"])
@login_required
def settings():
    if request.method == "POST":
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")


        if len(password1) < 6:
            flash("haslo zbyt krotkie", "error")
        elif len(password1) > 18:
            flash("hasło powinno byc max 18 znakow", "error")
        elif password1 != password2:
            flash("podane hasła są różne", "error")
        else:
            flash("hasło zostało pomyślnie", "success")
            current_user.password=generate_password_hash(password1, method="sha256")
            db.session.commit()
    return render_template("settings.html", user=current_user)

@views.route("/reviews", methods=["POST","GET"])
@login_required
def reviews():
    if current_user.admin:
        opinie = Review.query.all()
        wszyscy = User.query.all()
        maile={}
        for user in wszyscy:
            maile[user.id]=user.email
        return render_template("reviews.html", user=current_user, opinie=opinie, maile=maile)
    else:
        print("Brak dostepu")
        return redirect(url_for("views.home"))

@views.route("/set_status", methods=["GET"])
@login_required
def set_status():
    if request.method == "GET":

        action = request.args.get("action")
        review_id = request.args.get("review_id")

        review = Review.query.get(review_id)
        if review:
            if action == "zaakceptuj":
                flash("zakceptowane", "success")
                review.status= "zaakceptowane"
                db.session.commit()
            elif action == "odrzuc" :
                flash("odrzucone", "success")
                review.status = "odrzucone"
                db.session.commit()
    return redirect(url_for("views.reviews"))
