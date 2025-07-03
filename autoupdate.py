import os
import requests
import zipfile
import shutil
from tkinter import messagebox

def check_for_update(repo_url, current_version):
    """Checks for updates by comparing the current version with the latest version on GitHub."""
    try:
        if not repo_url.startswith("http://") and not repo_url.startswith("https://"):
            raise ValueError("Invalid URL format. Ensure the URL starts with 'http://' or 'https://'.")

        response = requests.get(f"{repo_url}/releases/latest", timeout=10)
        if response.status_code == 404:
            messagebox.showinfo("Info", "No updates available. No releases found.")
            return None

        response.raise_for_status()
        latest_version = response.url.split("/")[-1]

        # Ensure the latest version is a valid number
        if not latest_version.replace('.', '').isdigit():
            messagebox.showerror("Error", "Invalid version format retrieved from GitHub.")
            return None

        if latest_version != current_version:
            messagebox.showinfo(
                "Update Check",
                f"Current Version: {current_version}\nLatest Version: {latest_version}\n\nUpdate available!"
            )
            return latest_version
        else:
            messagebox.showinfo(
                "Update Check",
                f"Current Version: {current_version}\nLatest Version: {latest_version}\n\nYou are up-to-date!"
            )
            return None
    except (requests.RequestException, ValueError) as e:
        messagebox.showerror("Error", f"Failed to check for updates: {e}")
        return None

def download_and_extract_update(repo_url, latest_version, extract_to):
    """Downloads and extracts the latest update from GitHub."""
    try:
        zip_url = f"{repo_url}/archive/refs/tags/{latest_version}.zip"
        response = requests.get(zip_url, stream=True, timeout=10)
        response.raise_for_status()

        zip_path = os.path.join(extract_to, f"{latest_version}.zip")
        with open(zip_path, "wb") as zip_file:
            for chunk in response.iter_content(chunk_size=8192):
                zip_file.write(chunk)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)

        os.remove(zip_path)
        return True
    except (requests.RequestException, zipfile.BadZipFile, OSError) as e:
        messagebox.showerror("Error", f"Failed to download or extract update: {e}")
        return False

def apply_update(update_folder, target_folder):
    """Replaces the current application files with the updated files."""
    try:
        for item in os.listdir(update_folder):
            s = os.path.join(update_folder, item)
            d = os.path.join(target_folder, item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        shutil.rmtree(update_folder)
        messagebox.showinfo("Info", "Update applied successfully!")
    except OSError as e:
        messagebox.showerror("Error", f"Failed to apply update: {e}")

def prompt_update(current_version, extract_to, target_folder, repo_url="https://github.com/Veitners/Luna-reader"):
    """Prompts the user to update the application."""
    latest_version = check_for_update(repo_url, current_version)
    if latest_version:
        if messagebox.askyesno("Update Available", f"Version {latest_version} is available. Do you want to update?"):
            update_folder = os.path.join(extract_to, f"repo-{latest_version}")
            if download_and_extract_update(repo_url, latest_version, extract_to):
                apply_update(update_folder, target_folder)
                messagebox.showinfo("Update Complete", "The application has been updated successfully. Please restart the application.")
            else:
                messagebox.showerror("Update Failed", "Failed to download or apply the update.")
