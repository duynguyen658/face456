import datetime
# Home
import smtplib
import threading
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import cv2
import numpy as np
import os
import pygame
import dlib
import pandas as pd

# Liveness
import tensorflow as tf
from deepface import DeepFace

fake_detection_count = 0
unknown_detection_count = 0

current_time = datetime.datetime.now().strftime("%H:%M:%S")
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
full_current_time = f"{current_date} {current_time}"


def send_email(image_path, category):
    msg = MIMEMultipart()
    text = MIMEText(f"Hệ thống phát hiện hình ảnh {category} đáng ngờ xâm nhập hệ thống lúc {full_current_time}")
    msg.attach(text)

    image_data = open(image_path, 'rb').read()
    image_attachment = MIMEImage(image_data, name=os.path.basename(image_path))
    msg.attach(image_attachment)

    msg['Subject'] = f'CẢNH BÁO CÓ KẺ GIAN XÂM NHẬP - {category.upper()} - {full_current_time}'
    msg['From'] = 'minhduyho282@gmail.com'  # Thay đổi email của bạn
    msg['To'] = 'minhduyho282@gmail.com'  # Thay đổi email người nhận

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('minhduyho282@gmail.com', 'mfvtxiqpuadnqkeh')  # Thay đổi thông tin đăng nhập của bạn
        server.sendmail('minhduyho282@gmail.com', 'minhduyho282@gmail.com',
                        msg.as_string())  # Thay đổi email người nhận
        server.quit()
    except Exception as e:
        print("Không thể gửi email. Lỗi:", str(e))


def play_sound(category):
    # Khởi tạo pygame
    pygame.mixer.init()

    # Đặt âm thanh khi có ảnh fake
    fake_sound = pygame.mixer.Sound('beep.wav')  # Thay 'fake_sound.wav' bằng tên tệp âm thanh của bạn

    # Đặt âm thanh khi không nhận diện được
    unknown_sound = pygame.mixer.Sound('beep.wav')  # Thay 'unknown_sound.wav' bằng tên tệp âm thanh của bạn

    if category == "fake":
        fake_sound.play()
    elif category == "unknown":
        unknown_sound.play()


def clear_directory(directory):
    os.makedirs(directory, exist_ok=True)

    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Không thể xóa tệp {file_path}. Lỗi:", str(e))
    print(f"Directory '{directory}' cleared.")


def process_image(image, category):
    global fake_detection_count, unknown_detection_count
    fake_directory = "fake_images"
    unknown_directory = "unknown_images"

    if category == "fake":
        fake_detection_count += 1
        fake_image_filename = os.path.join(fake_directory, f"fake_image_{fake_detection_count}.jpg")
        cv2.imwrite(fake_image_filename, image)
        print(f"Processed and saved fake image: {fake_image_filename}")

        # Phát âm thanh khi có ảnh fake
        play_sound("fake")

        # Gửi email trong một luồng riêng biệt
        email_thread = threading.Thread(target=send_email, args=(fake_image_filename, "fake"))
        email_thread.start()


    elif category == "unknown":
        unknown_detection_count += 1
        unknown_image_filename = os.path.join(unknown_directory, f"unknown_image_{unknown_detection_count}.jpg")
        cv2.imwrite(unknown_image_filename, image)
        print(f"Processed and saved unknown image: {unknown_image_filename}")

        # Phát âm thanh khi không nhận diện được
        play_sound("unknown")

        # Gửi email trong một luồng riêng biệt
        email_thread = threading.Thread(target=send_email, args=(unknown_image_filename, "unknown"))
        email_thread.start()


# Load the detector
detector = dlib.get_frontal_face_detector()
print("Face detector initialized.")


def detect_faces(frame):
    # Convert frame to grayscale (dlib works best with grayscale images)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = detector(gray)

    # Convert dlib rectangles to a list of bounding boxes
    face_bounding_boxes = [(face.left(), face.top(), face.width(), face.height()) for face in faces]
    print(f"Faces detected: {face_bounding_boxes}")
    return face_bounding_boxes


def detect_liveness(extracted_face, liveness_model):
    img = extracted_face
    img = cv2.resize(img, (32, 32))
    img = img.astype('float') / 255.0
    img = tf.keras.preprocessing.image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    liveness = liveness_model.predict(img)
    liveness = liveness[0].argmax()
    print(f"Liveness detected: {liveness}")
    return liveness

def recognize_person(extracted_face):
    try:
        model = DeepFace.find(extracted_face,
                              db_path="Database",
                              detector_backend="mtcnn",
                              model_name="Facenet512",
                              distance_metric="cosine",
                              enforce_detection=False)
        if model and len(model) > 0:
            return model
        else:
            print("No person found in the database or empty result.")
            return []
    except Exception as e:
        print(f"Lỗi trong quá trình nhận dạng: {e}")
        return []
class BoundingBoxColor:
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    YELLOW = (0, 255, 255)
    PURPLE = (128, 0, 128)
    ORANGE = (0, 165, 255)
    WHITE = (255, 255, 255)


class BoundingBoxFont:
    FONT_HERSHEY_SIMPLEX = cv2.FONT_HERSHEY_SIMPLEX
    FONT_HERSHEY_PLAIN = cv2.FONT_HERSHEY_PLAIN
    FONT_HERSHEY_DUPLEX = cv2.FONT_HERSHEY_DUPLEX
    FONT_HERSHEY_COMPLEX = cv2.FONT_HERSHEY_COMPLEX
    FONT_HERSHEY_TRIPLEX = cv2.FONT_HERSHEY_TRIPLEX
    FONT_HERSHEY_COMPLEX_SMALL = cv2.FONT_HERSHEY_COMPLEX_SMALL
    FONT_HERSHEY_SCRIPT_SIMPLEX = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
    FONT_HERSHEY_SCRIPT_COMPLEX = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
    FONT_ITALIC = cv2.FONT_ITALIC


def draw_face_bbox(frame, face_coordinates, label, color=BoundingBoxColor.GREEN,
                   font=BoundingBoxFont.FONT_HERSHEY_SIMPLEX, font_scale=1, thickness=2):
    x, y, width, height = face_coordinates
    cv2.rectangle(frame, (x, y), (x + width, y + height), color, thickness)
    cv2.putText(frame, label, (x, y - 10), font, font_scale, color, thickness, cv2.LINE_AA)
    print(f"Drew bounding box with label: {label}")
