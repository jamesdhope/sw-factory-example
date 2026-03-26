# interface.py

class UserInterface:
    def __init__(self):
        self.history = []

    def display_message(self, message):
        print(f"Message: {message}")
        self.history.append(message)

    def get_user_input(self):
        user_input = input("You: ")
        self.history.append(user_input)
        return user_input

    def start_conversation(self):
        print("Starting conversation...")
        while True:
            reply = self.get_user_input()
            if reply.lower().strip() == "exit":
                print("Conversation ended.")
                break
            self.process_reply(reply)

    def process_reply(self, reply):
        # This function can be expanded for processing logic
        print(f"Processing reply: {reply}")
