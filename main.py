import os
import secrets

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from process_csv import process_csv

app = FastAPI()

security = HTTPBasic()

# Read username and password from a local file
with open("auth.txt", "r") as f:
    AUTH_USERNAME, AUTH_PASSWORD = f.read().strip().split(":")


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, AUTH_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, AUTH_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.post("/uploadfile/")
async def create_upload_file(
    file: UploadFile = File(...), user: str = Depends(get_current_user)
):
    file_location = f"files/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    # Assume `process_csv` is your function to generate the PDF
    pdf_path = process_csv(file_location)

    return FileResponse(
        path=pdf_path, filename=os.path.basename(pdf_path), media_type="application/pdf"
    )
