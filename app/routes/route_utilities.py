from flask import abort, make_response
from ..db import db
from app.models.task import Task
from app.models.goal import Goal

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except (ValueError, TypeError):
        abort(make_response({"message": f"{cls.__name__} {model_id} invalid"}, 400))

    model = db.session.get(cls, model_id)
    
    if not model:
        # Modificando el mensaje para que sea específico de la tarea
        abort(make_response({"message": f"{cls.__name__.lower()} {model_id} not found"}, 404))
    
    return model