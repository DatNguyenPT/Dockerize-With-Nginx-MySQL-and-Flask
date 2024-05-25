import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
from os import environ

# Create the Flask application
app = Flask(__name__)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')

# Set the secret key for session management
app.secret_key = 'dockerproject'

# Initialize the SQLAlchemy database
db = SQLAlchemy(app)

# Define the Todo model
class Todo(db.Model):
    __tablename__='Todo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)

# Define the User model
class User(db.Model):
    __tablename__='User'
    username = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100))

# Create the database tables
with app.app_context():
    db.create_all()

# Define the routes

# @app.route("/metrics")
# def custom_metrics():
#     return metrics.export()

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
    app.run(debug=True)
