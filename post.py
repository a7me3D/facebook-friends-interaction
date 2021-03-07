from lxml import html
import time
from dateparser import parse as date_parser

class Post():
    def __init__(self, post_url, driver):
        self.post_url = post_url
        self.driver = driver
        #TODO: validate post url
        self.driver.get(post_url)
        self.reaction_count = self.get_reaction_count(driver)
        if self.reaction_count>0:
            try:
                self.date = self.get_date()
                driver.find_element_by_xpath("//a[contains(@href,'reaction/profile')]").click() # Enter reactions list page
                self.get_all_users_page()
                self.users = self.get_users_list()
            except Exception as e:
                print(e)
                print(f"Cannot retrieve info from :{post_url}")
                self.reaction_count = 0
                pass


    def get_reaction_count(self, driver):
        reaction_count = self.driver.find_elements_by_xpath('//a[contains(@href,"reaction/profile")][1]/div/div')
        if len(reaction_count) == 0:
            return 0
        else:
            try:
                return ([int(s) for s in reaction_count[0].text.split() if s.isdigit()][0]+1)
            except:
                return len(reaction_count[0].text.split("and"))
    

    def get_all_users_page(self):
        try:
            self.driver.find_element_by_xpath("//a[contains(text(),'All')]").click()
        except:
            self.driver.find_element_by_xpath("//a[contains(@href,'fetch/?limit')]").click()
        
        url =  self.driver.current_url
        #Silly wait until next page (kill me pls)
        timeout=10 #timeout if things went really wrong
        while timeout>0 and( "?limit" not in url):
            time.sleep(1)
            timeout-=1
            url =  self.driver.current_url #maybe this time
            #click worked???? one more time
            if timeout==5:
                try:
                    self.driver.find_element_by_xpath("//a[contains(text(),'All')]").click()
                except:
                    self.driver.find_element_by_xpath("//a[contains(@href,'fetch/?limit')]").click()
            


        #generate url that shows all reactors (avoid "see more")
        url_p1 = url.split("?limit=")[0]
        url_p2 = "&".join(url.split("?limit=")[1].split("&")[1:])
        url = url_p1 + "?limit=" + str(self.reaction_count) + "&" + url_p2

        self.driver.get(url)
        time.sleep(1)
        return True
    
    def get_users_list(self):
        tree = html.fromstring(self.driver.page_source)
        users_table_xpath = "//table//li"

        for user_count in range(0,self.reaction_count):
            user_xpath = f"{users_table_xpath}{[user_count + 1]}/table/tbody/tr/td[@class]/table/tbody/tr/td[3]//a"
            try:
                user = tree.xpath(user_xpath)[0]
                yield {"user_name":user.text, "user_url":user.attrib['href'] }
            except:
                pass #avoid taksir rass

    def get_date(self):
        date=self.driver.find_element_by_xpath("//abbr") 
        init_date=date.text
        try:
            date = str(date_parser(init_date)).split()[0]
            return date
        except:
            return init_date