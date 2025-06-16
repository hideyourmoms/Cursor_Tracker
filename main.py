import pygame
import threading
from pynput.mouse import Listener
import win32gui
import win32con
import win32api
import time
from collections import deque


MAX_AGE = 1.0
MAX_TRAIL_POINTS = 200
trail = deque(maxlen=MAX_TRAIL_POINTS)

def mouse_tracker():
    def on_move(x, y):
        trail.append(((x, y), time.time()))
    with Listener(on_move=on_move) as listener:
        listener.join()

threading.Thread(target=mouse_tracker, daemon=True).start()

pygame.init()

MINI_WIDTH, MINI_HEIGHT = 400, 300
screen = pygame.display.set_mode((MINI_WIDTH, MINI_HEIGHT), pygame.NOFRAME | pygame.SRCALPHA)
pygame.display.set_caption("Overlay")

hwnd = pygame.display.get_wm_info()["window"]

extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
    extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST)
win32gui.SetLayeredWindowAttributes(hwnd, 0x000000, 255, win32con.LWA_COLORKEY)

screen_w = win32api.GetSystemMetrics(0)
screen_h = win32api.GetSystemMetrics(1)
x = screen_w - MINI_WIDTH - 20
y = screen_h - MINI_HEIGHT - 40

win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,
                      x, y, MINI_WIDTH, MINI_HEIGHT,
                      win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW)

def enforce_topmost():
    while True:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,
                              x, y, MINI_WIDTH, MINI_HEIGHT,
                              win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW)
        time.sleep(5)

threading.Thread(target=enforce_topmost, daemon=True).start()

clock = pygame.time.Clock()
running = True

while running:
    now = time.time()
    screen.fill((0, 0, 0, 0))

    valid_trail = [(pos, t) for (pos, t) in trail if now - t < MAX_AGE]

    for i in range(1, len(valid_trail), 1):
        (x1, y1), t1 = valid_trail[i - 1]
        (x2, y2), t2 = valid_trail[i]


        x1 = x1 * MINI_WIDTH / screen_w
        y1 = y1 * MINI_HEIGHT / screen_h
        x2 = x2 * MINI_WIDTH / screen_w
        y2 = y2 * MINI_HEIGHT / screen_h

        age = now - t1
        fade_factor = max(0, 1 - age / MAX_AGE)
        brightness = int(255 * fade_factor)
        color = (0, brightness, 0)

        pygame.draw.line(screen, color, (x1, y1), (x2, y2), 2)

    border_color = (200, 200, 200)
    pygame.draw.rect(screen, border_color, (0, 0, MINI_WIDTH, MINI_HEIGHT), 2)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(60)

pygame.quit()
