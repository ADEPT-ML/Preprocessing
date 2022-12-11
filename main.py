"""The main module with all API definitions of the Preprocessing service"""
from fastapi import FastAPI, Body, HTTPException
import dataclasses
import json
import pandas

import src.preprocessing as pp
from src import schema


app = FastAPI()


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


@app.post(
    "/clean",
    name="Remove all unusable sensors and buildings from the supplied list of buildings",
    summary="Returns a cleaned up JSON representation of the supplied building objects with only relevant sensors",
    description="""
        Removes all duplicate sensors within based on a threshold for unique sensor values.
        Removes all sensors with only NaN values.
        Removes all sensors with fewer values than the specified threshold.
        Removes all buildings with no remaining sensors.
    """,
    response_description="A JSON representation of the supplied building objects with only relevant sensors",
    responses={
        200: {
            "description": "JSON representation of the supplied building objects.",
            "content": {
                "application/json": {
                    "example": {
                        "EF 40a": {
                            "name": "EF 40a",
                            "sensors": [
                                    {"type": "Elektrizit\u00e4t",
                                        "desc": "P Summe", "unit": "kW"}
                            ],
                            "dataframe": "{\"Elektrizit\\u00e4t\":{\"1642809600000\":4.658038,\"1642810500000\":4.667821,\"1642811400000\":4.195286}}"
                        }
                    }
                }
            },
        },
        400: {
            "description": "Payload can not be empty.",
            "content": {
                "application/json": {
                    "example": {"detail": "Payload can not be empty"}
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            },
        }
    },
    tags=["Preprocessing"]
)
def clean_data(
    payload = Body(
        default=...,
        description="JSON representation of the supplied building objects with only relevant sensors",
        example={
            "payload": {
                "EF 40a": {
                    "name": "EF 40a",
                    "sensors": [
                    { "type": "Elektrizit\u00e4t", "desc": "P Summe", "unit": "kW" },
                    { "type": "Temperatur", "desc": "Wetterstation", "unit": "\u00b0C" }
                    ],
                    "dataframe": "{\"Elektrizit\\u00e4t\":{\"1642809600000\":4.658038,\"1642810500000\":4.667821,\"1642811400000\":4.195286},\"Temperatur\":{\"1642809600000\":4.5,\"1642810500000\":null,\"1642811400000\":null}}"
                }
            }
        },
        embed=True
    )
):
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
    try:
        if not payload:
            raise HTTPException(status_code=400, detail="Payload can not be empty")
        buildings = pp.json_to_buildings(json.loads(payload))
        pp.merge_duplicate_sensors(buildings, 10)
        pp.remove_nan_dict(buildings)
        pp.remove_unwanted_rows(buildings, 10)
        pp.remove_leftover_sensors(buildings)
        data = pp.remove_empty_buildings(buildings)
        
        return json.dumps(data, cls=JSONEncoder)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@app.post(
    "/interpolate",
    name="Interpolates all missing sensor values",
    summary="Interpolates all missing sensor values",
    description="The JSON representation of building objects",
    response_description="A JSON representation of the supplied building objects with interpolated sensor data",
    responses={
        200: {
            "description": "JSON representation of the supplied building objects with interpolated sensor data.",
            "content": {
                "application/json": {
                    "example": {
                        "EF 40a": {
                            "name": "EF 40a",
                            "sensors": [
                                { "type": "Elektrizit\u00e4t", "desc": "P Summe", "unit": "kW" }
                            ],
                            "dataframe": "{\"Elektrizit\\u00e4t\":{\"1642809600000\":4.658038,\"1642810500000\":4.426662,\"1642811400000\":4.195286}}"
                        }

                    }
                }
            },
        },
        400: {
            "description": "Payload can not be empty.",
            "content": {
                "application/json": {
                    "example": {"detail": "Payload can not be empty"}
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            },
        }
    },
    tags=["Interpolation"]
)
def interpolate_data(
    payload = Body(
        default=...,
        description="The JSON representation of building objects",
        example={
            "payload": {
                "EF 40a": {
                    "name": "EF 40a",
                    "sensors": [
                        { "type": "Elektrizit\u00e4t", "desc": "P Summe", "unit": "kW" }
                    ],
                    "dataframe": "{\"Elektrizit\\u00e4t\":{\"1642809600000\":4.658038,\"1642810500000\":null,\"1642811400000\":4.195286}}"
                }
            }
        },
        embed=True
    )
):
    """Interpolates all missing sensor values

    Args:
        payload: The JSON representation of building objects

    Returns:
        A JSON representation of the supplied building objects with interpolated sensor data
    """
    try:
        if not payload:
            raise HTTPException(status_code=400, detail="Payload can not be empty")
        buildings = pp.json_to_buildings(json.loads(payload))
        pp.interpolate_dict(buildings)

        return json.dumps(buildings, cls=JSONEncoder)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


schema.custom_openapi(app)
