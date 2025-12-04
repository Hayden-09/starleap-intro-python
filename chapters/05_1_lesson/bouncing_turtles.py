import turtle
import time
import random

screen = turtle.Screen()
screen.setup(800, 800)
turtle.tracer(False)

turtles: list[turtle.Turtle] = [ turtle. Turtle() ]

while True:
    for t in turtles:
       possible_moves = [t.forward, t.back, t.left, t.right]
       random_value = random.randint(0, 100)
       random.choice(possible_moves)(random_value)
    time.sleep(0.05)
    screen.update()

turtle.mainloop()