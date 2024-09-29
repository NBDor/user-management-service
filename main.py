from fastapi import FastAPI
from fastapi.routing import APIRoute
from app.api.v1.endpoints import users
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME or "User Management Service",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])


@app.get("/")
def read_root() -> dict:
    return {"message": "Welcome to the User Management Service"}


# Add this debugging code
print("Registered routes:")
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"Route: {route.path}, Methods: {route.methods}")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
