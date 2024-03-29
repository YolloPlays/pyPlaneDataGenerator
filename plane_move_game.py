"""
 @author jabo
 @create date 17.11.2023
 @desc Tool for Möller
"""
# TODO: Schieberegler für max_acceleration friction und acceleration

import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from idlelib.tooltip import Hovertip
from enum import Enum


GAME_WIDTH = 1020
GAME_HEIGHT = 600
OFFSET_PLAY_X = 10
OFFSET_PLAY_Y = 10

class GameState(Enum):
    NOT_STARTED = 0
    RUNNING = 1
    STOPPED = 2
    FINISHED_PLOT = 3
    @classmethod
    def toggle(cls, current_state):
        if current_state == cls.NOT_STARTED:
            return cls.RUNNING
        elif current_state == cls.RUNNING:
            return cls.STOPPED
        elif current_state == cls.STOPPED:
            return cls.FINISHED_PLOT
        elif current_state == cls.FINISHED_PLOT:
            return cls.NOT_STARTED
    

# 0 - Not started; 1 - Running; 2 - Stopped; 3 - Finished Plot
track_plane = GameState.NOT_STARTED
plane_data = []
radars = []

red_dot_on = False
block_root = False

class Plane:
    def __init__(self, gamecvs: tk.Canvas, x=100, y=100, acceleration=0.8, start_velocity_x=0, start_velovity_y=0, friction=0.99, max_acceleration=12, circle_size=30) -> None:
        self.x = x
        self.y = y
        self.acceleration = acceleration
        self.vx = start_velocity_x
        self.vy = start_velovity_y
        self.friction = friction
        self.max_acceleration = max_acceleration
        self.circle_size = circle_size
        self.gamecvs = gamecvs
        self.portrait = self.draw()
        
    def draw(self):
        return game_canvas.create_oval(self.x, self.y, self.x+self.circle_size, self.y+self.circle_size, fill="black", tag="plane")
        
    def move(self):
        if 'w' in currently_pressed and 'a' in currently_pressed:
            self.vy -= self.acceleration/2
            self.vx -= self.acceleration/2
        elif 'a' in currently_pressed and 's' in currently_pressed:
            self.vx -= self.acceleration/2
            self.vy += self.acceleration/2
        elif 's' in currently_pressed and 'd' in currently_pressed:
            self.vy += self.acceleration/2
            self.vx += self.acceleration/2
        elif 'd' in currently_pressed and 'w' in currently_pressed:
            self.vx += self.acceleration/2
            self.vy -= self.acceleration/2
        elif 'w' in currently_pressed:
            self.vy -= self.acceleration
        elif 'a' in currently_pressed:
            self.vx -= self.acceleration
        elif 's' in currently_pressed:
            self.vy += self.acceleration
        elif 'd' in currently_pressed:
            self.vx += self.acceleration
        
        # Berücksichtige Geschwindigkeitsgrenzen
        self.vx = max(-self.max_acceleration, min(self.vx, self.max_acceleration))
        self.vy = max(-self.max_acceleration, min(self.vy, self.max_acceleration))
        
        # Berücksichtige Reibung
        self.vx *= self.friction
        self.vy *= self.friction
        
        # Aktualisiere die Position basierend auf der Geschwindigkeit
        self.x = self.x+self.vx
        self.y = self.y+self.vy
        
        if self.x <= 4 or self.x >= self.gamecvs.winfo_width() - self.circle_size - 4:
            self.vx = 0
        if self.y <= 4 or self.y >= self.gamecvs.winfo_height() - self.circle_size - 4:
            self.vy = 0

        # Berücksichtige die Grenzen
        self.x = max(4, min(self.x, self.gamecvs.winfo_width()  - self.circle_size - 4))
        self.y = max(4, min(self.y, self.gamecvs.winfo_height() - self.circle_size - 4))

        # Kreis bewegen
        game_canvas.coords(self.portrait, self.x, self.y, self.x+self.circle_size, self.y+self.circle_size)
        
class Radar:
    def __init__(self, x, y, long=1, lat=1, rotation=0, size=16) -> None:
        self.x = x
        self.y = y
        self.long = long
        self.lat = lat
        self.rotation = rotation
        self.size = size
        self.size_off = size/2
        self.portrait = self.draw()
        
    def draw(self):
        return game_canvas.create_oval(self.x - self.size_off, self.y - self.size_off, self.x + self.size_off, self.y + self.size_off, fill="lightblue", tags="radar")
    
    def undraw(self):
        game_canvas.delete(self.portrait)
         
            
def tick_data(plane):
    if(track_plane == GameState.RUNNING):
        # clear_ax()
        plane_data.append((plane.x, -plane.y))
        # ax.scatter(*zip(*plane_data))
        # figure_canvas.draw()
    window.after(30, tick_data, plane)
        

