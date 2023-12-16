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


# 打开Chrome
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


# 登录网址
def login_web(thread_no, url):
    global drivers
    drivers[thread_no].get(url)
    drivers[thread_no].implicitly_wait(1)


def log(str):
    log_file = open("log.txt", "a+")
    info = "[%s] - %s\n" % (datetime.datetime.now(), str)
    print(info, end="")
    log_file.write(info)


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


# 发送请求
def send_request(thread_no, request):
    # 绑定输入框
    global drivers
    global response_ids
    wait = WebDriverWait(drivers[thread_no], 20, 0.5)
    try:

        #    "你将作为一名专业的股票分析员, 搜索互联网最新信息, 根据获取的最新数据回答问题: \
        #         对于以下股票{request}满分为100, 必须输出你对他们未来三天的升值态度的评分. \
        #        必须经过信息的联网查询与分析之后, 给出对应股票的分数. 格式为股票, 分数，并使用中文进行回答 "
        prompt_area = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='prompt-textarea']")))
        msg = f"\
        作为一名专业股票分析员，我需要ChatGPT给出对以下股票未来三天升值的预测评分，以百分制表示。\
        请基于互联网最新信息进行查询和分析，并以[股票1 = 分数1, 股票2 = 分数2, ...] 的格式进行回答。\
        股票名字分别是[{request}]。确保使用中文回答."
        prompt_area.send_keys(msg)
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
            log("问题发送成功")
            break

        except:
            log("%d chrome send_button 没有找到." % (thread_no))
            send_button = None
            # 那么问题就无法发送出去。
            # 问题无法发送出去，那就不会有回复，就算去调用receive，也会报异常。
            # 问题没有发出去，就重新发送。


# 接收响应
def receive_response(thread_no):
    # 当stop消失时，绑定所有对话元素
    global drivers
    global stops
    drivers[thread_no].implicitly_wait(2)
    wait = WebDriverWait(drivers[thread_no], 20, 0.5)
    # 在此处开始设置计时器，当超过5分钟仍然在此函数时，刷新页面，重置 request_ids[thread_no]
    begin = time.time()
    while not stops[thread_no]:
        # 等待stop消失
        try:
            cur = time.time()
            elapsed_time = (cur - begin)
            log("elapsed_time = %d" % (elapsed_time))
            if elapsed_time > 5 * 60:
                log("已超时五分钟, 重置Chrome.")
                response_ids[thread_no] = 1
                drivers[thread_no].refresh()
                begin = time.time()
                return

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
            log("%d chrome prompt_area stop_button is also found." % (thread_no))
    # 此时，才可以开始捕获回复

    try:
        if response_ids[thread_no] % 2 == 0:
            response_ids[thread_no] += 1
        print("%d, %d" % (thread_no, response_ids[thread_no]))
        element_with_conversation = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[@data-testid='conversation-turn-{response_ids[thread_no]}']"))
        )
        log("%d 捕获回答" % (thread_no))
        file = open(f"%s_%d_resp" % (datetime.date.today(), thread_no), "a+")
        file.write("%d:" % (response_ids[thread_no]))
        file.write(element_with_conversation.text)
        file.write("\n")
        file.close()
        # log("%d, %s" % (thread_no, element_with_conversation.text))
    except:
        log("暂时没有回答。")
        pass


company_names = [
    "藏格矿业",
    "云鼎科技",
    "沈阳机床",
    "英特集团",
    "东旭光电",
    "渤海租赁",
    "*ST民控",
    "合肥百货",
    "通程控股",
    "吉林化纤",
    "南京公用"
]


# 启动初始化
def init(thread_no):
    global company_names
    load_chrome(thread_no)
    login_web(thread_no, "https://chat.openai.com/")
    # login_web(thread_no, "https://www.bilibili.com/")
    # login(thread_no)
    i = 0
    while True:
        try:
            time.sleep(2)
            receive_response(thread_no)
            time.sleep(2)
            if i < len(company_names) - 1:
                send_request(thread_no, (company_names[i] + "," + company_names[i + 1]))
                i += 2
            elif i == len(company_names) - 1:
                send_request(thread_no, (company_names[i]))
            else:
                log("执行结束。共统计 %d 个股票。" % (i + 1))
                exit(0)
        except Exception as e:
            log("执行结束。共统计 %d 个股票。" % (i + 1))
            exit(0)


if __name__ == '__main__':
    threads = [None] * 5
    for i in range(1):
        threads[i] = threading.Thread(target=init, args=(i,))

    for i in range(1):
        threads[i].start()
    # time.sleep(60)
    # for i in range(5):
    #     threads[i].join()
    #     drivers[i].close()
    time.sleep(20)
    print("share_resource = %d" % (share_resource,))

    while True:
        pass
