import turtle
bob = turtle.Turtle()
print(bob)
bob.pensize(15)
bob.color("green")
bob.fillcolor("red")
n = 10

bob.penup()
bob.goto(0,-300)
bob.pendown()

for i in range(n):
    bob.begin_fill()
    bob.circle(50)
    bob.end_fill()
    bob.penup()
    bob.left(360/n)
    bob.fd(200)
    bob.pendown()

bill = turtle.Turtle()
bill.pensize(5)
bill.color("green")
bill.fillcolor("green")
bill.penup()
bill.goto(0,-150)
for x in range(n):
    bill.begin_fill()
    bill.circle(25)
    bill.end_fill()
    bill.penup()
    bill.left(360/n)
    bill.fd(150)
    bill.pendown()


turtle.mainloop()