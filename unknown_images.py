from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import os

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def get_unknown_images_form():
    return """
    <html>
        <head>
            <title>Ảnh kẻ gian</title>
        </head>
        <body>
            <h1>Ảnh kẻ gian</h1>
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
async def list_unknown_images():
    unknown_images_dir = "unknown_images"
    image_files = [f for f in os.listdir(unknown_images_dir) if f.endswith((".jpg", ".jpeg", ".png"))]

    if not image_files:
        return HTMLResponse("<h3>Không có ảnh kẻ gian.</h3>")

    image_list_html = "<h3>Danh sách ảnh:</h3><ul>"
    for image in image_files:
        image_list_html += f"<li>{image}</li>"
    image_list_html += "</ul>"

    return HTMLResponse(content=image_list_html)


@app.get("/select_image/")
async def get_selected_image(image: str):
    unknown_images_dir = "unknown_images"
    image_path = os.path.join(unknown_images_dir, image)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại.")

    return FileResponse(image_path, media_type="image/jpeg")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
