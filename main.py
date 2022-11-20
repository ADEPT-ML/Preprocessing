import dataclasses
import json
import preprocessing as pp
import pandas

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, pandas.DataFrame):
            return o.to_json()
        return super().default(o)

@app.get("/")
def read_root():
    return {"Hello": "there!"}


@app.post("/clean")
def clean_data(payload: str = Body(..., embed=True)):
    buildings = pp.json_to_buildings(json.loads(payload))
    pp.merge_duplicate_sensors(buildings, 10)  # <- not fully working yet
    pp.remove_nan_dict(buildings)
    pp.remove_unwanted_rows(buildings, 10)
    pp.remove_leftover_sensors(buildings)
    data = pp.remove_empty_buildings(buildings)

    return json.dumps(data, cls=JSONEncoder)

@app.post("/interpolate")
def interpolate_data(payload: str = Body(..., embed=True)):
    buildings = pp.json_to_buildings(json.loads(payload))
    pp.interpolate_dict(buildings)

    return json.dumps(buildings, cls=JSONEncoder)
