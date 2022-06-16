# pwm로 led밝기조절
# mcp3008(광센서) 이용해 주변 밝기에 따라 led밝기 조절
# gui 슬라이더 이용해 밝기, 소리 조절
# 기본 on/off 버튼, 공부/취침/자동모드 버튼, 설정버튼 누르면 새 창 열리고 공부/취침/자동모드 밝기 조절 가능

#-*-coding:utf-8-*- 

from curses.panel import top_panel
from tkinter import *
import tkinter
import tkinter.ttk
from tkinter import messagebox
import spidev
import RPi.GPIO as GPIO 
import threading

# MCP3008 채널중 센서에 연결한 채널 설정
ldr_channel = 0
# SPI 인스턴스 spi 생성
spi = spidev.SpiDev()
# SPI 통신 시작하기
spi.open(0, 0)
# SPI 통신 속도 설정
spi.max_speed_hz = 100000
# 0 ~ 7 까지 8개의 채널에서 SPI 데이터를 읽어옴
def readadc(adcnum): 
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

# 사용할 GPIO핀의 번호
led_pin_r = 18
led_pin_g = 12
# 불필요한 warning 제거
GPIO.setwarnings(False) 
# GPIO핀의 번호 모드 설정
GPIO.setmode(GPIO.BCM) 
# LED 핀의 OUT설정
GPIO.setup(led_pin_r, GPIO.OUT)
GPIO.setup(led_pin_g, GPIO.OUT)
# PWM 인스턴스를 PWM 핀으로 설정, 주파수  = 50Hz
p = GPIO.PWM(led_pin_r, 50) #led 1(yellow)
p2 = GPIO.PWM(led_pin_g, 50) #led 2(green)


# 모든 함수에서 사용할 전역변수
# 모든 led모드 기본 30%, 30%로 지정
m1_name = "Mode 1"
m1_led1 = 30
m1_led2 = 30

m2_name = "Mode 2"
m2_led1 = 30
m2_led2 = 30

ma_led1 = 30
ma_led2 = 30


def set_save(m1name, m1led1, m1led2, m2name, m2led1, m2led2, maled1, maled2):
        global m1_name, m1_led1, m1_led2, m2_name, m2_led1, m2_led2, ma_led1, ma_led2
        global m1_label, m2_label, auto_label
        
        #모드 이름, 밝기의 값이 바뀌지 않았는데 저장하려고 할 경우 나는 오류 예외처리(btn_save와 같은 오류)
        try:
            m1_name = m1name.get() #전역변수에 수정한 값 대입
            m1_led1 = m1led1.get()
            m1_led2 = m1led2.get()
            m1_label.config(text = "%s Led1 %d%%, Led2 %d%%" % (m1_name, m1_led1, m1_led2)) #현재 설정 창의 내용 바꿔줌
            btn_m1.config(text=m1_name) #기본 창의 버튼 이름 바꿈
            
            m2_name = m2name.get() #전역변수에 수정한 값 대입
            m2_led1 = m2led1.get()
            m2_led2 = m2led2.get()
            m2_label.config(text = "%s Led1 %d%%, Led2 %d%%" % (m2_name, m2_led1, m2_led2)) #현재 설정 창의 내용 바꿔줌
            btn_m2.config(text=m2_name) #기본 창의 버튼 이름 바꿈

            ma_led1 = maled1.get() #전역변수에 수정한 값 대입
            ma_led2 = maled2.get()
            auto_label.config(text = "Auto Led1 %d%%, Led2 %d%%" % (ma_led1, ma_led2)) #현재 설정 창의 내용 바꿔줌
        except TypeError:
            messagebox.showerror("오류!", "창 이름 또는 led의 값을 반드시 변경해야 합니다.")

