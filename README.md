# Auto File Organizer

A Python-based automatic file organizer that monitors a specified folder and sorts files into categories in real-time. Keep your folders clean and organized effortlessly!

## Features

- 🗂️ **Automatic File Categorization** - Sorts files into predefined categories (Images, Documents, Videos, Audio, etc.)
- 👁️ **Real-Time Monitoring** - Watches for new files and organizes them automatically
- 🔄 **Reversible Operations** - Unorganize files back to their original state
- 🚫 **Duplicate Detection** - Automatically removes duplicate files
- 📁 **Smart Folder Management** - Creates category folders only when needed
- 🧹 **Auto Cleanup** - Removes empty directories after unorganizing

## Supported File Categories

| Category | File Extensions |
|----------|----------------|
| **Images** | .jpg, .jpeg, .png, .gif, .bmp, .tiff, .svg, .webp |
| **Documents** | .pdf, .doc, .docx, .txt, .odt, .ppt, .pptx, .xls, .xlsx, .csv |
| **Videos** | .mp4, .mkv, .avi, .mov, .wmv, .flv, .webm |
| **Audio** | .mp3, .wav, .flac, .aac, .ogg, .m4a |
| **Archives** | .zip, .rar, .7z, .tar, .gz |
| **Code** | .py, .java, .c, .cpp, .cs, .js, .ts, .html, .css, .php, .json, .xml, .sql |
| **Installers** | .exe, .msi, .apk, .deb, .rpm, .pkg |
| **Other** | All other file types |

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Steps

1. Clone the repository:
```bash
git clone https://github.com/nedelcubianca/auto-file-organizer.git
cd auto-file-organizer
```

2. Install required dependencies:
```bash
pip install watchdog
```

3. **Configure the folder to organize** (IMPORTANT):

Open `file_organizer.py` and modify line 8 to point to your desired folder:

```python
# Change this line to your target folder
main_folder = Path.home() / "Downloads"  # Default is Downloads

# Examples:
# main_folder = Path.home() / "Desktop"
# main_folder = Path("C:/Users/YourName/Documents")
# main_folder = Path("/path/to/your/folder")
```

4. Run the program:
```bash
python auto-file-organizer.py
```

## How to Run

### On Windows:
```bash
# Navigate to the project folder
cd path/to/auto-file-organizer

# Run the script
python file_organizer.py
```

### On macOS/Linux:
```bash
# Navigate to the project folder
cd path/to/auto-file-organizer

# Run the script
python3 file_organizer.py
```

### Alternative: Run directly
If you're in the project directory, simply double-click `file_organizer.py` (if Python is properly configured on your system).

## Usage

When you run the program, you'll see a menu with the following options:

```
File Organizer:
Main folder: /path/to/your/folder

1 - Organize files
2 - Unorganize files (move back the way it was)
3 - Start real-time monitoring
4 - Exit
```

### Option 1: Organize Files
- Scans all files in the specified folder
- Moves files to appropriate category folders
- Removes duplicate files
- Cleans up empty directories
- **Note**: If you add new files after organizing, you need to run this option again to sort the newly added files

### Option 2: Unorganize Files
- Moves all files back to the main folder
- Removes duplicate files during the process
- Deletes all category folders
- Restores the original folder structure

### Option 3: Start Real-Time Monitoring
- Monitors the specified folder for new files
- Automatically organizes files as they arrive **in real-time**
- Works in both organized and unorganized modes
- **This is the recommended option** if you want continuous automatic organization
- Press `Ctrl+C` to stop monitoring

### Option 4: Exit
- Safely closes the application

## How It Works

### Organized Mode (Manual)
1. Run Option 1 to organize files
2. New files are detected in the specified folder
3. Files are categorized based on their extension
4. Files are moved to their respective category folders
5. Duplicates are automatically removed
6. Console displays: `Moved filename.ext to Category`
7. **Important**: If you add new files after organizing, you must run Option 1 again to sort them

