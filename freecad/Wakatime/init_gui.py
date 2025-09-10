
import FreeCADGui as Gui
import FreeCAD as App

from .Resources import logo


class WakatimeWorkbench(Gui.Workbench):
    MenuText = "WakaTime"
    ToolTip = "Configuration of FreeCAD WakaTime"
    Icon = logo

    def Initialize(self):
        self.appendToolbar("Wakatime", ["ActivateWakatime"])

    def GetClassName(self):
        return "Gui::PythonWorkbench"

class ActivateWakatime:
    def __init__(self):
        """Initialize command and resume logging if already active."""
        import threading
        self.stop_event = threading.Event()
        self.is_active = App.ParamGet("User parameter:Plugins/Wakatime").GetBool("is_active", False)
        self.thread = None
        if self.is_active:
            self._start_thread()
            App.Console.PrintMessage("[WakaTime] Activated on startup.\n")

    def GetResources(self):
        return {
            'Pixmap': logo ,
            'MenuText': 'Toggle WakaTime',
            'ToolTip': 'Enable or disable WakaTime logging',
        }

    def Activated(self):
        from .scripts.logWaka import check_wakatime
        if not check_wakatime():
            App.Console.PrintError("[WakaTime] CLI not available. Installation failed.\n")
            return

        if self.is_active:
            App.Console.PrintNotification("[WakaTime] Deactivating...\n")
            if self.thread and self.thread.is_alive():
                self.stop_event.set()
                self.thread.join(timeout=1)
            self.is_active = False
            App.ParamGet("User parameter:Plugins/Wakatime").SetBool("is_active", False)
            App.Console.PrintMessage("[WakaTime] Deactivated.\n")
        else:
            App.Console.PrintMessage("[WakaTime] Activating...\n")
            self._start_thread()
            self.is_active = True
            App.ParamGet("User parameter:Plugins/Wakatime").SetBool("is_active", True)
            App.Console.PrintMessage("[WakaTime] Activated.\n")

    def _start_thread(self):
        """Start or restart the WakaTime logging thread."""
        from .scripts.logWaka import log_time_to_wakatime
        import threading
        self.stop_event.clear()
        self.thread = threading.Thread(
            target=log_time_to_wakatime,
            args=(self.stop_event,),
            daemon=True
        )
        self.thread.start()

    def GetCheck(self):
        """Return toggle-button state: checked if logging is active."""
        return 1 if self.is_active else 0

Gui.addWorkbench(WakatimeWorkbench())
Gui.addCommand('ActivateWakatime', ActivateWakatime())