import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for
import models
from db import SessionLocal
import ai

app = Flask(__name__)
app.secret_key = "super_secret_key_for_sessions"

@app.route("/")
def home():
    return redirect("/login")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = SessionLocal()
        # Check if email already exists
        existing_user = db.query(models.User).filter_by(email=email).first()
        if existing_user:
            message = "This email is already registered! Please login."
            db.close()
            return render_template("signup.html", message=message)

        user = models.User(email=email, password=password)
        db.add(user)
        db.commit()
        db.close()

        return redirect("/login")

    return render_template("signup.html", message=message)

@app.route("/login", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = SessionLocal()
        user = db.query(models.User).filter_by(email=email, password=password).first()
        db.close()

        if user:
            session["user"] = user.id
            return redirect("/dashboard")
        else:
            message = "Invalid email or password!"

    return render_template("login.html", message=message)

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    message = None
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")

        db = SessionLocal()
        user = db.query(models.User).filter_by(email=email).first()
        
        if user:
            user.password = new_password
            db.commit()
            message = "Password updated successfully! You can now login."
        else:
            message = "Email not found!"
        db.close()

    return render_template("forgot.html", message=message)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = None
    if request.method == "POST":
        user_prompt = request.form.get("prompt")
        if user_prompt:
            result = ai.ask_ai(user_prompt)

            db = SessionLocal()
            try:
                new_report = models.Reports(
                    user_id=session.get("user"),
                    resume_text=user_prompt,
                    result=str(result)
                )
                db.add(new_report)
                db.commit()
            except Exception as e:
                print("Database Save Error:", e)
                db.rollback()
            finally:
                db.close()

    return render_template("dashboard.html", result=result)

@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()
    try:
        user_reports = db.query(models.Reports).filter_by(user_id=session.get("user")).all()
    except Exception as e:
        print("Fetch Error:", e)
        user_reports = []
    finally:
        db.close()

    return render_template("history.html", reports=user_reports)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)