import time
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

driver = None
response_id = 2


def open_chrome():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=" + r"D:/WebDriver/Chrome/User_Data/")
    # chrome_options.add_argument("--headless")
    global driver
    driver = uc.Chrome(options=chrome_options)


def login_openai():
    global driver
    driver.get("https://chat.openai.com/")
    driver.implicitly_wait(2)


def ask_question():
    global prompt_area
    global response_id
    global stop
    wait = WebDriverWait(driver, 20, 0.5)
    prompt_area = wait.until(EC.visibility_of_element_located((By.ID, "prompt-textarea")))
    send_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@data-testid="send-button"]')))
    # print(prompt_area)
    # print(send_button)
    global request
    request = input("Input: ")
    while not request.strip():
        print("问题不能为空，请重新输入:\n")
        request = input("Input: ")
    prompt_area.clear()
    prompt_area.send_keys(request)
    send_button.click()
    response_id += 1
    stop = False


def get_answer():
    global stop
    wait = WebDriverWait(driver, 120, 0.5)
    stop_ele = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Stop generating']")))
    print("正在回答...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    while not stop:
        try:
            # stop = wait.until(EC.invisibility_of_element_located((By.XPATH, "//button[@aria-label='Stop generating']")))
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@data-testid="send-button"]')))
            stop = True
            print("回答完毕，开启捕获")
        except Exception as ex:
            stop = False
            print("仍在回答...")

    time.sleep(3)
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
        pass
        # ask_question()
        # print(get_answer() + "\n")
