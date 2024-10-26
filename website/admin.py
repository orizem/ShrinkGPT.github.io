# admin.py

import os
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from sqlalchemy import asc, desc, func
from dotenv import load_dotenv

# LOCAL IMPORTS
from .models import User, Status, Reviews, Chat, db
from .utils.utils import (
    restricted_admin_route_decorator,
    create_test_users,
    create_test_reviews,
    create_test_chats,
)
from .utils.gpt import client

load_dotenv()

admin = Blueprint("admin", __name__)

# Dictionary to store API keys and their purposes
api_keys = {}


def load_api_keys():
    for key, value in os.environ.items():
        if key.endswith("_API_KEY"):
            purpose = key[:-8].title().replace("_", "-")
            api_keys[purpose] = value


load_api_keys()


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

    # Query for registered users by month and year
    register_query = (
        db.session.query(
            func.strftime("%Y-%m", Status.register_date).label("month_year"),
            func.count(Status.id).label("registered_count"),
        )
        .filter(Status.status == 0)
        .group_by("month_year")
        .order_by("month_year")
        .all()
    )

    # Query for deactivated users by month and year
    deactivate_query = (
        db.session.query(
            func.strftime("%Y-%m", Status.last_deactivate_date).label("month_year"),
            func.count(Status.id).label("deactivated_count"),
        )
        .filter(Status.status == -1)
        .group_by("month_year")
        .order_by("month_year")
        .all()
    )

    # Process data for the chart
    register_data = {
        month_year: registered_count for month_year, registered_count in register_query
    }
    deactivate_data = {
        month_year: deactivated_count
        for month_year, deactivated_count in deactivate_query
    }

    # Fill in missing months with zero counts
    all_months = sorted(set(register_data.keys()).union(deactivate_data.keys()))
    dates_chart_data = {
        "months": all_months,
        "registered": [register_data.get(month, 0) for month in all_months],
        "deactivated": [deactivate_data.get(month, 0) for month in all_months],
    }

    return render_template(
        "admin.html",
        users=users,
        page=page,
        rows_per_page=rows_per_page,
        total_users=users.total,
        reviews_chart_data=reviews_chart_data,
        avg_chats_per_user=avg_chats_per_user,
        chats_pie_chart_data=chats_pie_chart_data,
        dates_chart_data=dates_chart_data,
    )


# ROUTES
@admin.route("/generate_test_data", methods=["POST"])
@restricted_admin_route_decorator()
def generate_test_data():
    create_test_users()
    create_test_chats()
    create_test_reviews()
    return {'redirect(url_for("admin.admin_dashboard"))'}


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
    user_status.last_deactivate_date = datetime.today()
    flash(f"User {user_id} has been deactivated.", "info")

    db.session.add(user_status)
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))


@admin.route("/api")
@restricted_admin_route_decorator()
def api_keys_form():
    return render_template("api_keys.html", api_keys=api_keys)


@admin.route("/update_keys", methods=["POST"])
@restricted_admin_route_decorator()
def update_keys():
    for purpose, new_key in request.form.items():
        api_keys[purpose] = new_key
        env_var_name = f'{purpose.upper().replace("-", "_")}_API_KEY'
        os.environ[env_var_name] = new_key

        # Update .env file
        with open(os.path.join("website", ".env"), "r") as file:
            lines = file.readlines()

        with open(os.path.join("website", ".env"), "w") as file:
            updated = False
            for line in lines:
                if line.startswith(f"{env_var_name}="):
                    file.write(f'{env_var_name}="{new_key}"\n')
                    updated = True
                else:
                    file.write(line)

            if not updated:
                file.write(f'{env_var_name}="{new_key}"\n')

    client.api_key = os.environ.get("OPENAI_API_KEY")
    return redirect(url_for("admin.api_keys_form"))
