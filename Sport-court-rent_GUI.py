#!/usr/bin/env python
# coding: utf-8
__author__ = "DDENG"

import tkinter as tk    # python 3.x
from tkinter import ttk  # 美化元件
import tkinter.messagebox as tkMessageBox
# 載入驅動
from selenium import webdriver  # 打開網站
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import ImageTk, Image # 打開圖片和對圖片處理
import time  # 運行停頓
import re  # 正則 
import pytesseract  # 圖片轉文字

# 提醒視窗(確認)
def alert_check():
    while 1:
        try:
            driver.switch_to.alert.accept()
            break
        except:
            print("網頁載入中...")
# 確定&登入
def login():
    global account
    global password
    global rent_date
    global time_value
    global rent_date_xpath
    account = entry_account.get()
    password = entry_password.get()
    rent_date = entry_date.get()
    time_value = timechoosen.get()
    rent_date_xpath = f"//*[@onclick=\"GoToStep2('{rent_date}',1)\"]"    # 預約日期字串轉換
    win.destroy()    # 關閉視窗

# 重設
def reset():
    global time_value
    entry_account.delete(0, "end")
    entry_password.delete(0, "end")
    time_value = timechoosen.current(0)

# 關閉視窗
def quit():
   win.destroy()
   exit()

#  驗證碼辨識
class VerificationCode():
    def __init__(self):
        pass

    # 驗證碼截圖切割
    def get_pictures(self):
        # 抓取驗證碼位置
        driver.save_screenshot('ScreenShot.png')
        validcode = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_CaptchaImage"]')
        # print(validcode.location)
        # print(validcode.size)
        left = int(validcode.location['x']) * 1.25
        right = int(validcode.location['x'] + validcode.size['width']) * 1.25
        top = int(validcode.location['y']) * 1.25
        bottom = int(validcode.location['y'] + validcode.size['height']) * 1.25
        img = Image.open('ScreenShot.png')
        image_obj = img.crop((left, top, right, bottom))
        # image_obj.show()
        image_obj.save('capture.png')
        print('get_pictures : ok')
        return image_obj

    # 分二值 (黑、白)
    def processing_image(self):
        image_obj = self.get_pictures()
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
    def delete_spot(self):
        images = self.processing_image()
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
    def image_str(self):
        image = self.delete_spot()
        result = pytesseract.image_to_string(image)
        # 用正則提取數字，忽略異常符號
        regex = '\d+'
        result = ''.join(re.findall(regex, result))
        # 輸入驗證碼
        context = driver.find_element_by_name('ctl00$ContentPlaceHolder1$Captcha_text')
        context.send_keys(result)
        # time.sleep(1)
        # print(result)
        return result



# 建立tk視窗
win = tk.Tk()
win.wm_title("Badminton")
win.minsize(width=700,height=425)
win.resizable(width=False,height=False)

# 文字標籤
label_tittle=tk.Label(win,text="羽球場租借",font=("新細明體",30))
label_tittle.place(x=60,y=30)
label_account=tk.Label(win,text="請輸入帳號 : ", font=("新細明體",10))
label_account.place(x=30,y=130)
label_password=tk.Label(win,text="請輸入密碼 : ", font=("新細明體",10))
label_password.place(x=30,y=165)
label_date=tk.Label(win,text="請輸入日期 : ", font=("新細明體",10))
label_date.place(x=30,y=200)
label_tips=tk.Label(win,text="Ex: 2022 / 08 / 06 (日期之間無空格)", font=("新細明體",8), fg='red')
label_tips.place(x=315,y=205)
label_time=tk.Label(win,text="請選擇時段 : ", font=("新細明體",10))
label_time.place(x=30,y=235)

# 輸入框 帳號
entry_account=tk.Entry(win,font=(10))
entry_account.place(x=140,y=130,width=170,height=20)
# 輸入框 密碼
entry_password=tk.Entry(win,show='*',font=(10))  #密文型式
entry_password.place(x=140,y=165,width=170,height=20)
# 輸入框 日期
entry_date=tk.Entry(win,font=(10))
entry_date.place(x=140,y=200,width=170,height=20)

