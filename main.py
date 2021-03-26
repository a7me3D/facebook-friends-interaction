from post import Post
from plot import Plot
from server import Server
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json, time, os, argparse, getpass
from sys import exit
from lxml import html

MFACEBOOK_URL="https://m.facebook.com/"
profile_url="https://mbasic.facebook.com/me"

DRIVER_NAME="chromedriver.exe"
DRIVER_DIR=os.path.join(os.getcwd(),DRIVER_NAME)
print("driver",DRIVER_DIR)
#element load timeout
TIMEOUT = 5


def setup_driver(dir_driver):
    #webdriver options and config        

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--log-level=3")

    # chrome_options.add_argument("--headless")

    #Add headers
    # for header in headers:
    #     chrome_options.add_argument(f"{header}={headers[header]}")
    
    driver = webdriver.Chrome(options=chrome_options)

    return driver

def signin(driver):
    
    fb_login = input('enter your fb login: ') 
    fb_pass = getpass.getpass(prompt='enter your fb password: ') 
    
    driver.get(MFACEBOOK_URL)
    
    #Wait for inputs
    WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, 'm_login_email')))
    WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, 'm_login_password')))
    WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.NAME, 'login')))


    email_id = driver.find_element_by_id("m_login_email")
    pass_id = driver.find_element_by_id("m_login_password")
    confirm_id = driver.find_element_by_name("login")
    
    email_id.send_keys(fb_login)
    pass_id.send_keys(fb_pass)
    confirm_id.click()
    
    print("Logging in automatically...")

    time.sleep(5)
    if "Log" in driver.title:
        print("Login failed pls check your credentials and retry")
        driver.close()
        exit()
        return False

    return True


def get_urls_and_save(driver, profile_url, nbPages):
	driver.get(profile_url)
	#loads new page
	no_exception=True
	pageCount=0

	while (no_exception and ((pageCount < nbPages) or nbPages == 0)):
		try:
			next_page=driver.find_element_by_xpath("//*[contains(text(), 'See More Stories')]")
			append_urls()
			next_page.click()
			pageCount+=1
		except Exception as e :
			no_exception=False
        # time.sleep(2)

def append_urls():
	global posts
	posts_page=driver.find_elements_by_xpath("//*[contains(text(), 'Full Story')]")
	for post in posts_page :
			url=post.get_attribute('href')
			posts.append(url)


#init containers
posts = []
data = {"dates":set(), "users":{}}
users = data["users"]
dates = data["dates"]

if "__main__" == __name__ :

    args = argparse.ArgumentParser()
    args.add_argument("--update", action="store_true", help="Crawl users interactions ")
    args.add_argument('--pages', nargs='?', type=int, default=0)
    args = args.parse_args()
    
    #get nb of pages and validate
    nbPages = args.pages 
    if nbPages<0:
        print("number of pages should be > 0")
        exit()

    driver = setup_driver(DRIVER_DIR)
    
    if args.update:
        signin(driver)
        get_urls_and_save(driver, profile_url, nbPages)
        for url in posts:
            post=Post(url, driver)
            #append commentators
            post_date = str(post.date) 
            for commentator in post.commentators:
                try:
                    #if user exists
                    users[commentator["user_name"]]
                except :
                    users.update({commentator["user_name"]:[]})
                
                users[commentator["user_name"]].append(post_date)
            
            if post.reaction_count>0:
                dates.add(post_date)
                #append reactors
                for reactor in post.reactors:
                    try:
                        #if user exists
                        users[reactor["user_name"]]
                    except :
                        users.update({reactor["user_name"]:[]})
                    
                    users[reactor["user_name"]].append(post_date)


        data["dates"] = list(data["dates"]) #Serialize set
        with open("data.json", "w", encoding='utf-8') as outfile:  
            json.dump(data, outfile, ensure_ascii=False) 

    server = Server(9000)
    threading.Thread(target=server.start).start()

    driver.get("http://localhost:9000/chart.html")
    driver.maximize_window()
    # fig=Plot("data.json")
    # fig.plot_interactions_over_time()