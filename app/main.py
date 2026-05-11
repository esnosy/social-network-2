from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    abort,
)
from sqlalchemy import select

from . import db
from .models import Post, User

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.sign_in_get"))
    posts = db.session.execute(select(Post).order_by(Post.created_at.desc())).scalars()
    return render_template("index.html", posts=posts)


@main_bp.post("/create_post")
def create_post():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.sign_in_get"))
    text = request.form.get("text")
    if text is None:
        flash("Please provide post text")
        return redirect(url_for("main.index"))
    post = Post(user_id=user_id, text=text)  # type: ignore
    db.session.add(post)
    db.session.commit()
    return redirect(url_for("main.index"))


@main_bp.get("/profile/<username>")
def profile(username: str):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("auth.sign_in_get"))
    stmt = select(Post).where(Post.user_id == user_id).order_by(Post.created_at.desc())
    posts = db.session.execute(stmt).scalars().all()
    return render_template("profile.html", posts=posts)