#메뉴 - mode 창
def new_window():
    #전역변수 선언
    global m1_name, m1_led1, m1_led2
    global m2_name, m2_led1, m2_led2
    global ma_led1, ma_led2

    settings = Toplevel(gui_window)
    settings.geometry("300x250")
    settings.title("Mode")

    #mode 조정 프레임
    mode_top = tkinter.Frame(settings)
    mode_top.pack(side=TOP)

    notebook=tkinter.ttk.Notebook(mode_top, width=300, height=150)
    notebook.pack()

    tab1 = tkinter.Frame(mode_top)
    notebook.add(tab1, text="Mode 1")
    tab2 = tkinter.Frame(mode_top)
    notebook.add(tab2, text="Mode 2")
    tab3 = tkinter.Frame(mode_top)
    notebook.add(tab3, text="Auto")

    #tab1-----------------------------------------
    #모드 이름
    name = Label(tab1, text="모드 이름")
    name.grid(row=1, column=1)
    m1name = Entry(tab1)
    m1name.insert(0, m1_name)
    m1name.grid(row=1, column=2)

    #밝기조정(1, 2)
    led_y = Label(tab1, text="LED1 밝기 조정")
    led_y.grid(row=3, column=1)
    m1led1 = Scale(tab1, from_=0, to=100, orient=HORIZONTAL)
    m1led1.grid(row=3, column=2)

    led_g = Label(tab1, text="LED2 밝기 조정(탁상)")
    led_g.grid(row=5, column=1)
    m1led2 = Scale(tab1, from_=0, to=100, orient=HORIZONTAL)
    m1led2.grid(row=5, column=2)

    #tab2-----------------------------------------
    #모드 이름
    name = Label(tab2, text="모드 이름")
    name.grid(row=1, column=1)
    m2name = Entry(tab2)
    m2name.insert(0, m2_name)
    m2name.grid(row=1, column=2)

    #밝기조정(1, 2)
    led_y = Label(tab2, text="LED1 밝기 조정")
    led_y.grid(row=3, column=1)
    m2led1 = Scale(tab2, from_=0, to=100, orient=HORIZONTAL)
    m2led1.grid(row=3, column=2)

    led_g = Label(tab2, text="LED2 밝기 조정(탁상)")
    led_g.grid(row=5, column=1)
    m2led2 = Scale(tab2, from_=0, to=100, orient=HORIZONTAL)
    m2led2.grid(row=5, column=2)

    #tab3-----------------------------------------
    #밝기조정(1, 2)
    led_y = Label(tab3, text="LED1 밝기 조정")
    led_y.grid(row=3, column=1)
    maled1 = Scale(tab3, from_=0, to=100, orient=HORIZONTAL)
    maled1.grid(row=3, column=2)

    led_g = Label(tab3, text="LED2 밝기 조정(탁상)")
    led_g.grid(row=5, column=1)
    maled2 = Scale(tab3, from_=0, to=100, orient=HORIZONTAL)
    maled2.grid(row=5, column=2)

    #----------------------------------------------------
    #저장버튼 프레임
    mode_bot = tkinter.Frame(settings)
    mode_bot.pack(side=TOP)

    #저장버튼
    #모드 이름, 밝기의 값이 바뀌지 않았는데 저장하려고 할 경우 나는 오류 예외처리
    try:
        #저장 버튼을 눌렀을 때 다른 창에서도 값을 변경할 수 있도록 수정한 모든 값을 인자로 전달
        btn_save = Button(mode_bot, text="저장", command=lambda:set_save(m1name, m1led1, m1led2, m2name, m2led1, m2led2, maled1, maled2))
        btn_save.pack()
    except TypeError:
        messagebox.showerror("오류!", "창 이름 또는 led의 값을 반드시 변경해야 합니다.")


# 외부함수에서 사용하기 위해 라벨을 전역변수로 선언
m1_label = Label
m2_label = Label
auto_label = Label

#메뉴 - 현재설정 창
def now_window():
    nowMode = Toplevel(gui_window)
    nowMode.geometry("250x100")
    nowMode.title("현재 설정")
    
    global m1_label
    global m2_label
    global auto_label

    #현재설정 창의 내용
    m1_label = Label(nowMode, text="Mode 1 Led1 %d%%, Led2 %d%%" % (m1_led1, m1_led2))
    m1_label.pack()
    m2_label = Label(nowMode, text="Mode 2 Led1 %d%%, Led2 %d%%" % (m2_led1, m2_led2))
    m2_label.pack()
    auto_label = Label(nowMode, text="Auto Led1 %d%%, Led2 %d%%" % (ma_led1, ma_led2))
    auto_label.pack()

