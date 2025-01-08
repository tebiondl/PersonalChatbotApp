import json
import requests
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from datetime import datetime
import os

from huggingface_hub import InferenceClient
from dotenv import load_dotenv
load_dotenv()

class MainChatScreen(Screen):
    chat_history_container = ObjectProperty(None)
    message_input = ObjectProperty(None)
    chat_area = ObjectProperty(None)
    chat_history = ObjectProperty(None)
    current_chat_id = None
    send_button = ObjectProperty(None)

    def toggle_chat_history(self):
        if self.chat_history_container.size_hint_x == 0:
            self.chat_history_container.size_hint_x = 0.3
        else:
            self.chat_history_container.size_hint_x = 0

    def send_message(self):
        message = self.message_input.text
        if message:
            # Add message to chat area
            self.chat_area.add_widget(Label(text=message, size_hint_y=None, height=40))
            self.message_input.text = ''
            # Save current chat
            self.save_current_chat()
            # Call Hugging Face API
            self.call_hugging_face_api(message)

    def new_chat(self):
        # Save current chat to history if not empty
        if self.chat_area.children:
            self.save_current_chat()
        # Clear the chat area for a new chat
        self.chat_area.clear_widgets()
        self.current_chat_id = None

    def save_current_chat(self):
        chat_content = []
        for widget in self.chat_area.children:
            if isinstance(widget, Label):
                chat_content.append(widget.text)
        if chat_content:
            chat_data = {
                'id': self.current_chat_id or datetime.now().timestamp(),
                'timestamp': datetime.now().isoformat(),
                'messages': chat_content
            }
            self.current_chat_id = chat_data['id']
            self.update_chat_history(chat_data)

    def update_chat_history(self, chat_data):
        chat_history = self.load_all_chats()
        chat_history[chat_data['id']] = chat_data
        with open('chat_history.json', 'w') as f:
            json.dump(chat_history, f)
        self.refresh_chat_history()

    def load_all_chats(self):
        if os.path.exists('chat_history.json'):
            with open('chat_history.json', 'r') as f:
                return json.load(f)
        return {}

    def refresh_chat_history(self):
        self.chat_history.clear_widgets()
        chat_history = self.load_all_chats()
        for chat_id, chat_data in chat_history.items():
            self.add_chat_to_history(chat_data)

    def add_chat_to_history(self, chat_data):
        button = Button(text=chat_data['timestamp'], size_hint_y=None, height=40)
        button.bind(on_press=lambda x: self.load_chat(chat_data))
        self.chat_history.add_widget(button)

    def load_chat(self, chat_data):
        self.chat_area.clear_widgets()
        self.current_chat_id = chat_data['id']
        for message in chat_data['messages']:
            self.chat_area.add_widget(Label(text=message, size_hint_y=None, height=40))

    def call_hugging_face_api(self, message):
        self.send_button.disabled = True
        client = InferenceClient(token=os.getenv("HUGGING_FACE_API_KEY"))
        
        messages = [
            {
                "role": "user",
                "content": message
            }
        ]

        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.2-3B-Instruct", 
            messages=messages,
            max_tokens=500
        )

        response_message = completion.choices[0].message.content
        
        self.chat_area.add_widget(Label(text=response_message, size_hint_y=None, height=40))
        self.save_current_chat()
        self.send_button.disabled = False