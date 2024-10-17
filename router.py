from fastapi import APIRouter, Body
from starlette.responses import JSONResponse
from services import celery, generate_sn_task

router = APIRouter(tags=['SN generator'])

@router.post("/generate_sn")
async def generate_sn(params = Body(...)):
    task_id = generate_sn_task.delay(params["code_model"], params["number"], params["count"])
    return f'{task_id}'


@router.get("/tasks/{task_id}")
def get_status(task_id):
    task_status = celery.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_status.status,
    }
    return JSONResponse(result)
