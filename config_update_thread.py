from threading import Thread
from time import sleep

class ConfigLoader(Thread):
  def __init__(self, file):
     super(ConfigLoader, self).__init__()
  def run(self):
     while True:
        self.config = self.load(...)
        sleep(1)