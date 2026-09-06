import turtle
turtle.penup()
turtle.goto(-200,0)
turtle.pendown()

turtle.pensize(10)

turtle.pencolor("red")

turtle.seth(-90)

for i in range(1):
    turtle.circle(100,180)
    turtle.circle(-90, 180)
turtle.circle(90,180/2)
turtle.fd(100)
turtle.circle(80,180)
turtle.fd(100)
