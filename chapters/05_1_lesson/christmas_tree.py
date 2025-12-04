import turtle
grinch = turtle.Turtle()
print(grinch)
grinch.pensize(10)
grinch.color("green")
grinch.fillcolor("red")
n = 5
for i in range(n):
    grinch.begin_fill()
    grinch.fd(15)

turtle.mainloop()
