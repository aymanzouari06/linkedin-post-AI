from groq import Groq
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime
import random
import csv
import os

class ContentGenerator:
    def __init__(self, groq_api_key):
        self.client = Groq(api_key=groq_api_key)
        
        # Topics for data analysis posts
        self.topics = [
            "SQL Query Optimization",
            "Python Data Analysis Libraries",
            "Data Visualization Techniques",
            "Statistical Analysis Methods",
            "Business Intelligence Tools",
            "Data Cleaning Best Practices",
            "Excel Advanced Analytics",
            "Machine Learning Applications",
            "Data Privacy and Ethics",
            "Data Storytelling Techniques",
            "ETL Best Practices",
            "Data Quality Frameworks",
            "Dashboard Design Principles",
            "Performance Optimization",
            "Real-world Case Studies"
        ]
        
        # Post types for variety
        self.post_types = [
            {"type": "How-to Guide", "emoji": "📚"},
            {"type": "Quick Tip", "emoji": "💡"},
            {"type": "Case Study", "emoji": "🔍"},
            {"type": "Tool Review", "emoji": "🛠️"},
            {"type": "Best Practice", "emoji": "✨"},
            {"type": "Common Mistakes", "emoji": "⚠️"},
            {"type": "Industry Trend", "emoji": "📈"}
        ]

    def generate_post(self, topic=None, post_type=None):
        """Generate a LinkedIn post using Groq with Llama 3"""
        if not topic:
            topic = random.choice(self.topics)
        if not post_type:
            post_type = random.choice(self.post_types)

        prompt = f"""
        Create a professional LinkedIn post about {topic} for data analysts.
        Post type: {post_type['type']}
        
        Requirements:
        - Start with {post_type['emoji']} and an attention-grabbing headline
        - Include practical, actionable insights
        - Keep it concise (max 200 words)
        - Add 2-3 relevant hashtags
        - End with an engaging question or call to action
        - Format with appropriate line breaks for LinkedIn
        - Focus on real-world applications
        - Include specific examples when possible
        
        Make it sound natural and conversational, not overly promotional.
        """

        try:
            completion = self.client.chat.completions.create(
                model="llama3-70b-4096",  # Using Llama 3 70B model
                messages=[
                    {"role": "system", "content": "You are a senior data analyst sharing professional insights on LinkedIn."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                top_p=0.9
            )
            
            return {
                'content': completion.choices[0].message.content.strip(),
                'topic': topic,
                'post_type': post_type['type']
            }
            
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return {
                'content': f"{post_type['emoji']} Daily {topic} Tip\n\nStay tuned for more insights!\n\n#DataAnalysis #{topic.replace(' ', '')}",
                'topic': topic,
                'post_type': post_type['type']
            }

class ContentCalendar:
    def __init__(self, generator):
        self.generator = generator
        self.calendar_file = 'content_calendar.csv'
        
    def generate_weekly_content(self, num_posts=5):
        """Generate a week's worth of content"""
        posts = []
        used_topics = set()
        
        for _ in range(num_posts):
            # Ensure topic variety
            available_topics = [t for t in self.generator.topics if t not in used_topics]
            if not available_topics:
                used_topics.clear()
                available_topics = self.generator.topics
                
            topic = random.choice(available_topics)
            used_topics.add(topic)
            
            post = self.generator.generate_post(topic=topic)
            posts.append(post)
            
            # Add small delay between generations
            time.sleep(1)
            
        return posts
    
    def save_calendar(self, posts):
        """Save generated content to CSV"""
        exists = os.path.exists(self.calendar_file)
        mode = 'a' if exists else 'w'
        
        with open(self.calendar_file, mode, newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not exists:
                writer.writerow(['Date', 'Topic', 'Type', 'Content', 'Status'])
            
            for post in posts:
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d'),
                    post['topic'],
                    post['post_type'],
                    post['content'],
                    'Draft'
                ])

class LinkedInAssistant:
    def __init__(self, groq_api_key):
        self.content_generator = ContentGenerator(groq_api_key)
        self.calendar = ContentCalendar(self.content_generator)
        
    def generate_content_suggestions(self, num_suggestions=3):
        """Generate multiple post suggestions for review"""
        return [self.content_generator.generate_post() for _ in range(num_suggestions)]
    
    def preview_post(self, post):
        """Preview how the post will look"""
        print("\n=== Post Preview ===")
        print(f"Topic: {post['topic']}")
        print(f"Type: {post['post_type']}")
        print("\nContent:")
        print(post['content'])
        print("===================\n")
    
    def create_weekly_calendar(self):
        """Generate and save a week's worth of content"""
        posts = self.calendar.generate_weekly_content()
        self.calendar.save_calendar(posts)
        return posts
    
    def review_posts(self, posts):
        """Interactive review of generated posts"""
        approved_posts = []
        
        for post in posts:
            self.preview_post(post)
            approval = input("Would you like to approve this post? (yes/no): ").lower()
            
            if approval == 'yes':
                approved_posts.append(post)
                print("Post approved!")
            else:
                print("Post skipped.")
            
            print("\n")
        
        return approved_posts

def main():
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Please create a config.json file with your Groq API key.")
        return

    assistant = LinkedInAssistant(config['groq_api_key'])
    
    while True:
        print("\nLinkedIn Content Assistant")
        print("1. Generate single post suggestion")
        print("2. Generate multiple post suggestions")
        print("3. Create weekly content calendar")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            post = assistant.content_generator.generate_post()
            assistant.preview_post(post)
            
        elif choice == '2':
            num = int(input("How many suggestions would you like? "))
            posts = assistant.generate_content_suggestions(num)
            approved = assistant.review_posts(posts)
            print(f"\nApproved {len(approved)} posts out of {num}")
            
        elif choice == '3':
            print("\nGenerating weekly content calendar...")
            posts = assistant.create_weekly_calendar()
            print(f"Generated {len(posts)} posts and saved to content_calendar.csv")
            
        elif choice == '4':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()