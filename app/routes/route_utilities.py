from flask import abort, make_response
from ..db import db
from app.models.task import Task
from app.models.goal import Goal

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except (ValueError, TypeError):
        response = {"message": f"{cls.__name__} {model_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)
    
    if not model:
        response = {"message": f"{cls.__name__} {model_id} not found"}
        abort(make_response(response, 404))
    
    return model