#스레딩 함수
#광센서, led 제어
def ldr_led():
    p.start(0)
    p2.start(0)
    #auto모드와 다른 모드일때 상호배제를 위해 mutex 획득 및 반납
    lock.acquire()
    if mode == 1: #mode 1일 때
        now.config(text="Now Mode is <"+btn_m1.cget('text')+">") #무슨 모드인지 알려주는 레이블 변경
        p.ChangeDutyCycle(m1_led1) #led 밝기 변경
        p2.ChangeDutyCycle(m1_led2)
    
    elif mode == 2: #mode 2일 때
        now.config(text="Now Mode is <"+btn_m2.cget('text')+">") #무슨 모드인지 알려주는 레이블 변경
        p.ChangeDutyCycle(m2_led1) #led 밝기 변경
        p2.ChangeDutyCycle(m2_led2)
    
    else: #auto일 때
        now.config(text="Now Mode is <Auto>") #무슨 모드인지 알려주는 레이블 변경
        while mode==0:
            #readadc 함수로 ldr_channel의 SPI 데이터를 읽어옴
            ldr_value = readadc(ldr_channel) 
            if ldr_value <= 500: #방이 어두울 때
                led1_n = ma_led1 + 20 #20% 더 밝게 함
                led2_n = ma_led2 + 20
                if led1_n >= 100: #20% 더 밝게한 값이 100보다 크면 100%(최대)으로 설정
                    led1_n = 100
                if led2_n >= 100:
                    led2_n = 100
                ldr_label.config(image=img_moon) #주위가 어두움 - 달 픽토그램으로 변경
                p.ChangeDutyCycle(led1_n) #led 밝기 변경
                p2.ChangeDutyCycle(led2_n)
            else:
                ldr_label.config(image=img_sun) #주위가 밝음 - 해 픽토그램으로 변경
                p.ChangeDutyCycle(ma_led1) #led 밝기 변경
                p2.ChangeDutyCycle(ma_led2)
    lock.release()
    

# state==1 이면 on, 0이면 off
# state==1 일때만, 즉 on상태일때만 mode1/2, auto버튼 작동
state = 0

# mode 1, 2 구분
mode = 0

#thread lock
lock = threading.Lock()

def mode1():
    global state, mode
    if state == 0: # state가 0일때 버튼 작동X
        return
    mode = 1
    t1 = threading.Thread(target=ldr_led)
    t1.start()

def mode2():
    global state, mode
    if state == 0:
        return
    mode = 2
    t1 = threading.Thread(target=ldr_led)
    t1.start()

def auto():
    global state, mode
    mode = 0
    if state == 0:
        return
    t = threading.Thread(target=ldr_led)
    t.start()

def on():
    global state, mode
    mode = 0
    state = 1
    t = threading.Thread(target=ldr_led)
    t.start()

def off():
    global state, mode
    mode = 0
    state = 0
    now.config(text="OFF")
    p.stop()
    p2.stop()

#GUI
gui_window = Tk()
gui_window.geometry("300x150")
gui_window.title("ONE TOUCH LED")

#menu
menubar=Menu(gui_window)
filemenu=Menu(menubar,tearoff=0)
filemenu.add_command(label="현재 설정",command=now_window)
filemenu.add_command(label="Mode",command=new_window)
menubar.add_cascade(label="설정",menu=filemenu)


#top frame (on/off button)
frame_top = tkinter.Frame(gui_window)
frame_top.pack(side=TOP)

btn_on = Button(frame_top, text="ON", command=on)
btn_on.pack(side=LEFT)
btn_off = Button(frame_top, text="OFF", command=off)
btn_off.pack(side=RIGHT)


#bottom frame (mode 1/2/auto button, now/ldr_label label)
frame_bot = tkinter.Frame(gui_window)
frame_bot.pack(side=TOP)

btn_m1 = Button(frame_bot, text=m1_name, command=mode1)
btn_m1.grid(row=0, column=1)
btn_m2 = Button(frame_bot, text=m2_name, command=mode2)
btn_m2.grid(row=0, column=2)
btn_auto = Button(frame_bot, text="Auto", command=auto)
btn_auto.grid(row=0, column=3)

now = Label(frame_bot, text="OFF") # 실행하면 꺼진 상태가 기본
now.grid(row=1, column=2)

img_sun = PhotoImage(file="/home/pi/class/20195126_termp/img/sun24.png")
img_moon = PhotoImage(file="/home/pi/class/20195126_termp/img/moon24.png")

ldr_label = Label(frame_bot, image = img_sun) #전원 들어오면 기본 낮 상태. auto모드일 경우 주위밝기 감지
ldr_label.grid(row=2, column=2)

gui_window.config(menu=menubar)
gui_window.mainloop()