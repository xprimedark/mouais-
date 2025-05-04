import threading
from bot import start_bot
from app import start_flask

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask)
    bot_thread = threading.Thread(target=start_bot)

    flask_thread.start()
    bot_thread.start()

    flask_thread.join()
    bot_thread.join()
