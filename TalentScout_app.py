import streamlit as st
import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any

class TalentScoutChatbot:
    def __init__(self):
        self.required_fields = [
            'full_name', 'email', 'phone', 'years_experience', 
            'desired_position', 'current_location', 'tech_stack'
        ]
        self.current_state = "greeting"
        self.candidate_data = {}
        self.conversation_history = []
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'candidate_data' not in st.session_state:
            st.session_state.candidate_data = {}
        if 'current_state' not in st.session_state:
            st.session_state.current_state = "greeting"
        if 'tech_questions' not in st.session_state:
            st.session_state.tech_questions = []
        if 'collected_fields' not in st.session_state:
            st.session_state.collected_fields = set()
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0
        if 'candidate_answers' not in st.session_state:
            st.session_state.candidate_answers = {}
        if 'current_tech_index' not in st.session_state:
            st.session_state.current_tech_index = 0
    
    def get_greeting(self) -> str:
        """Return warm greeting message"""
        return """👋 Hello! I'm TalentScout, your AI Hiring Assistant.

I'm here to help streamline your application process by collecting your information and generating relevant technical questions.

Let's start with some basic information about you!"""

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove common separators and check for digits
        cleaned_phone = re.sub(r'[\s\-\(\)\+]', '', phone)
        return cleaned_phone.isdigit() and len(cleaned_phone) >= 10
    
    def mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data before saving"""
        masked_data = data.copy()
        
        if 'email' in masked_data:
            email_parts = masked_data['email'].split('@')
            if len(email_parts) == 2:
                username = email_parts[0]
                if len(username) > 2:
                    masked_username = username[0] + '*' * (len(username)-2) + username[-1]
                else:
                    masked_username = '*' * len(username)
                masked_data['email'] = f"{masked_username}@{email_parts[1]}"
        
        if 'phone' in masked_data:
            phone = masked_data['phone']
            if len(phone) > 4:
                masked_data['phone'] = '*' * (len(phone)-4) + phone[-4:]
            else:
                masked_data['phone'] = '*' * len(phone)
                
        return masked_data
    
    def save_candidate_data(self):
        """Save candidate data to simulated JSON database"""
        if st.session_state.candidate_data:
            # Combine all data including answers
            complete_data = {
                **st.session_state.candidate_data,
                'technical_answers': st.session_state.candidate_answers,
                'timestamp': datetime.now().isoformat()
            }
            
            masked_data = self.mask_sensitive_data(complete_data)
            
            # Simulated database - in production, this would connect to a real database
            try:
                if os.path.exists('simulated_candidates.json'):
                    with open('simulated_candidates.json', 'r') as f:
                        existing_data = json.load(f)
                else:
                    existing_data = []
                
                existing_data.append(masked_data)
                
                with open('simulated_candidates.json', 'w') as f:
                    json.dump(existing_data, f, indent=2)
                    
            except Exception as e:
                st.error(f"Error saving data: {e}")
    
    def generate_tech_questions(self, tech_stack: List[str]) -> List[Dict[str, Any]]:
        """Generate technical questions for each technology in the stack"""
        questions = []
        
        # Technology-specific question templates
        tech_question_templates = {
            'python': [
                "What are the key differences between lists and tuples in Python?",
                "How does Python handle memory management?",
                "Explain the concept of decorators in Python with an example.",
                "What is the Global Interpreter Lock (GIL) and how does it affect multithreading?",
                "CODING TASK (Optional): Write a function to reverse a string without using built-in reverse methods."
            ],
            'javascript': [
                "What is the difference between let, const, and var?",
                "Explain the concept of closures in JavaScript.",
                "How does the event loop work in JavaScript?",
                "What are promises and how do they differ from callbacks?",
                "CODING TASK (Optional): Implement a debounce function from scratch."
            ],
            'java': [
                "What is the difference between abstract classes and interfaces?",
                "Explain the concept of polymorphism in Java.",
                "How does garbage collection work in Java?",
                "What are the main principles of OOP and how does Java implement them?",
                "CODING TASK (Optional): Write a thread-safe singleton class implementation."
            ],
            'react': [
                "What is the virtual DOM and how does it improve performance?",
                "Explain the difference between state and props.",
                "What are React hooks and when would you use them?",
                "How does React handle component lifecycle?",
                "CODING TASK (Optional): Create a custom hook for handling API calls."
            ],
            'sql': [
                "What is the difference between INNER JOIN and LEFT JOIN?",
                "Explain database normalization with examples.",
                "What are indexes and how do they improve query performance?",
                "How would you handle database transactions?",
                "CODING TASK (Optional): Write a query to find the second highest salary from an employees table."
            ],
            'aws': [
                "What is the difference between EC2 and Lambda?",
                "Explain the shared responsibility model in AWS.",
                "How would you design a highly available architecture?",
                "What are the main security best practices in AWS?",
                "CODING TASK (Optional): Write a CloudFormation template for a basic S3 bucket."
            ]
        }
        
        for tech in tech_stack:
            tech_lower = tech.strip().lower()
            if tech_lower in tech_question_templates:
                questions.append({
                    'technology': tech,
                    'questions': tech_question_templates[tech_lower]
                })
            else:
                # Generic questions for unknown technologies
                questions.append({
                    'technology': tech,
                    'questions': [
                        f"What are the main features and advantages of {tech}?",
                        f"Describe a challenging project you've worked on using {tech}.",
                        f"What are the best practices for working with {tech}?",
                        f"How does {tech} handle scalability and performance?",
                        f"CODING TASK (Optional): Describe how you would implement a basic feature using {tech}."
                    ]
                })
        
        return questions
    
    def get_current_question(self):
        """Get the current question being asked"""
        if (st.session_state.tech_questions and 
            st.session_state.current_tech_index < len(st.session_state.tech_questions)):
            
            tech_qa = st.session_state.tech_questions[st.session_state.current_tech_index]
            
            if st.session_state.current_question_index < len(tech_qa['questions']):
                return {
                    'technology': tech_qa['technology'],
                    'question': tech_qa['questions'][st.session_state.current_question_index],
                    'question_number': st.session_state.current_question_index + 1,
                    'total_questions': len(tech_qa['questions'])
                }
        
        return None
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and return appropriate response"""
        user_input_lower = user_input.lower().strip()
        
        # Check for exit keywords
        exit_keywords = ['exit', 'quit', 'bye', 'thank you', 'thanks', 'goodbye']
        if any(keyword in user_input_lower for keyword in exit_keywords):
            if st.session_state.candidate_data:
                self.save_candidate_data()
            return "Thank you for your time! Your information and answers have been saved. We'll be in touch soon. Goodbye! 👋"
        
        current_state = st.session_state.current_state
        
        if current_state == "greeting":
            st.session_state.current_state = "collecting_info"
            return "Great! Let's start with your full name:"
        
        elif current_state == "collecting_info":
            collected_fields = st.session_state.collected_fields
            
            if 'full_name' not in collected_fields:
                st.session_state.candidate_data['full_name'] = user_input
                st.session_state.collected_fields.add('full_name')
                return "Thanks! What's your email address?"
            
            elif 'email' not in collected_fields:
                if self.validate_email(user_input):
                    st.session_state.candidate_data['email'] = user_input
                    st.session_state.collected_fields.add('email')
                    return "Perfect! What's your phone number?"
                else:
                    return "That doesn't look like a valid email format. Please enter a valid email address:"
            
            elif 'phone' not in collected_fields:
                if self.validate_phone(user_input):
                    st.session_state.candidate_data['phone'] = user_input
                    st.session_state.collected_fields.add('phone')
                    return "Great! How many years of professional experience do you have?"
                else:
                    return "Please enter a valid phone number (at least 10 digits):"
            
            elif 'years_experience' not in collected_fields:
                if user_input.isdigit() and 0 <= int(user_input) <= 50:
                    st.session_state.candidate_data['years_experience'] = user_input
                    st.session_state.collected_fields.add('years_experience')
                    return "What position(s) are you interested in?"
                else:
                    return "Please enter a valid number of years (0-50):"
            
            elif 'desired_position' not in collected_fields:
                st.session_state.candidate_data['desired_position'] = user_input
                st.session_state.collected_fields.add('desired_position')
                return "What's your current location?"
            
            elif 'current_location' not in collected_fields:
                st.session_state.candidate_data['current_location'] = user_input
                st.session_state.collected_fields.add('current_location')
                return "Almost done! Please list your tech stack (comma-separated, e.g., Python, JavaScript, React):"
            
            elif 'tech_stack' not in collected_fields:
                tech_list = [tech.strip() for tech in user_input.split(',') if tech.strip()]
                if tech_list:
                    st.session_state.candidate_data['tech_stack'] = tech_list
                    st.session_state.collected_fields.add('tech_stack')
                    
                    # Generate technical questions
                    st.session_state.tech_questions = self.generate_tech_questions(tech_list)
                    st.session_state.current_state = "asking_questions"
                    st.session_state.current_tech_index = 0
                    st.session_state.current_question_index = 0
                    
                    # Start asking questions
                    current_question = self.get_current_question()
                    if current_question:
                        return f"Excellent! Now let's go through some technical questions.\n\n**{current_question['technology']} - Question {current_question['question_number']}/{current_question['total_questions']}:**\n{current_question['question']}\n\nPlease provide your answer:"
                    else:
                        st.session_state.current_state = "completed"
                        return "No questions generated. Type 'exit' to end the conversation."
                else:
                    return "Please provide at least one technology in your tech stack (comma-separated):"
        
        elif current_state == "asking_questions":
            # Store the answer
            current_question = self.get_current_question()
            if current_question:
                tech = current_question['technology']
                question = current_question['question']
                
                # Initialize answers dictionary for this technology if not exists
                if tech not in st.session_state.candidate_answers:
                    st.session_state.candidate_answers[tech] = {}
                
                # Store the answer
                st.session_state.candidate_answers[tech][f"Q{current_question['question_number']}"] = {
                    'question': question,
                    'answer': user_input
                }
                
                # Move to next question
                st.session_state.current_question_index += 1
                
                # Check if we've finished questions for current technology
                if st.session_state.current_question_index >= len(st.session_state.tech_questions[st.session_state.current_tech_index]['questions']):
                    st.session_state.current_tech_index += 1
                    st.session_state.current_question_index = 0
                
                # Get next question
                next_question = self.get_current_question()
                if next_question:
                    return f"Thank you for your answer! \n\n**{next_question['technology']} - Question {next_question['question_number']}/{next_question['total_questions']}:**\n{next_question['question']}\n\nPlease provide your answer:"
                else:
                    # All questions completed
                    st.session_state.current_state = "completed"
                    self.save_candidate_data()
                    return "🎉 Fantastic! You've completed all technical questions. Your answers have been saved. Type 'exit' to end the conversation or ask any other questions."
            
            else:
                st.session_state.current_state = "completed"
                return "No more questions available. Type 'exit' to end the conversation."
        
        # Fallback for any other input
        return "I didn't understand that. Can you clarify?"

