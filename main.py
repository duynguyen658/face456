from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from typing import List

# Import các hàm từ các module khác
from login import login_users
from home import render_home_page
from upload import upload_image
from attendance import recognize_faces
from history import select_csv, edit_record, delete_records
from student_info import get_students, add_student, update_student, delete_student
from unknown_images import get_unknown_images_form, list_unknown_images, get_selected_image
from fake_images import get_fake_images_form, list_fake_images, get_selected_fake_image

app = FastAPI()

# Sử dụng SessionMiddleware để quản lý session
app.add_middleware(SessionMiddleware, secret_key="123456")

# Hàm quản lý session
IS_LOGGED_IN = "is_logged_in"


def set_session_by_key(request: Request, key: str, value):
    assert key is not None or value is not None, "Parameters key and value are required"
    request.session[key] = value


def get_session_by_key(request: Request, key: str):
    assert key is not None, "Parameter key is required"
    if not is_exist_key_in_session(request, key):
        return None
    return request.session[key]


def del_session_by_key(request: Request, key: str):
    assert key is not None, "Parameter key is required"
    if is_exist_key_in_session(request, key):
        del request.session[key]


def is_exist_key_in_session(request: Request, key: str):
    assert key is not None, "Parameter key is required"
    return key in request.session


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    if request.session.get("is_logged_in", False):
        return RedirectResponse(url="/home")
    else:
        return RedirectResponse(url="/login")
@app.get("/login/form", response_class=HTMLResponse)
async def login_form():
    return """
    <form action="/login" method="post">
        <label for="username">Username:</label><br>
        <input type="text" id="username" name="username"><br>
        <label for="password">Password:</label><br>
        <input type="password" id="password" name="password"><br><br>
        <input type="submit" value="Login">
    </form> 
    """


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if login_users(username, password):
       return set_session_by_key(request, IS_LOGGED_IN, True)
       # return RedirectResponse(url="/home", status_code=302) #
    else:
        return HTMLResponse(content="Login failed, please try again.", status_code=401)







@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return render_home_page()


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return "<h1>Trang Đăng Ký Thông Tin</h1>"
@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return upload_image()


@app.get("/attendance", response_class=HTMLResponse)
async def attendance_page(request: Request):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return recognize_faces()


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return await select_csv()


@app.post("/history/edit", response_class=HTMLResponse)
async def history_edit(request: Request, csv_file: str = Form(...), record_index: int = Form(...),
                       new_name: str = Form(...), new_date: str = Form(...), new_time: str = Form(...)):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return await edit_record(csv_file, record_index, new_name, new_date, new_time)


@app.post("/history/delete", response_class=HTMLResponse)
async def history_delete(request: Request, csv_file: str = Form(...), indices: List[int] = Form(...)):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return await delete_records(csv_file, indices)


# Tích hợp các endpoint từ student_info.py
@app.get("/students", response_class=HTMLResponse)
async def students_list(request: Request, search_query: str = ""):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return await get_students(search_query)


@app.post("/students", response_class=HTMLResponse)
async def student_add(request: Request, name: str = Form(...), dob: str = Form(...), mssv: str = Form(...),
                      gender: str = Form(...), class_name: str = Form(...), department: str = Form(...),
                      image_path: str = Form(...), time: str = Form(...)):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return await add_student(name, dob, mssv, gender, class_name, department, image_path, time)


@app.put("/students/{student_id}", response_class=HTMLResponse)
async def student_update(request: Request, student_id: int, name: str = Form(...), dob: str = Form(...),
                         mssv: str = Form(...), gender: str = Form(...), class_name: str = Form(...),
                         department: str = Form(...), image_path: str = Form(...), time: str = Form(...)):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return await update_student(student_id, name, dob, mssv, gender, class_name, department, image_path, time)


@app.delete("/students/{student_id}", response_class=HTMLResponse)
async def student_delete(request: Request, student_id: int):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return await delete_student(student_id)


# Tích hợp các endpoint từ unknown_images.py
@app.get("/unknown_images", response_class=HTMLResponse)
async def unknown_images_page(request: Request):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return get_unknown_images_form()


@app.get("/list_images", response_class=HTMLResponse)
async def list_images(request: Request):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return list_unknown_images()


@app.get("/select_image", response_class=FileResponse)
async def select_image(request: Request, image: str):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return get_selected_image(image)


# Tích hợp các endpoint từ fake_images.py
@app.get("/fake_images", response_class=HTMLResponse)
async def fake_images_page(request: Request):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return get_fake_images_form()


@app.get("/list_fake_images", response_class=HTMLResponse)
async def list_fake_images_route(request: Request):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return list_fake_images()


@app.get("/select_fake_image", response_class=FileResponse)
async def select_fake_image(request: Request, image: str):
    if not get_session_by_key(request, IS_LOGGED_IN):
        return RedirectResponse(url="/login")
    return get_selected_fake_image(image)


@app.post("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    del_session_by_key(request, IS_LOGGED_IN)
    return RedirectResponse(url="/login")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