def control(plane):
    plane.move()
    window.after(17, control, plane)

def set_keys(event):
    currently_pressed.add(event.keysym)
    
def _quit():
    window.quit()  # stops mainloop
    window.destroy()  # this is necessary on Windows to prevent
    # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    
# def clear_ax():
#     ax.clear()
#     ax.set_xlim(0,game_canvas.winfo_width())
#     ax.set_ylim(-game_canvas.winfo_height(), 0)

def toggle_track_plane():
    global track_plane
    track_plane = GameState.toggle(track_plane)
    if(track_plane == GameState.STOPPED):
        # clear_ax()
        # ax.scatter(*zip(*plane_data)) if len(plane_data)>0 else None
        # radar_tuple = list(map(lambda rad: (rad.x, -rad.y), radars))
        # ax.scatter(*zip(*radar_tuple), c='r') if len(radar_tuple)>0 else None
        # figure_canvas.draw()
        track_plane = GameState.FINISHED_PLOT
    elif track_plane == GameState.FINISHED_PLOT:
        track_plane = GameState.NOT_STARTED

def toggle_red_dot():
    global red_dot_on
    global track_plane
    if red_dot_on:
        canvas_dot.delete("recording")
        red_dot_on = False
    else:
        canvas_dot.create_oval(1, 24, 22, 45, fill="red", tags="recording",width=2)
        red_dot_on = True
        
    if track_plane == GameState.RUNNING:   
        window.after(700, toggle_red_dot)
    elif track_plane == GameState.FINISHED_PLOT:
        canvas_dot.delete("recording")
        red_dot_on = False
      
       
def change_label():
    if track_plane == GameState.NOT_STARTED:
        label.config(text="Idle")
    elif track_plane == GameState.RUNNING:
        label.config(text="Recording")
        toggle_red_dot()
    elif track_plane == GameState.FINISHED_PLOT:
        label.config(text="Finished")
        canvas_dot.delete("recording")  
                
def update_sizes(plane: Plane):
    window.update()
    plane.gameY=game_canvas.winfo_height()
    plane.gameX=game_canvas.winfo_width()
    # ax.set_xlim(0,game_canvas.winfo_width())
    # ax.set_ylim(-game_canvas.winfo_height(), 0)
    # ax.set_autoscalex_on(False)
    # ax.set_autoscaley_on(False)
    # figure_canvas.draw()
        
def reset():
    global track_plane
    global plane_data
    global red_dot_on
    
    track_plane = GameState.NOT_STARTED
    plane_data = []
    # clear_ax()
    # radar_tuple = list(map(lambda rad: (rad.x, -rad.y), radars))
    # ax.scatter(*zip(*radar_tuple), c='r') if len(radar_tuple)>0 else None
    # figure_canvas.draw()
    red_dot_on = False
    label.config(text="Idle")
    
def delete():
    global radars
    reset()
    # clear_ax()
    game_canvas.delete("radar")
    radars = []
    # figure_canvas.draw()
    
def network_toggle():
    if button3.config('relief')[-1] == 'sunken':
        button3.config(relief="raised")
        #Debug
        # print(list(map(lambda x: (x.x, x.y), radars)))
    else:
        button3.config(relief="sunken")

def on_radar(radarlist : list[Radar], x, y):
    for r in radarlist:
        if is_in_between(r.x - 30, x, r.x + r.size + 30) and is_in_between(r.y - 30, y, r.y + r.size + 30):
            return r
    return False

def is_in_between(a,b,c):
    return a <= b <= c
    

