from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, datetime
import os
import time
from sqlalchemy.exc import OperationalError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    status = db.Column(db.String(50), default="Pending")
    priority = db.Column(db.String(20))
    due_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user = User(
        username=data["username"],
        password=generate_password_hash(data["password"])
    )
    db.session.add(user)
    db.session.commit()
    return {"message": "User registered"}

def init_db():
    retries = 5
    while retries:
        try:
            with app.app_context():
                db.create_all()
            print("Database initialized")
            break
        except OperationalError:
            retries -= 1
            print("Waiting for database...")
            time.sleep(3)


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if user and check_password_hash(user.password, data["password"]):
        token = create_access_token(identity=str(user.id))
        return {"access_token": token}
    return {"error": "Invalid credentials"}, 401

@app.route("/tasks", methods=["GET", "POST"])
@jwt_required()
def tasks():
    user_id = int(get_jwt_identity())
    if request.method == "POST":
        data = request.json
        task = Task(
            title=data["title"],
            priority=data["priority"],
            due_date=datetime.strptime(data["due_date"], "%Y-%m-%d"),
            user_id=user_id
        )
        db.session.add(task)
        db.session.commit()
        return {"message": "Task created"}

    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "status": t.status,
        "priority": t.priority,
        "due_date": t.due_date.isoformat()
    } for t in tasks])

@app.route("/tasks/<int:id>/complete", methods=["PUT"])
@jwt_required()
def complete_task(id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=id, user_id=user_id).first()
    if not task:
        return {"error": "Not found"}, 404
    task.status = "Completed"
    db.session.commit()
    return {"message": "Completed"}

@app.route("/stats")
@jwt_required()
def stats():
    user_id = int(get_jwt_identity())
    total = Task.query.filter_by(user_id=user_id).count()
    completed = Task.query.filter_by(user_id=user_id, status="Completed").count()
    pending = total - completed

    return {
        "status": {"completed": completed, "pending": pending},
        "priority": {
            "Low": Task.query.filter_by(user_id=user_id, priority="Low").count(),
            "Medium": Task.query.filter_by(user_id=user_id, priority="Medium").count(),
            "High": Task.query.filter_by(user_id=user_id, priority="High").count()
        }
    }

@app.route("/reminders")
@jwt_required()
def reminders():
    user_id = int(get_jwt_identity())
    today = date.today()
    overdue = Task.query.filter(Task.user_id==user_id, Task.status!="Completed", Task.due_date < today).all()
    today_tasks = Task.query.filter(Task.user_id==user_id, Task.status!="Completed", Task.due_date == today).all()
    return {
        "overdue": [{"title": t.title} for t in overdue],
        "today": [{"title": t.title} for t in today_tasks]
    }

def reminder_job():
    overdue = Task.query.filter(Task.status!="Completed", Task.due_date < date.today()).count()
    if overdue > 0:
        print(f"[REMINDER] {overdue} overdue tasks")

scheduler = BackgroundScheduler()
scheduler.add_job(reminder_job, "interval", hours=24)
scheduler.start()

init_db()
app.run(host="0.0.0.0", port=5000)
