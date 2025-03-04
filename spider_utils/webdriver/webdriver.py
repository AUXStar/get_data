#!/usr/bin/env python
# coding=utf-8
###
# @FilePath     : /douyin/utils/webdriver/webdriver.py
# @Author       : njzy 48835121@qq.com
# @Date         : 2024-07-01 01:05:59
# @LastEditors  : njzy 48835121@qq.com
# @LastEditTime : 2024-08-05 16:33:11
###

from undetected_chromedriver.webelement import WebElement
from undetected_chromedriver.patcher import Patcher

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains as SeleniumActionChains
from selenium.webdriver.common.utils import keys_to_typing
from selenium.webdriver.common.by import By

from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.wheel_input import WheelInput

from seleniumwire.undetected_chromedriver import Chrome as BaseChrome
from seleniumwire.webdriver import ChromeOptions
from seleniumwire.request import Response

from brotli import decompress as br_decompress
from gzip import decompress as gzip_decompress
from random import randint

import shutil
import os
import time
from ..dirs import temp_dir
from ..mouse import mouse

# 替换驱动文件生成位置
Patcher.data_path = temp_dir(".undetected_chromedriver")

def get_body(response: Response):
    encoding = response.headers.get("content-encoding", "no_encoding")
    encoding = encoding.lower()
    if encoding == "br":
        return br_decompress(response.body)
    elif encoding == "gzip":
        return gzip_decompress(response.body)
    else:
        return response.body

class Chrome(BaseChrome):
    """
    继承Chrome，添加xpath查询语法
    """
    def __init__(self, download_driver=False,base=False,chrome_options:ChromeOptions=None):
        t = time.time()
        i = 0
        chrome_dir = ""
        if base:
            chrome_dir = temp_dir("chrome_files_base")
        else:
            while 1:
                i += 1
                chrome_dir = temp_dir(f"chrome_files{i}")
                if os.path.exists(chrome_dir):
                    if os.path.exists(os.path.join(chrome_dir, "lockfile")):
                        continue
                    else:
                        break
                else:
                    print("创建新chrome实例")
                    try:
                        shutil.copytree(temp_dir("chrome_files_base"), chrome_dir)
                    except:
                        print("无法创建实例")
                    break
        print(f"启动于{chrome_dir}")
        if chrome_options is None:
            chrome_options=ChromeOptions()
        opt = chrome_options
        opt.accept_insecure_certs = True
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        opt.add_argument("--user-agent={}".format(str(ua)))
        user_multi_procs = os.path.exists(temp_dir(".undetected_chromedriver")) and not(download_driver)
        super().__init__(
            user_multi_procs=user_multi_procs, user_data_dir=chrome_dir, options=opt
        )
        print(f"启动用时 {time.time()-t} s")

    def xpath(self, value):
        return self.find_element(By.XPATH, value)

    def xpaths(self, value):
        return self.find_elements(By.XPATH, value)

    def xpaths_recursive(self, value):
        return self.find_elements_recursive(By.XPATH, value)


class ActionChains(SeleniumActionChains):
    """
    重写鼠标操作
    """

    mouse_speed = 2
    last_point = (0, 0)
    human:bool

    def __init__(
        self,
        driver: WebDriver,
        duration: int = 0,
        devices: list[PointerInput | KeyInput | WheelInput] | None = None,
        human:bool=False
    ) -> None:
        super().__init__(driver, duration, devices)
        self.human=human

    def get_window_inner_size(self):
        return self._driver.execute_script(
            "return [window.innerWidth,window.innerHeight];"
        )

    def move_mouse(self, fx: int, fy: int, tx: int, ty: int):
        """
        鼠标移动基础方法，可以添加log查看具体移动
        """
        width, height = self.get_window_inner_size()
        if self.human:
            basic_coors = mouse.abs_mouse(int(fx), int(fy), int(tx), int(ty))
            for i in basic_coors:
                x, y = i[0], i[1]
                x, y = ((x if x < width else width), (y if y < height else height))
                x, y = (int(x if x > 0 else 0), int(y if y > 0 else 0))
                self.w3c_actions.pointer_action.move_to_location(x, y)
        else:
            self.w3c_actions.pointer_action.move_to_location(fx, fy)
            self.pause(0.1)
            self.w3c_actions.pointer_action.move_to_location(tx, ty)
        self.last_point = (tx, ty)
        return self
        

    def move_mouse_to(self, tx: int, ty: int):
        fx, fy = self.last_point
        self.move_mouse(fx, fy, tx, ty)
        return self

    def move_mouse_by(self, xoffset: int, yoffset: int):
        fx, fy = self.last_point
        self.move_mouse(fx, fy, (fx + xoffset), (fy + yoffset))
        return self

    def move_mouse_to_element(self, element: WebElement):
        rect = element.rect
        tx = int(rect["x"] + (rect["width"]) / 2)
        ty = int(rect["y"] + (rect["height"]) / 2)
        self.move_mouse_to(tx, ty)
        return self

    # overload move_by_offset

    def move_by_offset(self, xoffset: int, yoffset: int):
        """Moving the mouse to an offset from current mouse position.

        :Args:
         - xoffset: X offset to move to, as a positive or negative integer.
         - yoffset: Y offset to move to, as a positive or negative integer.
        """

        self.move_mouse_by(xoffset, yoffset)
        return self

    # overload move_to_element
    def move_to_element(self, to_element: WebElement):
        """Moving the mouse to the middle of an element.

        :Args:
         - to_element: The WebElement to move to.
        """

        self.move_mouse_to_element(to_element)
        return self

    # overload send_keys
    def send_keys(self, *keys_to_send: str):
        """Sends keys to current focused element.

        :Args:
         - keys_to_send: The keys to send.  Modifier keys constants can be found in the
           'Keys' class.
        """
        typing = keys_to_typing(keys_to_send)

        self.pause(randint(0, 5) / 10)
        for key in typing:
            self.key_down(key)
            self.key_up(key)
            self.pause(randint(0, 5) / 10)

        return self
