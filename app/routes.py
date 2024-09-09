#!/usr/bin/env python3
"""
This module defines the API routes for the application.

The API routes are used to interact with the application's data models.

Routes:
    - /users/<user_id>/ (GET): Retrieve a user by their ID.
    - /users/ (POST): Create a new user.
    - /users/<user_id>/ (PUT): Update a user by their ID.
    - /users/<user_id>/ (DELETE): Delete a user by their ID.
    - /users/<user_id>/inboxes/ (GET): Retrieve the inboxes for a user.
    - /users/<user_id>/inboxes/ (POST): Create a new inbox for a user.
    - /inboxes/<inbox_id>/ (GET): Retrieve an inbox by its ID.
    - /inboxes/<inbox_id>/ (PUT): Update an inbox by its ID.
    - /inboxes/<inbox_id>/ (DELETE): Delete an inbox by its ID.
    - /inboxes/<inbox_id>/messages/ (GET): Retrieve messages from an inbox.
    - /inboxes/<inbox_id>/messages/ (POST): Create a new message in an inbox.
    - /register/ (GET, POST): Register a new user.
    - /login/ (POST): Log in a user.
    - /logout/ (GET): Log out a user.
    - /account/ (GET): Retrieve the account information of the currently logged-in user.
"""
from datetime import timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_user, current_user, logout_user, login_required
from app.models import User, Inbox, Message
from app import db, bcrypt

api = Blueprint("api", __name__)

# @api.route("/users", methods=["GET"])
# def get_users():
#     users = User.query.all()
#     return jsonify([user.to_dict() for user in users])


