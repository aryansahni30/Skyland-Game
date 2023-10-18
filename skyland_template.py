from tkinter import *
import tkinter.font as font
import random
import time
import math

WIDTH, HEIGHT = 600, 400
CLOCK_RATE = 15
START_X, START_Y = 20, 350


class Skyland:
    def __init__(self, canvas):
        self.canvas = canvas
        self.canvas.bind_all('<KeyPress-space>', self.pause)
        self.canvas.bind_all('<KeyPress-Alt_L>', self.restart)

        self.land = Land(canvas)
        self.trophy = Trophy(canvas)
        self.AI1=AI(canvas,50,100,self)
        self.AI2=AI(canvas,400,100,self)
        self.avatar = Avatar(canvas, START_X, START_Y)
        self.score = 0

        self.text = canvas.create_text(150, 370, text='Score: 0  Time: 0.00',
                                       font=font.Font(family='Helvetica', size=15, weight='bold'))

        self.start_time = time.time()
        self.elapsed_time = 0
        self.is_game_over = False
        self.is_paused = False
        self.update()
        self.create_winning_objects()
    
    def start_movements(self):
        if not self.is_paused:
            self.move_balloon()
            self.AI1.move_spider()
            self.AI2.move_spider()

    def unpause_game(self):
        self.is_paused = False
        self.start_movements()

    def create_winning_objects(self):
        self.won_text = None
        self.won_trophy = None

    def show_winning_message(self):
        if self.won_text is None and self.won_trophy is None:
            self.won_text = self.canvas.create_text(250, 370, text='YOU WON!!PRESS OPTION KEY TO RESTART',
                                        font=font.Font(family='Helvetica', size=20, weight='bold'),
                                        fill='black')
            

    def restart(self, event=None):
        if self.is_game_over:
            self.is_game_over = False
            self.avatar.replace(self.avatar.initial_x, self.avatar.initial_y)
            self.trophy.replace()
            self.score = 0
            self.start_time = time.time()
            self.elapsed_time = 0
            self.land.reset_eggs()
            if self.won_text is not None:
                self.canvas.delete(self.won_text)  # Remove winning message
                self.won_text = None
            self.update()


    def pause(self, event=None):
        if not self.is_paused:
            self.elapsed_time += time.time() - self.start_time
        self.is_paused = not self.is_paused
        if not self.is_paused:
            self.start_time = time.time()

    def update(self):
        if not self.is_game_over and not self.is_paused:
            self.avatar.update(self.land, self.trophy)
            self.update_score_and_time()
            self.check_collision()

            if len(self.land.get_eggs()) == 0:
                self.is_game_over = True
                self.show_winning_message()

        self.canvas.after(CLOCK_RATE, self.update)
        if self.avatar.collide_with_spider(self.AI1) or self.avatar.collide_with_spider(self.AI2):  # Check collision with both spiders
            self.is_game_over = True

    def update_score_and_time(self):
        if not self.is_paused:
            elapsed_time = round(self.elapsed_time + time.time() - self.start_time, 2)
            self.canvas.itemconfigure(self.text, text=f'Score: {self.score}  Time: {elapsed_time:.2f}')

    def check_collision(self):
        collided_eggs = self.avatar.collide_with_eggs(self.land.get_eggs())
        self.score += len(collided_eggs)
        self.land.remove_eggs(collided_eggs)
        
        if len(self.land.get_eggs()) == 0:
            self.is_game_over = True
            self.show_winning_message()
        
        if self.avatar.collide_with_spider(self.AI1) or self.avatar.collide_with_spider(self.AI2):
            self.is_game_over = True
            self.pause()


