
import pygame
import random
import json
import os
import math
import wave
import struct
from datetime import datetime

# ============================================================
# TIC TAC TOE - MOBILE STYLE GUI GAME
# Python + Pygame
# ============================================================

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WIDTH, HEIGHT = 540, 900
FPS = 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")
CLOCK = pygame.time.Clock()

# -------------------- THEMES --------------------
DARK_THEME = {
    "BG": (14, 17, 27),
    "CARD": (25, 29, 43),
    "CARD2": (32, 37, 54),
    "WHITE": (245, 247, 250),
    "TEXT2": (170, 178, 195),
    "BLUE": (75, 135, 255),
    "BLUE2": (54, 105, 220),
    "GREEN": (67, 205, 133),
    "RED": (245, 86, 100),
    "YELLOW": (245, 194, 73),
    "PURPLE": (148, 105, 255),
    "GRID": (72, 79, 101),
    "BLACK": (8, 10, 16),
}

LIGHT_THEME = {
    "BG": (239, 242, 248),
    "CARD": (255, 255, 255),
    "CARD2": (228, 233, 243),
    "WHITE": (28, 32, 42),
    "TEXT2": (91, 99, 116),
    "BLUE": (54, 111, 235),
    "BLUE2": (43, 91, 200),
    "GREEN": (43, 180, 111),
    "RED": (220, 67, 83),
    "YELLOW": (218, 158, 35),
    "PURPLE": (119, 82, 215),
    "GRID": (153, 161, 178),
    "BLACK": (245, 247, 250),
}

IS_DARK = True

def apply_theme():
    palette = DARK_THEME if IS_DARK else LIGHT_THEME
    globals().update(palette)

apply_theme()

FONT_BIG = pygame.font.SysFont("arial", 48, bold=True)
FONT_TITLE = pygame.font.SysFont("arial", 36, bold=True)
FONT_H1 = pygame.font.SysFont("arial", 27, bold=True)
FONT_H2 = pygame.font.SysFont("arial", 22, bold=True)
FONT = pygame.font.SysFont("arial", 19)
FONT_SMALL = pygame.font.SysFont("arial", 15)
FONT_TINY = pygame.font.SysFont("arial", 13)

HISTORY_FILE = "tic_tac_toe_history.json"

# ============================================================
# EDIT THESE VALUES FOR YOUR GAME INFO
# ============================================================

GAME_CREATOR = "ABHISHEK RAJPOOT"
GAME_YEAR = "2026"
GAME_VERSION = "1.0.1"

# ============================================================
# HELPERS
# ============================================================

def clamp(v, a, b):
    return max(a, min(b, v))

def text(surface, value, font, color, center):
    img = font.render(str(value), True, color)
    surface.blit(img, img.get_rect(center=center))

def rounded_rect(surface, color, rect, radius=18, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)

def draw_gradient_background(surface):
    base = pygame.Color(*BG)
    end = pygame.Color(
        max(0, BG[0] - 8 if IS_DARK else BG[0] - 7),
        max(0, BG[1] - 8 if IS_DARK else BG[1] - 7),
        max(0, BG[2] - 3 if IS_DARK else BG[2] - 4),
    )
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        c = base.lerp(end, t)
        pygame.draw.line(surface, c, (0, y), (WIDTH, y))

def play_sound(sound):
    if sound_on and sound is not None:
        try:
            sound.play()
        except pygame.error:
            pass

def make_tone(path, frequency=440, duration=0.08, volume=0.28):
    if os.path.exists(path):
        return
    try:
        sample_rate = 44100
        frames = int(sample_rate * duration)
        with wave.open(path, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for i in range(frames):
                fade = min(1.0, i / 500, (frames - i) / 900)
                value = int(
                    32767 * volume * fade *
                    math.sin(2 * math.pi * frequency * i / sample_rate)
                )
                wav.writeframes(struct.pack("<h", value))
    except Exception:
        pass

def setup_audio():
    global click_sound, move_sound, win_sound, draw_sound

    click_sound = move_sound = win_sound = draw_sound = None

    try:
        os.makedirs("assets", exist_ok=True)

        make_tone("assets/click.wav", 520, 0.055, 0.20)
        make_tone("assets/move.wav", 390, 0.075, 0.24)
        make_tone("assets/win.wav", 720, 0.32, 0.24)
        make_tone("assets/draw.wav", 280, 0.24, 0.20)

        click_sound = pygame.mixer.Sound("assets/click.wav")
        move_sound = pygame.mixer.Sound("assets/move.wav")
        win_sound = pygame.mixer.Sound("assets/win.wav")
        draw_sound = pygame.mixer.Sound("assets/draw.wav")

        click_sound.set_volume(0.55)
        move_sound.set_volume(0.55)
        win_sound.set_volume(0.70)
        draw_sound.set_volume(0.60)
    except Exception:
        pass

def start_background_music():
    if not music_on:
        return
    music_path = os.path.join("assets", "background_music.mp3")
    if not os.path.exists(music_path):
        return
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.22)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

