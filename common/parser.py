import time
import uiautomator2 as u2
import random


class Helpers:
    @staticmethod
    def randomDelay(min=4000, max=6000):
        i = random.randint(min, max)
        time.sleep(i / 1000)


class Parser:
    def __init__(self, device_addr):
        self.d = u2.connect(device_addr)

    def scrollTop(self):
        self.d(scrollable=True).scroll.toBeginning(steps=10, max_swipes=99999)

    def scrollBottom(self):
        self.d(scrollable=True).scroll.toEnd(steps=10, max_swipes=99999)

    def dump(self):
        dump = self.d.dump_hierarchy(compressed=True, pretty=True)
        print(dump)

    def infiniteScrollBottom(self, action):
        i = 0
        while i < 3:
            self.d(scrollable=True).scroll.forward()
            action()
            i = i + 1

    def open(self, app_code):
        print('Opening ' + app_code)

        self.d.app_start(app_code, use_monkey=True)

        # Подождать 20 секунд пока приложение не откроется на экране
        pid = self.d.app_wait(app_code, front=True, timeout=20.0)

        # За 20 секунд приложение не загрузилось - кидаем ошибку
        if not pid:
            raise Exception(app_code + 'is not running')

    def close(self, app_code):
        print('Force closing app ' + app_code)
        self.d.shell('am force-stop ' + app_code)
