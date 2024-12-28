import pyfiglet
from datetime import datetime

def printBanner(text, target):
    print(pyfiglet.figlet_format(text))
    print("-"*50)
    print("Scanning Target: " + target)
    print("Scanning started at: " + str(datetime.now()))
    print("-"*50)