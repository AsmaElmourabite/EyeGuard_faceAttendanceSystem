import cv2
from email.mime.image import MIMEImage
import face_recognition
import numpy as np
import mysql.connector
from PIL import Image
import io
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SimpleFacerec:
    def __init__(self, db_config):
        self.db_config = db_config
        self.known_face_encodings = []
        self.known_face_occupation = []
        self.known_face_info = []
        self.recognized_faces = None
        self.frame_resizing = 0.25
        self.email_sent = set()
        self.load_encoding_images()

    def load_encoding_images(self):
        cnx = mysql.connector.connect(**self.db_config)
        cursor = cnx.cursor()
        query = ("SELECT image , Occupations , ID , First_name , Last_name , laste_time_attendance FROM people_data")
        cursor.execute(query)
        print("{} encoding images found.".format(cursor.rowcount))
        for (image, Occupations, ID, First_name, Last_name, laste_time_attendance) in cursor:
            img = Image.open(io.BytesIO(image))
            img = np.array(img)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_encoding = face_recognition.face_encodings(rgb_img)
            if len(img_encoding) > 0:
                self.known_face_encodings.append(img_encoding[0])
                self.known_face_occupation.append(Occupations)
                self.known_face_info.append({
                    'ID': ID,
                    'First name': First_name,
                    'Last name': Last_name,
                    'Occupations': Occupations,
                    'laste time attendance': laste_time_attendance
                })
        print("Encoding images loaded")
        cursor.close()
        cnx.close()

    @staticmethod
    def send_email(subject, message, student_info, student_image):
        try:
            msg = MIMEMultipart()
            msg['From'] = '23abderrahmane23@gmail.com'
            msg['To'] = '23abderrahmane@gmail.com'
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            # Add student information to the email body
            student_info_str = "\n".join([f"{key}: {value}" for key, value in student_info.items()])
            msg.attach(MIMEText(f"\Information:\n{student_info_str}\n\n", 'plain'))
            
            # Resize the entire frame to ensure the full image is included
            scale_factor = 0.5  
            resized_image = cv2.resize(student_image, (0, 0), fx=scale_factor, fy=scale_factor)
            
            # Encode the resized image
            _, img_encoded = cv2.imencode('.jpg', resized_image)
            img_data = img_encoded.tobytes()
            
            # Attach the resized image to the email
            image_part = MIMEImage(img_data, name="student_image.jpg")
            msg.attach(image_part)
            
            # Send the email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(msg['From'], 'equg vnex zpkl wzap')
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            server.quit()
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email. Error: {e}")

    def detect_known_faces(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []

        if face_encodings: 
            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"
                info = "No information"
                unid = 0
                
                if matches:
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        name = self.known_face_occupation[best_match_index]
                        info = self.known_face_info[best_match_index]
                        if info['Occupations'] == "student" and info['ID'] not in self.email_sent:
                            subject = "Alert: Student Detected"
                            message = "A student has been detected by the face recognition system."
                            # Capture the entire frame for email
                            student_image = frame
                            # Send email with the entire frame image
                            self.send_email(subject, message, info, student_image)
                            self.email_sent.add(info['ID'])
                    else:
                        subject = "Alert: Unknown Person Detected"
                        message = "A non-recognized person was detected by the face recognition system."
                        student_image = frame
                        self.send_email(subject, message, {}, student_image)
                        
                        self.email_sent.add(unid)

                face_names.append(name)
                if info != self.recognized_faces:
                    print("Person recognized:", info)
                    if 'laste time attendance' in info:
                        print("Last attendance time:", info['laste time attendance'])
                    self.recognized_faces = info
                    if isinstance(info, dict) and 'ID' in info:
                        self.update_laste_time_attendance(info['ID'])

        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names




    

    def update_laste_time_attendance(self, ID):
        cnx = mysql.connector.connect(**self.db_config)
        cursor = cnx.cursor()
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        query = ("UPDATE people_data SET laste_time_attendance = %s WHERE ID = %s")
        cursor.execute(query, (formatted_date, ID))
        cnx.commit()
        cursor.close()
        cnx.close()




# Database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'face_attendance_db',
}

# Initialize SimpleFacerec
sfr = SimpleFacerec(db_config)

# Initialize the video capture
cap = cv2.VideoCapture(0)

# Initialize the frame count
frame_count = 0

# Initialize face locations and names
face_locations = []
face_names = []

# Define a scale factor for the rectangle size
scale_factor = 1.6

img_bg = cv2.imread('Images/bg.png')

while True:
    ret, frame = cap.read()
    if frame_count % 50 == 0:
        face_locations, face_names = sfr.detect_known_faces(frame)
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        width = right - left
        height = bottom - top
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        left = left - (new_width - width) // 2
        top = top - (new_height - height) // 2
        right = left + new_width
        bottom = top + new_height
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    resized_img = cv2.resize(img_bg, (1100, 800), interpolation=cv2.INTER_AREA)
    resized_frame = cv2.resize(frame, (400, 300), interpolation=cv2.INTER_AREA)
    start_col = (resized_img.shape[1] - resized_frame.shape[1]) // 2
    resized_img[0:resized_frame.shape[0], start_col:start_col + resized_frame.shape[1]] = resized_frame
    font = cv2.FONT_HERSHEY_SIMPLEX
    if isinstance(sfr.recognized_faces, dict) and 'ID' in sfr.recognized_faces:
        info_id = "ID: " + str(sfr.recognized_faces['ID'])
        info_fn = "First name: " + sfr.recognized_faces['First name']
        info_ln = "Last name: " + sfr.recognized_faces['Last name']
        info_occ = "Occupations: " + sfr.recognized_faces['Occupations']
        info_lta = "laste time attendance: " + str(sfr.recognized_faces['laste time attendance'])
        cv2.putText(resized_img, info_id, (200, 450), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(resized_img, info_fn, (200, 500), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(resized_img, info_ln, (200, 550), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(resized_img, info_occ, (200, 600), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(resized_img, info_lta, (200, 650), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    elif sfr.recognized_faces:
        cv2.putText(resized_img, "This person isn't registered in the database!", (200, 450), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow('video_page', resized_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    frame_count += 1

cap.release()
cv2.destroyAllWindows()