@api.route("/users/<string:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Retrieve a user by their ID.

    Args:
        user_id (str): The ID of the user to retrieve.

    Returns:
        dict: A dictionary representing the user's information.

    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@api.route("/users", methods=["POST"])
def create_user():
    """
    Create a new user.

    This function handles the POST request to create a new user. It expects a JSON payload
    containing the user data. The user data is used to create a new User object, which is
    then added to the database session and committed. Finally, the function returns a JSON
    response with the newly created user data and a status code of 201.

    Returns:
        A JSON response containing the newly created user data and a status code of 201.
    """
    data = request.get_json()
    if "username" not in data or not data["username"]:
        return jsonify({"message": "Username is required"}), 400
    if "email" not in data or not data["email"]:
        return jsonify({"message": "Email is required"}), 400
    if "password" not in data or not data["password"]:
        return jsonify({"message": "Password is required"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already exists"}), 400
    user = User()
    try:
        user.from_dict(data)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
    return jsonify(user.to_dict()), 201


@api.route("/users/<string:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Update a user with the given user_id.

    Args:
        user_id (str): The ID of the user to update.

    Returns:
        dict: A JSON response containing the updated user information.
    """
    data = request.get_json()
    if "username" not in data or not data["username"]:
        return jsonify({"message": "Username is required"}), 400
    if "email" not in data or not data["email"]:
        return jsonify({"message": "Email is required"}), 400
    if "password" not in data or not data["password"]:
        return jsonify({"message": "Password is required"}), 400
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"message": "Email already exists"}), 400
        user.from_dict(data)
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@api.route("/users/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Delete a user from the database.

    Args:
        user_id (str): The ID of the user to be deleted.

    Returns:
        str: An empty string indicating a successful deletion.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        db.session.delete(user)
        db.session.commit()
        return "", 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@api.route("/users/<string:user_id>/inboxes", methods=["GET"])
def get_inboxes(user_id):
    """
    Retrieve the inboxes for a specific user.

    Args:
        user_id (str): The ID of the user.

    Returns:
        dict: A JSON response containing the inboxes for the user.
    """
    try:
        user = User.query.get(user_id)
        return jsonify([inbox.to_dict() for inbox in user.inboxes])
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@api.route("/users/<string:user_id>/inboxes", methods=["POST"])
def create_inbox(user_id):
    """
    Create a new inbox for a user.

    Args:
        user_id (str): The ID of the user.

    Returns:
        dict: A JSON response containing the created inbox details.
    """
    from dotenv import load_dotenv
    from os import getenv

    load_dotenv()
    base_url = getenv("BASE_URL")
    data = request.get_json()
    if not data["name"]:
        return jsonify({"message": "Name is required"}), 400
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        if data["name"] in [inbox.name for inbox in user.inboxes]:
            return jsonify({"message": "Inbox already exists"}), 400
        inbox = Inbox()
        inbox.user_id = user.id
        data["user_id"] = user.id
        user.inboxes.append(inbox)
        db.session.add(inbox)
        db.session.commit()
        data["url"] = f"{base_url}/inboxes/{inbox.id}"
        inbox.from_dict(data)
        db.session.commit()
        return jsonify(inbox.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@api.route("/inboxes/<string:inbox_id>", methods=["GET"])
def get_inbox(inbox_id):
    """
    Retrieve an inbox by its ID.

    Args:
        inbox_id (str): The ID of the inbox to retrieve.

    Returns:
        dict: A dictionary representation of the inbox.

    Raises:
        Unauthorized: If the user is not authorized to access the inbox.
    """
    try:
        inbox = Inbox.query.get(inbox_id)
        if not inbox:
            return jsonify({"message": "Inbox not found"}), 404
        if inbox.user_id != current_user.id:
            return jsonify({"message": "Unauthorized"}), 401
        return jsonify(inbox.to_dict())
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@api.route("/inboxes/<string:inbox_id>", methods=["PUT"])
def update_inbox(inbox_id):
    """
    Update an inbox with the given inbox_id.

    Args:
        inbox_id (str): The ID of the inbox to update.

    Returns:
        dict: A JSON response containing the updated inbox details.

    Raises:
        HTTPException: If the user is not authorized to update the inbox.

    """
    data = request.get_json()
    if "name" not in data or not data["name"]:
        return jsonify({"message": "Name is required"}), 400
    try:
        inbox = Inbox.query.get(inbox_id)
        if not inbox:
            return jsonify({"message": "Inbox not found"}), 404
        if inbox.user_id != current_user.id:
            return jsonify({"message": "Unauthorized"}), 401
        inbox.from_dict(data)
        db.session.commit()
        return jsonify(inbox.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@api.route("/inboxes/<string:inbox_id>", methods=["DELETE"])
def delete_inbox(inbox_id):
    """
    Delete an inbox.

    Args:
        inbox_id (str): The ID of the inbox to be deleted.

    Returns:
        tuple: A tuple containing an empty string and the HTTP status code 204.

    Raises:
        None
    """
    try:
        inbox = Inbox.query.get(inbox_id)
        if not inbox:
            return jsonify({"message": "Inbox not found"}), 404
        if inbox.user_id != current_user.id:
            return jsonify({"message": "Unauthorized"}), 401
        db.session.delete(inbox)
        db.session.commit()
        return "", 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@api.route("/inboxes/<string:inbox_id>/messages", methods=["GET"])
def get_messages(inbox_id):
    """
    Retrieve messages from an inbox.

    Args:
        inbox_id (str): The ID of the inbox.

    Returns:
        Flask Response: A JSON response containing the messages in the inbox.

    Raises:
        Unauthorized: If the user is not authorized to access the inbox.
    """
    data = request.headers.get("User-Id")
    inbox = Inbox.query.get(inbox_id)
    user_id = data.get("user_id")
    if not inbox:
        return jsonify({"message": "Inbox not found"}), 404
    if inbox.user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 401
    return jsonify([message.to_dict() for message in inbox.messages])


@api.route("/inboxes/<string:inbox_id>/messages", methods=["POST"])
def create_message(inbox_id):
    """
    Create a new message in the specified inbox.

    Args:
        inbox_id (str): The ID of the inbox to create the message in.

    Returns:
        dict: A JSON representation of the created message.
    """
    try:
        data = request.get_json()
        inbox = Inbox.query.get(inbox_id)
        if not inbox:
            return jsonify({"message": "Inbox not found"}), 404
        message = Message()
        message.from_dict(data)
        inbox.messages.append(message)
        db.session.add(message)
        db.session.commit()
        return jsonify(message.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


# Authentication routes
@api.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.

    This function handles the GET and POST requests to register a new user.
    If the request method is GET, it returns a message indicating that the user
    should register. If the request method is POST, it validates the form data
    and creates a new user in the database.

    Returns:
        A JSON response with a success message if the user is registered successfully,
        or an error message if the registration fails.
    """
    if current_user.is_authenticated:
        return jsonify({"message": "Already logged in"}), 400
    if request.method == "POST":
        # validate form data
        if not request.form.get("email"):
            return jsonify({"message": "Email is required"}), 400
        if not request.form.get("password"):
            return jsonify({"message": "Password is required"}), 400
        if not request.form.get("username"):
            return jsonify({"message": "Username is required"}), 400
        if User.query.filter_by(email=request.form.get("email")).first():
            return jsonify({"message": "Email already exists"}), 400
        try:
            user = User()
            user.from_dict(request.form)
            db.session.add(user)
            db.session.commit()
            return jsonify(user.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 500
    # return render_template("register.html")
    return jsonify({"message": "Register"}), 200


@api.route("/login", methods=["POST"])
def login():
    """
    Logs in a user by validating their email and password.

    Returns:
        A JSON response containing the user's information if the login is successful,
        or an error message if the login fails.
    """
    if not request.form.get("email"):
        return jsonify({"message": "Email is required"}), 400
    if not request.form.get("password"):
        return jsonify({"message": "Password is required"}), 400
    try:
        user = User.query.filter_by(email=request.form.get("email")).first()
        if not user or not bcrypt.check_password_hash(
            user.password, request.form.get("password")
        ):
            return jsonify({"message": "Invalid credentials"}), 400
    except Exception as e:
        return jsonify({"message": "Invalid credentials"}), 400
    login_user(user, duration=timedelta(days=1))
    return jsonify(user.to_dict()), 200


@api.route("/logout")
def logout():
    """
    Logout the user.

    This function logs out the currently authenticated user by calling the `logout_user()` function.
    It returns a JSON response with a success message and a status code of 200.

    Returns:
        A JSON response with a success message and a status code of 200.
    """
    logout_user()
    return jsonify({"message": "Logout"}), 200


@api.route("/account")
@login_required
def account():
    """
    This route returns the account information of the currently logged-in user.

    Returns:
        A JSON response containing the account information of the current user.
    """
    return jsonify(current_user.to_dict())


# Handle 404 errors
@api.errorhandler(404)
def page_not_found(e):
    return jsonify({"message": "404 Not Found"}), 404


# Handle 500 errors
@api.errorhandler(500)
def internal_server_error(e):
    return jsonify({"message": "500 Internal Server Error"}), 500


# Handle any other errors
@api.errorhandler(Exception)
def unhandled_exception(e):
    return jsonify({"message": str(e)}), 500
