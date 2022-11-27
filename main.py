"""The main module with all API definitions of the Preprocessing service"""
import dataclasses
import json
import src.preprocessing as pp
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
    """An enhanced version of the JSONEncoder class containing support for dataclasses and DataFrames."""

    def default(self, o):
        """Adds JSON encoding support for dataclasses and DataFrames.

        This function overrides the default function of JSONEncoder and adds support for encoding dataclasses and
        Pandas DataFrames as JSON. Uses the superclass default function for all other types.

        Args:
            o: The object to serialize into a JSON representation.

        Returns:
            The JSON representation of the specified object.
        """

        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, pandas.DataFrame):
            return o.to_json()
        return super().default(o)


@app.get(
    "/",
    name="Root path",
    summary="Returns the routes available through the API",
    description="Returns a route list for easier use of API through HATEOAS",
    response_description="List of urls to all available routes",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "payload": [
                            {
                                "path": "/examplePath",
                                "name": "example route"
                            }
                        ]
                    }
                }
            },
        }
    }
)
async def root():
    """Root API endpoint that lists all available API endpoints.

    Returns:
        A complete list of all possible API endpoints.
    """
    route_filter = ["openapi", "swagger_ui_html", "swagger_ui_redirect", "redoc_html"]
    url_list = [{"path": route.path, "name": route.name} for route in app.routes if route.name not in route_filter]
    return url_list


@app.post("/clean")
def clean_data(payload: str = Body(..., embed=True)):
    """Removes all unusable sensors and buildings from the supplied list of buildings.

    Removes all duplicate sensors within based on a threshold for unique sensor values.
    Removes all sensors with only NaN values.
    Removes all sensors with fewer values than the specified threshold.
    Removes all buildings with no remaining sensors.

    Args:
        payload: The JSON representation of building objects

    Returns:
        A JSON representation of the supplied building objects with only relevant sensors
    """
    buildings = pp.json_to_buildings(json.loads(payload))
    pp.merge_duplicate_sensors(buildings, 10)
    pp.remove_nan_dict(buildings)
    pp.remove_unwanted_rows(buildings, 10)
    pp.remove_leftover_sensors(buildings)
    data = pp.remove_empty_buildings(buildings)

    return json.dumps(data, cls=JSONEncoder)


@app.post("/interpolate")
def interpolate_data(payload: str = Body(..., embed=True)):
    """Interpolates all missing sensor values

    Args:
        payload: The JSON representation of building objects

    Returns:
        A JSON representation of the supplied building objects with interpolated sensor data
    """
    buildings = pp.json_to_buildings(json.loads(payload))
    pp.interpolate_dict(buildings)

    return json.dumps(buildings, cls=JSONEncoder)
