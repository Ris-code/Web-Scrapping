from dotenv import load_dotenv
from os import getenv
import json
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()
email = getenv('email')
password = getenv('password')
linkedin_url = 'https://www.linkedin.com/in/rishav-aich-ba88a7228/'

def login_to_linkedin(driver, email, password):
    driver.get('https://www.linkedin.com/login')
    try:
        wait = WebDriverWait(driver, 10)
        driver.find_element(By.ID, 'username').send_keys(email)
        driver.find_element(By.ID, 'password').send_keys(password)
        driver.find_element(By.ID, 'password').send_keys(Keys.RETURN)
        wait.until(EC.url_to_be('https://www.linkedin.com/feed/'))
        return True
    except Exception as e:
        print(f'Invalid Credentials. {str(e)}')
        return False

def scrape_profile_data(driver, linkedin_url):
    try:
        wait = WebDriverWait(driver, 10)
        driver.get(linkedin_url)
        check = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'profile-photo-edit__preview')))

        profile_image = driver.find_element(By.CLASS_NAME, 'profile-photo-edit__preview').get_attribute('src')
        name = driver.find_element(By.CLASS_NAME, 'text-heading-xlarge.inline.t-24.v-align-middle.break-words').text.strip()

        driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
        check = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'mn-connections__header')))
        connections_element = driver.find_element(By.CLASS_NAME, 'mn-connections__header')
        connections = connections_element.find_element(By.CLASS_NAME, 't-18.t-black.t-normal').text.strip()
        connections = int(connections.split()[0].replace(',', ''))
        
        driver.get(linkedin_url)
        check = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'display-flex.ph5.pv3')))
        summary = driver.find_element(By.CLASS_NAME, 'display-flex.ph5.pv3').text.strip()

        driver.get(linkedin_url + 'details/education/')
        date_pattern = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4})'
        check = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pvs-list')))
        education_items = driver.find_element(By.CLASS_NAME, 'pvs-list').find_elements(By.CLASS_NAME, 'pvs-entity')
        education = []

        for item in education_items:
            institution_element = item.find_element(By.CLASS_NAME, "display-flex.align-items-center.mr1.hoverable-link-text.t-bold")
            institution = institution_element.find_element(By.CLASS_NAME, "visually-hidden").text
            degree_element = item.find_element(By.CLASS_NAME, "t-14.t-normal")
            degree = degree_element.find_element(By.CLASS_NAME, "visually-hidden").text
            find_dates = re.findall(date_pattern, degree)
            
            if find_dates:
                degree = 'None'
            date_element = item.find_element(By.CLASS_NAME, "t-14.t-normal.t-black--light")
            date = date_element.find_element(By.CLASS_NAME, "visually-hidden").text
            graduation_dates = re.findall(date_pattern, date)
            
            if graduation_dates:
                graduation_date = graduation_dates[-1]
            else:
                graduation_date = 'None'

            education.append({
                'Institution Name': institution,
                'Degree': degree,
                'Graduation Date': graduation_date
            })

        driver.get(linkedin_url + 'details/skills/')
        check = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pvs-list')))
        skill_items = driver.find_element(By.CLASS_NAME, 'pvs-list').find_elements(By.CLASS_NAME, 'pvs-entity')
        skills = []

        for item in skill_items:
            skill_element = item.find_element(By.CLASS_NAME, "display-flex.align-items-center.mr1.hoverable-link-text.t-bold")
            skill = skill_element.find_element(By.CLASS_NAME, "visually-hidden").text
            skills.append(skill)

        return {
            'Profile Picture URL': profile_image,
            'Name': name,
            'Connections': connections,
            'Summary': summary,
            'Education': education,
            'Skills': skills,
        }
    
    except Exception as e:
        print(f'An error occurred: {str(e)}')
        return None

def save_to_json(data, filename='linkedin_profile.json'):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f'Data saved to {filename}')

if __name__ == "__main__":
    gecko = webdriver.Firefox()

    if login_to_linkedin(gecko, email, password):
        profile_data = scrape_profile_data(gecko, linkedin_url)
        if profile_data:
            save_to_json(profile_data)

    gecko.quit()
