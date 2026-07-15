import pygame
import sys
from datetime import datetime

pygame.init()

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LabGuard OS")

font_title = pygame.font.SysFont("Segoe UI", 32, bold=True)
font = pygame.font.SysFont("Segoe UI", 22)
font_small = pygame.font.SysFont("Segoe UI", 18)

WHITE = (255, 255, 255)
BG = (243, 243, 243)
BLUE = (0, 120, 215)
ACCENT = (98, 155, 255)
TEXT = (30, 30, 30)
SUBTEXT = (100, 100, 100)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)

SETUP_NAME = 0
SETUP_DOWNLOAD = 1
SETUP_CONFIG = 2
DESKTOP = 3
LABGUARD = 4

state = SETUP_NAME
name_input = ""
user_name = ""
progress = 0.0
current_view = None
counters = {"saludo": 0, "fecha": 0, "contador": 0}

clock = pygame.time.Clock()

def draw_button(text, x, y, w, h, mouse):
    rect = pygame.Rect(x, y, w, h)
    color = LIGHT_GRAY if rect.collidepoint(mouse) else WHITE
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, GRAY, rect, 1, border_radius=10)
    label = font.render(text, True, TEXT)
    screen.blit(label, (x + w//2 - label.get_width()//2,
                        y + h//2 - label.get_height()//2))
    return rect

def draw_progress(x, y, w, h, p):
    pygame.draw.rect(screen, GRAY, (x, y, w, h), border_radius=10)
    pygame.draw.rect(screen, ACCENT, (x, y, int(w * p), h), border_radius=10)

def draw_icon(text, x, y, mouse):
    rect = pygame.Rect(x, y, 90, 90)
    pygame.draw.rect(screen, WHITE, rect, border_radius=12)
    pygame.draw.rect(screen, GRAY, rect, 1, border_radius=12)
    label = font_small.render(text, True, TEXT)
    screen.blit(label, (x + 45 - label.get_width()//2, y + 100))
    return rect

while True:
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == SETUP_NAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name_input:
                    user_name = name_input
                    state = SETUP_DOWNLOAD
                    progress = 0.0
                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                else:
                    if len(name_input) < 20 and event.unicode.isprintable():
                        name_input += event.unicode

        elif state == DESKTOP:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if lab_icon.collidepoint(mouse):
                    state = LABGUARD
                    current_view = None

        elif state == LABGUARD:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = DESKTOP
                elif event.key == pygame.K_1:
                    counters["saludo"] += 1
                    current_view = "saludo"
                elif event.key == pygame.K_2:
                    counters["fecha"] += 1
                    current_view = "fecha"
                elif event.key == pygame.K_3:
                    counters["contador"] += 1
                    current_view = "contador"

    # DRAW
    if state == SETUP_NAME:
        screen.fill(WHITE)
        t = font_title.render("Configurar LabGuard OS", True, TEXT)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, 120))
        s = font.render("Ingresa tu nombre para continuar", True, SUBTEXT)
        screen.blit(s, (WIDTH//2 - s.get_width()//2, 180))

        box = pygame.Rect(WIDTH//2 - 200, 260, 400, 45)
        pygame.draw.rect(screen, WHITE, box, border_radius=10)
        pygame.draw.rect(screen, GRAY, box, 1, border_radius=10)
        txt = font.render(name_input, True, TEXT)
        screen.blit(txt, (box.x + 10, box.y + 8))

        hint = font_small.render("Presiona Enter para continuar", True, SUBTEXT)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 320))

    elif state == SETUP_DOWNLOAD:
        screen.fill(WHITE)
        t = font_title.render("Descargando archivos…", True, TEXT)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, 150))
        progress += 0.003
        if progress >= 1.0:
            state = SETUP_CONFIG
            progress = 0.0
        draw_progress(200, 300, 600, 30, progress)

    elif state == SETUP_CONFIG:
        screen.fill(WHITE)
        t = font_title.render("Configurando tu dispositivo…", True, TEXT)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, 150))
        progress += 0.002
        if progress >= 1.0:
            state = DESKTOP
        draw_progress(200, 300, 600, 30, progress)

    elif state == DESKTOP:
        screen.fill(ACCENT)
        lab_icon = draw_icon("LabGuard", 80, 120, mouse)
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - 50, WIDTH, 50))
        bar = font_small.render(f"Escritorio de {user_name}", True, TEXT)
        screen.blit(bar, (20, HEIGHT - 35))

    elif state == LABGUARD:
        screen.fill(BG)
        win_x, win_y, win_w, win_h = 150, 60, 700, 520
        pygame.draw.rect(screen, WHITE, (win_x, win_y, win_w, win_h), border_radius=12)
        pygame.draw.rect(screen, GRAY, (win_x, win_y, win_w, win_h), 1, border_radius=12)
        pygame.draw.rect(screen, BLUE, (win_x, win_y, win_w, 45), border_radius=12)
        title = font_title.render("LabGuard", True, WHITE)
        screen.blit(title, (win_x + 20, win_y + 5))

        draw_button("1. Saludo personalizado", win_x + 150, win_y + 100, 400, 50, mouse)
        draw_button("2. Fecha y hora actual", win_x + 150, win_y + 170, 400, 50, mouse)
        draw_button("3. Contadores de uso", win_x + 150, win_y + 240, 400, 50, mouse)
        draw_button("ESC. Volver al escritorio", win_x + 150, win_y + 310, 400, 50, mouse)

        if current_view == "saludo":
            msg = font.render(f"Hola, {user_name}!", True, TEXT)
            screen.blit(msg, (win_x + 250, win_y + 400))
        elif current_view == "fecha":
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            msg = font.render(now, True, TEXT)
            screen.blit(msg, (win_x + 230, win_y + 400))
        elif current_view == "contador":
            m1 = font_small.render(f"Saludo: {counters['saludo']}", True, TEXT)
            m2 = font_small.render(f"Fecha: {counters['fecha']}", True, TEXT)
            m3 = font_small.render(f"Contador: {counters['contador']}", True, TEXT)
            screen.blit(m1, (win_x + 250, win_y + 380))
            screen.blit(m2, (win_x + 250, win_y + 410))
            screen.blit(m3, (win_x + 250, win_y + 440))

    pygame.display.update()
    clock.tick(60)
