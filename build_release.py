import PyInstaller.__main__
import shutil
import os
import plistlib
import subprocess
import tomllib


def build():
    print("Building QR Network Scanner...")

    # Clean up previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    PyInstaller.__main__.run(
        [
            "src/qr_network/main.py",  # Updated entry point
            "--name=QRNetworkScanner",
            "--windowed",  # No console window
            "--icon=assets/icon.png",  # App Icon
            "--add-data=assets:assets",  # Include all help assets
            "--clean",
            "--noconfirm",
            # Hidden imports often needed for these libraries
            "--hidden-import=rich",
            "--hidden-import=zxingcpp",
            "--hidden-import=pkg_resources.extern",
            "--collect-all=rich",
        ]
    )
    # Update Info.plist with Camera Permissions
    plist_path = "dist/QRNetworkScanner.app/Contents/Info.plist"
    if os.path.exists(plist_path):
        print("Updating Info.plist with Camera Usage Description...")
        with open(plist_path, "rb") as f:
            plist = plistlib.load(f)

        plist[
            "NSCameraUsageDescription"
        ] = "This app needs access to the camera to scan QR codes for WiFi networks."

        # Set Version from pyproject.toml
        try:
            with open("pyproject.toml", "rb") as f:
                py_data = tomllib.load(f)
                version = py_data.get("project", {}).get("version", "1.0.0")

            plist["CFBundleShortVersionString"] = version
            plist["CFBundleVersion"] = version
            plist["CFBundleName"] = "QR Network Scanner"
            print(f"Setting App Version to: {version}")
        except Exception as e:
            print(f"Warning: Could not set version in Info.plist: {e}")

        with open(plist_path, "wb") as f:
            plistlib.dump(plist, f)
        print("Info.plist updated.")

    # Sign the application with entitlements (Ad-hoc signing)
    app_path = "dist/QRNetworkScanner.app"
    print("Signing application with entitlements...")
    try:
        subprocess.run(
            [
                "codesign",
                "--force",
                "--deep",
                "--sign",
                "-",  # Ad-hoc signing
                "--entitlements",
                "entitlements.plist",
                app_path,
            ],
            check=True,
        )
        print("Application signed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error signing application: {e}")

    # Create DMG
    dmg_path = "dist/QRNetworkScanner.dmg"
    dmg_root = "dist/dmg_root"
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
    if os.path.exists(dmg_root):
        shutil.rmtree(dmg_root)
    os.makedirs(dmg_root)

    print("Preparing DMG content...")
    # Copy app to dmg_root
    shutil.copytree(app_path, os.path.join(dmg_root, "QRNetworkScanner.app"))
    # Create symlink to /Applications
    os.symlink("/Applications", os.path.join(dmg_root, "Applications"))

    # Create a "Quick Install" text file
    with open(os.path.join(dmg_root, "PLEASE_READ_TO_INSTALL.txt"), "w") as f:
        f.write("QR NETWORK SCANNER: QUICK INSTALLATION\n")
        f.write("======================================\n\n")
        f.write(
            "1. DRAG the 'QRNetworkScanner' app icon onto the 'Applications' folder shortcut.\n"
        )
        f.write("2. OPEN your Applications folder and find 'QRNetworkScanner'.\n")
        f.write(
            "3. RIGHT-CLICK the app and select 'Open' to launch it for the first time.\n\n"
        )
        f.write("Thank you for using QR Network Scanner!")

    print("Creating DMG...")
    try:
        subprocess.run(
            [
                "hdiutil",
                "create",
                "-volname",
                "QR Network Scanner",
                "-srcfolder",
                dmg_root,
                "-ov",
                "-format",
                "UDZO",
                dmg_path,
            ],
            check=True,
        )
        print(f"DMG created successfully: {dmg_path}")
        # Clean up dmg_root after success
        shutil.rmtree(dmg_root)
    except subprocess.CalledProcessError as e:
        print(f"Error creating DMG: {e}")

    print(
        "Build complete. Check dist/QRNetworkScanner.app and dist/QRNetworkScanner.dmg"
    )


if __name__ == "__main__":
    build()
