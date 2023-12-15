import time
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

drivers = [None] * 2
response_ids = [2] * 2
stops = [True] * 2


# 开启网页
def open_chrome(user_data):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=" + f"D:/WebDriver/Chrome/User_Data/{user_data}")
    global drivers
    drivers[int(user_data)] = uc.Chrome(options=chrome_options)


# 登录openai
def login_openai(index):
    global drivers
    drivers[int(index)].get("https://chat.openai.com/")
    drivers[int(index)].implicitly_wait(1)


# 发送问题请求
def ask_question(thread_no, trade_info):
    msg = f" 你将作为一名专业的股票分析员, 搜索互联网最新信息, 根据获取的最新数据回答问题: \
          对于以下股票{trade_info}满分为100, 必须输出你对他们未来三天的升值态度的评分. \
          必须经过信息的查询与分析之后, 给出对应股票的分数. 格式为股票, 分数. "

    if not trade_info:
        print("股票不能为空")
        exit(-1)
    global drivers
    wait = WebDriverWait(drivers[int(thread_no)], 20, 0.5)
    # prompt_area = drivers[int(thread_no)].find_element(By.ID, "prompt-textarea")
    # send_button = drivers[int(thread_no)].find_element(By.XPATH, '//*[@data-testid="send-button"]')
    prompt_area = wait.until(EC.visibility_of_element_located((By.ID, "prompt-textarea")))
    send_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@data-testid="send-button"]')))
    prompt_area.clear()
    prompt_area.send_keys(msg)
    send_button.click()
    global response_ids
    response_ids[int(thread_no)] += 1
    global stops
    stops[int(thread_no)] = False


# 接收回复
def resp_answer(thread_no):
    global stops
    wait = WebDriverWait(drivers[int(thread_no)], 120, 0.5)
    if not stops[int(thread_no)]:
        print("问题发送成功，正在等待解答...")
    else:
        print("问题发送失败.")
    time.sleep(3)
    while not stops[int(thread_no)]:
        try:
            # wait.until(EC.invisibility_of_element_located((By.XPATH, "//button[@aria-label='Stop generating']")))
            # drivers[int(thread_no)].find_element(By.XPATH, "//button[@aria-label='Stop generating']")
            drivers[int(thread_no)].find_element(By.XPATH, '//*[@data-testid="send-button"]')
            stops[int(thread_no)] = True
            print("解答成功，开始捕获")
        except Exception as ex:
            stops[int(thread_no)] = False
            print("仍在解答...")

    global response_ids
    if response_ids[int(thread_no)] < 3:
        pass
    elif response_ids[int(thread_no)] >= 3:
        if (response_ids[int(thread_no)] % 2 == 0):
            response_ids[int(thread_no)] += 1

    time.sleep(2)
    response = drivers[int(thread_no)].find_element(By.XPATH,
                                                    f"//*[@data-testid='conversation-turn-{response_ids[int(thread_no)]}']")
    print(response.text)
    return response.text


def get_answer():
    global stop
    wait = WebDriverWait(drivers, 120, 0.5)
    # stop_ele = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Stop generating']")))

    if not stop:
        print("正在回答...")
    else:
        print("问题没有发送成功...")

    time.sleep(2)
    while not stop:
        try:
            stop = wait.until(EC.invisibility_of_element_located((By.XPATH, "//button[@aria-label='Stop generating']")))
            # wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@data-testid="send-button"]')))
            # driver.find_element(By.XPATH, '//*[@data-testid="send-button"]')
            # driver.find_element(By.XPATH, "//button[@aria-label='Stop generati ng']")
            stop = True
            print("回答完毕，开启捕获")
            # time.sleep(1)
        except Exception as ex:
            stop = True

    # time.sleep(3)
    global response_id
    if response_id < 3:
        pass
    elif response_id >= 3:
        if (response_id % 2 == 0):
            response_id += 1
        trace = f"//*[@data-testid='conversation-turn-{response_id}']"
        response = drivers.find_element(By.XPATH, trace)
    return response.text


trade = ['神州高铁' '美丽生态', '深物业A', '南 玻Ａ', '沙河股份', '深康佳Ａ']
index = 0


def thread(thread_no):
    global index
    open_chrome(thread_no)
    login_openai(thread_no)
    while True:
        ask_question(thread_no, trade[index])
        resp_answer(thread_no)
        index += 1


if __name__ == "__main__":
    thread(1)
    # open_chrome('0')
    # open_chrome('1')
    # login_openai('0')
    # login_openai('1')
    # # while True:
    # time.sleep(5)
    # ask_question('0', "国华网安")  # chatgpt3
    # ask_question('1', "ST深天")  # chatgpt4
    # while True:
    #     pass
    #     # print(colors.GREEN + get_answer() + colors.RESET + "\n")
