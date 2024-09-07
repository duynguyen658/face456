from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import os

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def get_fake_images_form():
    return """
    <html>
        <head>
            <title>Ảnh giả mạo</title>
        </head>
        <body>
            <h1>Ảnh giả mạo</h1>
            <form action="/select_image/" method="get">
                <label for="image">Chọn ảnh để xem:</label><br>
                <input type="text" id="image" name="image"><br><br>
                <input type="submit" value="Xem ảnh">
            </form>
            <br>
            <a href="/list_images/">Danh sách ảnh</a>
        </body>
    </html>
    """


@app.get("/list_images/", response_class=HTMLResponse)
async def list_fake_images():
    fake_images_dir = "fake_images"
    image_files = [f for f in os.listdir(fake_images_dir) if f.endswith((".jpg", ".jpeg", ".png"))]

    if not image_files:
        return HTMLResponse("<h3>Không có ảnh giả mạo.</h3>")

    image_list_html = "<h3>Danh sách ảnh:</h3><ul>"
    for image in image_files:
        image_list_html += f"<li>{image}</li>"
    image_list_html += "</ul>"

    return HTMLResponse(content=image_list_html)


@app.get("/select_image/")
async def get_selected_fake_image(image: str):
    fake_images_dir = "fake_images"
    image_path = os.path.join(fake_images_dir, image)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại.")

    return FileResponse(image_path, media_type="image/jpeg")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
