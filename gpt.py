import datetime
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import threading
import shutil

drivers = [None] * 10
lock = threading.Lock()
share_resource = 0
response_ids = [1] * 5
stops = [False] * 5


def del_user_data():
    try:
        shutil.rmtree("D:\\WebDriver")
        print("删除成功")
    except Exception as e:
        print("删除失败, %s" % (e))


def load_chrome(thread_no):
    global drivers
    global lock
    global share_resource
    options = uc.ChromeOptions()
    options.add_argument("--user-data-dir=" + f"C:/Users/Administrator/Desktop/WebDriver/{thread_no}")
    with  lock:
        drivers[thread_no] = uc.Chrome(options=options)
        drivers[thread_no].set_window_size(800, 600)
        share_resource += 1


def login_web(thread_no, url):
    global drivers
    drivers[thread_no].get(url)
    drivers[thread_no].implicitly_wait(1)


def log(str):
    print("[%s] - %s" % (datetime.datetime.now(), str))


# 登录
def login(thread_no):
    # 绑定到登录button
    global drivers
    wait = WebDriverWait(drivers[thread_no], 5, 1)
    try:
        login_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="login-button"]')))
        login_button.click()
    except:
        log("%d chrome login_button 没有找到." % (thread_no))

    try:
        user_name = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
        user_name.send_keys("siloq40cb@aiuop.com")
    except:
        log("%d chrome user_name 没有找到." % (thread_no))
    try:
        continue_button_1 = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[@class='c320322a4 c480bc568 c20af198f ce9190a97 _button-login-id']")))

        continue_button_1.click()
    except:
        log("%d chrome continue_button_1 没有找到." % (thread_no))

    try:
        password = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
        password.send_keys("0126sheng")
    except:
        log("%d chrome password 没有找到." % (thread_no))

    # continue_button.click()
    try:
        continue_button_2 = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//button[@class='c320322a4 c480bc568 c20af198f ce9190a97 _button-login-password']")))
        continue_button_2.click()
    except:
        log("%d chrome continue_button_2 没有找到." % (thread_no))


def send_request(thread_no, request):
    # 绑定输入框
    global drivers
    global response_ids
    wait = WebDriverWait(drivers[thread_no], 20, 0.5)
    try:
        prompt_area = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='prompt-textarea']")))
        prompt_area.send_keys("介绍一下C语言。")
    except:
        log("%d chrome prompt_area 没有找到." % (thread_no))
    # 绑定send按键

    send_button = None
    while not send_button:
        try:
            send_button = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@data-testid='send-button']")))
            send_button.click()
            response_ids[thread_no] += 1
            # 问题发送出去了，那就是等待stop变成run。
            # stop置为false就可以了。
            # 在接收问题处，不停的检查stop是否还存在，存在则false，不存在则true。
            stops[thread_no] = False
            break

        except:
            log("%d chrome send_button 没有找到." % (thread_no))
            send_button = None
            # 那么问题就无法发送出去。
            # 问题无法发送出去，那就不会有回复，就算去调用receive，也会报异常。
            # 问题没有发出去，就重新发送。


def receive_response(thread_no):
    # 当stop消失时，绑定所有对话元素
    global drivers
    global stops
    wait = WebDriverWait(drivers[thread_no], 20, 0.5)
    while not stops[thread_no]:
        # 等待stop消失
        try:
            stop_button = wait.until(
                EC.invisibility_of_element_located((By.XPATH, "//button[@aria-label='Stop generating']")))
            # 消失之后，再查看发送是否存在。如果发送存在且stop消失，则stops[]置为True
            if stop_button:
                try:
                    send_button = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[@data-testid='send-button']")))
                    log("%d chrome prompt_area stop_button 消失后，send_button is found." % (thread_no))
                    stops[thread_no] = True
                except:
                    log("%d chrome prompt_area stop_button 消失后，send_button not found." % (thread_no))
        except:
            log("%d chrome prompt_area stop_button not found." % (thread_no))
    # 此时，才可以开始捕获回复

    pass


# 初始化
def init(thread_no):
    # for i in range(thread_num):
    # del_user_data()
    load_chrome(thread_no)
    login_web(thread_no, "https://chat.openai.com/")
    login(thread_no)
    while True:
        receive_response(thread_no)
        send_request(thread_no, None)


if __name__ == '__main__':
    threads = [None] * 5
    for i in range(2):
        threads[i] = threading.Thread(target=init, args=(i,))

    for i in range(2):
        threads[i].start()
    # time.sleep(60)
    # for i in range(5):
    #     threads[i].join()
    #     drivers[i].close()
    print("share_resource = %d" % (share_resource,))
    while True:
        pass
