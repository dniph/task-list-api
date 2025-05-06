from flask import Blueprint, abort,make_response,request,Response
from app.models.task import Task
from ..db import db
from datetime import datetime

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()

    try:
        new_task = Task.from_dict(request_body)
        
    except KeyError as error:
        response = {"message": f"Invalid request: missing {error.args[0]}"}
        abort(make_response(response, 400))

    db.session.add(new_task)
    db.session.commit()

    return new_task.to_dict(), 201


@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))

    description_param = request.args.get("description")
    if description_param:
        query = query.where(Task.description.ilike(f"%{description_param}%"))

    query = query.order_by(Task.id)
    
    tasks = db.session.scalars(query)
    tasks_response = [task.to_dict() for task in tasks]
    return tasks_response

@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_task(task_id)

    return task.to_dict()

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        response = {"message": f"task {task_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)
    
    if not task:
        response = {"message": f"task {task_id} not found"}
        abort(make_response(response, 404))

    return task

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    # Actualiza campos requeridos
    task.title = request_body["title"]
    task.description = request_body["description"]

    # Manejo de completed_at (puede venir como null o string en formato ISO)
    completed_at_value = request_body.get("completed_at")
    if completed_at_value:
        try:
            task.completed_at = datetime.fromisoformat(completed_at_value)
        except ValueError:
            response = {"message": "Invalid datetime format for completed_at. Expected ISO 8601 format."}
            abort(make_response(response, 400))
    else:
        task.completed_at = None  # Si es null o no se incluye

    db.session.commit()

    return Response(status=204, mimetype="application/json")

@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")