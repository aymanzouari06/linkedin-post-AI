from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import schedule
import openai
import json
from datetime import datetime
import random

class LinkedInPostGenerator:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        openai.api_key = self.openai_api_key
        
        # Topics for data analysis posts
        self.topics = [
            "SQL and Database Management",
            "Python for Data Analysis",
            "Data Visualization Best Practices",
            "Statistical Analysis Methods",
            "Business Intelligence Tools",
            "Data Cleaning Techniques",
            "Excel Advanced Features",
            "Machine Learning Basics",
            "Data Ethics and Privacy",
            "Data Storytelling",
            "ETL Processes",
            "Data Quality Assurance",
            "Dashboard Design",
            "Performance Optimization",
            "Data Analysis Case Studies"
        ]
        
        # Templates for post generation
        self.templates = [
            "Share a practical tip about {topic} that data analysts can immediately apply.",
            "Explain a common misconception about {topic} in data analysis.",
            "Provide a step-by-step guide for beginners about {topic}.",
            "Compare different approaches to {topic} and their trade-offs.",
            "Share a real-world example of how {topic} solved a business problem."
        ]

    def generate_post_content(self):
        """Generate post content using GPT"""
        topic = random.choice(self.topics)
        template = random.choice(self.templates)
        
        prompt = f"""
        Create a LinkedIn post about {topic} for a data analyst audience.
        Follow this template idea: {template.format(topic=topic)}
        
        Requirements:
        - Keep it professional and informative
        - Include practical insights
        - Add 2-3 relevant hashtags
        - Maximum 200 words
        - Use emojis appropriately
        - Include a call to action or question at the end
        - Format it for LinkedIn (use line breaks for readability)
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional data analyst sharing knowledge on LinkedIn."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            # Fallback content in case of API error
            return f"📊 Daily Data Analysis Tip: {topic}\n\nStay tuned for more insights!\n\n#DataAnalysis #{topic.replace(' ', '')}"

class LinkedInAutomation:
    def __init__(self, email, password, openai_api_key):
        self.email = email
        self.password = password
        self.driver = None
        self.post_generator = LinkedInPostGenerator(openai_api_key)
        
    def setup_driver(self):
        """Initialize and configure the webdriver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        self.driver = webdriver.Chrome(options=options)
    
    def login(self):
        """Login to LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            ).send_keys(self.email)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.driver.find_element(By.CSS_SELECTOR, "[type='submit']").click()
            time.sleep(5)  # Wait for login to complete
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def create_post(self):
        """Create and publish a post"""
        try:
            # Generate content using LLM
            content = self.post_generator.generate_post_content()
            
            # Click on 'Start a post' button
            start_post_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Start a post']"))
            )
            start_post_button.click()
            time.sleep(2)
            
            # Find post input area and enter content
            post_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
            )
            post_input.send_keys(content)
            time.sleep(2)
            
            # Click post button
            post_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Post']")
            post_button.click()
            time.sleep(3)
            
            # Log successful post
            print(f"Successfully posted at {datetime.now()}")
            print(f"Content:\n{content}\n")
            return True
            
        except Exception as e:
            print(f"Failed to create post: {str(e)}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

def daily_post(automation):
    """Function to handle daily posting"""
    try:
        automation.setup_driver()
        if automation.login():
            automation.create_post()
        automation.close()
    except Exception as e:
        print(f"Daily post failed: {str(e)}")
        automation.close()

def main():
    # Load configuration from file
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Please create a config.json file with your credentials.")
        return

    # Initialize automation with credentials
    automation = LinkedInAutomation(
        email=config['linkedin_email'],
        password=config['linkedin_password'],
        openai_api_key=config['openai_api_key']
    )
    
    # Schedule daily post (adjust time as needed)
    schedule.every().day.at("10:00").do(daily_post, automation)
    
    print("LinkedIn automation started. Posts will be created daily at 10:00 AM.")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()