def stop_background_music():
    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass

def back_button(surface):
    rect = pygame.Rect(18, 18, 108, 46)
    rounded_rect(surface, CARD2, rect, 14)
    text(surface, "←  BACK", FONT_SMALL, WHITE, rect.center)
    return rect

def button(surface, rect, label, active=True, color=BLUE, font=FONT_H2):
    if active:
        rounded_rect(surface, color, rect, 15)
    else:
        rounded_rect(surface, (45, 49, 63), rect, 15)

    text_color = WHITE if active else (125, 130, 143)
    text(surface, label, font, text_color, rect.center)

def back_button(surface):
    rect = pygame.Rect(20, 20, 50, 45)
    rounded_rect(surface, CARD2, rect, 13)
    text(surface, "‹", FONT_TITLE, WHITE, rect.center)
    return rect

def input_box(surface, rect, value, active, placeholder):
    color = BLUE if active else GRID
    rounded_rect(surface, CARD, rect, 14, 2, color)

    shown = value if value else placeholder
    col = WHITE if value else TEXT2
    text(surface, shown, FONT, col, rect.center)

def get_mouse():
    return pygame.mouse.get_pos()

# ============================================================
# HISTORY
# ============================================================

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

def save_history(data):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data[-200:], f, indent=2, ensure_ascii=False)
    except Exception:
        pass

history = load_history()

def add_history(p1, p2, winner, mode, difficulty):
    record = {
        "date": datetime.now().strftime("%d-%m-%Y"),
        "time": datetime.now().strftime("%I:%M %p"),
        "player1": p1,
        "player2": p2,
        "result": winner,
        "mode": mode,
        "difficulty": difficulty if mode == "Computer" else "-"
    }
    history.append(record)
    save_history(history)

# ============================================================
# GAME DATA
# ============================================================

game_mode = "Computer"
difficulty = "Moderate"

player1_name = "Player 1"
player2_name = "Computer"

scores = {
    "Player 1": 0,
    "Player 2": 0,
    "Draw": 0
}

board = [""] * 9
current_player = "X"
game_over = False
winner = None
winning_line = None

screen_name = "home"

name_input = ""
name_input_2 = ""
active_input = 1

popup_timer = 0
popup_kind = ""
line_progress = 0

sound_on = True
music_on = True
click_sound = None
move_sound = None
win_sound = None
draw_sound = None

# ============================================================
# BUTTON RECTANGLES
# ============================================================

HOME_PLAY = pygame.Rect(70, 520, 400, 62)
HOME_HISTORY = pygame.Rect(70, 595, 190, 58)
HOME_SETTINGS = pygame.Rect(280, 595, 190, 58)
HOME_ABOUT = pygame.Rect(70, 665, 190, 58)
HOME_QUIT = pygame.Rect(280, 665, 190, 58)

MODE_COMPUTER = pygame.Rect(55, 205, 205, 72)
MODE_MULTI = pygame.Rect(280, 205, 205, 72)

DIFF_EASY = pygame.Rect(35, 335, 110, 58)
DIFF_MOD = pygame.Rect(155, 335, 110, 58)
DIFF_HARD = pygame.Rect(275, 335, 110, 58)
DIFF_EXTREME = pygame.Rect(395, 335, 110, 58)

START_GAME = pygame.Rect(70, 710, 400, 62)

RESET_GAME = pygame.Rect(295, 790, 175, 52)
RESTART_GAME = pygame.Rect(70, 790, 175, 52)

# ============================================================
# COMPUTER AI
# ============================================================

def available_moves(state):
    return [i for i, v in enumerate(state) if v == ""]

def check_winner(state):
    lines = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6)
    ]

    for a, b, c in lines:
        if state[a] and state[a] == state[b] == state[c]:
            return state[a], (a, b, c)

    if "" not in state:
        return "Draw", None

    return None, None

