from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
import random
import os

# Set full-screen size
Window.fullscreen = True
WIDTH, HEIGHT = Window.size
Window.clearcolor = (0,0,0,1)
# Object Sizes (Dynamic for all screens)
CAR_SIZE = WIDTH // 10  
OBSTACLE_SIZE = CAR_SIZE
OBSTACLE_SPEED = HEIGHT // 100 
BUTTON_HEIGHT = HEIGHT // 15  # Make sure obstacles stop before this height

# Best Score File
BEST_SCORE_FILE = "best_score.txt"

def load_best_score():
    if os.path.exists(BEST_SCORE_FILE):
        with open(BEST_SCORE_FILE, "r") as f:
            return int(f.read())
    return 0

def save_best_score(score):
    with open(BEST_SCORE_FILE, "w") as f:
        f.write(str(score))

class RacingGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.car_x = WIDTH // 2 - CAR_SIZE // 2
        self.car_y = HEIGHT * 0.40
        self.obstacles = []
        self.score = 0
        self.best_score = load_best_score()
        self.game_over = False

        # Draw Car
        with self.canvas:
            Color(1, 0, 0, 1)  # Red Car
            self.car = Rectangle(pos=(self.car_x, self.car_y), size=(CAR_SIZE, CAR_SIZE))

        # Score Display
        self.score_label = Label(text=f"Score: {self.score}", font_size=50, pos=(WIDTH // 2 - 50, HEIGHT - 100))
        self.add_widget(self.score_label)

        # Control Buttons
        self.left_btn = Button(text="LEFT", size_hint=(None, None), size=(WIDTH // 3, BUTTON_HEIGHT), pos=(WIDTH * 0.05, HEIGHT * 0.05))
        self.right_btn = Button(text="RIGHT", size_hint=(None, None), size=(WIDTH // 3, BUTTON_HEIGHT), pos=(WIDTH * 0.65, HEIGHT * 0.05))
        self.left_btn.bind(on_press=self.move_left)
        self.right_btn.bind(on_press=self.move_right)

        # Game Over Screen Elements
        self.wasted_label = Label(text="WASTED!!!", font_size=100, bold=True, color=(1, 0, 0, 1), pos=(WIDTH // 2 - 50, HEIGHT // 2 + 250))
        self.best_score_label = Label(text=f"Best Score: {self.best_score}", font_size=50, pos=(WIDTH // 2 - 50, HEIGHT // 3))
        self.restart_btn = Button(text="Restart", size_hint=(None, None), size=(WIDTH // 3, BUTTON_HEIGHT), pos=(WIDTH // 2 - WIDTH // 6, HEIGHT // 2 - 50))
        self.restart_btn.bind(on_press=self.restart_game)

        # Add game UI
        self.add_widget(self.left_btn)
        self.add_widget(self.right_btn)

        # Add game over screen UI but hide it
        self.add_widget(self.wasted_label)
        self.add_widget(self.best_score_label)
        self.add_widget(self.restart_btn)
        self.hide_game_over_screen()

        # Start Game Loop
        Clock.schedule_interval(self.update, 1/60)

    def move_left(self, instance):
        if not self.game_over:
            self.car_x = max(0, self.car_x - WIDTH // 10)
            self.car.pos = (self.car_x, self.car_y)

    def move_right(self, instance):
        if not self.game_over:
            self.car_x = min(WIDTH - CAR_SIZE, self.car_x + WIDTH // 10)
            self.car.pos = (self.car_x, self.car_y)

    def update(self, dt):
        if self.game_over:
            return

        # Spawn Obstacles
        if random.randint(1, 40) == 1:
            with self.canvas:
                Color(1, 1, 1, 1)  # White Obstacles
                obstacle = Rectangle(pos=(random.randint(0, WIDTH - OBSTACLE_SIZE), HEIGHT), size=(OBSTACLE_SIZE, OBSTACLE_SIZE))
                self.obstacles.append(obstacle)

        # Move Obstacles
        for obstacle in self.obstacles:
            obstacle.pos = (obstacle.pos[0], obstacle.pos[1] - OBSTACLE_SPEED)
            # Stop obstacles from overlapping buttons
            if obstacle.pos[1] < BUTTON_HEIGHT + 50:  # 10-pixel buffer
                self.obstacles.remove(obstacle)
                self.canvas.remove(obstacle)
                self.score += 1
                self.score_label.text = f"Score: {self.score}"  # Update score display

        # Collision Check
        for obstacle in self.obstacles:
            if (self.car_x < obstacle.pos[0] + OBSTACLE_SIZE and
                self.car_x + CAR_SIZE > obstacle.pos[0] and
                self.car_y < obstacle.pos[1] + OBSTACLE_SIZE and
                self.car_y + CAR_SIZE > obstacle.pos[1]):
                self.game_over_screen()

    def game_over_screen(self):
        self.game_over = True
        if self.score > self.best_score:
            self.best_score = self.score
            save_best_score(self.best_score)

        # Hide game elements
        self.left_btn.opacity = 0
        self.right_btn.opacity = 0
        self.score_label.opacity = 0

        # Show Game Over Screen
        self.wasted_label.opacity = 1
        self.best_score_label.opacity = 1
        self.best_score_label.text = f"Best Score: {self.best_score}"
        self.restart_btn.opacity = 1

    def hide_game_over_screen(self):
        """Hides the game over screen elements"""
        self.wasted_label.opacity = 0
        self.best_score_label.opacity = 0 
        self.restart_btn.opacity = 0

    def restart_game(self, instance):
        """Restarts the game properly"""
        self.game_over = False
        self.score = 0
        self.car_x = WIDTH // 2 - CAR_SIZE // 2  # Reset car position
        self.obstacles = []

        # Clear everything and redraw car
        self.canvas.clear()
        with self.canvas:
            Color(1, 0, 0, 1)  # Red Car
            self.car = Rectangle(pos=(self.car_x, self.car_y), size=(CAR_SIZE, CAR_SIZE))

        # Remove and re-add buttons to fix disappearing issue
        self.remove_widget(self.left_btn)
        self.remove_widget(self.right_btn)
        self.remove_widget(self.restart_btn)
        self.remove_widget(self.score_label)
        self.remove_widget(self.best_score_label)
        self.remove_widget(self.wasted_label)
        self.add_widget(self.left_btn)
        self.add_widget(self.right_btn)
        self.add_widget(self.restart_btn)
        self.add_widget(self.score_label)
        self.add_widget(self.best_score_label)
        self.add_widget(self.wasted_label)

        # Reset Score Display
        self.score_label.text = f"Score: {self.score}"
        self.score_label.opacity = 1

        # Show Buttons Again
        self.left_btn.opacity = 1
        self.right_btn.opacity = 1
        self.restart_btn.opacity = 1
        self.score_label.opacity = 1
        # Hide Game Over Screen
        self.hide_game_over_screen()

class RacingApp(App):
    def build(self):
        return RacingGame()

if __name__ == "__main__":
    RacingApp().run()