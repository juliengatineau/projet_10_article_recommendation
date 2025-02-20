import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if event.is_directory:
            return
        print(f'File changed: {event.src_path}')
        self.callback()

def restart_flask():
    global flask_process
    if flask_process:
        flask_process.terminate()
        flask_process.wait()
    flask_process = subprocess.Popen(["flask", "run"])

if __name__ == "__main__":
    # Obtenir le chemin du dossier où se trouve le fichier script
    directory_to_watch = os.path.dirname(os.path.abspath(__file__))
    print(f'Starting to watch directory: {directory_to_watch}')
    
    flask_process = None
    restart_flask()  # Démarrer Flask pour la première fois

    event_handler = FileChangeHandler(restart_flask)
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if flask_process:
            flask_process.terminate()
    observer.join()