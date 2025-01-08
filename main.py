from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.main_chat import MainChatScreen

import os
from kivy.lang import Builder

# Try to import android module
try:
    import android
except ImportError:
    android = None

# Load the common widgets and styles
Builder.load_file('kv/common.kv')

# Load individual screen layouts
Builder.load_file('kv/main_chat.kv')

class MainApp(App):
    def build(self):
        # Check if running on Android and request permissions
        if android:
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

        sm = ScreenManager()

        # Main chat screen
        main_chat_screen = MainChatScreen(name='main_chat')
        sm.add_widget(main_chat_screen)

        return sm

if __name__ == '__main__':
    MainApp().run()
