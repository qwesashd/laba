import os
import shutil
import datetime
import time
import schedule
import threading
import fnmatch


class Manager:
    def __init__(self):
        self.storage_directory = "file_storage"
        self.backup_directory = "backup_storage"
        if not os.path.exists(self.storage_directory):
            os.makedirs(self.storage_directory)
        if not os.path.exists(self.backup_directory):
            os.makedirs(self.backup_directory)

        self.stop_flag = threading.Event()

    def save_file(self, file_path):
        file_id = str(datetime.datetime.now().strftime("%M%S%f"))
        file_name = os.path.basename(file_path)
        destination_path = os.path.join(self.storage_directory, file_id + '.' + file_path.split('.')[-1])
        shutil.copy(file_path, destination_path)
        return file_id

    def get_file_path(self, file_id):
        for filename in os.listdir(self.storage_directory):
            if fnmatch.fnmatch(filename, file_id + '*'):
                file_path = os.path.join(self.storage_directory, filename)
                return file_path
        return None

    def delete_file(self, file_id):
        path_to_directory = os.path.abspath("file_storage")
        for filename in os.listdir(path_to_directory):
            if fnmatch.fnmatch(filename, file_id + '*'):
                os.remove(os.path.join(path_to_directory, filename))

    def rename_file(self, old_file_id, new_file_id):
        path_to_directory = os.path.abspath("file_storage")
        for filename in os.listdir(path_to_directory):
            if filename.startswith(old_file_id):
                res = filename.split(".")[-1]
                old_file_path = os.path.join(path_to_directory, filename)
                new_file_path = os.path.join(path_to_directory, new_file_id + "." + res)
                os.rename(old_file_path, new_file_path)	

    def get_file_paths(self, file_ids):
        file_paths = []
        for filename in os.listdir(self.storage_directory):
            for file_id in file_ids.split():
                if filename.startswith(file_id):
                    file_paths.append(os.path.join(self.storage_directory, filename))
        return file_paths

    def list_file(self):
        files = []
        for file_id in os.listdir(self.storage_directory):
            file_path = self.get_file_path(file_id)
            files.append([file_id, os.path.abspath(file_path)])
        return files

    def get_file_path_by_id(self, id):
        path_to_directory = os.path.join(os.getcwd(), "file_storage")
        for filename in os.listdir(path_to_directory):
            if filename.startswith(id):
                path_to_file = os.path.join(path_to_directory, filename)
                return path_to_file



    def restore_from_backup(self, backup_path):
        if not os.path.exists(backup_path):
            raise ValueError(f"Backup directory {backup_path} does not exist")

        backup_files = os.listdir(backup_path)
        existing_files = os.listdir(self.storage_directory)
        files_to_restore = []

        for backup_file in backup_files:
            if backup_file not in existing_files:
                files_to_restore.append(backup_file)
            else:
                existing_files.remove(backup_file)

        for file_to_restore in files_to_restore:
            backup_file_path = os.path.join(backup_path, file_to_restore)
            destination_path = os.path.join(self.storage_directory, file_to_restore)
            shutil.copy(backup_file_path, destination_path)

        for file_to_delete in existing_files:
            file_path = os.path.join(self.storage_directory, file_to_delete)
            os.remove(file_path)
    
    def auto_backup(self):
        backup_time = datetime.datetime.now()
        backup_time_str = backup_time.strftime('%Y%m%d%H%M%S')

        backup_dir = os.path.join(self.backup_directory, backup_time_str)
        os.makedirs(backup_dir, exist_ok=True)

        for file_name in os.listdir(self.storage_directory):
            file_path = os.path.join(self.storage_directory, file_name)
            backup_file_path = os.path.join(backup_dir, file_name)
            shutil.copy2(file_path, backup_file_path)

        return backup_dir

    def stop(self):
        self.stop_flag.set()      

    def start(self, interval=None):
        if interval is not None:
            self.backup_interval = interval

        schedule.every(self.backup_interval).seconds.do(self.auto_backup)

        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(1)

        t = threading.Thread(target=run_schedule)
        t.start()