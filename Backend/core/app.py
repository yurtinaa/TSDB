from fastapi import FastAPI, Depends, UploadFile, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import services
from schemas import *
from typing import Optional, List
from core.auth.router import router as auth_router
from core.auth.service import check_auth
import uvicorn

app = FastAPI(title="Intelligent Analysis System")

origins = [
    "http://127.0.0.1:8000/",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

app.include_router(auth_router)


@app.post("/file/upload-file", tags=['time-series'], response_model=List[int])
async def upload_file(file: UploadFile):
    res = await services.insert_time_series(file)
    if not res[0]:
        raise HTTPException(status_code=500, detail=res[1])
    return res


@app.post("/file/upload", tags=['time-series'], response_model=List[TimeSeriesDTO])
async def upload(id: int, file: UploadFile):
    res = await services.save_time_series(id, file)
    if not res[0]:
        raise HTTPException(status_code=500, detail=res[1])
    return res


@app.get("/time-series/get-to-display", tags=['time-series'], response_model=List[DgTimeSeriesToDisplay])
async def get_time_series_to_display(project_id: int, user: check_auth = Depends()):
    return await services.get_time_series_to_display(project_id, user.id)


@app.get("/time-series/get-for-data-grid", tags=['time-series'], dependencies=[Depends(check_auth)], response_model=List[DgTimeSeries])
async def get_time_series_for_data_grid(ts_ids: List[int] = Query()):
    return await services.get_time_series_for_data_grid(ts_ids)


@app.delete("/time-series/delete", tags=['time-series'], dependencies=[Depends(check_auth)], response_model=bool)
async def delete_time_series(ts_ids: List[int] = Query()):
    return await services.delete_time_series(ts_ids)


@app.post("/primitive/find", tags=['time-series'], dependencies=[Depends(check_auth)], response_model=List[DgPrimitiveToDisplay])
async def find_primitive(primitives: List[PrimitiveDTO]):
    project_id = await services.find_primitives(primitives)
    return await services.get_primitives_to_display(project_id)


@app.get("/primitive/get-to-display", tags=['time-series'], dependencies=[Depends(check_auth)], response_model=List[DgPrimitiveToDisplay])
async def get_primitives_to_display(project_id: int):
    return await services.get_primitives_to_display(project_id)


@app.post("/project/insert", tags=['project'], response_model=bool)
async def insert_project(
        item: InputProjectAndPrimitives,
        background_tasks: BackgroundTasks,
        user: check_auth = Depends()
):
    return await services.insert_project(item, background_tasks, user.id)


@app.get("/projects/get", tags=['project'], response_model=List[DgProject])
async def get_projects(user: check_auth = Depends()):
    return await services.get_projects(user.id)


@app.delete("/project/delete", tags=['project'], dependencies=[Depends(check_auth)], response_model=bool)
async def delete_project(id: int):
    return await services.delete_project(id)


@app.get("/project/get-data-for-editing", tags=['project'], dependencies=[Depends(check_auth)], response_model=OutProjectAndTimeSeries)
async def get_data_for_project_editing(id: int):
    return await services.get_data_for_project_editing(id)


@app.post("/project/update", tags=['project'], dependencies=[Depends(check_auth)], response_model=bool)
async def update_project(id: int, project: ProjectDTO):
    return await services.update_project(id, project)


if __name__ == "__main__":
    uvicorn.run(
        'core.app:app',
        host='0.0.0.0',
        port=8000,
        reload=False
    )
