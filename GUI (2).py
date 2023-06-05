import os
import tkinter as tk
from tkinter import filedialog
import shutil
import schedule
from datetime import datetime
from manager import Manager
from tkinter import messagebox


class FileManagerGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("File Manager")
        self.pack()
        self.file_manager = Manager()
        self.create_widgets()
        self.master.after(60000 * 60 * 24, self.file_manager.auto_backup)
        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def create_widgets(self):
        self.save_button = tk.Button(self, text="Save File", command=self.open_save_file_window)
        self.save_button.pack(side="top")

        self.delete_button = tk.Button(self, text="Delete File", command=self.open_delete_file_window)
        self.delete_button.pack(side="top")

        self.rename_button = tk.Button(self, text="Rename File", command=self.open_rename_file_window)
        self.rename_button.pack(side="top")

        self.list_files_button = tk.Button(self, text="List Files", command=self.open_list_files_window)
        self.list_files_button.pack(side="top")

        self.get_path_button = tk.Button(self, text="Get File Path", command=self.open_get_path_window)
        self.get_path_button.pack(side="top")

        self.restore_button = tk.Button(self, text="Restore from Backup", command=self.open_restore_from_backup_window)
        self.restore_button.pack(side="top")

        self.backup_button = tk.Button(self, text="Change Backup Time", command=self.open_change_backup_time_window)
        self.backup_button.pack(side="top")

        self.list_files_by_id_button = tk.Button(self, text="List Files by ID", command=self.open_list_files_by_id_window)
        self.list_files_by_id_button.pack(side="top")

        self.id_input = tk.Entry(self, width=70)
        self.id_input.pack(side="top")

        self.path_output = tk.Label(self, text="")
        self.path_output.pack(side="top")

    def show_message(self, message):
        messagebox.showinfo("Notification", message)

    def on_window_close(self):
        self.file_manager.stop()
        self.master.destroy()

    def open_save_file_window(self):
        filepath = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select File to Save")
        if filepath:
            file_id = self.file_manager.save_file(filepath)
            self.show_message("File saved with ID: {}".format(file_id.split(".")[0]))

    def open_delete_file_window(self):
        file_id = self.id_input.get()
        if file_id:
            self.file_manager.delete_file(file_id)
            self.show_message("File with ID {} deleted".format(file_id))

    def open_rename_file_window(self):
        ids = self.id_input.get()
        new_id, old_id = ids.split()
        if new_id and old_id:
            self.file_manager.rename_file(old_id, new_id)
            self.show_message("File renamed to {}".format(new_id))

    def open_list_files_window(self):
        file_list = self.file_manager.list_file()
        if file_list:
            file_list_str = "\n".join(
                ["ID: {} | Path: {}".format(file_id.split(".")[0], filepath) for file_id, filepath in file_list])
            self.show_message(file_list_str)
        else:
            self.show_message("File list is empty")

    def open_get_path_window(self):
        file_id = self.id_input.get()
        file_path = self.file_manager.get_file_path(file_id)
        if file_path:
            self.show_message(file_path)
        else:
            self.show_message("File with ID {} does not exist".format(file_id))

    def open_restore_from_backup_window(self):
        backup_dir = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Backup Directory")
        if backup_dir:
            try:
                self.file_manager.restore_from_backup(backup_dir)
                self.show_message("Restored from backup")
            except Exception as e:
                self.show_message("Error: {}".format(str(e)))
        else:
            self.show_message("Select a backup directory for restore")

    def open_change_backup_time_window(self):
        self.number_window = tk.Toplevel(root)
        self.number_window.title("Enter time in seconds")
        self.number_entry = tk.Entry(self.number_window)
        self.number_entry.pack()
        self.accept_button = tk.Button(self.number_window, text="Accept", command=self.accept_number)
        self.accept_button.pack()
        self.number_window.geometry("400x300+100+100")
        self.number_window.wait_window()

        self.number = int(eval(self.number))
        self.file_manager.start(self.number)
        self.show_message("Time changed")

    def open_list_files_by_id_window(self):
        file_ids = self.id_input.get()
        file_paths = self.file_manager.get_file_paths(file_ids)
        if file_paths:
            file_paths_str = "\n".join(file_paths)
            self.show_message(file_paths_str)
        else:
            self.show_message("IDs do not exist")

    def accept_number(self):
        self.number = self.number_entry.get()
        self.number_window.destroy()


root = tk.Tk()
root.geometry("650x500")
app = FileManagerGUI(master=root)
app.mainloop()
