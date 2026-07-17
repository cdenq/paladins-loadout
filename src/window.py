"""Find and focus the Paladins game window before running any script phase.

Windows restricts SetForegroundWindow to prevent background apps from
stealing focus (see https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-setforegroundwindow) --
calling it directly on a background window is usually a silent no-op (the
taskbar icon just flashes). We work around this with the same combination
pywinauto and others use: attach our input thread to the current foreground
thread, and send a synthetic ALT keypress immediately before the call (this
satisfies Windows' "received the last input event" exemption).

If Paladins is running elevated (common for anti-cheat), a non-elevated
script cannot focus or send input to it at all (User Interface Privilege
Isolation) -- run this script elevated too in that case.
"""

from __future__ import annotations

import time

import psutil
import win32api
import win32con
import win32gui
import win32process

WINDOW_TITLE = "Paladins"
PROCESS_EXE = "paladins.exe"


class WindowNotFoundError(RuntimeError):
    pass


class WindowFocusError(RuntimeError):
    pass


def find_window(title_substr: str = WINDOW_TITLE, exe_name: str = PROCESS_EXE) -> int:
    """Find a visible top-level window whose owning process is exe_name
    (and, as a secondary check, whose title contains title_substr).

    Matching by process is required, not just an extra safety check: a
    plain title substring match on "Paladins" also matches unrelated
    windows like a VS Code/Explorer/browser window with "paladins-loadout"
    in its title (e.g. this very project folder) -- exe_name rules those
    out entirely.
    """
    matches = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if title_substr.lower() not in title.lower():
            return True
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc_name = psutil.Process(pid).name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return True
        if proc_name.lower() != exe_name.lower():
            return True
        matches.append(hwnd)
        return True

    win32gui.EnumWindows(callback, None)
    if not matches:
        raise WindowNotFoundError(
            f"No visible window found for process '{exe_name}' with title containing '{title_substr}'. "
            "Is Paladins running?"
        )
    return matches[0]


def _try_attach(target_thread: int, fg_thread: int) -> bool:
    """AttachThreadInput errors (e.g. ERROR_INVALID_PARAMETER) if the two
    threads already match -- which can happen if ShowWindow(SW_RESTORE)
    already gave hwnd the foreground on its own. Treat that as "no
    attach needed" rather than letting it crash the whole call."""
    if target_thread == fg_thread:
        return False
    try:
        return bool(win32process.AttachThreadInput(target_thread, fg_thread, True))
    except win32api.error:
        return False


def focus_window(hwnd: int, tries: int = 10, delay: float = 0.1) -> None:
    """Restore (if minimized) and bring hwnd to the foreground, verifying success."""
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(delay)

    if win32gui.GetForegroundWindow() == hwnd:
        return

    fg_hwnd = win32gui.GetForegroundWindow()
    fg_thread, _ = win32process.GetWindowThreadProcessId(fg_hwnd)
    target_thread, _ = win32process.GetWindowThreadProcessId(hwnd)

    attached = _try_attach(target_thread, fg_thread)

    try:
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
        try:
            win32gui.SetForegroundWindow(hwnd)
        except win32gui.error:
            pass
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    finally:
        if attached:
            try:
                win32process.AttachThreadInput(target_thread, fg_thread, False)
            except win32api.error:
                pass

    for _ in range(tries):
        if win32gui.GetForegroundWindow() == hwnd:
            return
        win32gui.BringWindowToTop(hwnd)
        try:
            win32gui.SetForegroundWindow(hwnd)
        except win32gui.error:
            pass
        time.sleep(delay)

    if win32gui.GetForegroundWindow() != hwnd:
        raise WindowFocusError(
            "Could not bring the Paladins window to the foreground. "
            "If Paladins is running as Administrator, run this script as "
            "Administrator too -- Windows blocks a non-elevated process "
            "from focusing an elevated one."
        )


def focus_paladins(title_substr: str = WINDOW_TITLE, exe_name: str = PROCESS_EXE) -> None:
    """Find the Paladins window and bring it to the foreground. Raises
    WindowNotFoundError / WindowFocusError on failure."""
    hwnd = find_window(title_substr, exe_name)
    focus_window(hwnd)