class Land:
    def __init__(self, canvas):
        self.canvas = canvas

        # Sky
        self.canvas.create_rectangle(0, 0, WIDTH, START_Y - 100, fill='lightblue')

        # Valley
        self.canvas.create_rectangle(0, START_Y - 120, WIDTH, START_Y, fill='limegreen')

        # Clouds
        self.make_cloud(100, 80)
        self.make_cloud(400, 100)
        self.make_cloud(200, 200)

        # Hills
        self.make_hill( 50, 230, 250, 230, height=100, delta=3)
        self.make_hill(150, 300, 350, 300, height=100, delta=3)
        self.make_hill(250, 250, 450, 250, height=100, delta=3)
        self.make_hill(350, 300, 550, 300, height=100, delta=3)


        # Create eggs
        self.eggs = []
        self.create_eggs(5)

    def make_hill(self, x1, y1, x2, y2, height=100, delta=3):
        mid_x = (x1 + x2) / 2
        hill= self.canvas.create_polygon(x1, y1, mid_x, y1 - height, x2+delta, y1, fill='brown')
        return hill
    
    def cases(self, x1, y1, x2, y2):
        rect= self.canvas.create_rectangle(x1, y1, x2, y2, fill='coral', outline='black')
        return rect
    def get_obstacles(self):
        return [self.ground, self.start, self.stop] + self.rect

    def make_cloud(self, x, y):
        cloud_radius = 30
        cloud_distance = 40

        for i in range(3):
            cloud_x = x + (i - 1) * cloud_distance
            cloud_y = y
            self.canvas.create_oval(cloud_x - cloud_radius, cloud_y - cloud_radius,
                                    cloud_x + cloud_radius, cloud_y + cloud_radius, fill='white')

    def create_eggs(self, num_eggs):
        cluster_radius = 40

        self.create_star_cluster(150, 150, 7, 15)
        self.create_star_cluster(500, 150, 7, 15)
        self.create_star_cluster(300, 300, 7, 15)

    def create_star_cluster(self, center_x, center_y, num_eggs, radius):
        angle_increment = 360 / num_eggs
        for i in range(num_eggs):
            angle = math.radians(i * angle_increment)
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            star = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='white')
            self.eggs.append(star)

    def get_eggs(self):
        return self.eggs

    def remove_eggs(self, collided_eggs):
        for star in collided_eggs:
            self.eggs.remove(star)
            self.canvas.delete(star)

    def reset_eggs(self):
        for star in self.eggs:
            self.canvas.delete(star)
        self.create_eggs(5)


class Trophy:
    def __init__(self, canvas):
        self.canvas = canvas

        self.x = WIDTH - 30
        self.y = START_Y - 30
        self.trophy = self.canvas.create_polygon(self.x, self.y - 30, self.x + 20, self.y,
                                                 self.x - 20, self.y, fill='gold')

    def replace(self):
        self.canvas.coords(self.trophy, self.x, self.y - 30, self.x + 20, self.y, self.x - 20, self.y)

class AI:
    def __init__(self, canvas, x, y,skyland):
        self.canvas = canvas
        self.skyland = skyland
        self.spider = self.make_spider(x, y)
        self.thread = self.canvas.create_line(x + 10, 0, x + 10, y + 5, fill='ivory2', width=3)
        self.direction = 1  # Direction of spider movement (1: down, -1: up)
        self.speed = 1  # Speed of spider movement
        self.canvas.after(0, self.move_spider) 
        self.is_moving = False
        

    
            

  

    def make_spider(self, x, y):
        color1 = 'black'
        head = self.canvas.create_oval(5, 5, 15, 13, fill=color1)
        torso = self.canvas.create_oval(0, 10, 20, 40, fill=color1)
        legs = [self.canvas.create_line(-5 - i * 5, 10 * i + 5, 5, 10 * i + 15, fill=color1, width=4) for i in range(2)] + \
               [self.canvas.create_line(15, 10 * i + 15, 25 + i * 5, 10 * i + 5, fill=color1, width=4) for i in range(2)] + \
               [self.canvas.create_line(-10 + i * 5, 10 * i + 35, 5, 10 * i + 25, fill=color1, width=4) for i in range(2)] + \
               [self.canvas.create_line(15, 10 * i + 25, 30 - i * 5, 10 * i + 35, fill=color1, width=4) for i in range(2)]

        spider = [head, torso] + legs
        for part in spider:
            self.canvas.move(part, x, y)
        return spider
    
    def move_spider(self):
        # Get current spider coordinates
        spider_coords = self.canvas.coords(self.spider[0])
        x1, y1, x2, y2 = spider_coords

        # If the game is not paused, move the spider
        if not self.skyland.is_paused:
            # Check if the spider reaches the top or bottom boundary
            if y1 <= 0:
                self.direction = 1  # Change direction to down
            elif y2 >= HEIGHT:
                self.direction = -1  # Change direction to up

            # Move the spider based on the direction and speed
            movement = self.direction * self.speed
            self.canvas.move(self.spider[0], 0, movement)
            self.canvas.move(self.spider[1], 0, movement)
            self.canvas.move(self.spider[2], 0, movement)
            self.canvas.move(self.spider[3], 0, movement)
            self.canvas.move(self.spider[4], 0, movement)
            self.canvas.move(self.spider[5], 0, movement)
            self.canvas.move(self.spider[6], 0, movement)
            self.canvas.move(self.spider[7], 0, movement)
            self.canvas.move(self.spider[8], 0, movement)
            self.canvas.move(self.spider[9], 0, movement)

        # Schedule the next spider movement
        self.canvas.after(CLOCK_RATE, self.move_spider)
    

