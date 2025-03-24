import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from pathlib import Path
import shutil
import datetime
import platform
import re
import webbrowser
import urllib.request
import tempfile
import gzip
import io
import threading
import zipfile
import time

# Application version
APP_VERSION = "1.0.0"
APP_NAME = "PyEnv"
AUTHOR = "Kaustubh Parab"
GITHUB_URL = "https://github.com/iamkaustic"
GITHUB_REPO = "iamkaustic/PyEnv"  # Just username/repo format
DEMO_MODE = False  # Set to False when you have a real GitHub repo

class PyEnvManager:
    def __init__(self, root):
        self.root = root
        self.root.title("PyEnv - Python Environment Manager")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Set app icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Initialize data storage
        self.config_file = Path.home() / ".pyenv_manager_config.json"
        self.environments = self.load_environments()
        
        # Get system Python version
        self.system_python_version = self.get_system_python_version()
        
        self.setup_ui()
    
    def load_environments(self):
        """Load saved environments from config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_environments(self):
        """Save environments to config file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.environments, f)
    
    def setup_ui(self):
        """Set up the main user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header frame
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side: App title and version with update button
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # App title
        ttk.Label(title_frame, text=f"{APP_NAME}", 
                 font=("Helvetica", 16, "bold")).pack(side=tk.TOP, anchor=tk.W)
        
        # Version and update button
        version_update_frame = ttk.Frame(title_frame)
        version_update_frame.pack(side=tk.BOTTOM, anchor=tk.W, pady=(2, 0))
        
        ttk.Label(version_update_frame, text=f"v{APP_VERSION}").pack(side=tk.LEFT)
        
        check_update_btn = ttk.Button(version_update_frame, text="Check for Updates", 
                                     command=self.check_for_updates, width=15)
        check_update_btn.pack(side=tk.LEFT, padx=5)
        
        # Right side: Python version and actions
        python_frame = ttk.Frame(header_frame)
        python_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # About button at top right
        about_btn = ttk.Button(python_frame, text="About", command=self.show_about, width=10)
        about_btn.pack(side=tk.TOP, anchor=tk.E, pady=(0, 5))
        
        # Python version info
        ttk.Label(python_frame, text=f"System Python: {self.system_python_version}", 
                 font=("Helvetica", 10)).pack(side=tk.TOP, anchor=tk.E)
        
        # Python action buttons
        python_actions_frame = ttk.Frame(python_frame)
        python_actions_frame.pack(side=tk.BOTTOM, anchor=tk.E)
        
        change_python_btn = ttk.Button(python_actions_frame, text="Change Python", 
                                      command=self.change_python_version, width=15)
        change_python_btn.pack(side=tk.LEFT, padx=2)
        
        download_python_btn = ttk.Button(python_actions_frame, text="Download Python", 
                                        command=self.download_python, width=15)
        download_python_btn.pack(side=tk.LEFT, padx=2)
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Create buttons
        create_btn = ttk.Button(button_frame, text="Create New Environment", 
                               command=self.create_environment, width=25)
        create_btn.pack(side=tk.LEFT, padx=5)
        
        open_btn = ttk.Button(button_frame, text="Open Environment", 
                             command=self.open_environment, width=25)
        open_btn.pack(side=tk.LEFT, padx=5)
        
        # Create environments list frame
        list_frame = ttk.LabelFrame(main_frame, text="Your Python Environments")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for environments
        columns = ("name", "path", "python_version")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        self.tree.heading("name", text="Name")
        self.tree.heading("path", text="Path")
        self.tree.heading("python_version", text="Python Version")
        
        # Define columns
        self.tree.column("name", width=150)
        self.tree.column("path", width=350)
        self.tree.column("python_version", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_environment_double_click)
        
        # Create right-click menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Manage Packages", command=self.manage_packages)
        self.context_menu.add_command(label="Open in Explorer", command=self.open_in_explorer)
        self.context_menu.add_command(label="Backup Environment", command=self.backup_environment)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Remove Environment", command=self.remove_environment)
        
        # Bind right-click event
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Populate the tree with saved environments
        self.refresh_environments_list()
    
    def refresh_environments_list(self):
        """Refresh the environments list in the treeview"""
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add environments to the tree
        for env in self.environments:
            self.tree.insert("", tk.END, values=(
                env.get("name", "Unknown"),
                env.get("path", ""),
                env.get("python_version", "Unknown")
            ))
    
    def create_environment(self):
        """Create a new Python environment"""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Environment")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create form
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name field
        ttk.Label(form_frame, text="Environment Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Path field
        ttk.Label(form_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(form_frame)
        path_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=path_var, width=30)
        path_entry.pack(side=tk.LEFT)
        
        def browse_path():
            path = filedialog.askdirectory(title="Select Directory for Environment")
            if path:
                path_var.set(path)
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=browse_path)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Python executable field
        ttk.Label(form_frame, text="Python Executable:").grid(row=2, column=0, sticky=tk.W, pady=5)
        python_frame = ttk.Frame(form_frame)
        python_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        python_var = tk.StringVar(value=sys.executable)
        python_entry = ttk.Entry(python_frame, textvariable=python_var, width=30)
        python_entry.pack(side=tk.LEFT)
        
        def browse_python():
            filetypes = [("Python Executable", "python.exe")] if sys.platform == "win32" else []
            path = filedialog.askopenfilename(title="Select Python Executable", filetypes=filetypes)
            if path:
                python_var.set(path)
        
        browse_python_btn = ttk.Button(python_frame, text="Browse...", command=browse_python)
        browse_python_btn.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def on_cancel():
            dialog.destroy()
        
        def on_create():
            name = name_var.get().strip()
            path = path_var.get().strip()
            python_exe = python_var.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a name for the environment")
                return
            
            if not path:
                messagebox.showerror("Error", "Please select a location for the environment")
                return
            
            if not python_exe:
                messagebox.showerror("Error", "Please select a Python executable")
                return
            
            # Create the environment
            env_path = os.path.join(path, name)
            
            # Show progress
            progress_window = tk.Toplevel(dialog)
            progress_window.title("Creating Environment")
            progress_window.geometry("300x100")
            progress_window.transient(dialog)
            progress_window.grab_set()
            
            ttk.Label(progress_window, text="Creating Python environment...").pack(pady=10)
            progress = ttk.Progressbar(progress_window, mode="indeterminate")
            progress.pack(fill=tk.X, padx=20)
            progress.start()
            
            # Update UI
            self.root.update()
            
            try:
                # Create the virtual environment
                subprocess.run([python_exe, "-m", "venv", env_path], check=True)
                
                # Get Python version
                if sys.platform == "win32":
                    python_path = os.path.join(env_path, "Scripts", "python.exe")
                else:
                    python_path = os.path.join(env_path, "bin", "python")
                
                result = subprocess.run([python_path, "--version"], 
                                       capture_output=True, text=True, check=True)
                python_version = result.stdout.strip()
                
                # Add to environments list
                self.environments.append({
                    "name": name,
                    "path": env_path,
                    "python_version": python_version
                })
                
                # Save environments
                self.save_environments()
                
                # Refresh the list
                self.refresh_environments_list()
                
                # Close dialogs
                progress_window.destroy()
                dialog.destroy()
                
                messagebox.showinfo("Success", f"Python environment '{name}' created successfully!")
                
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Error", f"Failed to create environment: {str(e)}")
        
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Create", command=on_create).pack(side=tk.LEFT, padx=5)
    
    def open_environment(self):
        """Open an existing Python environment"""
        path = filedialog.askdirectory(title="Select Python Environment Directory")
        if not path:
            return
        
        # Check if it's a valid Python environment
        is_valid = False
        python_version = "Unknown"
        
        if sys.platform == "win32":
            python_path = os.path.join(path, "Scripts", "python.exe")
        else:
            python_path = os.path.join(path, "bin", "python")
        
        if os.path.exists(python_path):
            try:
                result = subprocess.run([python_path, "--version"], 
                                       capture_output=True, text=True, check=True)
                python_version = result.stdout.strip()
                is_valid = True
            except:
                pass
        
        if not is_valid:
            messagebox.showerror("Error", "The selected directory is not a valid Python environment")
            return
        
        # Check if already in the list
        for env in self.environments:
            if env["path"] == path:
                messagebox.showinfo("Info", "This environment is already in your list")
                return
        
        # Add to environments list
        name = os.path.basename(path)
        self.environments.append({
            "name": name,
            "path": path,
            "python_version": python_version
        })
        
        # Save environments
        self.save_environments()
        
        # Refresh the list
        self.refresh_environments_list()
        
        messagebox.showinfo("Success", f"Python environment '{name}' added to your list")
    
    def on_environment_double_click(self, event):
        """Handle double-click on environment in the list"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.manage_packages()
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def get_selected_environment(self):
        """Get the selected environment from the tree"""
        selected = self.tree.selection()[0] if self.tree.selection() else None
        if not selected:
            messagebox.showinfo("Info", "Please select an environment first")
            return None
        
        values = self.tree.item(selected, "values")
        env_path = values[1]
        
        for env in self.environments:
            if env["path"] == env_path:
                return env
        
        return None
    
    def manage_packages(self):
        """Open package management window for the selected environment"""
        env = self.get_selected_environment()
        if not env:
            return
        
        # Create package management window
        pkg_window = tk.Toplevel(self.root)
        pkg_window.title(f"Package Manager - {env['name']}")
        pkg_window.geometry("700x500")
        pkg_window.transient(self.root)
        
        # Create main frame
        main_frame = ttk.Frame(pkg_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        ttk.Label(main_frame, text=f"Manage Packages for {env['name']}", 
                 font=("Helvetica", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Installed packages tab
        installed_tab = ttk.Frame(notebook, padding="10")
        notebook.add(installed_tab, text="Installed Packages")
        
        # Install new packages tab
        install_tab = ttk.Frame(notebook, padding="10")
        notebook.add(install_tab, text="Install New Packages")
        
        # Dependencies tab
        dependencies_tab = ttk.Frame(notebook, padding="10")
        notebook.add(dependencies_tab, text="Dependencies")
        
        # Upgrade tab
        upgrade_tab = ttk.Frame(notebook, padding="10")
        notebook.add(upgrade_tab, text="Upgrade Packages")
        
        # Set up installed packages tab
        ttk.Label(installed_tab, text="Installed Packages:").pack(anchor=tk.W)
        
        list_frame = ttk.Frame(installed_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview for packages
        columns = ("name", "version", "latest_version")
        pkg_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        pkg_tree.heading("name", text="Package Name")
        pkg_tree.heading("version", text="Version")
        pkg_tree.heading("latest_version", text="Latest Version")
        
        # Define columns
        pkg_tree.column("name", width=200)
        pkg_tree.column("version", width=100)
        pkg_tree.column("latest_version", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=pkg_tree.yview)
        pkg_tree.configure(yscroll=scrollbar.set)
        
        # Pack tree and scrollbar
        pkg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(installed_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        refresh_btn = ttk.Button(button_frame, text="Refresh List")
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        uninstall_btn = ttk.Button(button_frame, text="Uninstall Selected")
        uninstall_btn.pack(side=tk.LEFT, padx=5)
        
        upgrade_btn = ttk.Button(button_frame, text="Upgrade Selected")
        upgrade_btn.pack(side=tk.LEFT, padx=5)
        
        show_deps_btn = ttk.Button(button_frame, text="Show Dependencies")
        show_deps_btn.pack(side=tk.LEFT, padx=5)
        
        # Set up dependencies tab
        ttk.Label(dependencies_tab, text="Select a package to view its dependencies:").pack(anchor=tk.W, pady=(0, 5))
        
        # Package selection frame
        deps_pkg_frame = ttk.Frame(dependencies_tab)
        deps_pkg_frame.pack(fill=tk.X, pady=5)
        
        deps_pkg_var = tk.StringVar()
        deps_pkg_combo = ttk.Combobox(deps_pkg_frame, textvariable=deps_pkg_var, width=40)
        deps_pkg_combo.pack(side=tk.LEFT)
        
        deps_view_btn = ttk.Button(deps_pkg_frame, text="View Dependencies")
        deps_view_btn.pack(side=tk.LEFT, padx=5)
        
        # Dependencies tree frame
        deps_frame = ttk.LabelFrame(dependencies_tab, text="Dependencies")
        deps_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview for dependencies
        deps_columns = ("name", "version", "required_by")
        deps_tree = ttk.Treeview(deps_frame, columns=deps_columns, show="headings")
        
        # Define headings
        deps_tree.heading("name", text="Package Name")
        deps_tree.heading("version", text="Version")
        deps_tree.heading("required_by", text="Required By")
        
        # Define columns
        deps_tree.column("name", width=150)
        deps_tree.column("version", width=100)
        deps_tree.column("required_by", width=200)
        
        # Add scrollbar
        deps_scrollbar = ttk.Scrollbar(deps_frame, orient=tk.VERTICAL, command=deps_tree.yview)
        deps_tree.configure(yscroll=deps_scrollbar.set)
        
        # Pack tree and scrollbar
        deps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        deps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Set up upgrade tab
        ttk.Label(upgrade_tab, text="Packages with available updates:").pack(anchor=tk.W, pady=(0, 5))
        
        # Upgradable packages frame
        upgrade_frame = ttk.Frame(upgrade_tab)
        upgrade_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview for upgradable packages
        upgrade_columns = ("name", "current_version", "latest_version")
        upgrade_tree = ttk.Treeview(upgrade_frame, columns=upgrade_columns, show="headings")
        
        # Define headings
        upgrade_tree.heading("name", text="Package Name")
        upgrade_tree.heading("current_version", text="Current Version")
        upgrade_tree.heading("latest_version", text="Latest Version")
        
        # Define columns
        upgrade_tree.column("name", width=200)
        upgrade_tree.column("current_version", width=100)
        upgrade_tree.column("latest_version", width=100)
        
        # Add scrollbar
        upgrade_scrollbar = ttk.Scrollbar(upgrade_frame, orient=tk.VERTICAL, command=upgrade_tree.yview)
        upgrade_tree.configure(yscroll=upgrade_scrollbar.set)
        
        # Pack tree and scrollbar
        upgrade_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        upgrade_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Upgrade buttons frame
        upgrade_btn_frame = ttk.Frame(upgrade_tab)
        upgrade_btn_frame.pack(fill=tk.X, pady=10)
        
        upgrade_selected_btn = ttk.Button(upgrade_btn_frame, text="Upgrade Selected")
        upgrade_selected_btn.pack(side=tk.LEFT, padx=5)
        
        upgrade_all_btn = ttk.Button(upgrade_btn_frame, text="Upgrade All")
        upgrade_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Local package installation frame
        local_frame = ttk.LabelFrame(upgrade_tab, text="Install from Local File")
        local_frame.pack(fill=tk.X, pady=10)
        
        local_file_frame = ttk.Frame(local_frame)
        local_file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        local_file_var = tk.StringVar()
        local_file_entry = ttk.Entry(local_file_frame, textvariable=local_file_var, width=50)
        local_file_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        def browse_local_file():
            file_path = filedialog.askopenfilename(
                title="Select Package File",
                filetypes=[("Python Packages", "*.whl *.tar.gz"), ("All Files", "*.*")]
            )
            if file_path:
                local_file_var.set(file_path)
        
        browse_file_btn = ttk.Button(local_file_frame, text="Browse...", command=browse_local_file)
        browse_file_btn.pack(side=tk.LEFT)
        
        install_local_btn = ttk.Button(local_frame, text="Install Local Package")
        install_local_btn.pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        # Set up install new packages tab
        ttk.Label(install_tab, text="Package Name:").pack(anchor=tk.W, pady=(0, 5))
        
        # Package name and version frame
        pkg_frame = ttk.Frame(install_tab)
        pkg_frame.pack(fill=tk.X)
        
        pkg_name_var = tk.StringVar()
        pkg_name_entry = ttk.Entry(pkg_frame, textvariable=pkg_name_var, width=40)
        pkg_name_entry.pack(side=tk.LEFT)
        
        ttk.Label(pkg_frame, text="Version (optional):").pack(side=tk.LEFT, padx=(10, 5))
        
        pkg_version_var = tk.StringVar()
        pkg_version_entry = ttk.Entry(pkg_frame, textvariable=pkg_version_var, width=15)
        pkg_version_entry.pack(side=tk.LEFT)
        
        # Install button
        install_btn = ttk.Button(install_tab, text="Install Package")
        install_btn.pack(anchor=tk.W, pady=10)
        
        # Output frame
        output_frame = ttk.LabelFrame(install_tab, text="Output")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        output_text = tk.Text(output_frame, height=10, wrap=tk.WORD)
        output_text.pack(fill=tk.BOTH, expand=True)
        
        # Get Python executable path
        if sys.platform == "win32":
            python_exe = os.path.join(env["path"], "Scripts", "python.exe")
            pip_exe = os.path.join(env["path"], "Scripts", "pip.exe")
        else:
            python_exe = os.path.join(env["path"], "bin", "python")
            pip_exe = os.path.join(env["path"], "bin", "pip")
        
        # Function to load installed packages
        def load_installed_packages():
            # Clear the tree
            for item in pkg_tree.get_children():
                pkg_tree.delete(item)
            
            try:
                # Run pip list
                result = subprocess.run([pip_exe, "list", "--format=json"], 
                                       capture_output=True, text=True, check=True)
                
                packages = json.loads(result.stdout)
                
                # Get latest versions for packages
                latest_versions = {}
                
                # Add packages to the tree
                for pkg in packages:
                    pkg_name = pkg.get("name", "Unknown")
                    pkg_version = pkg.get("version", "Unknown")
                    
                    # Add to combobox for dependencies
                    deps_pkg_combo['values'] = [p.get("name") for p in packages]
                    
                    pkg_tree.insert("", tk.END, values=(
                        pkg_name,
                        pkg_version,
                        "Checking..."
                    ))
                
                # Update latest versions in background
                pkg_window.after(100, check_for_updates)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to get installed packages: {str(e)}")
        
        # Function to check for package updates
        def check_for_updates():
            try:
                # Run pip list --outdated
                result = subprocess.run(
                    [pip_exe, "list", "--outdated", "--format=json"],
                    capture_output=True, text=True, check=True
                )
                
                outdated_packages = json.loads(result.stdout)
                outdated_dict = {pkg["name"]: pkg["latest_version"] for pkg in outdated_packages}
                
                # Update the tree with latest versions
                for item in pkg_tree.get_children():
                    values = pkg_tree.item(item, "values")
                    pkg_name = values[0]
                    current_version = values[1]
                    
                    if pkg_name in outdated_dict:
                        latest_version = outdated_dict[pkg_name]
                        pkg_tree.item(item, values=(pkg_name, current_version, latest_version))
                    else:
                        pkg_tree.item(item, values=(pkg_name, current_version, "Up to date"))
                
                # Populate upgrade tab
                for item in upgrade_tree.get_children():
                    upgrade_tree.delete(item)
                
                for pkg in outdated_packages:
                    upgrade_tree.insert("", tk.END, values=(
                        pkg.get("name", "Unknown"),
                        pkg.get("version", "Unknown"),
                        pkg.get("latest_version", "Unknown")
                    ))
                
            except Exception as e:
                print(f"Error checking for updates: {str(e)}")
        
        # Function to show dependencies for a package
        def show_dependencies():
            pkg_name = deps_pkg_var.get()
            if not pkg_name:
                messagebox.showinfo("Info", "Please select a package")
                return
            
            # Clear the tree
            for item in deps_tree.get_children():
                deps_tree.delete(item)
            
            try:
                # Run pip show
                result = subprocess.run(
                    [pip_exe, "show", pkg_name],
                    capture_output=True, text=True, check=True
                )
                
                # Parse the output
                output = result.stdout
                requires = None
                required_by = None
                
                for line in output.splitlines():
                    if line.startswith("Requires:"):
                        requires = line.replace("Requires:", "").strip()
                    elif line.startswith("Required-by:"):
                        required_by = line.replace("Required-by:", "").strip()
                
                if requires:
                    deps = [dep.strip() for dep in requires.split(",") if dep.strip()]
                    for dep in deps:
                        # Get version of dependency
                        try:
                            show_result = subprocess.run(
                                [pip_exe, "show", dep],
                                capture_output=True, text=True, check=True
                            )
                            
                            dep_version = "Unknown"
                            for line in show_result.stdout.splitlines():
                                if line.startswith("Version:"):
                                    dep_version = line.replace("Version:", "").strip()
                                    break
                            
                            deps_tree.insert("", tk.END, values=(
                                dep,
                                dep_version,
                                pkg_name
                            ))
                        except:
                            deps_tree.insert("", tk.END, values=(
                                dep,
                                "Not installed",
                                pkg_name
                            ))
                else:
                    deps_tree.insert("", tk.END, values=(
                        "No dependencies",
                        "",
                        ""
                    ))
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to get dependencies: {str(e)}")
        
        # Function to upgrade selected package
        def upgrade_selected_package():
            selected = pkg_tree.selection()[0] if pkg_tree.selection() else None
            if not selected:
                messagebox.showinfo("Info", "Please select a package to upgrade")
                return
            
            values = pkg_tree.item(selected, "values")
            pkg_name = values[0]
            latest_version = values[2]
            
            if latest_version == "Up to date":
                messagebox.showinfo("Info", f"Package '{pkg_name}' is already up to date")
                return
            
            # Confirm upgrade
            if messagebox.askyesno("Confirm", f"Upgrade {pkg_name} to version {latest_version}?"):
                # Clear output
                output_text.delete(1.0, tk.END)
                
                try:
                    # Run pip install --upgrade
                    process = subprocess.Popen(
                        [pip_exe, "install", "--upgrade", pkg_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    # Show output in real-time
                    for line in process.stdout:
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)
                        pkg_window.update()
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        output_text.insert(tk.END, f"\nPackage '{pkg_name}' upgraded successfully\n")
                        
                        # Refresh the list
                        load_installed_packages()
                    else:
                        output_text.insert(tk.END, f"\nFailed to upgrade package '{pkg_name}'\n")
                    
                except Exception as e:
                    output_text.insert(tk.END, f"\nError: {str(e)}\n")
        
        # Function to upgrade selected package from upgrade tab
        def upgrade_selected_from_tab():
            selected = upgrade_tree.selection()[0] if upgrade_tree.selection() else None
            if not selected:
                messagebox.showinfo("Info", "Please select a package to upgrade")
                return
            
            values = upgrade_tree.item(selected, "values")
            pkg_name = values[0]
            latest_version = values[2]
            
            # Confirm upgrade
            if messagebox.askyesno("Confirm", f"Upgrade {pkg_name} to version {latest_version}?"):
                # Switch to install tab to show output
                notebook.select(1)  # Switch to install tab
                
                # Clear output
                output_text.delete(1.0, tk.END)
                
                try:
                    # Run pip install --upgrade
                    process = subprocess.Popen(
                        [pip_exe, "install", "--upgrade", pkg_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    # Show output in real-time
                    for line in process.stdout:
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)
                        pkg_window.update()
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        output_text.insert(tk.END, f"\nPackage '{pkg_name}' upgraded successfully\n")
                        
                        # Refresh the list
                        load_installed_packages()
                    else:
                        output_text.insert(tk.END, f"\nFailed to upgrade package '{pkg_name}'\n")
                    
                except Exception as e:
                    output_text.insert(tk.END, f"\nError: {str(e)}\n")
        
        # Function to upgrade all packages
        def upgrade_all_packages():
            if not upgrade_tree.get_children():
                messagebox.showinfo("Info", "No packages need upgrading")
                return
            
            # Confirm upgrade
            if messagebox.askyesno("Confirm", "Upgrade all outdated packages?"):
                # Switch to install tab to show output
                notebook.select(1)  # Switch to install tab
                
                # Clear output
                output_text.delete(1.0, tk.END)
                
                try:
                    # Run pip install --upgrade for all outdated packages
                    process = subprocess.Popen(
                        [pip_exe, "install", "--upgrade", *[upgrade_tree.item(item, "values")[0] for item in upgrade_tree.get_children()]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    # Show output in real-time
                    for line in process.stdout:
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)
                        pkg_window.update()
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        output_text.insert(tk.END, "\nAll packages upgraded successfully\n")
                        
                        # Refresh the list
                        load_installed_packages()
                    else:
                        output_text.insert(tk.END, "\nFailed to upgrade some packages\n")
                    
                except Exception as e:
                    output_text.insert(tk.END, f"\nError: {str(e)}\n")
        
        # Function to install local package
        def install_local_package():
            file_path = local_file_var.get().strip()
            if not file_path:
                messagebox.showerror("Error", "Please select a package file")
                return
            
            if not os.path.exists(file_path):
                messagebox.showerror("Error", "The selected file does not exist")
                return
            
            # Switch to install tab to show output
            notebook.select(1)  # Switch to install tab
            
            # Clear output
            output_text.delete(1.0, tk.END)
            
            try:
                # Run pip install
                process = subprocess.Popen(
                    [pip_exe, "install", file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Show output in real-time
                for line in process.stdout:
                    output_text.insert(tk.END, line)
                    output_text.see(tk.END)
                    pkg_window.update()
                
                process.wait()
                
                if process.returncode == 0:
                    output_text.insert(tk.END, f"\nPackage installed successfully from '{file_path}'\n")
                    
                    # Refresh the list
                    load_installed_packages()
                else:
                    output_text.insert(tk.END, f"\nFailed to install package from '{file_path}'\n")
                
            except Exception as e:
                output_text.insert(tk.END, f"\nError: {str(e)}\n")
        
        # Function to uninstall selected package
        def uninstall_package():
            selected = pkg_tree.selection()[0] if pkg_tree.selection() else None
            if not selected:
                messagebox.showinfo("Info", "Please select a package to uninstall")
                return
            
            values = pkg_tree.item(selected, "values")
            pkg_name = values[0]
            
            if messagebox.askyesno("Confirm", f"Are you sure you want to uninstall {pkg_name}?"):
                try:
                    # Run pip uninstall
                    subprocess.run([pip_exe, "uninstall", "-y", pkg_name], check=True)
                    
                    # Refresh the list
                    load_installed_packages()
                    
                    messagebox.showinfo("Success", f"Package '{pkg_name}' uninstalled successfully")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to uninstall package: {str(e)}")
        
        # Function to install package
        def install_package():
            pkg_name = pkg_name_var.get().strip()
            pkg_version = pkg_version_var.get().strip()
            
            if not pkg_name:
                messagebox.showerror("Error", "Please enter a package name")
                return
            
            # Clear output
            output_text.delete(1.0, tk.END)
            
            # Prepare command
            if pkg_version:
                pkg_spec = f"{pkg_name}=={pkg_version}"
            else:
                pkg_spec = pkg_name
            
            try:
                # Run pip install
                process = subprocess.Popen(
                    [pip_exe, "install", pkg_spec],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Show output in real-time
                for line in process.stdout:
                    output_text.insert(tk.END, line)
                    output_text.see(tk.END)
                    pkg_window.update()
                
                process.wait()
                
                if process.returncode == 0:
                    output_text.insert(tk.END, f"\nPackage '{pkg_spec}' installed successfully\n")
                    
                    # Refresh the list
                    load_installed_packages()
                else:
                    output_text.insert(tk.END, f"\nFailed to install package '{pkg_spec}'\n")
                
            except Exception as e:
                output_text.insert(tk.END, f"\nError: {str(e)}\n")
        
        # Connect functions to buttons
        refresh_btn.config(command=load_installed_packages)
        uninstall_btn.config(command=uninstall_package)
        install_btn.config(command=install_package)
        upgrade_btn.config(command=upgrade_selected_package)
        show_deps_btn.config(command=lambda: notebook.select(2))  # Switch to dependencies tab
        
        deps_view_btn.config(command=show_dependencies)
        upgrade_selected_btn.config(command=upgrade_selected_from_tab)
        upgrade_all_btn.config(command=upgrade_all_packages)
        install_local_btn.config(command=install_local_package)
        
        # Load installed packages
        load_installed_packages()
    
    def open_in_explorer(self):
        """Open the environment directory in file explorer"""
        env = self.get_selected_environment()
        if not env:
            return
        
        path = env["path"]
        
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])
    
    def remove_environment(self):
        """Remove the environment from the list (does not delete files)"""
        env = self.get_selected_environment()
        if not env:
            return
        
        if messagebox.askyesno("Confirm", f"Remove '{env['name']}' from the list? (This will not delete the environment files)"):
            # Remove from the list
            self.environments = [e for e in self.environments if e["path"] != env["path"]]
            
            # Save environments
            self.save_environments()
            
            # Refresh the list
            self.refresh_environments_list()

    def backup_environment(self):
        """Backup the selected environment"""
        env = self.get_selected_environment()
        if not env:
            return
        
        # Ask for backup location
        backup_path = filedialog.askdirectory(title="Select Backup Location")
        if not backup_path:
            return
        
        # Create backup directory
        backup_dir = os.path.join(backup_path, f"{env['name']}_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy environment files
        try:
            shutil.copytree(env["path"], os.path.join(backup_dir, env["name"]))
            messagebox.showinfo("Success", f"Environment '{env['name']}' backed up successfully to '{backup_dir}'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to backup environment: {str(e)}")

    def get_system_python_version(self):
        """Get the system Python version"""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                   capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return "Unknown"
    
    def check_for_updates(self):
        """Check for updates from GitHub and update if available"""
        # Create update dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Check for Updates")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="Check for Updates", 
                 font=("Helvetica", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Current version info
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(version_frame, text="Current Version:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(version_frame, text=APP_VERSION).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        status_text = tk.Text(status_frame, height=10, width=50, wrap=tk.WORD)
        status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        status_text.config(state=tk.DISABLED)
        
        # Progress bar
        progress = ttk.Progressbar(main_frame, mode="determinate")
        progress.pack(fill=tk.X, pady=10)
        progress["value"] = 0
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        update_btn = ttk.Button(button_frame, text="Update", state=tk.DISABLED)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = ttk.Button(button_frame, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Function to append text to status
        def append_status(text):
            status_text.config(state=tk.NORMAL)
            status_text.insert(tk.END, text + "\n")
            status_text.see(tk.END)
            status_text.config(state=tk.DISABLED)
            dialog.update()
        
        # Function to download and update
        def download_and_update(release_data):
            try:
                append_status("Preparing to update...")
                progress["value"] = 0
                
                # Find the zip asset
                zip_asset = None
                for asset in release_data['assets']:
                    if asset['name'].endswith('.zip'):
                        zip_asset = asset
                        break
                
                if not zip_asset:
                    append_status("Error: No zip file found in release assets.")
                    append_status("Please make sure the GitHub release includes a .zip file.")
                    close_btn.config(state=tk.NORMAL)
                    return
                
                # Download the zip file
                append_status(f"Downloading update package: {zip_asset['name']}...")
                download_url = zip_asset['browser_download_url']
                
                # Create temp directory
                temp_dir = tempfile.mkdtemp()
                zip_path = os.path.join(temp_dir, zip_asset['name'])
                
                # Function to update progress bar
                def update_progress(count, block_size, total_size):
                    if total_size > 0:
                        percent = min(count * block_size * 100 / total_size, 100)
                        progress["value"] = percent
                        dialog.update()
                
                # Download the file
                urllib.request.urlretrieve(download_url, zip_path, reporthook=update_progress)
                
                append_status("Download complete.")
                append_status("Extracting files...")
                progress["value"] = 0
                
                # Extract the zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Get total files for progress tracking
                    total_files = len(zip_ref.namelist())
                    extracted = 0
                    
                    # Extract each file
                    for file in zip_ref.namelist():
                        zip_ref.extract(file, temp_dir)
                        extracted += 1
                        progress["value"] = (extracted / total_files) * 100
                        if extracted % 10 == 0:  # Update UI every 10 files
                            dialog.update()
                
                # Find the extracted directory
                extracted_dir = None
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path) and item != "__MACOSX":  # Skip macOS metadata
                        extracted_dir = item_path
                        break
                
                if not extracted_dir:
                    append_status("Error: Could not find extracted directory.")
                    close_btn.config(state=tk.NORMAL)
                    return
                
                append_status("Preparing to apply update...")
                progress["value"] = 0
                
                # Get current application directory
                app_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Create backup of current version
                backup_dir = os.path.join(app_dir, f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
                append_status(f"Creating backup in: {backup_dir}")
                shutil.copytree(app_dir, backup_dir, ignore=shutil.ignore_patterns('backup_*'))
                
                # Create update script
                update_script = """
import os
import sys
import shutil
import time
import subprocess

# Wait for the parent process to exit
time.sleep(2)

# Start the application with the new Python
subprocess.Popen([r"{python}", r"{script}"])
                """.format(python=sys.executable, script=os.path.abspath(__file__))
                
                # Write update script to a temporary file
                with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
                    f.write(update_script)
                    restart_script_path = f.name
                
                # Run the restart script
                subprocess.Popen([sys.executable, restart_script_path])
                
                # Close the application
                self.root.quit()
                
            except Exception as e:
                append_status(f"Error during update: {str(e)}")
                close_btn.config(state=tk.NORMAL)
        
        # Function to check for updates
        def do_check_for_updates():
            try:
                append_status("Checking for updates...")
                progress["value"] = 10
                
                # Demo mode for testing without a real GitHub repo
                if DEMO_MODE:
                    append_status("Running in demo mode (no actual GitHub repository connected)")
                    progress["value"] = 30
                    
                    # Simulate a delay
                    time.sleep(1)
                    
                    # Simulate finding a new version
                    latest_version = "1.1.0"
                    append_status(f"Latest version: {latest_version}")
                    
                    progress["value"] = 50
                    
                    # Simulate release notes
                    release_notes = """
## What's New in 1.1.0

### New Features
- Added automatic update system
- Improved Python version management
- Enhanced package dependency visualization

### Bug Fixes
- Fixed issue with environment creation on some systems
- Improved error handling throughout the application
- Better compatibility with different Python versions
                    """
                    
                    append_status("Update available!")
                    append_status(f"Release notes:\n{release_notes}")
                    
                    # Enable update button
                    update_btn.config(state=tk.NORMAL)
                    
                    # Configure update button for demo mode
                    def demo_update():
                        update_btn.config(state=tk.DISABLED)
                        close_btn.config(state=tk.DISABLED)
                        
                        append_status("Preparing to update...")
                        progress["value"] = 0
                        
                        # Simulate download
                        for i in range(0, 101, 10):
                            append_status(f"Downloading update: {i}%") if i % 30 == 0 else None
                            progress["value"] = i
                            time.sleep(0.2)
                            dialog.update()
                        
                        append_status("Download complete.")
                        append_status("Extracting files...")
                        progress["value"] = 0
                        
                        # Simulate extraction
                        for i in range(0, 101, 5):
                            progress["value"] = i
                            time.sleep(0.1)
                            dialog.update()
                        
                        append_status("Preparing to apply update...")
                        append_status("Creating backup of current version...")
                        progress["value"] = 0
                        
                        # Simulate backup and update
                        for i in range(0, 101, 20):
                            append_status(f"Backing up files: {i}%") if i % 40 == 0 else None
                            progress["value"] = i
                            time.sleep(0.2)
                            dialog.update()
                        
                        append_status("Update ready. The application will restart to apply the update.")
                        progress["value"] = 100
                        
                        # Show demo message
                        messagebox.showinfo("Demo Mode", 
                                           "This is a demonstration of the update feature.\n\n"
                                           "In a real deployment, the application would download "
                                           "and install the update from GitHub.\n\n"
                                           "To use this feature, set DEMO_MODE to False and "
                                           "configure a valid GitHub repository.")
                        
                        close_btn.config(state=tk.NORMAL)
                    
                    update_btn.config(command=demo_update)
                    
                else:
                    # Real GitHub API implementation
                    # Fetch latest release info from GitHub API
                    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
                    
                    append_status(f"Connecting to GitHub API: {api_url}")
                    
                    headers = {
                        'User-Agent': 'Python Environment Manager Update Checker',
                        'Accept': 'application/vnd.github.v3+json'
                    }
                    
                    req = urllib.request.Request(api_url, headers=headers)
                    
                    try:
                        with urllib.request.urlopen(req) as response:
                            data = json.loads(response.read().decode('utf-8'))
                            
                            # Debug output
                            append_status(f"API response received. Status: {response.status}")
                            
                            if 'tag_name' not in data:
                                append_status("Error: Invalid response from GitHub API")
                                append_status(f"Response keys: {', '.join(data.keys())}")
                                progress["value"] = 0
                                return
                            
                            latest_version = data['tag_name'].lstrip('v')
                            progress["value"] = 30
                            
                            append_status(f"Latest version: {latest_version}")
                            
                            # Compare versions
                            try:
                                current_version_parts = [int(x) for x in APP_VERSION.split('.')]
                                latest_version_parts = [int(x) for x in latest_version.split('.')]
                                
                                # Pad with zeros if needed
                                while len(current_version_parts) < 3:
                                    current_version_parts.append(0)
                                while len(latest_version_parts) < 3:
                                    latest_version_parts.append(0)
                                
                                update_available = False
                                for i in range(3):
                                    if latest_version_parts[i] > current_version_parts[i]:
                                        update_available = True
                                        break
                                    elif latest_version_parts[i] < current_version_parts[i]:
                                        break
                                
                                progress["value"] = 50
                                
                                if update_available:
                                    append_status("Update available!")
                                    
                                    # Check if body exists in the response
                                    if 'body' in data and data['body']:
                                        append_status(f"Release notes:\n{data['body']}")
                                    else:
                                        append_status("No release notes available.")
                                    
                                    # Check if there are assets
                                    if 'assets' not in data or not data['assets']:
                                        append_status("Warning: No assets found in this release.")
                                        append_status("The update cannot be downloaded automatically.")
                                        progress["value"] = 100
                                        return
                                    
                                    # Enable update button
                                    update_btn.config(state=tk.NORMAL)
                                    
                                    # Configure update button
                                    def do_update():
                                        update_btn.config(state=tk.DISABLED)
                                        close_btn.config(state=tk.DISABLED)
                                        download_and_update(data)
                                    
                                    update_btn.config(command=do_update)
                                else:
                                    append_status("You have the latest version.")
                            except ValueError as e:
                                append_status(f"Error parsing version numbers: {str(e)}")
                                append_status(f"Current version: {APP_VERSION}, Latest version: {latest_version}")
                        
                    except urllib.error.HTTPError as e:
                        if e.code == 404:
                            append_status(f"Error: GitHub repository '{GITHUB_REPO}' not found or no releases available.")
                            append_status("Please check the GITHUB_REPO constant in the code.")
                            append_status("Make sure you have created at least one release on GitHub.")
                        else:
                            append_status(f"HTTP Error: {e.code} - {e.reason}")
                            append_status(f"Response: {e.read().decode('utf-8')}")
                    except urllib.error.URLError as e:
                        append_status(f"Connection Error: {e.reason}")
                        append_status("Please check your internet connection.")
                    except json.JSONDecodeError as e:
                        append_status(f"Error parsing GitHub API response: {str(e)}")
                
                progress["value"] = 100
                
            except Exception as e:
                append_status(f"Error checking for updates: {str(e)}")
                progress["value"] = 0
                
                # Log the error for debugging
                import traceback
                append_status("Detailed error information:")
                append_status(traceback.format_exc())
                print(f"Version fetch error: {str(e)}")
                print(traceback.format_exc())
        
        # Start the update check in a separate thread
        threading.Thread(target=do_check_for_updates, daemon=True).start()
    
    def change_python_version(self):
        """Change the Python version used by the application"""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Python Version")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create form
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current Python info
        ttk.Label(form_frame, text="Current Python:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(form_frame, text=f"{self.system_python_version}").grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(form_frame, text=f"{sys.executable}").grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Separator(form_frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        # New Python executable
        ttk.Label(form_frame, text="Select New Python Executable:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        python_frame = ttk.Frame(form_frame)
        python_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        python_var = tk.StringVar()
        python_entry = ttk.Entry(python_frame, textvariable=python_var, width=30)
        python_entry.pack(side=tk.LEFT)
        
        def browse_python():
            filetypes = [("Python Executable", "python.exe")] if sys.platform == "win32" else []
            path = filedialog.askopenfilename(title="Select Python Executable", filetypes=filetypes)
            if path:
                python_var.set(path)
                
                # Get version of selected Python
                try:
                    result = subprocess.run([path, "--version"], 
                                           capture_output=True, text=True, check=True)
                    version_label.config(text=f"Version: {result.stdout.strip()}")
                except:
                    version_label.config(text="Version: Unknown")
        
        browse_python_btn = ttk.Button(python_frame, text="Browse...", command=browse_python)
        browse_python_btn.pack(side=tk.LEFT, padx=5)
        
        # Version info
        version_label = ttk.Label(form_frame, text="Version: ")
        version_label.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Warning
        warning_frame = ttk.Frame(form_frame)
        warning_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Label(warning_frame, text="Warning:", font=("Helvetica", 9, "bold")).pack(anchor=tk.W)
        ttk.Label(warning_frame, text="Changing Python version will restart the application.", 
                 wraplength=400).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        def on_cancel():
            dialog.destroy()
        
        def on_change():
            new_python = python_var.get().strip()
            if not new_python:
                messagebox.showerror("Error", "Please select a Python executable")
                return
            
            if not os.path.exists(new_python):
                messagebox.showerror("Error", "The selected file does not exist")
                return
            
            # Verify it's a Python executable
            try:
                result = subprocess.run([new_python, "--version"], 
                                       capture_output=True, text=True, check=True)
                
                # Create a restart script
                restart_script = """
import os
import sys
import subprocess
import time

# Wait for the parent process to exit
time.sleep(1)

# Start the application with the new Python
subprocess.Popen([r"{python}", r"{script}"])
                """.format(python=new_python, script=os.path.abspath(__file__))
                
                # Write restart script to a temporary file
                with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
                    f.write(restart_script)
                    restart_script_path = f.name
                
                # Run the restart script
                subprocess.Popen([sys.executable, restart_script_path])
                
                # Close the application
                self.root.quit()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to verify Python executable: {str(e)}")
        
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Change", command=on_change).pack(side=tk.LEFT, padx=5)
    
    def download_python(self):
        """Open dialog to download Python"""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Download Python")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="Download Python", 
                 font=("Helvetica", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Description
        ttk.Label(main_frame, text="Select a Python version to download:", 
                 wraplength=550).pack(anchor=tk.W, pady=(0, 10))
        
        # Version selection frame
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(version_frame, text="Python Version:").pack(side=tk.LEFT)
        
        # Python versions - default list
        default_versions = ["3.12.0", "3.11.7", "3.10.13", "3.9.18", "3.8.18"]
        version_var = tk.StringVar(value=default_versions[0])
        version_combo = ttk.Combobox(version_frame, textvariable=version_var, values=default_versions, width=10)
        version_combo.pack(side=tk.LEFT, padx=5)
        
        # Refresh button for versions
        def fetch_python_versions():
            refresh_btn.config(text="Refreshing...", state="disabled")
            status_label.config(text="Fetching latest Python versions...")
            progress["value"] = 10
            dialog.update()
            
            # Function to actually fetch versions in a separate thread
            def do_fetch():
                try:
                    # Fetch the Python downloads page
                    url = "https://www.python.org/downloads/"
                    
                    # Create a request with headers that accept gzip encoding
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate'
                    }
                    
                    req = urllib.request.Request(url, headers=headers)
                    
                    with urllib.request.urlopen(req) as response:
                        # Check if the response is gzipped
                        if response.info().get('Content-Encoding') == 'gzip':
                            html = gzip.decompress(response.read()).decode('utf-8')
                        else:
                            html = response.read().decode('utf-8')
                    
                    progress["value"] = 50
                    dialog.update()
                    
                    # Extract version numbers using regex
                    # Look for Python 3.x.y release links
                    pattern = r'Python\s+(\d+\.\d+\.\d+)'
                    matches = re.findall(pattern, html)
                    
                    # Filter to only get Python 3.x versions and sort them
                    versions = []
                    for match in matches:
                        if match.startswith('3.'):
                            versions.append(match)
                    
                    # Remove duplicates and sort in descending order
                    versions = sorted(list(set(versions)), key=lambda v: [int(x) for x in v.split('.')], reverse=True)
                    
                    # Take the top 10 versions
                    versions = versions[:10] if len(versions) > 10 else versions
                    
                    progress["value"] = 80
                    dialog.update()
                    
                    # Update the combobox
                    if versions:
                        version_combo['values'] = versions
                        version_var.set(versions[0])  # Set to latest version
                        status_label.config(text=f"Found {len(versions)} Python versions")
                    else:
                        # If no versions found, revert to default list
                        version_combo['values'] = default_versions
                        status_label.config(text="Could not fetch versions, using default list")
                    
                    progress["value"] = 100
                    refresh_btn.config(text="Refresh Versions", state="normal")
                    
                    # After a delay, reset progress bar
                    dialog.after(2000, lambda: setattr(progress, "value", 0))
                    
                except Exception as e:
                    status_label.config(text=f"Error fetching versions: {str(e)}")
                    refresh_btn.config(text="Refresh Versions", state="normal")
                    progress["value"] = 0
                    
                    # Log the error for debugging
                    print(f"Version fetch error: {str(e)}")
            
            # Run in a separate thread to keep UI responsive
            import threading
            threading.Thread(target=do_fetch, daemon=True).start()
        
        refresh_btn = ttk.Button(version_frame, text="Refresh Versions", command=fetch_python_versions)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Auto-fetch versions on startup
        dialog.after(100, fetch_python_versions)
        
        # OS selection
        os_frame = ttk.Frame(main_frame)
        os_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(os_frame, text="Operating System:").pack(side=tk.LEFT)
        
        # Detect current OS
        current_os = "Windows"
        if sys.platform == "darwin":
            current_os = "macOS"
        elif sys.platform.startswith("linux"):
            current_os = "Linux"
        
        os_var = tk.StringVar(value=current_os)
        os_combo = ttk.Combobox(os_frame, textvariable=os_var, 
                               values=["Windows", "macOS", "Linux"], width=10)
        os_combo.pack(side=tk.LEFT, padx=5)
        
        # Architecture selection
        arch_frame = ttk.Frame(main_frame)
        arch_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(arch_frame, text="Architecture:").pack(side=tk.LEFT)
        
        # Detect current architecture
        current_arch = "64-bit"
        if platform.architecture()[0] == "32bit":
            current_arch = "32-bit"
        
        arch_var = tk.StringVar(value=current_arch)
        arch_combo = ttk.Combobox(arch_frame, textvariable=arch_var, 
                                 values=["64-bit", "32-bit"], width=10)
        arch_combo.pack(side=tk.LEFT, padx=5)
        
        # Download options
        download_frame = ttk.LabelFrame(main_frame, text="Download Options")
        download_frame.pack(fill=tk.X, pady=10)
        
        # Option to download installer or embeddable package
        package_var = tk.StringVar(value="Installer")
        ttk.Radiobutton(download_frame, text="Installer (recommended)", 
                       variable=package_var, value="Installer").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Radiobutton(download_frame, text="Embeddable package (portable)", 
                       variable=package_var, value="Embeddable").pack(anchor=tk.W, padx=10, pady=5)
        
        # Download location
        location_frame = ttk.Frame(main_frame)
        location_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(location_frame, text="Download Location:").pack(anchor=tk.W)
        
        loc_select_frame = ttk.Frame(location_frame)
        loc_select_frame.pack(fill=tk.X, pady=5)
        
        location_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        location_entry = ttk.Entry(loc_select_frame, textvariable=location_var, width=50)
        location_entry.pack(side=tk.LEFT)
        
        def browse_location():
            path = filedialog.askdirectory(title="Select Download Location")
            if path:
                location_var.set(path)
        
        browse_loc_btn = ttk.Button(loc_select_frame, text="Browse...", command=browse_location)
        browse_loc_btn.pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        status_label = ttk.Label(status_frame, text="")
        status_label.pack(anchor=tk.W)
        
        progress = ttk.Progressbar(status_frame, mode="determinate")
        progress.pack(fill=tk.X, pady=5)
        progress["value"] = 0
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def on_cancel():
            dialog.destroy()
        
        def on_download():
            version = version_var.get()
            os_name = os_var.get()
            arch = arch_var.get()
            package_type = package_var.get()
            location = location_var.get()
            
            if not os.path.exists(location):
                messagebox.showerror("Error", "The download location does not exist")
                return
            
            # Construct download URL
            base_url = "https://www.python.org/ftp/python/"
            
            # Format version for URL (e.g., 3.10.2 -> 3.10.2)
            version_parts = version.split(".")
            if len(version_parts) == 2:
                version = f"{version}.0"
            
            # Determine file extension and architecture string
            file_ext = ""
            arch_str = ""
            
            if os_name == "Windows":
                if package_type == "Installer":
                    file_ext = ".exe"
                    if arch == "64-bit":
                        arch_str = "-amd64"
                    else:
                        arch_str = ""
                else:  # Embeddable
                    file_ext = ".zip"
                    if arch == "64-bit":
                        arch_str = "-amd64"
                    else:
                        arch_str = ""
            elif os_name == "macOS":
                file_ext = ".pkg"
                if float(version_parts[0] + "." + version_parts[1]) >= 3.8:
                    arch_str = "-macos11" if arch == "64-bit" else "-macos11"
                else:
                    arch_str = "-macosx10.9" if arch == "64-bit" else "-macosx10.9"
            else:  # Linux
                # For Linux, we'll open the download page instead
                linux_url = f"https://www.python.org/downloads/release/python-{version.replace('.', '')}"
                webbrowser.open(linux_url)
                status_label.config(text="Opening Python download page for Linux...")
                return
            
            # Construct filename
            if os_name == "Windows":
                if package_type == "Installer":
                    filename = f"python-{version}{arch_str}{file_ext}"
                else:
                    filename = f"python-{version}{arch_str}-embed{file_ext}"
            else:  # macOS
                filename = f"python-{version}{arch_str}{file_ext}"
            
            # Full URL
            url = f"{base_url}{version}/{filename}"
            
            # Full path to save
            save_path = os.path.join(location, filename)
            
            # Download function
            def download_file():
                try:
                    status_label.config(text=f"Downloading {filename}...")
                    
                    # Function to update progress bar
                    def update_progress(count, block_size, total_size):
                        if total_size > 0:
                            percent = min(count * block_size * 100 / total_size, 100)
                            progress["value"] = percent
                            dialog.update()
                    
                    # Download the file
                    urllib.request.urlretrieve(url, save_path, reporthook=update_progress)
                    
                    status_label.config(text=f"Download complete: {save_path}")
                    messagebox.showinfo("Success", f"Python {version} downloaded successfully to {save_path}")
                    
                    # Ask if user wants to run the installer
                    if os_name == "Windows" and package_type == "Installer":
                        if messagebox.askyesno("Install Python", "Do you want to run the Python installer now?"):
                            subprocess.Popen([save_path])
                    
                except Exception as e:
                    status_label.config(text=f"Error: {str(e)}")
                    messagebox.showerror("Error", f"Failed to download Python: {str(e)}")
                    
                    # Offer to open the download page
                    if messagebox.askyesno("Open Download Page", "Would you like to open the Python download page in your browser?"):
                        download_page = f"https://www.python.org/downloads/release/python-{version.replace('.', '')}"
                        webbrowser.open(download_page)
            
            # Start download in a separate thread to keep UI responsive
            import threading
            threading.Thread(target=download_file, daemon=True).start()
        
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Download", command=on_download).pack(side=tk.LEFT, padx=5)
        
        # Add a direct link to Python website
        link_frame = ttk.Frame(main_frame)
        link_frame.pack(fill=tk.X, pady=10)
        
        def open_python_website():
            webbrowser.open("https://www.python.org/downloads/")
        
        link_label = ttk.Label(link_frame, text="Visit Python.org for more download options", 
                              foreground="blue", cursor="hand2")
        link_label.pack(anchor=tk.W)
        link_label.bind("<Button-1>", lambda e: open_python_website())

    def show_about(self):
        """Show about dialog with application information"""
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title(f"About {APP_NAME}")
        about_dialog.geometry("400x300")
        about_dialog.transient(self.root)
        about_dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(about_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # App logo/icon (if available)
        try:
            logo_img = tk.PhotoImage(file="icon.png")
            logo_img = logo_img.subsample(3, 3)  # Scale down the image
            logo_label = ttk.Label(main_frame, image=logo_img)
            logo_label.image = logo_img  # Keep a reference
            logo_label.pack(pady=(0, 10))
        except:
            # If icon not found, just show the app name
            ttk.Label(main_frame, text=APP_NAME, 
                     font=("Helvetica", 18, "bold")).pack(pady=(0, 10))
        
        # App information
        ttk.Label(main_frame, text=f"Version {APP_VERSION}", 
                 font=("Helvetica", 10)).pack(pady=(0, 15))
        
        ttk.Label(main_frame, text=f"Developed by {AUTHOR}", 
                 font=("Helvetica", 10)).pack(pady=(0, 5))
        
        # GitHub link
        github_frame = ttk.Frame(main_frame)
        github_frame.pack(pady=(0, 15))
        
        ttk.Label(github_frame, text="GitHub: ").pack(side=tk.LEFT)
        
        github_link = ttk.Label(github_frame, text=GITHUB_URL, 
                               foreground="blue", cursor="hand2")
        github_link.pack(side=tk.LEFT)
        github_link.bind("<Button-1>", lambda e: self.open_url(GITHUB_URL))
        
        # Description
        description = (
            f"{APP_NAME} is a comprehensive tool for managing Python virtual environments, "
            "packages, and Python installations. It provides an intuitive graphical interface "
            "for tasks that would otherwise require command-line operations."
        )
        
        desc_label = ttk.Label(main_frame, text=description, wraplength=350, justify=tk.CENTER)
        desc_label.pack(pady=(0, 15))
        
        # Close button
        ttk.Button(main_frame, text="Close", command=about_dialog.destroy).pack()
    
    def open_url(self, url):
        """Open a URL in the default web browser"""
        import webbrowser
        webbrowser.open(url)

def main():
    root = tk.Tk()
    app = PyEnvManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
