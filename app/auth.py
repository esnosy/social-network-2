import hashlib
import secrets

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import select

from . import db
from .models import User


def hash_password(password: str, salt: str):
    return hashlib.sha256((password + salt).encode()).hexdigest()


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/sign_in")
def sign_in_get():
    if session.get("user_id") is not None:
        return redirect(url_for("main.index"))
    return render_template("sign_in.html")


@auth_bp.post("/sign_in")
def sign_in_post():
    if session.get("user_id") is not None:
        return redirect(url_for("main.index"))
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        flash("Please provide username and password")
        return redirect(url_for("auth.sign_in_get"))
    user = (
        db.session.execute(select(User).where(User.username == username))
        .scalars()
        .first()
    )
    if user is None:
        flash("User doesn't exist")
        return redirect(url_for("auth.sign_in_get"))
    if hash_password(password, user.salt) != user.password_hash:
        flash("Wrong password")
        return redirect(url_for("auth.sign_in_get"))
    session["user_id"] = user.user_id
    session["username"] = user.username
    return redirect(url_for("main.index"))


@auth_bp.post("/sign_up")
def sign_up_post():
    if session.get("user_id") is not None:
        return redirect(url_for("main.index"))
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        flash("Please provide username and password")
        return redirect(url_for("auth.sign_in_get"))
    user = (
        db.session.execute(select(User).where(User.username == username))
        .scalars()
        .first()
    )
    if user:
        flash("User already exists")
        return redirect(url_for("auth.sign_in_get"))
    salt = secrets.token_hex(16)
    new_user = User()
    new_user.username = username
    new_user.password_hash = hash_password(password, salt)
    new_user.salt = salt
    db.session.add(new_user)
    db.session.commit()
    new_user = (
        db.session.execute(select(User).where(User.username == username))
        .scalars()
        .first()
    )
    if new_user is None:
        flash("Failed to sign in")
        return redirect(url_for("auth.sign_in_get"))
    session["user_id"] = new_user.user_id
    session["username"] = new_user.username
    return redirect(url_for("main.index"))


@auth_bp.get("/sign_out")
def sign_out():
    if session.get("user_id") is not None:
        session.clear()
    return redirect(url_for("auth.sign_in_get"))
