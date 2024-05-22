import sys
import cv2
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QWidget
from PyQt5.QtCore import QTimer, QThread, Qt
from PyQt5.QtGui import QPixmap, QImage
import subprocess
import mysql.connector
import importlib
import io
#from login import WelcomeScreen


class RunScript(QThread):
    def run(self):
        subprocess.call(['python', 'main_video.py'])

class DatabaseManager:
    @staticmethod
    def connect():
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='face_attendance_db'
        )

    @staticmethod
    def execute_query(query, params=None, fetch=False):
        conn = DatabaseManager.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()


class Home(QMainWindow):
    def __init__(self):
        self.app = QApplication([])
        self.main_window = MainWindow()
        super(Home, self).__init__()
        loadUi("app.ui", self)
        self.setup_ui()
        
    def setup_ui(self):
        self.cam.clicked.connect(self.gotocam)
        self.show_teacher.clicked.connect(self.showTeachers)
        self.show_students.clicked.connect(self.showStudents)
        self.show_all.clicked.connect(self.showAll)
        self.list.clicked.connect(self.showList)
        self.AddMenue.clicked.connect(self.showAddMenu)
        self.UpdateMenue.clicked.connect(self.showUpdateMenu)
        self.accountCreationMenue.clicked.connect(self.showAccountMenu)
        self.findButton.clicked.connect(self.find_and_display)
        self.saveButton.clicked.connect(self.update_db)
        self.deleteButton.clicked.connect(self.delete_db)
        self.Addtodb.clicked.connect(self.add_to_db)
        self.AddAccount.clicked.connect(self.create_account)
        #self.logout_button.clicked.connect(self.logout)

        self.hide_containers()

    def hide_containers(self):
        self.container_list.hide()
        self.container_add.hide()
        self.container_update.hide()
        self.container_update_2.hide()
        self.container_create_account.hide()
        self.accueil.show()
        
    '''def logout(self):
        self.close()  
        self.login_window = WelcomeScreen() 
        self.login_window.show()
    '''
    def clear_alert(self):
        self.alert.clear()
        self.alert_2.clear()
        self.alert_3.clear()
        self.alert_4.clear()
        self.alert_cam.clear()
        
    

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        
        ret, frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()

        if not ret:
            self.alert.setText("Failed to capture image!")
            QTimer.singleShot(3000, self.clear_alert)
            return None

        ret, im_arr = cv2.imencode('.jpg', frame)
        if not ret:
            self.alert.setText("Failed to encode image!")
            QTimer.singleShot(3000, self.clear_alert)
            return None

        im_bytes = im_arr.tobytes()
        self.alert.setText("Image captured successfully!")
        QTimer.singleShot(3000, self.clear_alert)
        return im_bytes



    def add_to_db(self):
        fn = self.fn.text()
        ln = self.ln.text()
        occ = self.occ.currentText()
        img_data = self.capture_image()

        if img_data is None:
            return

        query = "INSERT INTO people_data (First_name, Last_name, Occupations, image) VALUES (%s, %s, %s, %s)"
        DatabaseManager.execute_query(query, (fn, ln, occ, img_data))

        # Verify the image data after insertion
        query = "SELECT image FROM people_data WHERE First_name = %s AND Last_name = %s AND Occupations = %s"
        result = DatabaseManager.execute_query(query, (fn, ln, occ), fetch=True)
        if result:
            stored_img_data = result[0][0]
            if stored_img_data == img_data:
                self.alert.setText("Information added to database successfully!")
            
        else:
            self.alert.setText("Failed to verify image data in database!")

        self.fn.clear()
        self.ln.clear()
        self.occ.clear()
        QTimer.singleShot(3000, self.clear_alert)
        self.stop_video_capture()
        self.main_window.close()



    def create_account(self):
        user = self.user.text()
        password = self.password.text()
        if not user or not password:
            self.alert_2.setText("Please fill all the information needed!")
            QTimer.singleShot(3000, self.clear_alert)
            return

        query = "SELECT * FROM account_details WHERE Username = %s"
        result = DatabaseManager.execute_query(query, (user,), fetch=True)

        if result:
            self.alert_2.setText("Username already exists!")
        else:
            query = "INSERT INTO account_details (Username, Password) VALUES (%s, %s)"
            DatabaseManager.execute_query(query, (user, password))
            self.alert_2.setText("Account created successfully!")
            self.user.clear()
            self.password.clear()
        QTimer.singleShot(3000, self.clear_alert)

    def gotocam(self):
        self.hide_containers()
        self.alert_cam.setText("Please wait!")
        self.stop_video_capture()
        QTimer.singleShot(6500, self.clear_alert)

        self.thread = RunScript()
        self.thread.start()

    def showList(self):
        self.container_list.show()
        self.container_add.hide()
        self.container_update.hide()
        self.container_create_account.hide()
        self.accueil.hide()
        self.stop_video_capture()

    def showAddMenu(self):
        self.container_add.show()
        self.container_list.hide()
        self.container_update.hide()
        self.container_create_account.hide()
        self.accueil.hide()
        self.main_window.show()
        self.start_video_capture()

    def start_video_capture(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video_display)
        self.timer.start(30)

    def update_video_display(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            scaled_pixmap = pixmap.scaled(self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio)
            self.video_label.setPixmap(scaled_pixmap)
        else:
            self.video_label.setText("Error: Cannot read frame from camera")

    def closeEvent(self, event):
        self.cap.release()
        event.accept()


    def stop_video_capture(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()

    def showUpdateMenu(self):
        self.container_update.show()
        self.container_list.hide()
        self.container_add.hide()
        self.container_create_account.hide()
        self.accueil.hide()
        self.stop_video_capture()

    def showAccountMenu(self):
        self.container_create_account.show()
        self.container_update.hide()
        self.container_list.hide()
        self.container_add.hide()
        self.accueil.hide()
        self.stop_video_capture()

    def showTeachers(self):
        self.show_records("teacher")

    def showStudents(self):
        self.show_records("student")

    def showAll(self):
        self.show_records()

    def show_records(self, occupation=None):
        query = "SELECT * FROM people_data"
        if occupation:
            query += " WHERE Occupations = %s"
            rows = DatabaseManager.execute_query(query, (occupation,), fetch=True)
        else:
            rows = DatabaseManager.execute_query(query, fetch=True)

        text = ""
        for row in rows:
            info_without_image = row[:-1]
            text += '<p style="font-size:20px; line-height:1.6;">' + ', '.join(map(str, info_without_image)) + '</p>'
        self.textEdit.setText(text)

    def find_and_display(self):
        id_search = self.id_search.text()
        query = "SELECT First_name, Last_name, Occupations, image FROM people_data WHERE ID = %s"
        result = DatabaseManager.execute_query(query, (id_search,), fetch=True)

        if result:
            first_name, last_name, occupations, image_data = result[0]
            self.lineEdit_fn.setText(first_name)
            self.lineEdit_ln.setText(last_name)
            self.lineEdit_occ.setText(occupations)

            try:
                image = QImage.fromData(image_data)
                if image.isNull():
                    raise ValueError("Image is null or corrupted")
                pixmap = QPixmap.fromImage(image)
                self.image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
                self.container_update_2.show()
            except Exception as e:
                self.alert_3.setText(f"Failed to display image: {e}")
                self.container_update_2.hide()
                
        else:
            self.alert_3.setText("This ID doesn't exist in the database!")
            QTimer.singleShot(3000, self.clear_alert)
            self.container_update_2.hide()
            self.video_label.hide()




    def update_db(self):
        fn = self.lineEdit_fn.text()
        ln = self.lineEdit_ln.text()
        occ = self.lineEdit_occ.text()
        id_search = self.id_search.text()
        query = "UPDATE people_data SET First_name = %s, Last_name = %s, Occupations = %s WHERE ID = %s"
        DatabaseManager.execute_query(query, (fn, ln, occ, id_search))
        self.alert_4.setText("Updated successfully!")
        QTimer.singleShot(3000, self.clear_alert)

    def delete_db(self):
        id_search = self.id_search.text()
        self.lineEdit_fn.clear()
        self.lineEdit_ln.clear()
        self.lineEdit_occ.clear()
        self.container_update_2.hide()
        self.image_label.hide()
        query = "DELETE FROM people_data WHERE ID = %s"
        DatabaseManager.execute_query(query, (id_search,))
        self.alert_4.setText("Deleted from the database!")
        QTimer.singleShot(3000, self.clear_alert)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Video Feed")
        self.video_label = QLabel()
        self.setCentralWidget(self.video_label)

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Home()
    window.show()
    sys.exit(app.exec_())
