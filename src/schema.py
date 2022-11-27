from fastapi.openapi.utils import get_openapi


def custom_openapi(app):
    # check for cached schema
    if app.openapi_schema:
        return app.openapi_schema

    # top-level api schema
    openapi_schema = get_openapi(
        title="Preprocessing API",
        version="0.1.0",
        description="API for preprocessing on building data",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://user-images.githubusercontent.com/61744142/188621988-a3d82a34-c2b3-4084-bae9-6b35fdf8ba9b.png"
    }

    # cache
    app.openapi_schema = openapi_schema
    return app.openapi_schema
