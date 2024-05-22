import sys
from PyQt5.uic import loadUi
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
import mysql.connector
from PyQt5.QtCore import pyqtSignal
import subprocess


class WelcomeScreen(QMainWindow):
    
    def __init__(self,load_ui=True):
        super(WelcomeScreen, self).__init__()
        if load_ui:
            loadUi("login.ui", self)
            self.login_button.clicked.connect(self.login)

        
    def clear_alert(self):
        self.alert.clear()

    def login(self):
        user=self.username.text()
        pwd=self.password.text()
        if len(user)==0 or len(pwd)==0:
            self.alert.setText("Please fill all the informations !")
            QTimer.singleShot(3000, self.clear_alert)
        else:
            
                # connecting to DB and validating the Uname and pwd
                conn = mysql.connector.connect(
                    host='localhost',  
                    user='root',  
                    password='',  
                    database='face_attendance_db'  
                )
                cur=conn.cursor()
                query = ('SELECT * from account_details where Username=%s and Password=%s')
                cur.execute(query, (user,pwd))
                if cur.fetchone():
                    subprocess.run(["python", "main_app.py"])
                    self.close()  
                    
                    
                else:
                    self.alert.setText("username or password incorrect !")
                    QTimer.singleShot(3000, self.clear_alert)
            



    

app = QApplication(sys.argv)
welcome= WelcomeScreen()
widget = QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(875)
widget.setFixedWidth(1125)
widget.show()
try:
    sys.exit((app.exec()))
except:
    print("exiting")






