import tkinter as tk
import serial


LOGICAL_ROWS, LOGICAL_COLS = 1000, 1000
CANVAS_SIZE = 500
CELL_SIZE = CANVAS_SIZE / LOGICAL_ROWS
ball = [500, 500, -10, -1]
pbl = 490
pblo = 490
target_pbl = 490

val_sum = 0
counter = 0
pressure_const = 300
start_up = True
last_scorer = 0
player_score = 0
ai_score = 0

ai_speed = 4  
running = False

PORT = "COM7"
BAUD = 9600
ser = serial.Serial(PORT, BAUD, timeout=0.01)

root = tk.Tk()
canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="black")
canvas.pack()

player_paddle = None
ai_paddle = None
ball_rect = None
score_text = None
center_line = []
start_screen = None


def show_start_screen():
    global running, start_screen
    running = False
    canvas.delete("all")
    msg = "PONG\n\nPress 1 for Easy\nPress 2 for Medium\nPress 3 for Hard\n\nSpace = Quit to menu"
    start_screen = canvas.create_text(CANVAS_SIZE/2, CANVAS_SIZE/2, text=msg, fill="white",font=("Courier", 18), justify="center")


def start_game(difficulty):
    global ai_speed, player_score, ai_score, last_scorer
    global player_paddle, ai_paddle, ball_rect, score_text, center_line, running

    ai_speed = {1: 3, 2: 5, 3: 8}.get(difficulty, 4)

    player_score = 0
    ai_score = 0
    last_scorer = 0
    running = True

    canvas.delete("all")

    center_line = []
    for y in range(0, CANVAS_SIZE, 20):
        rect = canvas.create_rectangle(CANVAS_SIZE/2 - 2, y, CANVAS_SIZE/2 + 2, y+10, fill="white", outline="")
        center_line.append(rect)

    global pbl, pblo
    player_paddle = canvas.create_rectangle(60*CELL_SIZE, pbl*CELL_SIZE,80*CELL_SIZE, (pbl+200)*CELL_SIZE,fill="white")
    ai_paddle = canvas.create_rectangle((LOGICAL_COLS-60)*CELL_SIZE, pblo*CELL_SIZE,(LOGICAL_COLS-40)*CELL_SIZE, (pblo+200)*CELL_SIZE, fill="white")

    ball[0] = LOGICAL_COLS//2
    ball[1] = LOGICAL_ROWS//2
    ball_rect = canvas.create_rectangle(ball[0]*CELL_SIZE, ball[1]*CELL_SIZE, (ball[0]+20)*CELL_SIZE, (ball[1]+20)*CELL_SIZE,fill="white")

    
    score_text = canvas.create_text(CANVAS_SIZE/2, 30, text="0   0", fill="white", font=("Courier", 24))

    update_paddle()
    move_ball()
    update_balloons()



def sign(x): return (x > 0) - (x < 0)


import random

balloons = []  

def spawn_balloons(intensity):
    global balloons
    num = min(5, intensity // 50) 
    for _ in range(num):
        x = random.randint(50, CANVAS_SIZE - 50)
        y = CANVAS_SIZE + 20
        speed = random.uniform(1, 3)

        oval = canvas.create_oval(x-15, y-15, x+15, y+15, fill="red", outline="black")
        face = canvas.create_text(x, y, text=">_<", fill="white", font=("Courier", 10, "bold"))

        balloons.append([oval, face, x, y, speed])


def update_balloons():
    global balloons
    if not running:
        return

    for balloon in balloons[:]:
        oval, face, x, y, speed = balloon
        y -= speed
        canvas.coords(oval, x-15, y-15, x+15, y+15)
        canvas.coords(face, x, y)

        if y < -20:  
            canvas.delete(oval)
            canvas.delete(face)
            balloons.remove(balloon)
        else:
            balloon[3] = y  

    root.after(30, update_balloons)


def update_paddle():
    global pbl, target_pbl
    if not running:
        return

    try:
        while ser.in_waiting:
            line = ser.readline().decode("utf-8", errors="replace").strip()
        if line and line.isdigit():
            val = int(line)
            mapped = int(val - pressure_const)
            new_target = max(0, min(LOGICAL_ROWS-200, mapped*50))

            movement = abs(new_target - target_pbl)
            if movement > 100:
                spawn_balloons(movement)

            target_pbl = new_target
    except Exception as e:
        print("Serial error:", e)

    pbl += (target_pbl - pbl) * 0.2

    canvas.coords(player_paddle,
                  60*CELL_SIZE, pbl*CELL_SIZE,
                  80*CELL_SIZE, (pbl+200)*CELL_SIZE)

    root.after(16, update_paddle)


def reset_ball(scorer):
    global ball, last_scorer
    last_scorer = scorer
    ball[0] = LOGICAL_COLS//2
    ball[1] = LOGICAL_ROWS//2
    if scorer == 0:
        ball[2], ball[3] = 10, -1
    else:
        ball[2], ball[3] = -10, -1


def move_ball():
    global ball, pblo, player_score, ai_score
    if not running:
        return

    ball[0] += ball[2]
    ball[1] += ball[3]

    if ball[1] <= 0 or ball[1] >= LOGICAL_ROWS-20:
        ball[3] *= -1

    if 60 <= ball[0] <= 80 and pbl <= ball[1] <= pbl+200:
        ball[0] = 81
        ball[2] = abs(ball[2])
        ball[3] += (ball[1] - (pbl+100))//30

    if LOGICAL_COLS-80 <= ball[0] <= LOGICAL_COLS-60 and pblo <= ball[1] <= pblo+200:
        ball[0] = LOGICAL_COLS-81
        ball[2] = -abs(ball[2])
        ball[3] += (ball[1] - (pblo+100))//30

    if ball[0] < 0:
        ai_score += 1
        canvas.itemconfig(score_text, text=f"{player_score}   {ai_score}")
        reset_ball("ai")
    elif ball[0] > LOGICAL_COLS-20:
        player_score += 1
        canvas.itemconfig(score_text, text=f"{player_score}   {ai_score}")
        reset_ball(0)

    pblo -= sign((pblo+100)-ball[1])*ai_speed
    pblo = max(0, min(LOGICAL_ROWS-200, pblo))

    canvas.coords(
        ball_rect,
        ball[0]*CELL_SIZE, ball[1]*CELL_SIZE,
        (ball[0]+20)*CELL_SIZE, (ball[1]+20)*CELL_SIZE
    )
    canvas.coords(
        ai_paddle,
        (LOGICAL_COLS-60)*CELL_SIZE, pblo*CELL_SIZE,
        (LOGICAL_COLS-40)*CELL_SIZE, (pblo+200)*CELL_SIZE
    )

    root.after(16, move_ball)


def find_pressure():
    global pressure_const, val_sum, counter, start_up
    if start_up:
        if val_sum < 7000:
            try:
                while ser.in_waiting:
                    line = ser.readline().decode("utf-8", errors="replace").strip()
                if line and line.isdigit():
                    counter += 1
                    val = int(line)
                    val_sum += val
            except Exception as e:
                print("Serial error:", e)
            root.after(50, find_pressure)
        else:
            start_up = False
            pressure_const = int(val_sum / counter)+2
            print("Calibration complete, pressure_const =", pressure_const)
            show_start_screen()


def on_key(event):
    if event.char == "1":
        start_game(1)
    elif event.char == "2":
        start_game(2)
    elif event.char == "3":
        start_game(3)
    elif event.keysym == "space":
        show_start_screen()


root.bind("<Key>", on_key)

find_pressure()
root.mainloop()
