"""
 @author jabo
 @create date 17.11.2023
 @desc Tool for Möller
"""
# TODO: Schieberegler für max_acceleration friction und acceleration

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from idlelib.tooltip import Hovertip


GAME_WIDTH = 1020
GAME_HEIGHT = 600
OFFSET_PLAY_X = 10
OFFSET_PLAY_Y = 10

# 0 - Not started; 1 - Running; 2 - Stopped; 3 - Finished Plot
track_plane = 0
plane_data = []
radars = []

red_dot_on = False

class Plane:
    def __init__(self, gamecvs: tk.Canvas, x=100, y=100, acceleration=0.4, start_velocity_x=0, start_velovity_y=0, friction=0.99, max_acceleration=6, circle_size=30) -> None:
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
    def __init__(self, x, y, size=16) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.size_off = size/2
        self.portrait = self.draw()
        
    def draw(self):
        return game_canvas.create_oval(self.x - self.size_off, self.y - self.size_off, self.x + self.size_off, self.y + self.size_off, fill="lightblue", tags="radar")
    
    def undraw(self):
        game_canvas.delete(self.portrait)
         
            
def tick_data(plane):
    if(track_plane == 1):
        plane_data.append((plane.x, -plane.y))
    window.after(30, tick_data, plane)
        

def control(plane):
    plane.move()
    window.after(10, control, plane)

def set_keys(event):
    currently_pressed.add(event.keysym)
    
def _quit():
    window.quit()  # stops mainloop
    window.destroy()  # this is necessary on Windows to prevent
    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

def toggle_track_plane():
    global track_plane
    track_plane = track_plane + 1
    if(track_plane == 2):
        ax.scatter(*zip(*plane_data))
        figure_canvas.draw()
        track_plane = 3
    elif track_plane == 3:
        track_plane = 0

def toggle_red_dot():
    global red_dot_on
    global track_plane
    if red_dot_on:
        canvas_dot.delete("recording")
        red_dot_on = False
    else:
        canvas_dot.create_oval(1, 24, 22, 45, fill="red", tags="recording",width=2)
        red_dot_on = True
        
    if track_plane == 1:   
        window.after(700, toggle_red_dot)
    elif track_plane > 1:
        canvas_dot.delete("recording")
        red_dot_on = False
      
       
def change_label():
    if track_plane == 0:
        label.config(text="Idle")
    elif track_plane == 1:
        label.config(text="Recording")
        toggle_red_dot()
    elif track_plane > 2:
        label.config(text="Finished")
        canvas_dot.delete("recording")  
                
def update_sizes(plane: Plane):
    window.update()
    plane.gameY=game_canvas.winfo_height()
    plane.gameX=game_canvas.winfo_width()
    ax.set_xlim(0,game_canvas.winfo_width())
    ax.set_ylim(-game_canvas.winfo_height(), 0)
    figure_canvas.draw()
        
def reset():
    global track_plane
    global plane_data
    global red_dot_on
    
    track_plane = 0
    plane_data = []

    red_dot_on = False
    label.config(text="Idle")
    
def delete():
    global radars
    reset()
    ax.clear()
    game_canvas.delete("radar")
    radars = []
    ax.set_xlim(0,game_canvas.winfo_width())
    ax.set_ylim(-game_canvas.winfo_height(), 0)
    figure_canvas.draw()
    
def network_toggle():
    if button3.config('relief')[-1] == 'sunken':
        button3.config(relief="raised")
        #Debug
        print(list(map(lambda x: (x.x, x.y), radars)))
    else:
        button3.config(relief="sunken")

def is_in_valid_boundaries(x, y):
    global game_canvas
    x_valid = is_in_between(game_canvas.winfo_rootx(), x, game_canvas.winfo_rootx()+game_canvas.winfo_width())
    y_valid = is_in_between(game_canvas.winfo_rooty(), y, game_canvas.winfo_rooty()+game_canvas.winfo_height())
    return x_valid and y_valid

def on_radar(radarlist : list[Radar], x, y):
    for r in radarlist:
        if is_in_between(r.x - 30, x, r.x + r.size + 30) and is_in_between(r.y - 30, y, r.y + r.size + 30):
            return r
    return False

def is_in_between(a,b,c):
    return a <= b <= c
    

def mouse_press(event: tk.Event):
    global radars
    if is_in_valid_boundaries(event.x_root, event.y_root):
        if button3.config('relief')[-1] == 'sunken':
            if not on_radar(radars, event.x, event.y):
                radar = Radar(event.x, event.y)
                radars.append(radar)
        else:
            r = on_radar(radars, event.x, event.y)
            if r:
                radars.remove(r)
                r.undraw()
        

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
game_frame.pack(fill="both")

game_canvas = tk.Canvas(game_frame, bg="lightgray")
game_canvas.pack(side="left", padx=OFFSET_PLAY_X, pady=OFFSET_PLAY_Y, fill="both", expand=1)

buttons_frame = tk.Frame(game_frame, bg="#e6e6e6")
buttons_frame.pack(side="left", pady=OFFSET_PLAY_Y, fill="y", expand=0)
reset_icon = tk.PhotoImage(file = "pyPlaneDataGenerator\\icons\\reset.png")
button1 = tk.Button(buttons_frame, bg="#d1e6ed", command=reset, image=reset_icon)
button1.pack(side="top", pady=40, padx=OFFSET_PLAY_X)
button1_tip = Hovertip(button1, "Reset", hover_delay=600)
trash_icon = tk.PhotoImage(file = "pyPlaneDataGenerator\\icons\\trash.png")
button2 = tk.Button(buttons_frame, bg="#d1e6ed", command=delete, image=trash_icon)
button2.pack(side="top", pady=40, padx=OFFSET_PLAY_X)
button2_tip = Hovertip(button2, "Delete", hover_delay=600)
radar_icon = tk.PhotoImage(file = "pyPlaneDataGenerator\\icons\\radar.png")
button3 = tk.Button(buttons_frame, bg="#d1e6ed", command=network_toggle, image=radar_icon)
button3.pack(side="top", pady=40, padx=OFFSET_PLAY_X)
button3_tip = Hovertip(button3, "Radar", hover_delay=600)

fig, ax = plt.subplots()
figure_canvas = FigureCanvasTkAgg(fig, game_frame)
# figure_canvas.draw()
figure_canvas.get_tk_widget().pack(side="left", fill="both", expand=1, padx=OFFSET_PLAY_X, pady=OFFSET_PLAY_Y)

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