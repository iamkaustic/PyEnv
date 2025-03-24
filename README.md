# Python Environment Manager

A comprehensive GUI application to create, manage, and maintain Python virtual environments and installations.

![Python Environment Manager](https://img.shields.io/badge/Python-Environment%20Manager-blue)
![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## 🚀 Features

### Environment Management
- Create new Python virtual environments
- Open and manage existing environments
- Navigate to environment directories
- Back up environments to a safe location

### Package Management
- View all installed packages with versions
- Install new packages from PyPI
- Install packages from local files (.whl or .tar.gz)
- Uninstall packages with a single click
- View package dependencies
- Upgrade packages to their latest versions

### Python Version Management
- Display current Python version
- Change Python version used by the application
- Download new Python versions directly from python.org
- Auto-fetch the latest available Python versions

## 📋 Requirements

- Python 3.6+
- Tkinter (included in standard Python installation)
- Pillow (optional, for better icon support)

## 🔧 Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/python-environment-manager.git
   cd python-environment-manager
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## 🖥️ Usage

### Starting the Application

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
2. Use the package management window with multiple tabs:
   - **Installed Packages**: View, uninstall, or upgrade existing packages
   - **Install New Packages**: Search and install packages from PyPI
   - **Dependencies**: View dependencies for any installed package
   - **Upgrades**: See available upgrades and update packages

### Working with Package Dependencies

1. Open the package manager for an environment
2. Go to the "Dependencies" tab
3. Select a package from the dropdown
4. View all dependencies and their versions

### Upgrading Packages

1. Open the package manager for an environment
2. Go to the "Upgrades" tab
3. Select packages to upgrade
4. Click "Upgrade Selected" or "Upgrade All"

### Backing Up Environments

1. Right-click on an environment in the list
2. Select "Backup Environment"
3. Choose a destination directory
4. A timestamped backup will be created

### Managing Python Versions

1. Use the "Change Python" button in the main interface to:
   - Select a different Python installation
   - Restart the application with the new Python version

2. Use the "Download Python" button to:
   - View available Python versions (auto-refreshed from python.org)
   - Select version, OS, and architecture
   - Download the installer or embeddable package
   - Run the installer directly from the application

## 🛠️ Advanced Features

### Local Package Installation

Install packages from local wheel (.whl) or source distribution (.tar.gz) files:

1. Open the package manager
2. Go to the "Install New Packages" tab
3. Click "Install from File"
4. Select your package file

### Python Version Auto-Detection

The application automatically detects:
- The system Python version
- Available Python installations
- Appropriate download options for your platform

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT

## 📞 Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.
