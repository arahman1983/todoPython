import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///todo.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""
    if request.method == "POST":
       print ("post")
        # return render_template("index.html", len=len(items), items = items)
    else:
        items = db.execute("SELECT todo.id as t_id,description,isComplete, title FROM todo INNER JOIN categories ON categories.id = todo.cat_id WHERE user_id=:user_id  AND todo.isDeleted='false'", user_id= session["user_id"])
        cats = db.execute("SELECT * FROM categories")
        return render_template("index.html", len=len(items), items = items, lenCat=len(cats), cats=cats)
    return apology("TODO")

@app.route("/deleteitem/<page_id>")
@login_required
def delete(page_id):
    """Show history of transactions"""
    pagid = int(page_id)
    db.execute("UPDATE todo SET isDeleted='true' WHERE id=?",pagid )
    return redirect("/")

    return apology("TODO")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        if not request.form.get("item"):
            return apology("must provide Item describtion", 403)

        if not request.form.get("catSelect"):
            return apology("must provide Item category", 403)

        db.execute("INSERT INTO todo (user_id, cat_id, description) VALUES (?,?,?)",session["user_id"],request.form.get("catSelect"),request.form.get("item"))
        return redirect("/")
    else:
        cats = db.execute("SELECT * FROM categories")
        return render_template("add.html", len=len(cats), cats = cats)
    return apology("TODO")


@app.route("/edit/<page_id>", methods=["GET", "POST"])
@login_required
def edit(page_id):
    pageid = int(page_id)
    print(f"pageid: {pageid}")
    if request.method == "POST":
        isCompleted = request.form.get("isCompleted")
        db.execute("UPDATE todo SET isComplete = :isCompleted WHERE id = :item_id",item_id = pageid, isCompleted = isCompleted)
        return redirect("/")
    else:
        item = db.execute("SELECT todo.id as t_id,description,isComplete, title FROM todo INNER JOIN categories ON categories.id = todo.cat_id WHERE t_id= :item_id AND user_id= :user_id AND isDeleted ='false'",item_id = pageid,user_id= session["user_id"]  )
        return render_template("edit.html", item = item[0])
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure confirm password was submitted
        elif not request.form.get("cpassword"):
            return apology("must provide confirm password", 403)
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :password) ",
                    username=request.form.get("username"), password = generate_password_hash(request.form.get("password")))
        return redirect("/")
    else:
        return render_template("register.html")
    return apology("TODO")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)