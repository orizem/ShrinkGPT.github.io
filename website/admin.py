# admin.py

import os
from datetime import datetime
from flask import (
    Blueprint,
    Response,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from typing import Dict
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
def admin_dashboard() -> str:
    """Admin Dashboard

    This route handles GET requests for the admin dashboard page.
    It fetches various data points and renders the admin.html template.

    Parameters
    ----------
    None
        This route does not accept any parameters.

    Returns
    -------
    render_template
        Renders the 'admin.html' template with dashboard data.

    Notes
    -----
    This endpoint requires authentication and admin privileges.
    It performs the following operations:
    1. Fetches users from the database based on pagination parameters
    2. Queries reviews data for chart generation
    3. Calculates average chats per user
    4. Prepares pie chart data for users with and without chats
    5. Queries registered and deactivated users by month and year

    Examples
    --------
    >>> admin_dashboard()
    Renders the admin dashboard with all necessary data.
    """
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
def generate_test_data() -> Dict[str, str]:
    """Generate Test Data

    This route handles POST requests to generate test data for the application.
    It creates sample users, chats, and reviews to populate the database for testing purposes.

    Parameters
    ----------
    None
        This route does not accept any parameters.

    Returns
    -------
    dict
        A dictionary containing a redirect URL.

    Notes
    -----
    This endpoint is intended for development and testing purposes only.
    It should not be exposed in production environments.
    The function performs the following operations:
    1. Creates sample users
    2. Generates test chats
    3. Creates test reviews

    Examples
    --------
    >>> generate_test_data()
    Generates test data and redirects to the admin dashboard.
    """
    create_test_users()
    create_test_chats()
    create_test_reviews()
    return {'redirect(url_for("admin.admin_dashboard"))'}


@admin.route("/delete/<int:user_id>", methods=["POST"])
@restricted_admin_route_decorator()
def delete_user(user_id: int) -> Response:
    """Delete User

    This route handles POST requests to delete a user from the database.

    Parameters
    ----------
    user_id : int
        The ID of the user to be deleted.

    Returns
    -------
    redirect
        Redirects to the admin dashboard after deletion.

    Notes
    -----
    This endpoint requires authentication and admin privileges.
    It removes the specified user and associated data from the system.
    The operation is irreversible and should be used cautiously.

    Examples
    --------
    >>> delete_user(123)
    Deletes the user with ID 123 and redirects to the admin dashboard.
    """
    # Delete the user from the database
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))


@admin.route("/activate/<int:user_id>", methods=["POST"])
@restricted_admin_route_decorator()
def activate_user(user_id: int) -> Response:
    """Activate User

    This route handles POST requests to activate a deactivated user account.

    Parameters
    ----------
    user_id : int
        The ID of the user to be activated.

    Returns
    -------
    redirect
        Redirects to the admin dashboard after activation.

    Notes
    -----
    This endpoint requires authentication and admin privileges.
    Only users with status -1 (deactivated) can be activated.
    The function updates the user's status to 0 (active).

    Examples
    --------
    >>> activate_user(456)
    Activates the user with ID 456 and redirects to the admin dashboard.
    """
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
def deactivate_user(user_id: int) -> Response:
    """
    Deactivate User

    This route handles POST requests to deactivate an active user account.

    Parameters
    ----------
    user_id : int
        The ID of the user to be deactivated.

    Returns
    -------
    redirect
        Redirects to the admin dashboard after deactivation.

    Notes
    -----
    This endpoint requires authentication and admin privileges.
    Only active users (status 0) can be deactivated.
    The function updates the user's status to -1 (deactivated).

    Examples
    --------
    >>> deactivate_user(789)
    Deactivates the user with ID 789 and redirects to the admin dashboard.
    """
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
def api_keys_form() -> str:
    """
    API Keys Form

    This route renders the API keys form page.

    Parameters
    ----------
    None
        This route does not accept any parameters.

    Returns
    -------
    render_template
        Renders the 'api_keys.html' template with api_keys dictionary.

    Notes
    -----
    This endpoint requires authentication and admin privileges.
    It displays the current API keys stored in the system.

    Examples
    --------
    >>> api_keys_form()
    Renders the API keys form page with all available API keys.
    """
    return render_template("api_keys.html", api_keys=api_keys)


@admin.route("/update_keys", methods=["POST"])
@restricted_admin_route_decorator()
def update_keys() -> Response:
    """
    Update API Keys

    This route handles POST requests to update API keys stored in the system.

    Parameters
    ----------
    None
        This route does not accept any parameters directly.
        It processes form data submitted via POST request.

    Returns
    -------
    redirect
        Redirects to the API keys form page after updating.

    Notes
    -----
    This endpoint requires authentication and admin privileges.
    It updates both the in-memory dictionary and the .env file.
    The function iterates through form data to update each API key.

    Examples
    --------
    >>> update_keys()
    Updates API keys based on form submission and redirects to the API keys form page.
    """
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
