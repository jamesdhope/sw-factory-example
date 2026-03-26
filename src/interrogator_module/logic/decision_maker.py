# decision_maker.py

class LogicModule:
    def __init__(self, ui, comms):
        self.ui = ui
        self.comms = comms

    def analyze_conversation(self, conversation_history):
        ai_indicators = ["AI", "robot", "algorithm"]  # Sample indicators
        human_indicators = ["human", "person", "real"]  # Sample indicators

        ai_count = sum(1 for message in conversation_history if any(indicator in message for indicator in ai_indicators))
        human_count = sum(1 for message in conversation_history if any(indicator in message for indicator in human_indicators))

        if ai_count > human_count:
            return "AI likely"
        elif human_count > ai_count:
            return "Human likely"
        else:
            return "Indeterminate"

    def make_decision(self):
        conversation_history = self.ui.history
        decision = self.analyze_conversation(conversation_history)
        self.ui.display_message(f"Decision: {decision}")

# Example initialization and use of LogicModule
if __name__ == "__main__":
    from src.interrogator_module.ui.interface import UserInterface
    from src.interrogator_module.communication.interface import CommunicationInterface

    ui = UserInterface()
    comms = CommunicationInterface(ui)
    logic = LogicModule(ui, comms)

    comms.connect()
    while True:
        user_input = ui.get_user_input()
        if user_input.lower().strip() == "exit":
            print("Ending logic module interaction.")
            break
        comms.send_message(user_input)
        comms.receive_message()
        logic.make_decision()
