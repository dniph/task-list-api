from flask import Blueprint, abort,make_response,request,Response
from app.models.task import Task
from ..db import db
from datetime import datetime
from sqlalchemy import asc, desc
from .route_utilities import validate_model

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()

    try:
        new_task = Task.from_dict(request_body)
    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_task)
    db.session.commit()  
    
    return {"task": new_task.to_dict()}, 201


@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))

    description_param = request.args.get("description")
    if description_param:
        query = query.where(Task.description.ilike(f"%{description_param}%"))

    sort_param = request.args.get("sort")
    query = query.order_by(get_sort_order(sort_param))
    
    tasks = db.session.scalars(query)
    tasks_response = [task.to_dict() for task in tasks]
    return tasks_response

@tasks_bp.get("/<task_id>")
@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task,task_id)
    return {"task": task.to_dict()}, 200


    return task

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task,task_id)
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
    task = validate_model(Task,task_id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

#wave 03 
@tasks_bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    task = validate_model(Task, task_id)
    
    # Actualiza completed_at al momento actual (UTC)
    task.completed_at = datetime.utcnow()
    db.session.commit()
    
    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):
    task = validate_model(Task, task_id)
    
    # Establece completed_at como None (incompleta)
    task.completed_at = None
    db.session.commit()
    
    return Response(status=204, mimetype="application/json")



def get_sort_order(sort_param):
    if sort_param == "asc":
        return Task.title.asc()
    elif sort_param == "desc":
        return Task.title.desc()
    elif sort_param == "id":
        return Task.id.asc()  
    elif sort_param == "is_complete":
        return Task.is_complete.asc()  
    return Task.id