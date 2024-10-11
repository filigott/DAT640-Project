from dialoguekit.platforms import FlaskSocketPlatform
from music_agent import MusicAgent

def chat_bot():
    platform = FlaskSocketPlatform(MusicAgent)
    platform.start()

if __name__ == '__main__':
    chat_bot()