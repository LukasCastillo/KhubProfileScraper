import requests
import threading
from bs4 import BeautifulSoup

# add your current cookie session here
cookies = {'MoodleSession': '', 'MOODLEID1_': ''}

# gets the html data of the user from their id
def get_profile_html_from_id(id):
    return requests.get('https://khub.mc.pshs.edu.ph/user/profile.php?id=' + str(id) + '&showallcourses=1', cookies=cookies).text

users = []

# returns a user based on the id
def get_user(id):
    # object that holds the user
    user = {
        "id": id,
        "name": "",
        "courses": "",
        "pic": "",
        "desc": "",
        "email": "",
        "city": "",
    }
    try:
        # gets the html
        profile_html = get_profile_html_from_id(id)
        profile_soup = BeautifulSoup(profile_html, "html.parser")
        profile_div = profile_soup.find_all("div", class_="card-profile")[0]
        # gets name
        try: user['name'] = profile_div.find_all("h3")[0].text
        except: pass
        # gets pic link
        try: user['pic'] = profile_div.find_all("img")[0]['src']
        except: pass
        # get courses
        try:
            courses_list = profile_soup.find_all("dt", string="Course profiles")[0].parent.find_all("ul")[0].contents
            courses_str = ""
            for c in courses_list:
                courses_str += c.text + " && "
            user["courses"] = courses_str
        except: pass

        user_info_div = profile_div.find_all('div', class_='userinfo')[0]
        # gets description
        try: user['desc'] = user_info_div.find_all('div', class_="userdescription")[0].contents[0].contents[0].text
        except: pass
        info_list = user_info_div.find_all('ul')[0]
        # gets email
        try: user['email'] = info_list.find_all('dt', string="Email address:")[0].parent.find_all('a')[0].text
        except: pass
        # gets city
        try: user['city'] = info_list.find_all('dt', string="City/town:")[0].parent.find_all('dd')[0].text
        except: pass
    except:
        pass
    return user


def get_id(user):
    return user["id"]

# write the results to a file
def write_users_to_file():
    print("sorting list")
    users.sort(key=get_id)
    print("finished sorting list")
    file = open("data.csv", "w", encoding="utf-8")
    file.write("id,name,email,city,description,picture,courses\n")
    print("writing to file")
    for user in users:
        file.write(str(user["id"]) + "," + user["name"] + "," + user["email"] + "," + user["city"] + "," + user["desc"] + "," + user["pic"] + "," + user["courses"] + "\n")
    file.close()
    print("finished writing to file")

running = True
current_id = 0
lock = threading.Lock()

# main proc that runs get_user()
def proc():
    global running
    global current_id
    global lock
    while running:
        user = get_user(current_id)
        if not user["name"] == "":
            print("sucessfully got user: " + str(current_id))
        else: 
            print("could not get user: " + str(current_id))

        users.append(user)

        with lock:
            current_id += 1
        if current_id > 2800:
            print("max reached!")
            running = False

# threads to speedup stuff
threads = [threading.Thread(target=proc) for _ in range(6)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

write_users_to_file()