# button 確定
bt_check=tk.Button(win,text="確定",activebackground="yellow",activeforeground="red",command=login)
bt_check.place(x=40,y=330,width=60,height=30)
# button reset
bt_reset=tk.Button(win,text="reset",activebackground="yellow",activeforeground="red",command=reset)
bt_reset.place(x=150,y=330,width=60,height=30)
# button 關閉
bt_close=tk.Button(win,text="關閉",activebackground="yellow",activeforeground="red",command=quit)
bt_close.place(x=260,y=330,width=60,height=30)

# Time Combobox
time_value = tk.StringVar()
timechoosen = ttk.Combobox(win, width=15, textvariable=time_value)
# Time combobox list
timechoosen['values'] = ('    -----------------   ',
                         ' 09 ~ 10 ',
                         ' 10 ~ 11 ',
                         ' 11 ~ 12 ',
                         ' 19 ~ 20 ',
                         ' 20 ~ 21 ',
                         ' 21 ~ 22 ',)
timechoosen.place(x=140,y=235)
timechoosen.current(0) # 預設選項0-31

win.attributes('-topmost', True)  # 置頂 Tkinter 視窗
win.mainloop()


if __name__ == '__main__':
    option = webdriver.ChromeOptions()
    driver = webdriver.Chrome('chromedriver.exe', chrome_options=option)
    driver.get("https://scr.cyc.org.tw/tp08.aspx?module=login_page&files=login")

    # 提醒視窗(確定)
    alert_check()
    alert_check()
    time.sleep(1)

    # 輸入帳號
    context = driver.find_element_by_name('ctl00$ContentPlaceHolder1$loginid')
    context.send_keys(account)

    # 輸入密碼
    context = driver.find_element_by_name('loginpw')
    context.send_keys(password)

    # 擷取驗證碼及輸入驗證碼
    vc = VerificationCode()
    i = 0
    while True:
        try:
            captcha = vc.image_str()
            # time.sleep(1)
            driver.find_element_by_name('login_but').click()
            print("驗證碼:",captcha)
            # 按租借羽球場按鈕
            driver.find_element_by_xpath("//*[@id='ContentPlaceHolder1_button_image']/table/tbody/tr[3]/td[2]/img").click()
            break
        except:
            time.sleep(1)
            i += 1
            print('驗證碼錯誤','第',i,'次重新整理')
            # 提醒視窗(確認)
            alert_check()

    # 按注意事項確認
    driver.find_element_by_xpath("/html/body/table[1]/tbody/tr[3]/td/div/table/tbody/tr[4]/td/img").click()

    # 提醒視窗(確認)
    alert_check()

    # 點選日期
    while 1:
        try:
            book = WebDriverWait(driver, 0.015, 0.001).until(
                EC.presence_of_element_located((By.XPATH, rent_date_xpath)))
            book.click()  # 偵測到可以預訂按鈕就點擊按鈕
            print('可以點選!')
            break  # 跳出迴圈
        except:
            print("還不能點選! 重新整理!")
            driver.refresh()  # 重整頁面

    # 點選場地時段
    if time_value == ' 09 ~ 10 ':
        t = 20
    elif time_value == ' 10 ~ 11 ':
        t = 26
    elif time_value == ' 11 ~ 12 ':
        t = 32
    elif time_value == ' 19 ~ 20 ':
        t = 8
        driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_Step2_data"]/div[3]').click()  # 晚上時段
    elif time_value == ' 20 ~ 21 ':
        t = 14
        driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_Step2_data"]/div[3]').click()  # 晚上時段
    elif time_value == ' 21 ~ 22 ':
        t = 20
        driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_Step2_data"]/div[3]').click()  # 晚上時段
    i = 1
    while i < 7:
        try:
            driver.find_element_by_xpath(f'//*[@id="ContentPlaceHolder1_Step2_data"]/table/tbody/tr[{t}]/td[4]/img').click()
            alert_check()
            driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_Step3Info_lab"]/span[2]/a[2]').click()  # 回我的訂單
            print("羽", i, "預約成功!請去付款!")
            break
        except:
            print("羽", i, "預約失敗!")
            i += 1
            t += 1

