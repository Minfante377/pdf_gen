import os
import secrets

import matplotlib
from fastapi import Depends, FastAPI, File, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from starlette.responses import RedirectResponse

matplotlib.use("pdf")

app = FastAPI()


class NotAuthenticatedException(Exception):
    pass


# Secret key for session management
with open("secret.txt", "r") as f:
    SECRET = f.read()

# Read username and password from a local file
with open("auth.txt", "r") as f:
    AUTH_USERNAME, AUTH_PASSWORD = f.read().strip().split(":")

# Basic authentication security
manager = LoginManager(
    SECRET,
    "/login",
    use_cookie=True,
    not_authenticated_exception=NotAuthenticatedException,
)


# Login route
@app.post("/login/")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    if data.username == AUTH_USERNAME and secrets.compare_digest(
        data.password, AUTH_PASSWORD
    ):
        # Correct credentials, set session or cookie here if needed
        token = manager.create_access_token(data={"sub": data.username})
        response = RedirectResponse(url="/", status_code=302)
        manager.set_cookie(response, token)
        return response
    else:
        raise InvalidCredentialsException


@manager.user_loader()
def load_user(user_id: str):
    return AUTH_USERNAME


# Protected endpoint example
@app.post("/uploadfile/")
def create_upload_file(file: UploadFile = File(...), username: str = Depends(manager)):
    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb+") as f:
        f.write(file.file.read())

    pdf_path = process_csv(file_location)
    return FileResponse(
        path=pdf_path, filename=os.path.basename(pdf_path), media_type="application/pdf"
    )


@app.get("/")
def home(username: str = Depends(manager)):
    content = """
        <body>
            <form action='/uploadfile' enctype='multipart/form-data' method='post'>
            <input name='file' type='file'>
            <input type='submit'>
            </form>
        </body>
    """
    return HTMLResponse(content=content)


@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    return RedirectResponse(url="/login_form")


@app.get("/login_form", response_class=HTMLResponse)
def login_form():
    return """
    <!DOCTYPE html>
    <html>
       <body>
          <form method="POST"  action="/login">
             <label for="username">Username:</label><br>
             <input type="text" id="username" name="username"><br>
             <label for="password">Password:</label><br>
             <input type="password" id="password" name="password"><br><br>
             <input type="submit" value="Submit">
          </form>
       </body>
    </html>
    """


# Main function to run the app
if __name__ == "__main__":
    import uvicorn

    from process_csv import process_csv

    uvicorn.run(app, host="0.0.0.0", port=8000)
