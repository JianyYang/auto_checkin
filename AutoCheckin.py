import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import argparse
import requests
from requests.cookies import RequestsCookieJar
from requests.utils import dict_from_cookiejar, cookiejar_from_dict
import threading
import time
import base64
from datetime import datetime

def push_msg(skey: str, title: str, content: str):
    params = {"title": title, "desp": content}
    push_url = "https://sctapi.ftqq.com/" + skey +".send"
    requests.get(push_url, params=params)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="CordCloud Checkin")
    parser.add_argument("-u", "--username", help="username", type=str,required=True)
    parser.add_argument("-p", "--password", help="password", type=str,required=True)
    parser.add_argument("-U","--url",help="cordcloud url",type=str,required=True)
    parser.add_argument("-s","--skey",help="skey",type=str,required=True)
    parser.add_argument("-P","--proxykey",help="proxykey",type=str,required=True)
    args=parser.parse_args()

    username = args.username
    password = args.password
    url = args.url
    skey = args.skey
    proxykey = args.proxykey

    proxyserver = "http://" + proxykey + "&wait=5000@proxy.zenrows.com:8001"
    print(proxyserver)
    
    testurl = "https://www.c-cloud.xyz/auth/login"
    proxies = {"http": proxyserver, "https": proxyserver}
    testresponse = requests.get(testurl, proxies=proxies, verify=False)
    print(testresponse.text)

    options = uc.ChromeOptions()
    options.add_argument("--window-size=1280,1024")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--excludeSwitches=enable-automation")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f'--proxy-server=http://fa82f17718a8576a773e9e24605649449559e3a9:antibot=true@proxy.zenrows.com:8001')
    
    driver = uc.Chrome(driver_executable_path="/usr/bin/chromedriver", use_subprocess=True, options=options)
    driver.implicitly_wait(10)
    try:
        
        now = datetime.now()
        nowstr = str(now)

        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers":{
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            }
        })
        
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => False
            })
        """})
        
        driver.get(f'{url}/auth/login')
        
        time.sleep(30)
        list_windows = driver.window_handles
        print(list_windows)
        driver.switch_to.window(list_windows[0])
        
        print(driver.title)
        print(driver.current_url)

        driver.save_screenshot('screenshot_' + nowstr + '.png')

        f = open('screenshot_' + nowstr + '.png','rb') 
        encodedata = base64.b64encode(f.read())
        print("data:image/bmp;base64," + str(encodedata.decode()))
        f.close()
        
        email_input = driver.find_element(by=By.ID, value="email")
        email_input.send_keys(username)
        password_input = driver.find_element(by=By.ID, value="passwd")
        password_input.send_keys(password)
        driver.find_element(by=By.ID, value="login").click()
        text = driver.find_element(by=By.XPATH, value="/html/body/main/div[2]/section/div[2]/div[1]/div[1]/div/div[2]/p[2]").text
        print("Login success!")
        print(text)

        cookies = driver.get_cookies()
        c={}
        for cookie in cookies:
            cookie = dict(cookie)
            c[cookie["name"]] = cookie["value"]
        
        response = requests.post(f'{url}/user/checkin', cookies=c, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.52",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": url,
            "Referer": f"{url}/user"
        },timeout=10)

        result = response.json()
        print(result)
        push_title = "Cord签到:" + result["msg"]    
        if result["ret"] == 1 and "trafficInfo" in result:
            un_used = result["trafficInfo"]["unUsedTraffic"] if "unUsedTraffic" in result["trafficInfo"] else "无效key"
            push_title += "剩: " + un_used
            push_content = "剩余流量: " + un_used
        else:
            push_content = "签到过了."
        push_msg(skey, push_title, push_content)
    
    except Exception as e:
        print(e)
    finally:
        driver.quit()
