import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from prometheus_client import start_http_server
import re

# Create the Flask application
app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')

serverID = environ.get('serverID')

# Set the secret key for session management
app.secret_key = 'dockerproject'

# Initialize the SQLAlchemy database
db = SQLAlchemy(app)


# Define the Todo model
class Todo(db.Model):
    __tablename__ = 'Todo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)


# Define the User model
class User(db.Model):
    __tablename__ = 'User'
    username = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100))


# Create the database tables
with app.app_context():
    db.create_all()


# Define the routes
@app.route("/nginx_stats")
def nginx_stats():
    try:
        # Read NGINX access log file
        with open('/var/log/nginx/access.log', 'r') as logfile:
            log_data = logfile.readlines()

        # Parse NGINX log entries and extract statistics
        stats = parse_nginx_logs(log_data)
        return jsonify(stats)
    except FileNotFoundError:
        return jsonify({"error": "NGINX log file not found"})


def parse_nginx_logs(log_data):
    num_connections = len(log_data)
    num_successful_connections = 0
    num_failed_connections = 0
    forwarded_servers = []
    request_ips = []
    request_times = []

    for log_entry in log_data:
        fields = log_entry.split()
        # Check if the request was successful or failed
        if fields[8] == '200':
            num_successful_connections += 1
        else:
            num_failed_connections += 1
        
        # Extract the server that the client was forwarded to (upstream server)
        forwarded_servers.append(fields[-3])
        # Extract the request IP
        request_ips.append(fields[0])
        # Extract the request processing time
        request_times.append(float(fields[-1]))

    # Calculate average request time
    avg_request_time = sum(request_times) / len(request_times) if request_times else 0

    # Calculate success/failure ratio
    success_failure_ratio = num_successful_connections / num_failed_connections if num_failed_connections else num_successful_connections

    stats = {
        "num_connections": num_connections,
        "num_successful_connections": num_successful_connections,
        "num_failed_connections": num_failed_connections,
        "forwarded_servers": forwarded_servers,
        "request_ips": request_ips,
        "avg_request_time": avg_request_time,
        "success_failure_ratio": success_failure_ratio
    }

    return stats


@app.route('/status/<int:status>')
def echo_status(status):
    return 'Status: %s' % status, status


@app.route('/welcome', methods=['GET'])
def welcome():
    return jsonify({'message': f'Welcome to server {serverID}'})



@app.route("/")
def account():
    print("Incoming Request:")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Remote Address: {request.remote_addr}")
    print("")
    return render_template("login.html")


@app.route("/register")
def signup():
    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return redirect(url_for("home"))
    else:
        flash('Invalid username or password', 'error')
        return redirect(url_for("account"))


@app.route("/verifysignup", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()
    if user:
        flash('This username is already taken', 'error')
        return render_template("register.html")
    else:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
    return redirect(url_for("account"))


@app.route("/home")
def home():
    todo_list = Todo.query.all()
    return render_template("base.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))


# Run the Flask application
if __name__ == "__main__":
    # Start HTTP server for Prometheus metrics
    start_http_server(8000)  # Prometheus metrics server on a different port
    app.run(debug=True, port=5000)  # Flask app running on port 5000
