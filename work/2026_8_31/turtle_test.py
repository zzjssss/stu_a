import turtle

turtle.penup()
turtle.fd(-200)
turtle.pendown()
turtle.pensize(20)
turtle.pencolor("yellow")
turtle.seth(-44)
for i in range(4):
    turtle.circle(40,88)
    turtle.circle(-40,88)
turtle.circle(40,88/2)
turtle.fd(80)
turtle.circle(40,180)
turtle.fd(80)
turtle.mainloop()