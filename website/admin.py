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
from sqlalchemy import asc, desc

# LOCAL IMPORTS
from .models import User, Status, Reviews, Chat, db
from .utils.utils import restricted_admin_route_decorator

admin = Blueprint("admin", __name__)


@admin.route("/admin_dashboard")
@restricted_admin_route_decorator()
def admin_dashboard():
    # Get the current page, rows per page, order column and order type from the request
    page = request.args.get(key="page", default=1, type=int)
    rows_per_page = request.args.get(key="rows_per_page", default=5, type=int)
    column = request.args.get(key="column", default=None, type=str)
    order = request.args.get(key="order", default=None, type=str)

    # Fetch the users from the database based on the pagination parameters
    query = User.query
    if column is not None:
        attr = getattr(User, column)
        query = query.order_by(asc(attr) if order is None else desc(attr))

    users = query.paginate(page=page, per_page=rows_per_page)

    # Query the reviews data
    reviews_data = (
        db.session.query(Reviews.stars, db.func.count(Reviews.stars))
        .group_by(Reviews.stars)
        .all()
    )

    # Process the data into a format suitable for the chart
    reviews_chart_data = [
        {"name": f"{stars} Stars", "y": count} for stars, count in reviews_data
    ]

    # Calculate average chats per user
    total_chats = db.session.query(db.func.count(Chat.id)).scalar()
    total_users = db.session.query(db.func.count(User.id)).scalar()
    avg_chats_per_user = total_chats / total_users if total_users > 0 else 0

    # Calculate users with and without chats
    users_with_chats = db.session.query(Chat.user_id).distinct().count()
    users_without_chats = total_users - users_with_chats

    # Prepare pie chart data
    chats_pie_chart_data = [
        {"name": "Users with Chats", "y": users_with_chats},
        {"name": "Users without Chats", "y": users_without_chats},
    ]

    return render_template(
        "admin.html",
        users=users,
        page=page,
        rows_per_page=rows_per_page,
        total_users=users.total,
        reviews_chart_data=reviews_chart_data,
        avg_chats_per_user=avg_chats_per_user,
        chats_pie_chart_data=chats_pie_chart_data,
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


@admin.route("/activate/<int:user_id>", methods=["POST"])
@restricted_admin_route_decorator()
def activate_user(user_id):
    # Activate user
    user_status = Status.query.filter_by(user_id=user_id).first()
    if user_status.status not in [0, -1]:
        return redirect(url_for("admin.admin_dashboard"))

    user_status.status = 0  # Activate the user
    flash(f"User {user_id} has been activated.", "info")

    db.session.add(user_status)
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))


@admin.route("/deactivate/<int:user_id>", methods=["POST"])
@restricted_admin_route_decorator()
def deactivate_user(user_id):
    # Deactivate user
    user_status = Status.query.filter_by(user_id=user_id).first()
    if user_status.status not in [0, -1]:
        return redirect(url_for("admin.admin_dashboard"))

    user_status.status = -1  # Deactivate the user
    flash(f"User {user_id} has been deactivated.", "info")

    db.session.add(user_status)
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))
