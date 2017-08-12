import sys
import os
from time import sleep
from tkinter import *

def main():
    top = Tk()
    quit = Button(top, text='Hello World!',
    command=top.quit)
    quit.pack()
    mainloop()




if __name__=='__main__':
    main()
