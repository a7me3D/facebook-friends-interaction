from datetime import datetime, timedelta
from lxml import html
import time


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
                time.sleep(2)
                self.get_all_users_page()
                self.date = self.date_parser(self.date)
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

        #generate url that shows all reactors (avoid "see more")
        url =  self.driver.current_url
        url_p1 = url.split("?limit=")[0]
        url_p2 = "&".join(url.split("?limit=")[1].split("&")[1:])
        url = url_p1 + "?limit=" + str(self.reaction_count) + "&" + url_p2
        self.driver.get(url)
        return True
    
    def get_users_list(self):
        users = []
        tree = html.fromstring(self.driver.page_source)
        users_table_xpath = "//table//li"
        users_table = tree.xpath(users_table_xpath)

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
        return init_date
    
    def date_parser(self, date):
        init_date=date
        """
        Ref: https://github.com/rugantio/fbcrawl/blob/bda7d6a7da49a57c8a0863b6679c013f74fdb4c1/fbcrawl/items.py#L330
        """
        months = {
            'january':1,
            'february':2,
            'march':3,
            'april':4,
            'may':5,
            'june':6,
            'july':7,
            'august':8,
            'september':9,
            'october':10,
            'november':11,
            'december':12
        }

        months_abbr = {
            'jan':1,
            'feb':2,
            'mar':3,
            'apr':4,
            'may':5,
            'jun':6,
            'jul':7,
            'aug':8,
            'sep':9,
            'oct':10,
            'nov':11,
            'dec':12
        }

        days = {
            'monday':0,
            'tuesday':1,
            'wednesday':2,
            'thursday':3,
            'friday':4,
            'saturday':5,
            'sunday':6
        }

        date = init_date.split()

        #Quick fix 24h -> 12h 
        if ('at' in date and date[-1].lower() not in ["am", "pm"] ):
            date.append(" ")

        year, month, day = [int(i) for i in str(datetime.now().date()).split(sep='-')] #default is today
        l = len(date)
        #sanity check
        if l == 0:
            return 'Error: no data'
        #Yesterday, Now, 4hr, 50mins
        elif l == 1:
            if date[0].isalpha():
                if date[0].lower() == 'yesterday':
                    day = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[2])
                    #check that yesterday was not in another month
                    month = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[1])
                elif date[0].lower() == 'now':
                        return datetime(year,month,day).date()    #return today
                else:  #not recognized, (return date or init_date)
                    return date
            else:
                #4h, 50min (exploit future parsing)
                l = 2
                new_date = [x for x in date[0] if x.isdigit()]
                date[0] = ''.join(new_date)
                new_date = [x for x in date[0] if not(x.isdigit())]
                date[1] = ''.join(new_date)
        # l = 2
        elif l == 2:
            if date[1] == 'now':
                return datetime(year,month,day).date()
            #22 min (yesterday)
            if date[1] == 'min' or date[1] == 'mins':
                if int(str(datetime.now().time()).split(sep=':')[1]) - int(date[0]) < 0 and int(str(datetime.now().time()).split(sep=':')[0])==0:
                    day = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[2])
                    month = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[1])
                    return datetime(year,month,day).date()
                #22 min (today)
                else:
                    return datetime(year,month,day).date()

            #4 h (yesterday)
            elif date[1] == 'hr' or date[1] == 'hrs':
                if int(str(datetime.now().time()).split(sep=':')[0]) - int(date[0]) < 0:
                    day = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[2])
                    month = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[1])
                    print(datetime(year,month,day).date())
                #4 h (today)
                else:
                    print(datetime(year,month,day).date())

            #2 jan
            elif len(date[1]) == 3 and date[1].isalpha():
                day = int(date[0])
                month = months_abbr[date[1].lower()]
                return datetime(year,month,day).date()
            #2 january
            elif len(date[1]) > 3 and date[1].isalpha():
                day = int(date[0])
                month = months[date[1]]
                return datetime(year,month,day).date()
            #jan 2
            elif len(date[0]) == 3 and date[0].isalpha():
                day = int(date[1])
                month = months_abbr[date[0].lower()]
                return datetime(year,month,day).date()
            #january 2
            elif len(date[0]) > 3 and date[0].isalpha():
                day = int(date[1])
                month = months[date[0]]
                return datetime(year,month,day).date()
            #parsing failed
            else:
                return date
            return date
        # l = 3
        elif l == 3:
            #5 hours ago
            if date[2] == 'ago':
                if date[1] == 'hour' or date[1] == 'hours' or date[1] == 'hr' or date[1] == 'hrs':
                    # 5 hours ago (yesterday)
                    if int(str(datetime.now().time()).split(sep=':')[0]) - int(date[0]) < 0:
                        day = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[2])
                        month = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[1])
                        return datetime(year,month,day).date()
                    # 5 hours ago (today)
                    else:
                        return datetime(year,month,day).date()
                #10 minutes ago
                elif date[1] == 'minute' or date[1] == 'minutes' or date[1] == 'min' or date[1] == 'mins':
                    #22 minutes ago (yesterday)
                    if int(str(datetime.now().time()).split(sep=':')[1]) - int(date[0]) < 0 and int(str(datetime.now().time()).split(sep=':')[0])==0:
                        day = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[2])
                        month = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[1])
                        return datetime(year,month,day).date()
                    #22 minutes ago (today)
                    else:
                        return datetime(year,month,day).date()
                else:
                    return date
            else:
                #21 Jun 2017
                if len(date[1]) == 3 and date[1].isalpha() and date[2].isdigit():
                    day = int(date[0])
                    month = months_abbr[date[1].lower()]
                    year = int(date[2])
                    return datetime(year,month,day).date()
                #21 June 2017
                elif len(date[1]) > 3 and date[1].isalpha() and date[2].isdigit():
                    day = int(date[0])
                    month = months[date[1].lower()]
                    year = int(date[2])
                    return datetime(year,month,day).date()
                #Jul 11, 2016
                elif len(date[0]) == 3 and len(date[1]) == 3 and date[0].isalpha():
                    day = int(date[1][:-1])
                    month = months_abbr[date[0].lower()]
                    year = int(date[2])
                    return datetime(year,month,day).date()
                #parsing failed
                else:
                    return date
        # l = 4
        elif l == 4:
            #yesterday at 23:32 PM
            if date[0].lower() == 'yesterday' and date[1] == 'at':
                day = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[2])
                month = int(str(datetime.now().date()-timedelta(1)).split(sep='-')[1])
                return datetime(year,month,day).date()
            #Thursday at 4:27 PM
            elif date[1] == 'at':
                today = datetime.now().weekday() #today as a weekday
                weekday = days[date[0].lower()]   #day to be match as number weekday
                #weekday is chronologically always lower than day
                delta = today - weekday
                if delta >= 0:
                    day = int(str(datetime.now().date()-timedelta(delta)).split(sep='-')[2])
                    month = int(str(datetime.now().date()-timedelta(delta)).split(sep='-')[1])
                    return datetime(year,month,day).date()
                #monday = 0 saturday = 6
                else:
                    delta += 8
                    day = int(str(datetime.now().date()-timedelta(delta)).split(sep='-')[2])
                    month = int(str(datetime.now().date()-timedelta(delta)).split(sep='-')[1])
                    return datetime(year,month,day).date()
            #parsing failed
            else:
                return date
        # l = 5
        elif l == 5:
            if date[2] == 'at':
                #Jan 29 at 10:00 PM
                if len(date[0]) == 3:
                    day = int(date[1])
                    month = months_abbr[date[0].lower()]
                    return datetime(year,month,day).date()
                #29 february at 21:49
                else:
                    day = int(date[1])
                    month = months[date[0].lower()]
                    return datetime(year,month,day).date()
            #parsing failed
            else:
                return date
        # l = 6
        elif l == 6:
            if date[3] == 'at':
                date[1]
                #Aug 25, 2016 at 7:00 PM
                if len(date[0]) == 3:
                    day = int(date[1][:-1])
                    month = months_abbr[date[0].lower()]
                    year = int(date[2])
                    return datetime(year,month,day).date()
                #August 25, 2016 at 7:00 PM
                else:
                    day = int(date[1][:-1])
                    month = months[date[0].lower()]
                    year = int(date[2])
                    return datetime(year,month,day).date()
            #parsing failed
            else:
                return date
        # l > 6
        #parsing failed - l too big
        else:
            return date
   

#TODO: users_list format user interaction over time