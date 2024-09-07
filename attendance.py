from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import tensorflow as tf
import datetime
import os
from helpers.streamlit_attendance import send_email, process_image, detect_faces, detect_liveness, recognize_person, \
    draw_face_bbox, clear_directory
import pygame
import uuid
import time
import csv

app = FastAPI()

# Initialize the liveness model
liveness_model = tf.keras.models.load_model('liveness.model')

fake_directory = "fake_images"
unknown_directory = "unknown_images"
csv_dir = "CSV"
os.makedirs(fake_directory, exist_ok=True)
os.makedirs(unknown_directory, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)

clear_directory(fake_directory)
clear_directory(unknown_directory)


@app.websocket("/ws/attendance")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    pygame.mixer.init()
    sound_alert = pygame.mixer.Sound('beep.wav')  # Path to the alert sound file

    last_attendance_time = {}
    time_limit_between_attendance = 20

    try:
        while True:
            try:
                data = await websocket.receive_bytes()
                nparr = np.frombuffer(data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                full_current_time = f"{current_date} {current_time}"
                cv2.putText(frame, f"Time: {full_current_time}", (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 1, cv2.LINE_AA)

                faces = detect_faces(frame)

                if len(faces) > 1:
                    await websocket.send_json(
                        {"status": "error", "message": "System can only recognize one person at a time"})
                    continue

                if len(faces) == 1:
                    xmin, ymin, width, height = faces[0]
                    xmax = xmin + width
                    ymax = ymin + height
                    extracted_face = frame[ymin:ymax, xmin:xmax]

                    # Check liveness
                    liveness = detect_liveness(extracted_face, liveness_model)

                    if liveness == 0:
                        draw_face_bbox(frame, (xmin, ymin, width, height), "fake", (0, 255, 0))
                        process_image(frame, "fake")
                        fake_image_path = os.path.join(fake_directory, f"fake_image_{time.time()}.jpg")
                        cv2.imwrite(fake_image_path, frame)
                        send_email(fake_image_path, "fake")
                        sound_alert.play()  # Play alert sound
                        await websocket.send_json({"status": "fake", "message": "Warning: Fake person detected"})
                        continue

                    # Recognize person
                    model_result = recognize_person(extracted_face)

                    if model_result and len(model_result) > 0:
                        df = model_result[0]
                        if not df.empty and 'identity' in df.columns:
                            person_name = df.iloc[0]['identity'].split("\\")[-1].split(".")[0]
                            distance = df.iloc[0]['distance']
                            recognized_name = person_name if distance < 0.4 else "unknown"
                        else:
                            recognized_name = "unknown"
                    else:
                        recognized_name = "unknown"

                    if recognized_name == "unknown":
                        draw_face_bbox(frame, (xmin, ymin, width, height), recognized_name, (0, 0, 255))
                        process_image(frame, "unknown")

                        # Save image with new name
                        unknown_image_path = os.path.join(unknown_directory, f"unknown_image_{time.time()}.jpg")
                        cv2.imwrite(unknown_image_path, frame)
                        send_email(unknown_image_path, "unknown")
                        sound_alert.play()  # Play alert sound
                        await websocket.send_json({"status": "unknown", "message": "Warning: Intruder detected"})
                        continue

                    now_time = time.time()
                    if recognized_name not in last_attendance_time or (
                            now_time - last_attendance_time[recognized_name]) > time_limit_between_attendance:
                        csv_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                        csv_file = os.path.join(csv_dir, f"attendance_{csv_time}.csv")

                        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                            fieldnames = ["Tên", "Thời gian truy cập"]
                            writer = csv.DictWriter(file, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerow({"Tên": recognized_name, "Thời gian truy cập": full_current_time})

                        last_attendance_time[recognized_name] = now_time

                    draw_face_bbox(frame, (xmin, ymin, width, height), recognized_name, (0, 255, 0))

                    # Generate UUID token
                    token = str(uuid.uuid4())
                    await websocket.send_json(
                        {"status": "success", "name": recognized_name, "time": full_current_time, "token": token})

                else:
                    await websocket.send_json({"status": "error", "message": "No face detected"})

            except WebSocketDisconnect:
                print("WebSocket disconnected")
                break
            except Exception as e:
                await websocket.send_json({"status": "error", "message": str(e)})

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
