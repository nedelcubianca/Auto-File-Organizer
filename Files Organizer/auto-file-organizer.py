import os
import time
import shutil
from pathlib import Path
# watchdog is a library to monitor file system events
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

main_folder = Path.home() / "Downloads"
# file_categories is a dictionary where keys are folder names and values are lists of file extensions
file_categories = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".java", ".c", ".cpp", ".cs", ".js", ".ts", ".html", ".css", ".php", ".json", ".xml", ".sql"],
    "Installers": [".exe", ".msi", ".apk", ".deb", ".rpm", ".pkg"],
}

# List of all category folder names
all_categories = list(file_categories.keys()) + ["Other"]
# observer is an object Watchdog used to monitor file system events
observer = None  # None means monitoring is not active (global variable)
organize_mode = True # True means organizing, False means unorganizing

def print_msg(msg: str):
    print(msg)

# create category folder inside main folder
def make_folder(name: str) -> Path:
    folder_path = main_folder / name # slash is from pathlib
    # Create the folder only if we are in organize mode
    if organize_mode:
        folder_path.mkdir(exist_ok=True) # create folder if not exists
    return folder_path

# this function  receives a file path and returns the category name based on its extension
def find_category(file_path: Path) -> str:
    extension = file_path.suffix.lower() # suffix gets the file extension ( from pathlib)
    for cat, ext_list in file_categories.items():
        if extension in ext_list:
            return cat
    return "Other"

# this function verifies if a file with the same name exists in the target folder
# we want to delete duplicates
def get_unique_file(folder: Path, filename: str) -> Path:
    target_path = folder / filename
    # Check if a file with the same name already exists in the destination folder
    if target_path.exists():
        return None  # signals that a file with this name already exists in the destination folder
    return target_path

def move_file(file_path: Path):
    global organize_mode
    if not file_path.is_file():
        return

    filename = file_path.name

    # 1. If the file is already in a category folder -> IGNORE
    if file_path.parent.name in all_categories:
        return

    if not organize_mode:
        # In unorganized mode, just confirm that the file was added
        print_msg(f"File added in unorganized mode: {filename}")
        return

    category = find_category(file_path)
    dest_folder = make_folder(category)
    dest_path = dest_folder / filename  # where it should arrive
    # Check for duplicates
    if dest_path.exists():
        try:
            file_path.unlink()
            print_msg(f"Duplicate removed: {filename}")
        except Exception as e:
            print_msg(f"Error removing duplicate {filename}: {e}")
        return
    # move the file to the category folder
    try:
        shutil.move(str(file_path), str(dest_path))
        print_msg(f"Moved {filename} to {category}")
    except Exception as e:
        print_msg(f"Error moving {filename}: {e}")


# this function organizes files in the given folder and its subfolders
def organize_folder(start_folder: Path):
    # Sort files in all subfolders
    stack = [start_folder]
    while stack:
        current_folder = stack.pop()
        # iterdir() lists all items in the current folder
        for item in current_folder.iterdir():
            # if item is a folder and not a category folder, add it to stack to process later
            if item.is_dir() and item.name not in all_categories:
                stack.append(item)
                continue
            # skip category folders
            if item.is_dir() and item.name in all_categories:
                continue

            if item.is_file():
                move_file(item) # move the file to its category folder

# this function deletes empty directories
# if remove_category_folders is False, it will not delete the main category folders
def delete_empty_dirs(start_folder: Path, remove_category_folders: bool = False):
    # use a stack to traverse directories
    stack = [start_folder]
    # collect all directories first
    all_dirs = []
    while stack:
        current = stack.pop()
        for item in current.iterdir():
            if item.is_dir():
                stack.append(item)
                all_dirs.append(item)  

    # deleting the empty folders in reverse order
    for folder in reversed(all_dirs):  # reversed ensures deep folders come before parents
        try:
            is_empty = not any(folder.iterdir()) # not any is null if folder is empty
        except PermissionError:
            is_empty = False

        if not is_empty:
            continue
        # prevent removing main folder
        if folder == main_folder:
            continue
        # even if one category folder is empty, we may want to keep it
        if (
            not remove_category_folders
            and folder.parent == main_folder
            and folder.name in all_categories
        ):
            continue

        try:
            folder.rmdir()
            print_msg(f"Removed empty folder: {folder}")
        except Exception as e:
            print_msg(f"Error removing folder {folder}: {e}")


def unorganize_files():
    print_msg("Unorganizing files...")

    for cat in all_categories:
        folder = main_folder / cat
        if not folder.exists():
            continue

        for item in list(folder.iterdir()):
            if item.is_file():
                target_path = get_unique_file(main_folder, item.name)

                # Duplicate -> delete the file instead of moving it
                if target_path is None:
                    try:
                        item.unlink()  # deletes this file
                        print_msg(f"Deleted duplicate file: {item.name}")
                    except Exception as e:
                        print_msg(f"Error deleting duplicate {item}: {e}")
                    continue
                # Not duplicate -> move normally
                try:
                    shutil.move(str(item), str(target_path))
                    print_msg(f"Moved back: {item.name}")
                except Exception as e:
                    print_msg(f"Error moving back {item}: {e}")

    # remove all empty folders at the end
    delete_empty_dirs(main_folder, remove_category_folders=True)
    print_msg("Finished unorganizing files!")

# this is a class which inherits FileSystemEventHandler from watchdog and defines actions on file system events
class SimpleHandler(FileSystemEventHandler):
            def on_deleted(self, event):
                if not event.is_directory:
                    path = Path(event.src_path)
                    # Check if the file still exists in any category folder
                    # If yes, it means it was moved, not deleted
                    file_still_exists = False
                    for cat in all_categories:
                        cat_folder = main_folder / cat
                        if cat_folder.exists() and (cat_folder / path.name).exists():
                            file_still_exists = True
                            break
                    
                    # Only display the message if the file was truly deleted.
                    if not file_still_exists:
                        print_msg(f"File deleted: {path.name}")

            def on_created(self, event):
                # we want to process only files, not directories
                if not event.is_directory:
                    time.sleep(0.5)
                    move_file(Path(event.src_path))

            def on_moved(self, event):
                target = Path(event.dest_path)
                if main_folder in target.parents or target.parent == main_folder:
                    time.sleep(0.5)
                    move_file(target)

def start_monitoring():
    global observer
    if observer is not None:
        print_msg("Monitoring is already running.")
        return

    print_msg(f"Starting monitoring on: {main_folder}")
    event_handler = SimpleHandler()
    observer = Observer()
    observer.schedule(event_handler, str(main_folder), recursive=True)
    observer.start()
    print_msg("Monitoring started!")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_msg("Stopping monitor...")
        observer.stop()
        observer.join()
        observer = None
        print_msg("Monitor stopped!")

def main():
    global organize_mode
    print("\nFile Organizer:")
    print("Main folder:", main_folder)
    print("")
    while True:
        print("1 - Organize files")
        print("2 - Unorganize files (move back the way it was)")
        print("3 - Start real-time monitoring")
        print("4 - Exit")

        choice = input("Choose option: ")

        if choice == "1":
            organize_mode = True
            organize_folder(main_folder)
            delete_empty_dirs(main_folder, remove_category_folders=False)
        elif choice == "2":
            organize_mode = False
            unorganize_files()
        elif choice == "3":
            start_monitoring()
        elif choice == "4":
            print("Hope it helps! Goodbye!")
            break
        else:
            print("Invalid option. Try a number between 1-4\n")


if __name__ == "__main__":
    main()