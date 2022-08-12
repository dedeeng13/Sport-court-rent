#!/usr/bin/env python
# coding: utf-8
__author__ = "DDENG"


from selenium import webdriver  # 用於打開網站
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
#載入驅動
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time  # 運行停頓
import pyautogui
import re  # 用於正則
from PIL import Image  # 用於打開圖片和對圖片處理
import pytesseract  # 用於圖片轉文字



def login():
    # 提醒視窗(確定)
    pyautogui.keyDown('enter')
    pyautogui.keyUp('enter')
    pyautogui.keyDown('enter')
    pyautogui.keyUp('enter')
    time.sleep(1)
    # 輸入帳號
    context = driver.find_element_by_name('ctl00$ContentPlaceHolder1$loginid')
    context.send_keys("你的帳號")
    # 輸入密碼
    context = driver.find_element_by_name('loginpw')
    context.send_keys("你的密碼")

# 驗證碼截圖切割
def get_pictures():
    # 抓取驗證碼位置
    img = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_CaptchaImage"]')
    location = img.location
    size = img.size  # 獲取驗證碼的大小參數
    left = location['x'] + 174
    top = location['y'] + 70
    right = left + size['width'] + 15
    bottom = top + size['height'] + 5
    driver.save_screenshot('CaptchaImage.png')  # 截圖
    page_snap_obj = Image.open('CaptchaImage.png')
    image_obj = page_snap_obj.crop((left, top, right, bottom))  # 擷取驗證碼的部分 (左,上,右,下)
    # image_obj.show()
    print('get_pictures : ok')
    return image_obj

# 分二值 (黑、白)
def processing_image():
    image_obj = get_pictures()
    img = image_obj.convert("L")  # 轉灰度
    pixdata = img.load()
    w, h = img.size
    threshold = 160
    # 遍歷所有像素，大於閾值的爲黑色
    for y in range(h):
        for x in range(w):
            if pixdata[x, y] < threshold:
                pixdata[x, y] = 0
            else:
                pixdata[x, y] = 255
    # img.show()
    print('processing_image : ok')
    return img

# 去黑點
def delete_spot():
    images = processing_image()
    data = images.getdata()
    w, h = images.size
    black_point = 0
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            mid_pixel = data[w * y + x]  # 中央像素點像素值
            if mid_pixel < 50:  # 找出上下左右四個方向像素點像素值
                top_pixel = data[w * (y - 1) + x]
                left_pixel = data[w * y + (x - 1)]
                down_pixel = data[w * (y + 1) + x]
                right_pixel = data[w * y + (x + 1)]
                # 判斷上下左右的黑色像素點總個數
                if top_pixel < 10:
                    black_point += 1
                if left_pixel < 10:
                    black_point += 1
                if down_pixel < 10:
                    black_point += 1
                if right_pixel < 10:
                    black_point += 1
                if black_point < 1:
                    images.putpixel((x, y), 255)   # putpixel(xy座標, color) 白:255
                black_point = 0
    # images.show()
    print('delete_spot : ok')
    return images

# 圖片轉文字
def image_str():
    image = delete_spot()
    result = pytesseract.image_to_string(image)
    # 可能存在異常符號，用正則提取其中的數字
    regex = '\d+'
    result = ''.join(re.findall(regex, result))
    # 輸入驗證碼
    context = driver.find_element_by_name('ctl00$ContentPlaceHolder1$Captcha_text')
    context.send_keys(result)
    time.sleep(2)
    # print(result)
    return result

def court_time():
    # 按注意事項確認
    driver.find_element_by_xpath("/html/body/table[1]/tbody/tr[3]/td/div/table/tbody/tr[4]/td/img").click()

    # 提醒視窗(確認)
    pyautogui.keyDown('enter')
    pyautogui.keyUp('enter')

    while 1:
        try:
            book = WebDriverWait(driver, 0.5, 0.25).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_Date_Lab"]/table/tbody/tr[5]/td[4]/table/tbody/tr[2]/td/img')))  # 8/17
            book.click() # 偵測到可以預訂按鈕就點擊按鈕
            print ('可以點選!')
            break  # 跳出迴圈
        except:
            print("還不能點選! 重新整理!")
            driver.refresh() # 重整頁面
    # 點選場地時段  (從 羽1 -> 羽6 搶)
    i = 1
    t = 20
    while i < 7:
        try:
            driver.find_element_by_xpath(f'//*[@id="ContentPlaceHolder1_Step2_data"]/table/tbody/tr[{t}]/td[4]/img').click()  # 9:00-10:00  羽1-羽6   方法2
            # 提醒視窗(確認)
            pyautogui.keyDown('enter')
            pyautogui.keyUp('enter')
            driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_Step3Info_lab"]/span[2]/a[2]').click()  # 回我的訂單
            print("羽",i,"預約成功!請去付款!")
            break
        except:
            print("羽",i,"預約失敗!")
            i += 1
            t += 1

# == 開始 ==
option = webdriver.ChromeOptions()
driver = webdriver.Chrome('chromedriver.exe', chrome_options=option)
driver.get("https://scr.cyc.org.tw/tp08.aspx?module=login_page&files=login")

# 登入
login()
# 驗證碼
i = 0
while True:
    try:
        captcha = image_str()
        time.sleep(1)
        driver.find_element_by_name('login_but').click()
        print("驗證碼:",captcha)
        # 按租借羽球場按鈕
        driver.find_element_by_xpath("//*[@id='ContentPlaceHolder1_button_image']/table/tbody/tr[3]/td[2]/img").click()
        break
    except:
        time.sleep(1)
        i += 1
        print('驗證碼錯誤','第',i,'次重新整理')
        # # 提醒視窗(確認)
        pyautogui.keyDown('enter')
        pyautogui.keyUp('enter')
# 選擇球類、日期、時段、場地
court_time()