def minimax(state, maximizing):
    result, _ = check_winner(state)

    if result == "O":
        return 1
    if result == "X":
        return -1
    if result == "Draw":
        return 0

    if maximizing:
        best = -999
        for i in available_moves(state):
            state[i] = "O"
            best = max(best, minimax(state, False))
            state[i] = ""
        return best
    else:
        best = 999
        for i in available_moves(state):
            state[i] = "X"
            best = min(best, minimax(state, True))
            state[i] = ""
        return best

def find_best_move(state):
    moves = available_moves(state)

    if not moves:
        return None

    best_score = -999
    best_move = random.choice(moves)

    for move in moves:
        state[move] = "O"
        score = minimax(state, False)
        state[move] = ""

        if score > best_score:
            best_score = score
            best_move = move

    return best_move

def medium_move():
    """Moderate = noticeably easier than the old version."""
    moves = available_moves(board)

    if not moves:
        return None

    # Only use tactical play about 60% of the time.
    # The other 40% is intentionally random.
    if random.random() < 0.60:
        # Try to win.
        for move in moves:
            board[move] = "O"
            result, _ = check_winner(board)
            board[move] = ""
            if result == "O":
                return move

        # Sometimes block, but not every time.
        if random.random() < 0.75:
            for move in moves:
                board[move] = "X"
                result, _ = check_winner(board)
                board[move] = ""
                if result == "X":
                    return move

        # Prefer center only sometimes.
        if board[4] == "" and random.random() < 0.55:
            return 4

    return random.choice(moves)

def easy_move():
    moves = available_moves(board)
    return random.choice(moves) if moves else None

def hard_move():
    return find_best_move(board)

def computer_move():
    if difficulty == "Easy":
        return easy_move()
    elif difficulty == "Moderate":
        return medium_move()
    elif difficulty == "Hard":
        # Mostly perfect, tiny chance of a random move
        if random.random() < 0.15:
            return easy_move()
        return find_best_move(board)
    else:
        return find_best_move(board)

# ============================================================
# GAME LOGIC
# ============================================================

def reset_board():
    global board, current_player, game_over, winner
    global winning_line, popup_timer, popup_kind, line_progress

    board = [""] * 9
    current_player = "X"
    game_over = False
    winner = None
    winning_line = None
    popup_timer = 0
    popup_kind = ""
    line_progress = 0

def start_new_game():
    global player1_name, player2_name

    reset_board()

    if not player1_name.strip():
        player1_name = "Player 1"

    if game_mode == "Computer":
        player2_name = "Computer"
    elif not player2_name.strip():
        player2_name = "Player 2"

def finish_game(result, line):
    global game_over, winner, winning_line, popup_timer, popup_kind
    global line_progress

    game_over = True
    winner = result
    winning_line = line
    line_progress = 0

    if result == "Draw":
        popup_kind = "draw"
        scores["Draw"] += 1
        play_sound(draw_sound)
        add_history(player1_name, player2_name, "Draw", game_mode, difficulty)
    elif result == "X":
        popup_kind = "p1"
        scores["Player 1"] += 1
        play_sound(win_sound)
        add_history(player1_name, player2_name, player1_name, game_mode, difficulty)
    else:
        popup_kind = "p2"
        scores["Player 2"] += 1
        play_sound(win_sound)
        add_history(player1_name, player2_name, player2_name, game_mode, difficulty)

    popup_timer = pygame.time.get_ticks()

def make_move(index):
    global current_player

    if board[index] != "" or game_over:
        return

    # In computer mode, player can only move as X.
    if game_mode == "Computer" and current_player != "X":
        return

    board[index] = current_player
    play_sound(move_sound)

    result, line = check_winner(board)

    if result:
        finish_game(result, line)
        return

    current_player = "O" if current_player == "X" else "X"

def computer_turn():
    if game_mode != "Computer":
        return

    if game_over or current_player != "O":
        return

    move = computer_move()
    if move is not None:
        board[move] = "O"
        play_sound(move_sound)

        result, line = check_winner(board)
        if result:
            finish_game(result, line)
        else:
            globals()["current_player"] = "X"

# ============================================================
# DRAW HOME
# ============================================================