class Avatar:
    def __init__(self, canvas, initial_x, initial_y):
        self.canvas = canvas
        color1 = 'lime'
        color2 = 'peach puff'
        self.head = self.canvas.create_oval(0, 0, 10, 10, fill=color2)
        self.torso = self.canvas.create_rectangle(0, 10, 10, 20, fill=color1)
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.replace(initial_x, initial_y)
        self.canvas.bind_all('<KeyPress-Left>', self.move)
        self.canvas.bind_all('<KeyPress-Right>', self.move)
        self.canvas.bind_all('<KeyPress-Up>', self.move)
        self.canvas.bind_all('<KeyPress-Down>', self.move)

        self.x = 1
        self.y = 0
        self.gravity=0.1

    def update(self, land, trophy):
        self.canvas.move(self.head, self.x, self.y)
        self.canvas.move(self.torso, self.x, self.y)
        self.check_boundary()

        # Apply gravity
        self.y += self.gravity
        self.canvas.move(self.head, self.x, self.y)
        self.canvas.move(self.torso, self.x, self.y)
        self.check_boundary()
    
    def check_boundary(self):
        avatar_coords = self.canvas.coords(self.head)
        x1, y1, x2, y2 = avatar_coords
        avatar_width = x2 - x1
        avatar_height = y2 - y1

        if x1 < 0:
            self.x = abs(self.x)  # Move away from the left wall
        if x2 > WIDTH:
            self.x = -abs(self.x)  # Move away from the right wall
        if y1 < 0:
            self.y = abs(self.y)  # Move away from the top wall
        if y2 > HEIGHT:
            self.y = -abs(self.y)  # Move away from the bottom wall

        # Adjust avatar position to stay within boundaries
        if x1 < 0:
            self.x = 0  # Stop horizontal movement
            self.canvas.move(self.head, -x1, 0)
            self.canvas.move(self.torso, -x1, 0)
        if x2 > WIDTH:
            self.x = 0  # Stop horizontal movement
            self.canvas.move(self.head, WIDTH - x2, 0)
            self.canvas.move(self.torso, WIDTH - x2, 0)
        if y1 < 0:
            self.y = 0  # Stop vertical movement
            self.canvas.move(self.head, 0, -y1)
            self.canvas.move(self.torso, 0, -y1)
        if y2 > HEIGHT:
            self.y = 0  # Stop vertical movement
            self.canvas.move(self.head, 0, HEIGHT - y2)
            self.canvas.move(self.torso, 0, HEIGHT - y2)

    def move(self, event=None):
        if event.keysym == 'Left':
            self.x = -1
        elif event.keysym == 'Right':
            self.x = 1
        elif event.keysym == 'Up':  # jumping
            self.y = -2
        elif event.keysym == 'Down':  # ducking
            self.y = 2

    def replace(self, x, y):
        self.canvas.delete(self.head)
        self.canvas.delete(self.torso)
        self.head = self.canvas.create_oval(x, y, x + 10, y + 10, fill='peach puff')
        self.torso = self.canvas.create_rectangle(x, y + 10, x + 10, y + 20, fill='lime')

    def collide_with_eggs(self, eggs):
        collided_eggs = []
        avatar_coords = self.canvas.coords(self.head)

        for star in eggs:
            star_coords = self.canvas.coords(star)
            if self.is_collision(avatar_coords, star_coords):
                collided_eggs.append(star)

        return collided_eggs

    def is_collision(self, coords1, coords2):
        x1, y1, x2, y2 = coords1
        x3, y3, x4, y4 = coords2
        return not (x2 < x3 or x4 < x1 or y2 < y3 or y4 < y1)
    
    def collide_with_spider(self, spider):
        avatar_coords = self.canvas.bbox(self.head)
        spider_coords = self.canvas.bbox(spider.spider[0])  # Assuming spider[0] is the main part of the spider

        # Check for overlap between avatar and spider
        if (avatar_coords[2] >= spider_coords[0] and avatar_coords[0] <= spider_coords[2]) and \
           (avatar_coords[3] >= spider_coords[1] and avatar_coords[1] <= spider_coords[3]):
            return True
        else:
            return False


window = Tk()
window.title("Skyland")
canvas = Canvas(window, width=WIDTH, height=HEIGHT, bg='sky blue')
canvas.pack()
skyland = Skyland(canvas)
window.mainloop()