### Organized Mode (Real-Time Monitoring)
1. Run Option 3 to start monitoring
2. The system continuously watches for new files
3. Files are automatically organized as soon as they appear
4. No need to manually run Option 1 each time
5. Console displays: `Moved filename.ext to Category`

### Unorganized Mode
1. New files remain in the main folder
2. No automatic categorization occurs
3. Files are kept in their original location
4. Console displays: `File added in unorganized mode: filename.ext`

## Problems Encountered & Solutions

### Problem 1: Files Being Deleted Immediately in Unorganized Mode
**Issue**: When monitoring was active in unorganized mode, newly added files were being deleted immediately instead of remaining in the target folder.

**Cause**: The `move_file()` function was checking for duplicates and deleting new files if a file with the same name already existed in the main folder.

**Solution**: Modified the unorganized mode logic to simply acknowledge new files without moving or deleting them:
```python
if not organize_mode:
    print_msg(f"File added in unorganized mode: {filename}")
    return
```

### Problem 2: False Deletion Messages in Organized Mode
**Issue**: When adding files in organized mode, the system would display a "File deleted" message even though the file was successfully moved to a category folder.

**Cause**: The `watchdog` library interprets file moves as two separate events:
1. A deletion event from the source location (main folder)
2. A creation event in the destination location (category folder)

This caused the `on_deleted()` handler to trigger and display deletion messages for files that were actually just being moved.

**Solution**: Added logic to check if a "deleted" file actually still exists in a category folder before displaying the deletion message:
```python
def on_deleted(self, event):
    if not event.is_directory:
        path = Path(event.src_path)
        file_still_exists = False
        for cat in all_categories:
            cat_folder = main_folder / cat
            if cat_folder.exists() and (cat_folder / path.name).exists():
                file_still_exists = True
                break
        
        if not file_still_exists:
            print_msg(f"File deleted: {path.name}")
```

### Problem 3: Duplicate File Handling
**Issue**: Initial implementation would create multiple copies of files with the same name.

**Solution**: Implemented duplicate detection that:
- Checks if a file with the same name exists in the destination folder
- Deletes the new file if a duplicate is found
- Keeps the original file intact

## Customization

### Change the Target Folder
Edit the `main_folder` variable at the top of the code (line 8):
```python
main_folder = Path.home() / "Downloads"  # Change to your desired folder

# Examples for different operating systems:
# Windows:
main_folder = Path("C:/Users/YourName/Documents")
main_folder = Path("D:/MyFolder")

# macOS/Linux:
main_folder = Path.home() / "Desktop"
main_folder = Path("/Users/YourName/MyFolder")
main_folder = Path("/home/username/projects")
```

### Add New File Categories
Add entries to the `file_categories` dictionary:
```python
file_categories = {
    "YourCategory": [".ext1", ".ext2", ".ext3"],
    # ... other categories
}
```

### Modify File Extensions
Edit the extension lists in the `file_categories` dictionary to match your needs.

## Technical Details

- **Language**: Python 3
- **Main Library**: `watchdog` for file system monitoring
- **File Operations**: Uses `pathlib` for cross-platform compatibility
- **Architecture**: Event-driven using the Observer pattern

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Created with ❤️ for keeping Downloads folders organized worldwide!

## Acknowledgments

- Thanks to the `watchdog` library maintainers for making file system monitoring easy
- Inspired by the universal struggle of managing cluttered folders

---

**Note**: Always backup your important files before running any file organization tool for the first time!

## Quick Start Summary

1. Install Python 3.6+
2. Install watchdog: `pip install watchdog`
3. Edit `file_organizer.py` line 8 to set your target folder
4. Run: `python file_organizer.py`
5. Choose:
   - **Option 1** for one-time organization (run again for new files)
   - **Option 3** for continuous real-time monitoring (recommended)

## Important Notes

⚠️ **Manual Organization (Option 1)**: If you're not using real-time monitoring and add new files to the folder, you need to run Option 1 again to organize the newly added files.

✅ **Real-Time Monitoring (Option 3)**: This automatically organizes files as they arrive, so you don't need to manually run Option 1 each time.
