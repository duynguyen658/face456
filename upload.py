from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import os
import sqlite3
from datetime import datetime
import cv2

app = FastAPI()

frame_width = 640
frame_height = 480

def create_database_connection():
    conn = sqlite3.connect('student_info.db')
    cursor = conn.cursor()
    return conn, cursor

def close_database_connection(conn):
    conn.close()

@app.on_event("startup")
async def startup_event():
    conn, cursor = create_database_connection()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_info (
            ID INTEGER PRIMARY KEY,
            name TEXT,
            dob DATE,
            student_id TEXT,
            gender TEXT,
            class_name TEXT,
            department TEXT,
            image_path TEXT
        )
    ''')
    conn.commit()
    close_database_connection(conn)
@app.get("/upload", response_class=HTMLResponse)
async def upload_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Đăng Kí Thông Tin</title>
        <style>
            #video {
                border: 1px solid black;
                display: none; /* Hide the video element initially */
            }
            #canvas {
                display: none; /* Hide the canvas element initially */
            }
        </style>
    </head>
    <body>
        <h1>Đăng Kí Thông Tin</h1>
        <h2>Chọn một trong hai cách:</h2>
        <h3>Tải lên ảnh</h3>
        <form action="/submit_info/" enctype="multipart/form-data" method="post">
            <label for="name">Tên:</label><br>
            <input type="text" id="name" name="name"><br><br>
            <label for="dob">Ngày sinh:</label><br>
            <input type="date" id="dob" name="dob"><br><br>
            <label for="student_id">Mã sinh viên:</label><br>
            <input type="text" id="student_id" name="student_id"><br><br>
            <label for="gender">Giới tính:</label><br>
            <input type="text" id="gender" name="gender"><br><br>
            <label for="class_name">Lớp:</label><br>
            <input type="text" id="class_name" name="class_name"><br><br>
            <label for="department">Khoa:</label><br>
            <input type="text" id="department" name="department"><br><br>
            <label for="image">Tải lên ảnh:</label><br>
            <input type="file" id="image" name="image"><br><br>
            <input type="submit" value="Tải lên">
        </form>
        <h3>Chụp ảnh trực tiếp</h3>
        <button id="startCamera">Mở Camera</button><br>
        <video id="video" width="640" height="480" autoplay></video><br>
        <button id="capture" style="display:none;">Chụp ảnh</button><br>
        <canvas id="canvas" width="640" height="480"></canvas>
        <form id="captureForm" action="/capture_image/" method="post">
            <input type="hidden" name="name" id="captureName">
            <input type="hidden" name="image_data" id="imageData">
            <input type="submit" value="Lưu ảnh" style="display:none;" id="saveCapture">
        </form>
        <h3>Hoàn tất đăng ký</h3>
        <form action="/complete_registration/" method="post">
            <input type="submit" value="Đăng ký">
        </form>

        <script>
            const startCameraButton = document.getElementById('startCamera');
            const captureButton = document.getElementById('capture');
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const context = canvas.getContext('2d');

            startCameraButton.addEventListener('click', () => {
                // Show the video and capture button
                video.style.display = 'block';
                captureButton.style.display = 'block';
                startCameraButton.style.display = 'none';

                // Initialize the camera
                navigator.mediaDevices.getUserMedia({ video: true })
                    .then(stream => {
                        video.srcObject = stream;
                        video.play();
                    })
                    .catch(err => {
                        console.error("Error accessing the camera: ", err);
                    });
            });

            captureButton.addEventListener('click', () => {
                // Ensure canvas size matches the video size
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                // Draw the video frame to the canvas
                context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

                // Get the image data as a Base64 string
                const imageData = canvas.toDataURL('image/jpeg');
                document.getElementById('imageData').value = imageData;

                // Show the save button and form
                document.getElementById('saveCapture').style.display = 'block';
                document.getElementById('captureForm').style.display = 'block';
            });
        </script>
    </body>
    </html>
    """

@app.post("/submit_info/")
async def submit_info(
        name: str = Form(...),
        dob: str = Form(...),
        student_id: str = Form(...),
        gender: str = Form(...),
        class_name: str = Form(...),
        department: str = Form(...),
        image: UploadFile = File(...)
):
    image_name = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    image_path = os.path.join("Database", image_name)

    # Ensure the "Database" folder exists
    if not os.path.exists("Database"):
        os.makedirs("Database")

    # Save the uploaded image
    with open(image_path, "wb") as f:
        contents = await image.read()
        f.write(contents)

    # Save the student info to the database
    conn, cursor = create_database_connection()
    cursor.execute('''
        INSERT INTO student_info (name, dob, student_id, gender, class_name, department, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, dob, student_id, gender, class_name, department, image_path))
    conn.commit()
    close_database_connection(conn)

    return {"message": "Đã lưu thông tin vào cơ sở dữ liệu."}

@app.post("/capture_image/")
async def capture_image(name: str = Form(...), image_data: str = Form(...)):
    image_name = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    image_path = os.path.join("Database", image_name)

    # Ensure the "Database" folder exists
    if not os.path.exists("Database"):
        os.makedirs("Database")

    # Decode the image data
    import base64
    import re
    image_data = re.sub('^data:image/.+;base64,', '', image_data)
    image_data = base64.b64decode(image_data)

    with open(image_path, "wb") as f:
        f.write(image_data)

    # Save the captured image info to the database
    conn, cursor = create_database_connection()
    cursor.execute('''
        INSERT INTO student_info (name, dob, student_id, gender, class_name, department, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, "unknown", "unknown", "unknown", "unknown", "unknown", image_path))
    conn.commit()
    close_database_connection(conn)

    return {"message": f"Đã lưu ảnh tại: {image_path}"}

@app.post("/complete_registration/")
async def complete_registration():
    # You can handle additional registration logic here
    return {"message": "Đăng ký hoàn tất!"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