def main():
    st.set_page_config(
        page_title="TalentScout Hiring Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize chatbot
    chatbot = TalentScoutChatbot()
    chatbot.initialize_session_state()
    
    # Sidebar for settings
    with st.sidebar:
        st.title("⚙️ Settings")
        st.subheader("API Configuration")
        api_key = st.text_input("LLM API Key (Optional)", type="password", 
                               help="For enhanced question generation")
        st.divider()
        st.subheader("Conversation Info")
        st.write(f"Status: {st.session_state.current_state}")
        st.write(f"Fields collected: {len(st.session_state.collected_fields)}/7")
        
        if st.session_state.tech_questions:
            total_questions = sum(len(tech['questions']) for tech in st.session_state.tech_questions)
            answered_questions = len(st.session_state.candidate_answers)
            st.write(f"Questions answered: {answered_questions}/{total_questions}")
        
        if st.button("Reset Conversation"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content area
    st.title("🤖 TalentScout Hiring Assistant")
    st.markdown("""
    Welcome to the AI-powered hiring assistant! I'll help collect your information 
    and generate relevant technical questions for your screening process.
    """)
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'assistant':
                st.chat_message("assistant").markdown(message['content'])
            else:
                st.chat_message("user").markdown(message['content'])
    
    # User input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        
        # Process input and get response
        response = chatbot.process_user_input(user_input)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        
        # Rerun to update the display
        st.rerun()
    
    # Display technical questions and answers
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.tech_questions:
            with st.expander("📋 Generated Technical Questions", expanded=True):
                for i, tech_qa in enumerate(st.session_state.tech_questions):
                    st.subheader(f"**{tech_qa['technology']}**")
                    for j, question in enumerate(tech_qa['questions'], 1):
                        status = "✅" if (tech_qa['technology'] in st.session_state.candidate_answers and 
                                        f"Q{j}" in st.session_state.candidate_answers[tech_qa['technology']]) else "⏳"
                        st.write(f"{status} {j}. {question}")
                    st.divider()
    
    with col2:
        if st.session_state.candidate_answers:
            with st.expander("📝 Candidate Answers", expanded=True):
                for tech, answers in st.session_state.candidate_answers.items():
                    st.subheader(f"**{tech}**")
                    for q_key, qa in answers.items():
                        st.write(f"**{q_key}: {qa['question']}**")
                        st.write(f"*Answer:* {qa['answer']}")
                        st.divider()
    
    # Display collected candidate data (for demo purposes)
    if st.session_state.candidate_data:
        with st.expander("👤 Collected Candidate Information", expanded=False):
            st.json(st.session_state.candidate_data)

if __name__ == "__main__":
    main()