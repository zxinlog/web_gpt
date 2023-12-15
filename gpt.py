import time
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = None
response_id = 2
stop = True


class colors:
    RESET = '\033[0m'  # 重置样式
    BOLD = '\033[1m'  # 粗体
    UNDERLINE = '\033[4m'  # 下划线
    RED = '\033[31m'  # 红色文本
    GREEN = '\033[32m'  # 绿色文本
    YELLOW = '\033[33m'  # 黄色文本
    BLUE = '\033[34m'  # 蓝色文本
    PURPLE = '\033[35m'  # 紫色文本
    CYAN = '\033[36m'  # 青色文本
    WHITE = '\033[37m'  # 白色文本


# 开启网页
def open_chrome():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=" + r"D:/WebDriver/Chrome/User_Data/")
    global driver
    driver = uc.Chrome(options=chrome_options)


# 登录openai
def login_openai():
    global driver
    driver.get("https://chat.openai.com/")
    driver.implicitly_wait(1)


def ask_question():
    global prompt_area
    global response_id
    global stop

    global request
    request = input("Input: ")
    while not request.strip():
        print("问题不能为空，请重新输入:\n")
        request = input("Input: ")

    wait = WebDriverWait(driver, 20, 0.5)
    prompt_area = wait.until(EC.visibility_of_element_located((By.ID, "prompt-textarea")))
    send_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@data-testid="send-button"]')))
    prompt_area.clear()
    prompt_area.send_keys(request)
    send_button.click()
    response_id += 1
    stop = False


def get_answer():
    global stop
    wait = WebDriverWait(driver, 120, 0.5)
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
        response = driver.find_element(By.XPATH, trace)
    return response.text


if __name__ == "__main__":
    open_chrome()
    login_openai()
    while True:
        ask_question()
        print(colors.GREEN + get_answer() + colors.RESET + "\n")
