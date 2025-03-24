# Python Environment Manager

A simple GUI application to create and manage Python virtual environments.

## Features

- Create new Python environments
- Open existing Python environments
- Manage packages (install/uninstall)
- View installed packages
- Easy navigation to environment directories

## Requirements

- Python 3.6+
- Tkinter (included in standard Python installation)
- Pillow (optional, for better icon support)

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:

```
python pyenv_manager.py
```

### Creating a New Environment

1. Click "Create New Environment"
2. Enter a name for your environment
3. Select a location where the environment will be created
4. Choose the Python executable to use (defaults to current Python)
5. Click "Create"

### Opening an Existing Environment

1. Click "Open Environment"
2. Navigate to and select the directory containing your Python environment
3. The environment will be added to your list

### Managing Packages

1. Double-click on an environment in the list or right-click and select "Manage Packages"
2. Use the "Installed Packages" tab to view and uninstall packages
3. Use the "Install New Packages" tab to install new packages

## License

MIT
