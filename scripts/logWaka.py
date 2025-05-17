def log_time_to_wakatime(stop_event):
    import subprocess
    import time
    import os
    import FreeCAD as App
    import FreeCADGui as Gui
    import threading
    import inspect

    # Version info
    freecad_wakatime_version = "0.5.0"
    freecad_version = ".".join(App.Version()[:3])
    debug = App.ParamGet("User parameter:Plugins/Wakatime").GetBool("debug", False)

    # Timestamps
    last_logged_time = 0
    last_mod_time = 0

    # Determine wakatime-cli path
    wakatime_dir = os.path.join(os.path.expanduser("~"), "wakatime-cli")
    if os.name == 'nt':
        wakatime_cli = os.path.join(wakatime_dir, "wakatime-cli.exe")
    else:
        wakatime_cli = os.path.join(wakatime_dir, "wakatime")

    # Debounced observer
    class DocumentObserver:
        def __init__(self):
            self.last_event = 0

        def slotChangedObject(self, obj, doc):
            now = time.time()
            # ignore events more frequent than 10s
            if now - self.last_event < 10:
                return
            self.last_event = now
            nonlocal last_mod_time
            last_mod_time = now
            if debug:
                App.Console.PrintMessage(f"[WakaTime-Debug] Object changed at {now}\n")

    observer = DocumentObserver()
    App.addDocumentObserver(observer)
    App.Console.PrintMessage("[WakaTime] Observer added\n")

    projectName = None
    while not stop_event.is_set():
        # Ensure document has a valid name
        label = None
        try:
            label = App.ActiveDocument.Label
        except Exception:
            App.Console.PrintError("[WakaTime] No active document, retrying...\n")
            time.sleep(10)
            continue

        if label.startswith("Unnamed"):
            App.Console.PrintMessage("[WakaTime] Please save project to start logging.\n")
            time.sleep(10)
            continue

        if label != projectName:
            projectName = label
            App.Console.PrintMessage(f"[WakaTime] Project: {projectName}\n")

        now = time.time()
        # Log if document was modified in the last 60s and last log older than 60s
        if last_mod_time and now - last_logged_time > 60 and now - last_mod_time < 60:
            App.Console.PrintMessage(f"[WakaTime] Logging time for project '{projectName}'...\n")
            try:
                subprocess.call([
                    wakatime_cli,
                    '--plugin', f"freecad/{freecad_version} freecad-wakatime/{freecad_wakatime_version}",
                    '--entity-type', 'app',
                    '--entity', projectName,
                    '--project', projectName,
                    '--language', 'FreeCAD',
                    '--write'
                ])
                last_logged_time = time.time()
                App.Console.PrintMessage("[WakaTime] Time logged.\n")
            except Exception as e:
                App.Console.PrintError(f"[WakaTime] Error logging time: {e}\n")

        else:
            if debug:
                App.Console.PrintMessage(f"[WakaTime] Next check in 10s.\n")
        time.sleep(10)


def check_wakatime():
    import subprocess
    import os
    import FreeCAD as App

    wakatime_dir = os.path.join(os.path.expanduser("~"), "wakatime-cli")
    # define cli path
    if os.name == 'nt':
        cli = os.path.join(wakatime_dir, "wakatime-cli.exe")
        url = "https://github.com/wakatime/wakatime-cli/releases/latest/download/wakatime-cli-windows-amd64.zip"
    else:
        cli = os.path.join(wakatime_dir, "wakatime")
        url = "https://github.com/wakatime/wakatime-cli/releases/latest/download/wakatime-cli-linux-amd64.zip"

    # install if missing
    if not os.path.exists(cli):
        try:
            import urllib.request, zipfile
            zip_path = os.path.join(os.path.expanduser("~"), "wakatime-cli.zip")
            urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(wakatime_dir)
            # rename and set exec
            for f in os.listdir(wakatime_dir):
                if f.startswith("wakatime-cli"):
                    src = os.path.join(wakatime_dir, f)
                    dst = cli
                    os.rename(src, dst)
                    if os.name != 'nt': os.chmod(dst, 0o755)
                    break
            os.remove(zip_path)
            return True
        except Exception as e:
            App.Console.PrintError(f"[WakaTime] Installation error: {e}\n")
            return False
    # test version
    try:
        subprocess.call([cli, '--version'])
        return True
    except Exception as e:
        App.Console.PrintError(f"[WakaTime] CLI check error: {e}\n")
        return False