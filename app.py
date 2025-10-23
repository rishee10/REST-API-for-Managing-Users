from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = "users.json"

# Helper functions
def read_users():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def write_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

def find_user(email):
    users = read_users()
    for user in users:
        if user['email'] == email:
            return user
    return None

# Routes
@app.route("/")
def index():
    users = read_users()
    return render_template("index.html", users=users)

@app.route("/add", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        age = request.form.get("age")
        
        if find_user(email):
            return "Error: Email already exists!"
        
        users = read_users()
        users.append({"name": name, "email": email, "age": age})
        write_users(users)
        return redirect(url_for("index"))
    
    return render_template("add_user.html")

@app.route("/update/<path:email>", methods=["GET", "POST"])
def update_user(email):
    users = read_users()

    # Find the index of the user in this 'users' list
    idx = next((i for i, u in enumerate(users) if u.get('email') == email), None)
    if idx is None:
        return "User not found!", 404

    user = users[idx]

    if request.method == "POST":
        new_name = request.form.get("name")
        new_email = request.form.get("email")
        new_age = request.form.get("age")

        # If email changed, ensure new email is unique
        if new_email != email and any(u.get('email') == new_email for u in users):
            return "Error: This new email already exists!", 400

        # Update the item in the users list
        users[idx] = {
            "name": new_name,
            "email": new_email,
            "age": new_age
        }

        write_users(users)
        return redirect(url_for("index"))

    return render_template("update_user.html", user=user)



@app.route("/delete/<email>")
def delete_user(email):
    users = read_users()
    users = [user for user in users if user['email'] != email]
    write_users(users)
    return redirect(url_for("index"))

# REST API endpoints
@app.route("/api/users", methods=["GET"])
def api_get_users():
    return jsonify(read_users())

@app.route("/api/users", methods=["POST"])
def api_add_user():
    data = request.json
    if find_user(data['email']):
        return jsonify({"error": "Email already exists!"}), 400
    users = read_users()
    users.append(data)
    write_users(users)
    return jsonify({"message": "User added successfully!"}), 201

@app.route("/api/users/<email>", methods=["PUT"])
def api_update_user(email):
    users = read_users()
    user = find_user(email)
    if not user:
        return jsonify({"error": "User not found!"}), 404
    
    data = request.json
    user['name'] = data.get('name', user['name'])
    user['age'] = data.get('age', user['age'])
    write_users(users)
    return jsonify({"message": "User updated successfully!"})

@app.route("/api/users/<email>", methods=["DELETE"])
def api_delete_user(email):
    users = read_users()
    if not find_user(email):
        return jsonify({"error": "User not found!"}), 404
    users = [u for u in users if u['email'] != email]
    write_users(users)
    return jsonify({"message": "User deleted successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
