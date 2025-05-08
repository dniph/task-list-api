from flask import Blueprint, request, Response, abort, make_response
from app.models.goal import Goal
from app.models.task import Task
from ..db import db
from .route_utilities import validate_model

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@bp.post("")
def create_goal():
    request_body = request.get_json()

    try:
        new_goal = Goal.from_dict(request_body)
    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_goal)
    db.session.commit()
    
    return {"goal": new_goal.to_dict()}, 201

@bp.get("")
def get_all_goals():
    goals = Goal.query.all()
    goals_response = [goal.to_dict() for goal in goals]
    return goals_response

@bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    return {"goal": goal.to_dict()}, 200

@bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")



@bp.route("/<goal_id>/tasks", methods=["POST"])
def assign_tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    if not request_body or "task_ids" not in request_body:
        abort(400, description={"details": "Invalid data"})

    
    new_tasks = []
    for task_id in request_body["task_ids"]:
        task = validate_model(Task, task_id)
        new_tasks.append(task)

    
    for task in goal.tasks:
        task.goal_id = None

    for task in new_tasks:
        task.goal_id = goal.id

    db.session.commit()

    return {
        "id": goal.id,
        "task_ids": request_body["task_ids"]
    }, 200



@bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_for_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    
    return {
        "id": goal.id,
        "title": goal.title,
        "tasks": [task.to_dict() for task in goal.tasks]
    }, 200