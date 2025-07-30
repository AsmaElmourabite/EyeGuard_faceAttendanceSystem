🎯 EyeGuard – Système de Présence par Reconnaissance Faciale
Ce projet est une solution complète de gestion de la présence basée sur la reconnaissance faciale, développée avec Python, OpenCV, et MySQL. Il permet de capturer les visages en temps réel via une webcam, d’enregistrer automatiquement les présences, et de notifier par email en cas de reconnaissance ou de détection d’un visage inconnu.

🚀 Fonctionnalités
🔍 Reconnaissance faciale en temps réel via webcam.

🗂️ Base de données MySQL pour stocker les utilisateurs et l'historique de présence.

📧 Alertes email automatiques pour visages reconnus et non reconnus.

🖥️ Interface utilisateur conviviale pour ajouter, modifier, ou supprimer les utilisateurs.

🛠️ Installation
Prérequis :
Python 3.x

MySQL Server

Webcam intégrée ou USB

Étapes :
Cloner le dépôt :

bash
Copier
Modifier
git clone https://github.com/AsmaElmourabite/EyeGuard_faceAttendanceSystem.git
cd EyeGuard_faceAttendanceSystem
Installer les dépendances :

bash
Copier
Modifier
pip install -r requirements.txt
Configurer la base de données MySQL :

Créer une base de données nommée face_recognition.

Importer le script SQL (s’il est fourni) ou créer les tables nécessaires.

Configurer l’envoi d’emails :

Modifier les informations d’identification email dans le code (email, mot de passe, etc.).

🧪 Utilisation
Lancer le système de détection :

bash
Copier
Modifier
python main.py
Utiliser l’interface pour :

Ajouter un utilisateur avec photo.

Démarrer la détection faciale.

Consulter les présences enregistrées.

📂 Structure du Projet
bash
Copier
Modifier
EyeGuard_faceAttendanceSystem/
│
├── dataset/               # Images enregistrées
├── trainers/              # Fichiers de modèle de reconnaissance
├── main.py                # Fichier principal
├── face_recognition.py    # Script de reconnaissance faciale
├── db_config.py           # Configuration MySQL
└── README.md              # Ce fichier
📧 Notifications
Le système envoie des notifications email :

✅ Quand un visage connu est reconnu.

❗ Quand un visage inconnu est détecté.
