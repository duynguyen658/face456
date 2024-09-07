from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import JSONResponse
import sqlite3
import pandas as pd

app = FastAPI()


def create_table():
    conn = sqlite3.connect('student_info.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_info (
            ID INTEGER PRIMARY KEY,
            Tên TEXT,
            "Ngày sinh" DATE,
            "Mã số chức vụ" TEXT,
            "Giới tính" TEXT,
            "Chức vụ" TEXT,
            "Đơn vị/Phòng ban" TEXT,
            "Đường dẫn ảnh" TEXT,
            "Thời gian" TEXT
        )
    ''')
    conn.commit()
    conn.close()


@app.on_event("startup")
async def startup_event():
    create_table()


@app.get("/students/")
async def get_students(search_query: str = ""):
    conn = sqlite3.connect('student_info.db')
    df = pd.read_sql_query('SELECT * FROM student_info', conn)
    conn.close()

    if not df.empty:
        if search_query:
            df = df[df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().values, axis=1)]
        return df.to_dict(orient="records")
    else:
        return {"message": "Không có thông tin người dùng trong cơ sở dữ liệu."}


@app.post("/students/")
async def add_student(
        name: str = Form(...),
        dob: str = Form(...),
        mssv: str = Form(...),
        gender: str = Form(...),
        class_name: str = Form(...),
        department: str = Form(...),
        image_path: str = Form(...),
        time: str = Form(...)
):
    conn = sqlite3.connect('student_info.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student_info (Tên, "Ngày sinh", "Mã số chức vụ", "Giới tính", "Chức vụ", "Đơn vị/Phòng ban", "Đường dẫn ảnh", "Thời gian")
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, dob, mssv, gender, class_name, department, image_path, time))
    conn.commit()
    conn.close()
    return {"message": "Đã thêm thông tin người dùng thành công!"}


@app.put("/students/{student_id}/")
async def update_student(
        student_id: int,
        name: str = Form(...),
        dob: str = Form(...),
        mssv: str = Form(...),
        gender: str = Form(...),
        class_name: str = Form(...),
        department: str = Form(...),
        image_path: str = Form(...),
        time: str = Form(...)
):
    conn = sqlite3.connect('student_info.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE student_info 
        SET Tên=?, "Ngày sinh"=?, "Mã số chức vụ"=?, "Giới tính"=?, "Chức vụ"=?, "Đơn vị/Phòng ban"=?, "Đường dẫn ảnh"=?, "Thời gian"=?
        WHERE ID = ?
    ''', (name, dob, mssv, gender, class_name, department, image_path, time, student_id))
    conn.commit()
    conn.close()
    return {"message": "Đã cập nhật thông tin người dùng thành công!"}


@app.delete("/students/{student_id}/")
async def delete_student(student_id: int):
    conn = sqlite3.connect('student_info.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM student_info WHERE ID = ?', (student_id,))
    conn.commit()
    conn.close()
    return {"message": "Đã xóa người dùng thành công!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
