# admin.py

import sqlite3

from io import BytesIO
from flask import (
    Blueprint,
    render_template,
    Flask,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from flask_login import login_user, logout_user, current_user

# LOCAL IMPORTS
from .models import User, db
from .utils.utils import restricted_admin_route_decorator

admin = Blueprint("admin", __name__)

@admin.route("/admin_dashboard")
@restricted_admin_route_decorator()
def admin_dashboard():
    # Get the current page and rows per page from the request
    page = int(request.args.get("page", 1))
    rows_per_page = int(request.args.get("rows_per_page", 10))

    # Fetch the users from the database based on the pagination parameters
    users = User.query.paginate(page=page, per_page=rows_per_page)

    return render_template(
        "admin.html",
        users=users,
        page=page,
        rows_per_page=rows_per_page,
        total_users=users.total,
    )

# ROUTES
@admin.route("/delete/<int:user_id>", methods=["POST"])
@restricted_admin_route_decorator()
def delete_user(user_id):
    # Delete the user from the database
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))