def draw_home():
    draw_gradient_background(SCREEN)

    # Decorative circles
    pygame.draw.circle(SCREEN, (27, 35, 58), (50, 105), 80)
    pygame.draw.circle(SCREEN, (30, 28, 55), (500, 150), 105)

    text(SCREEN, "TIC TAC TOE", FONT_BIG, WHITE, (WIDTH // 2, 115))
    text(SCREEN, "Classic game • Modern experience", FONT, TEXT2, (WIDTH // 2, 155))

    # Small X / O decoration
    text(SCREEN, "X", FONT_TITLE, BLUE, (120, 245))
    text(SCREEN, "O", FONT_TITLE, GREEN, (420, 245))

    rounded_rect(SCREEN, CARD, (55, 285, 430, 180), 24)

    text(SCREEN, "Current Score", FONT_H2, WHITE, (WIDTH // 2, 320))

    rounded_rect(SCREEN, CARD2, (80, 350, 115, 80), 18)
    rounded_rect(SCREEN, CARD2, (212, 350, 115, 80), 18)
    rounded_rect(SCREEN, CARD2, (345, 350, 115, 80), 18)

    text(SCREEN, "P1", FONT_SMALL, TEXT2, (137, 372))
    text(SCREEN, str(scores["Player 1"]), FONT_H1, BLUE, (137, 405))

    text(SCREEN, "P2", FONT_SMALL, TEXT2, (269, 372))
    text(SCREEN, str(scores["Player 2"]), FONT_H1, GREEN, (269, 405))

    text(SCREEN, "DRAW", FONT_SMALL, TEXT2, (402, 372))
    text(SCREEN, str(scores["Draw"]), FONT_H1, YELLOW, (402, 405))

    button(SCREEN, HOME_PLAY, "PLAY GAME", True, BLUE, FONT_H1)
    button(SCREEN, HOME_HISTORY, "HISTORY", True, CARD2, FONT)
    button(SCREEN, HOME_SETTINGS, "SETTINGS", True, CARD2, FONT)
    button(SCREEN, HOME_ABOUT, "ABOUT", True, CARD2, FONT)
    button(SCREEN, HOME_QUIT, "EXIT", True, (75, 48, 60), FONT)

    text(SCREEN, f"v{GAME_VERSION}", FONT_TINY, TEXT2, (WIDTH // 2, 850))

# ============================================================
# DRAW SETUP
# ============================================================

def draw_setup():
    draw_gradient_background(SCREEN)
    back = back_button(SCREEN)

    text(SCREEN, "Game Setup", FONT_TITLE, WHITE, (WIDTH // 2 + 45, 42))

    text(SCREEN, "Choose Game Mode", FONT_H2, WHITE, (WIDTH // 2, 150))

    button(SCREEN, MODE_COMPUTER, "VS COMPUTER",
           game_mode == "Computer",
           BLUE if game_mode == "Computer" else CARD2, FONT)

    button(SCREEN, MODE_MULTI, "MULTIPLAYER",
           game_mode == "Multiplayer",
           GREEN if game_mode == "Multiplayer" else CARD2, FONT)

    text(SCREEN, "Difficulty", FONT_H2, WHITE, (WIDTH // 2, 305))

    button(SCREEN, DIFF_EASY, "EASY",
           difficulty == "Easy",
           GREEN if difficulty == "Easy" else CARD2, FONT_SMALL)

    button(SCREEN, DIFF_MOD, "MODERATE",
           difficulty == "Moderate",
           BLUE if difficulty == "Moderate" else CARD2, FONT_SMALL)

    button(SCREEN, DIFF_HARD, "HARD",
           difficulty == "Hard",
           PURPLE if difficulty == "Hard" else CARD2, FONT_SMALL)

    button(SCREEN, DIFF_EXTREME, "EXTREME",
           difficulty == "Extreme",
           RED if difficulty == "Extreme" else CARD2, FONT_SMALL)

    # Names
    text(SCREEN, "Player Names", FONT_H2, WHITE, (WIDTH // 2, 430))

    input_box(
        SCREEN,
        pygame.Rect(70, 470, 400, 55),
        name_input,
        active_input == 1,
        "Player 1 name"
    )

    if game_mode == "Multiplayer":
        input_box(
            SCREEN,
            pygame.Rect(70, 540, 400, 55),
            name_input_2,
            active_input == 2,
            "Player 2 name"
        )
    else:
        rounded_rect(SCREEN, CARD2, (70, 540, 400, 55), 14)
        text(SCREEN, "Player 2 = Computer", FONT, TEXT2, (WIDTH // 2, 567))

    button(SCREEN, START_GAME, "START MATCH", True, BLUE, FONT_H1)

    text(SCREEN, "X always starts the match", FONT_SMALL, TEXT2, (WIDTH // 2, 785))

    return back

# ============================================================
# DRAW GAME
# ============================================================

def draw_game():
    draw_gradient_background(SCREEN)

    back = back_button(SCREEN)

    text(SCREEN, player1_name, FONT_H2, BLUE, (165, 48))
    text(SCREEN, "VS", FONT_SMALL, TEXT2, (300, 48))
    text(SCREEN, player2_name, FONT_H2, GREEN, (435, 48))

    # Score bar
    rounded_rect(SCREEN, CARD, (55, 82, 430, 72), 18)

    text(SCREEN, f"{scores['Player 1']}", FONT_H1, BLUE, (155, 118))
    text(SCREEN, "SCORE", FONT_SMALL, TEXT2, (270, 118))
    text(SCREEN, f"{scores['Player 2']}", FONT_H1, GREEN, (385, 118))

    # Turn indicator
    turn_name = player1_name if current_player == "X" else player2_name
    turn_color = BLUE if current_player == "X" else GREEN

    rounded_rect(SCREEN, CARD2, (90, 175, 360, 48), 18)
    text(SCREEN, f"{turn_name}'s turn ({current_player})", FONT, turn_color,
         (WIDTH // 2, 199))

    # Board
    board_size = 420
    board_x = 60
    board_y = 250
    cell = board_size // 3

    rounded_rect(SCREEN, CARD, (board_x, board_y, board_size, board_size), 25)

    # Grid
    for i in range(1, 3):
        x = board_x + i * cell
        pygame.draw.line(SCREEN, GRID, (x, board_y + 28),
                         (x, board_y + board_size - 28), 4)

        y = board_y + i * cell
        pygame.draw.line(SCREEN, GRID, (board_x + 28, y),
                         (board_x + board_size - 28, y), 4)

    # Symbols
    for i, value in enumerate(board):
        row = i // 3
        col = i % 3

        cx = board_x + col * cell + cell // 2
        cy = board_y + row * cell + cell // 2

        if value == "X":
            # Smooth X
            pygame.draw.line(
                SCREEN, BLUE,
                (cx - 35, cy - 35),
                (cx + 35, cy + 35), 9
            )
            pygame.draw.line(
                SCREEN, BLUE,
                (cx + 35, cy - 35),
                (cx - 35, cy + 35), 9
            )
        elif value == "O":
            pygame.draw.circle(SCREEN, GREEN, (cx, cy), 38, 9)

    # Winning line
    if winning_line:
        a, b, c = winning_line

        def center_of(idx):
            row = idx // 3
            col = idx % 3
            return (
                board_x + col * cell + cell // 2,
                board_y + row * cell + cell // 2
            )

        start = center_of(a)
        end = center_of(c)

        # Animated progress
        p = clamp(line_progress / 18.0, 0, 1)
        current_end = (
            int(start[0] + (end[0] - start[0]) * p),
            int(start[1] + (end[1] - start[1]) * p)
        )

        line_color = BLUE if winner == "X" else GREEN
        pygame.draw.line(SCREEN, WHITE, start, current_end, 16)
        pygame.draw.line(SCREEN, line_color, start, current_end, 9)

    # Bottom controls
    button(SCREEN, RESTART_GAME, "RESTART", True, BLUE, FONT)
    button(SCREEN, RESET_GAME, "RESET SCORE", True, CARD2, FONT)

    text(SCREEN, "Restart = new round  •  Reset = score to zero",
         FONT_TINY, TEXT2, (WIDTH // 2, 870))

    return back

# ============================================================
# POPUP
# ============================================================

def draw_result_popup():
    if not game_over:
        return

    # Dim layer
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    SCREEN.blit(overlay, (0, 0))

    box = pygame.Rect(45, 290, 450, 320)
    rounded_rect(SCREEN, CARD, box, 28)

    if popup_kind == "draw":
        title = "MATCH DRAW"
        sub = "Nobody wins this round."
        color = YELLOW
    elif popup_kind == "p1":
        title = f"{player1_name} WINS!"
        sub = "Player 1 takes the round."
        color = BLUE
    else:
        title = f"{player2_name} WINS!"
        sub = "Player 2 takes the round."
        color = GREEN

    text(SCREEN, title, FONT_TITLE, color, (WIDTH // 2, 355))
    text(SCREEN, sub, FONT, TEXT2, (WIDTH // 2, 400))

    if popup_kind != "draw":
        text(SCREEN, "★  ROUND COMPLETE  ★", FONT_H2, WHITE,
             (WIDTH // 2, 450))
    else:
        text(SCREEN, "★  WELL PLAYED  ★", FONT_H2, WHITE,
             (WIDTH // 2, 450))

    again = pygame.Rect(80, 505, 175, 55)
    menu = pygame.Rect(285, 505, 175, 55)

    button(SCREEN, again, "PLAY AGAIN", True, BLUE, FONT)
    button(SCREEN, menu, "MAIN MENU", True, CARD2, FONT)

    return again, menu

# ============================================================
# HISTORY SCREEN
# ============================================================

def draw_history():
    draw_gradient_background(SCREEN)
    back = back_button(SCREEN)

    text(SCREEN, "Game History", FONT_TITLE, WHITE, (WIDTH // 2 + 45, 42))

    if not history:
        rounded_rect(SCREEN, CARD, (45, 190, 450, 190), 25)
        text(SCREEN, "No matches played yet.", FONT_H2, TEXT2,
             (WIDTH // 2, 270))
        text(SCREEN, "Your completed games will appear here.",
             FONT, TEXT2, (WIDTH // 2, 315))
        return back

    # Recent first
    visible = history[-8:][::-1]

    y = 95
    for record in visible:
        card = pygame.Rect(35, y, 470, 88)
        rounded_rect(SCREEN, CARD, card, 17)

        result = record.get("result", "Unknown")

        if result == "Draw":
            result_color = YELLOW
            result_text = "DRAW"
        elif result == record.get("player1"):
            result_color = BLUE
            result_text = "P1 WIN"
        else:
            result_color = GREEN
            result_text = "P2 WIN"

        text(SCREEN, result_text, FONT_H2, result_color, (88, y + 28))

        p1 = record.get("player1", "Player 1")
        p2 = record.get("player2", "Player 2")
        date = record.get("date", "")
        tm = record.get("time", "")
        mode = record.get("mode", "")

        text(SCREEN, f"{p1}  vs  {p2}", FONT, WHITE, (290, y + 24))
        text(SCREEN, f"{date}  •  {tm}  •  {mode}",
             FONT_TINY, TEXT2, (290, y + 52))

        y += 98

    clear_rect = pygame.Rect(150, 825, 240, 48)
    button(SCREEN, clear_rect, "CLEAR HISTORY", True, (80, 50, 62), FONT_SMALL)

    return back, clear_rect

# ============================================================
# SETTINGS
# ============================================================

def draw_settings():
    draw_gradient_background(SCREEN)
    back = back_button(SCREEN)

    text(SCREEN, "Settings", FONT_TITLE, WHITE, (WIDTH // 2 + 45, 42))

    rounded_rect(SCREEN, CARD, (45, 110, 450, 385), 25)

    text(SCREEN, "Sound Effects", FONT_H2, WHITE, (155, 170))
    sound_rect = pygame.Rect(350, 145, 90, 42)
    button(SCREEN, sound_rect, "ON" if sound_on else "OFF",
           True, GREEN if sound_on else CARD2, FONT_SMALL)

    text(SCREEN, "Background Music", FONT_H2, WHITE, (155, 245))
    music_rect = pygame.Rect(350, 220, 90, 42)
    button(SCREEN, music_rect, "ON" if music_on else "OFF",
           True, GREEN if music_on else CARD2, FONT_SMALL)

    text(SCREEN, "Theme", FONT_H2, WHITE, (155, 320))
    theme_rect = pygame.Rect(350, 295, 90, 42)
    button(SCREEN, theme_rect, "DARK" if IS_DARK else "LIGHT",
           True, BLUE, FONT_SMALL)

    text(SCREEN, "Version", FONT_H2, WHITE, (155, 395))
    text(SCREEN, GAME_VERSION, FONT, TEXT2, (395, 395))

    rounded_rect(SCREEN, CARD2, (45, 525, 450, 145), 22)
    text(SCREEN, "CREATED BY", FONT_H2, YELLOW, (WIDTH // 2, 560))
    text(SCREEN, GAME_CREATOR, FONT_H1, WHITE, (WIDTH // 2, 600))
    text(SCREEN, f"© {GAME_YEAR}  •  Tic Tac Toe", FONT_SMALL, TEXT2,
         (WIDTH // 2, 635))

    text(SCREEN, "Put your music file at: assets/background_music.mp3",
         FONT_TINY, TEXT2, (WIDTH // 2, 710))

    return back, sound_rect, music_rect, theme_rect

# ============================================================
# ABOUT
# ============================================================

def draw_about():
    draw_gradient_background(SCREEN)
    back = back_button(SCREEN)

    text(SCREEN, "About", FONT_TITLE, WHITE, (WIDTH // 2 + 45, 42))

    rounded_rect(SCREEN, CARD, (45, 125, 450, 440), 28)

    text(SCREEN, "TIC TAC TOE", FONT_BIG, BLUE, (WIDTH // 2, 205))
    text(SCREEN, "Mobile-style GUI Edition", FONT_H2, WHITE,
         (WIDTH // 2, 250))

    text(SCREEN, "Created by", FONT_SMALL, TEXT2, (WIDTH // 2, 315))
    text(SCREEN, GAME_CREATOR, FONT_H1, GREEN, (WIDTH // 2, 350))

    text(SCREEN, "Year", FONT_SMALL, TEXT2, (WIDTH // 2, 405))
    text(SCREEN, GAME_YEAR, FONT_H2, WHITE, (WIDTH // 2, 435))

    text(SCREEN, f"Version {GAME_VERSION}", FONT_SMALL, TEXT2,
         (WIDTH // 2, 490))

    text(SCREEN, "Built with Python + Pygame", FONT, TEXT2,
         (WIDTH // 2, 610))

    text(SCREEN, "Edit the creator name and year in the code.",
         FONT_SMALL, TEXT2, (WIDTH // 2, 645))

    return back

# ============================================================
# INPUT HANDLING
# ============================================================

def setup_mouse(pos):
    global game_mode, difficulty, active_input
    global name_input, name_input_2, screen_name
    global player1_name, player2_name

    if back_button_rect.collidepoint(pos):
        play_sound(click_sound)
        screen_name = "home"
        return

    if MODE_COMPUTER.collidepoint(pos):
        play_sound(click_sound)
        game_mode = "Computer"
        active_input = 1
        return

    if MODE_MULTI.collidepoint(pos):
        play_sound(click_sound)
        game_mode = "Multiplayer"
        active_input = 1
        return

    if DIFF_EASY.collidepoint(pos):
        play_sound(click_sound)
        difficulty = "Easy"
        return

    if DIFF_MOD.collidepoint(pos):
        play_sound(click_sound)
        difficulty = "Moderate"
        return

    if DIFF_HARD.collidepoint(pos):
        play_sound(click_sound)
        difficulty = "Hard"
        return

    if DIFF_EXTREME.collidepoint(pos):
        play_sound(click_sound)
        difficulty = "Extreme"
        return

    p1box = pygame.Rect(70, 470, 400, 55)
    p2box = pygame.Rect(70, 540, 400, 55)

    if p1box.collidepoint(pos):
        active_input = 1
        return

    if game_mode == "Multiplayer" and p2box.collidepoint(pos):
        active_input = 2
        return

    if START_GAME.collidepoint(pos):
        play_sound(click_sound)
        player1_name = name_input.strip() or "Player 1"

        if game_mode == "Computer":
            player2_name = "Computer"
        else:
            player2_name = name_input_2.strip() or "Player 2"

        start_new_game()
        screen_name = "game"
        return

def history_mouse(pos):
    global history, screen_name

    if back_button_rect.collidepoint(pos):
        screen_name = "home"
        return

    clear_rect = pygame.Rect(150, 825, 240, 48)

    if clear_rect.collidepoint(pos):
        play_sound(click_sound)
        history = []
        save_history(history)

def settings_mouse(pos):
    global sound_on, music_on, IS_DARK, screen_name

    if back_button_rect.collidepoint(pos):
        play_sound(click_sound)
        screen_name = "home"
        return

    if sound_rect_global.collidepoint(pos):
        sound_on = not sound_on
        if sound_on:
            play_sound(click_sound)
        return

    if music_rect_global.collidepoint(pos):
        music_on = not music_on
        play_sound(click_sound)
        if music_on:
            start_background_music()
        else:
            stop_background_music()
        return

    if theme_rect_global.collidepoint(pos):
        IS_DARK = not IS_DARK
        apply_theme()
        play_sound(click_sound)
        return

def game_mouse(pos):
    global screen_name, scores

    if back_button_rect.collidepoint(pos):
        play_sound(click_sound)
        screen_name = "setup"
        return

    if RESET_GAME.collidepoint(pos):
        play_sound(click_sound)
        scores = {
            "Player 1": 0,
            "Player 2": 0,
            "Draw": 0
        }
        reset_board()
        return

    if RESTART_GAME.collidepoint(pos):
        play_sound(click_sound)
        start_new_game()
        return

    # Result popup buttons
    if game_over:
        again = pygame.Rect(80, 505, 175, 55)
        menu = pygame.Rect(285, 505, 175, 55)

        if again.collidepoint(pos):
            play_sound(click_sound)
            start_new_game()
            return

        if menu.collidepoint(pos):
            play_sound(click_sound)
            screen_name = "home"
            return

        return

    # Board click
    board_x = 60
    board_y = 250
    cell = 140

    if pygame.Rect(board_x, board_y, 420, 420).collidepoint(pos):
        col = (pos[0] - board_x) // cell
        row = (pos[1] - board_y) // cell

        if 0 <= row <= 2 and 0 <= col <= 2:
            index = row * 3 + col
            make_move(index)

def home_mouse(pos):
    global screen_name

    if HOME_PLAY.collidepoint(pos):
        play_sound(click_sound)
        screen_name = "setup"
    elif HOME_HISTORY.collidepoint(pos):
        play_sound(click_sound)
        screen_name = "history"
    elif HOME_SETTINGS.collidepoint(pos):
        play_sound(click_sound)
        screen_name = "settings"
    elif HOME_ABOUT.collidepoint(pos):
        play_sound(click_sound)
        screen_name = "about"
    elif HOME_QUIT.collidepoint(pos):
        pygame.quit()
        raise SystemExit

# ============================================================
# MAIN LOOP
# ============================================================

running = True
last_computer_move = 0

back_button_rect = pygame.Rect(18, 18, 108, 46)
sound_rect_global = pygame.Rect(350, 145, 90, 42)
music_rect_global = pygame.Rect(350, 220, 90, 42)
theme_rect_global = pygame.Rect(350, 295, 90, 42)

setup_audio()
start_background_music()

while running:
    CLOCK.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if screen_name == "setup":
                if event.key == pygame.K_BACKSPACE:
                    if active_input == 1:
                        name_input = name_input[:-1]
                    else:
                        name_input_2 = name_input_2[:-1]

                elif event.key == pygame.K_TAB:
                    active_input = 2 if active_input == 1 else 1

                elif event.key == pygame.K_RETURN:
                    player1_name = name_input.strip() or "Player 1"

                    if game_mode == "Computer":
                        player2_name = "Computer"
                    else:
                        player2_name = name_input_2.strip() or "Player 2"

                    start_new_game()
                    screen_name = "game"

                elif event.unicode.isprintable():
                    if active_input == 1 and len(name_input) < 18:
                        name_input += event.unicode
                    elif active_input == 2 and len(name_input_2) < 18:
                        name_input_2 += event.unicode

            elif event.key == pygame.K_ESCAPE:
                if screen_name == "game":
                    screen_name = "setup"
                elif screen_name != "home":
                    screen_name = "home"

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if screen_name == "home":
                home_mouse(pos)

            elif screen_name == "setup":
                setup_mouse(pos)

            elif screen_name == "game":
                game_mouse(pos)

            elif screen_name == "history":
                history_mouse(pos)

            elif screen_name == "settings":
                settings_mouse(pos)

            elif screen_name == "about":
                if back_button_rect.collidepoint(pos):
                    play_sound(click_sound)
                    screen_name = "home"

    # Computer AI delay
    if screen_name == "game" and game_mode == "Computer":
        if current_player == "O" and not game_over:
            now = pygame.time.get_ticks()
            if now - last_computer_move > 450:
                computer_turn()
                last_computer_move = now

    # Winning line animation
    if game_over and winning_line:
        if line_progress < 18:
            line_progress += 1

    # -------------------- DRAW --------------------

    if screen_name == "home":
        draw_home()

    elif screen_name == "setup":
        draw_setup()

    elif screen_name == "game":
        draw_game()

        if game_over and line_progress >= 12:
            draw_result_popup()

    elif screen_name == "history":
        draw_history()

    elif screen_name == "settings":
        draw_settings()

    elif screen_name == "about":
        draw_about()

    pygame.display.flip()

pygame.quit()