def mouse_press(event: tk.Event):
    global radars, block_root
    if block_root:
        return
    if event.widget == game_canvas:
        if button3.config('relief')[-1] == 'sunken':
            if not on_radar(radars, event.x, event.y):
                radar = Radar(event.x, event.y)
                radars.append(radar)
                # clear_ax()
                # radar_tuple = list(map(lambda rad: (rad.x, -rad.y), radars))
                # ax.scatter(*zip(*radar_tuple), c='r') if len(radar_tuple)>0 else None
                # ax.scatter(*zip(*plane_data)) if len(plane_data)>0 else None
                # figure_canvas.draw()
        else:
            if r:= on_radar(radars, event.x, event.y):
                block_root = True
                def unblock_root():
                    global block_root
                    block_root = False
                def handle_scale(event):
                    r.rotation = rot.get()
                    r.lat = lat.get()
                    r.long = long.get()
                def debug(fuckoff):
                    print(r.lat, r.long, r.rotation)
                pop_up = tk.Toplevel(window)
                pop_up.resizable(False, False)
                pop_up.title("Radar")
                pop_up.geometry("300x300+1200+250")
                pop_up.protocol("WM_DELETE_WINDOW", lambda : (unblock_root(), pop_up.destroy(), print(block_root)))
                pop_up.bind("<i>", debug)
                lat = tk.IntVar(value=r.lat)
                long = tk.IntVar(value=r.long)
                rot = tk.IntVar(value=r.rotation)
                sl_lat = tk.Scale(pop_up, from_=0, to=100, orient="horizontal", variable=lat, command=handle_scale)
                sl_long = tk.Scale(pop_up, from_=0, to=100, orient="horizontal", variable=long, command=handle_scale)
                sl_rot = tk.Scale(pop_up, from_=0, to=100, orient="horizontal", variable=rot, command=handle_scale)
                btn_del = tk.Button(pop_up, text="Delete", command=lambda: (radars.remove(r), r.undraw(), pop_up.destroy(), unblock_root()))
                sl_lat.pack(expand=True)
                sl_long.pack(expand=True)
                sl_rot.pack(expand=True)
                btn_del.pack(expand=True)
                # radars.remove(r)
                # r.undraw()
                # clear_ax()
                # radar_tuple = list(map(lambda rad: (rad.x, -rad.y), radars))
                # ax.scatter(*zip(*radar_tuple), c='r') if len(radar_tuple)>0 else None
                # ax.scatter(*zip(*plane_data)) if len(plane_data)>0 else None
                # figure_canvas.draw()
                
        

# Tasten drücken
def on_key_press(event):
    set_keys(event)

# Tasten loslassen
def on_key_release(event: tk.Event):
    if(event.keysym == 'space'):
        toggle_track_plane()
        change_label()
    # Debug purposes
    # if(event.keysym == 'i'):
    #     game_canvas.update()
    #     print(game_canvas.winfo_width(), game_canvas.winfo_reqwidth())
    currently_pressed.remove(event.keysym)

window = tk.Tk()
window.title("my game")
window.state("zoomed")
# Bindungen für Tasten
window.bind("<Key>", on_key_press)
window.bind("<KeyRelease>", on_key_release)
window.bind("<1>", mouse_press)

title_frame = tk.Frame(window, bg="#c8ebf7")
title_frame.pack(fill="x", expand=0)

label = tk.Label(title_frame, text="Idle", fg="#000000", bg="#c8ebf7", font=("Segoe UI Black", 30))
label.pack(padx=10, pady=20, side="left")

canvas_dot = tk.Canvas(title_frame, bg="#c8ebf7", highlightthickness=0, relief='ridge', height=60, width=24)
#canvas_dot.create_oval(1, 24, 22, 45, fill="red", tags="reccording",width=2)
canvas_dot.pack(side="left")

game_frame = title_frame = tk.Frame(window)
game_frame.pack(fill="both", expand=1)

game_canvas = tk.Canvas(game_frame, bg="lightgray")
game_canvas.pack(side="left", padx=OFFSET_PLAY_X, pady=OFFSET_PLAY_Y, fill="both", expand=1)

buttons_frame = tk.Frame(game_frame, bg="#e6e6e6")
buttons_frame.pack(side="left", pady=OFFSET_PLAY_Y+120, fill="y", expand=0)
reset_icon = tk.PhotoImage(file = "icons\\reset.png")
button1 = tk.Button(buttons_frame, bg="#d1e6ed", command=reset, image=reset_icon)
button1.pack(side="top", pady=40, padx=OFFSET_PLAY_X)
button1_tip = Hovertip(button1, "Reset", hover_delay=600)
trash_icon = tk.PhotoImage(file = "icons\\trash.png")
button2 = tk.Button(buttons_frame, bg="#d1e6ed", command=delete, image=trash_icon)
button2.pack(side="top", pady=40, padx=OFFSET_PLAY_X)
button2_tip = Hovertip(button2, "Delete", hover_delay=600)
radar_icon = tk.PhotoImage(file = "icons\\radar.png")
button3 = tk.Button(buttons_frame, bg="#d1e6ed", command=network_toggle, image=radar_icon)
button3.pack(side="top", pady=40, padx=OFFSET_PLAY_X)
button3_tip = Hovertip(button3, "Radar", hover_delay=600)

# fig, ax = plt.subplots()
# figure_canvas = FigureCanvasTkAgg(fig, game_frame)
# figure_canvas.draw()
# figure_canvas.get_tk_widget().pack(side="left", fill="both", expand=1, padx=OFFSET_PLAY_X, pady=OFFSET_PLAY_Y)

# Globale Variable zur Verfolgung der derzeit gedrückten Tasten
currently_pressed = set()

# Plane logic
plane = Plane(game_canvas)
window.after(3, update_sizes, plane)
control(plane)
tick_data(plane)


# Window necessities
window.protocol("WM_DELETE_WINDOW", _quit)
window.mainloop()