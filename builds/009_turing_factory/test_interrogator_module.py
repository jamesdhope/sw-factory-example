from interrogator_module import InterrogatorModule


def test_initiate_dialog():
    interrogator = InterrogatorModule()
    interrogator.initiate_dialog('AI')
    assert any('AI: Responding as Artificial Intelligence.' in msg for msg in interrogator.conversation_history)

    interrogator.initiate_dialog('Human')
    assert any('Human: Responding as a Human Proxy.' in msg for msg in interrogator.conversation_history)


def test_record_guess():
    interrogator = InterrogatorModule()
    interrogator.record_guess('AI', 'Machine')
    assert any('Guess recorded: AI is guessed to be a Machine.' in msg for msg in interrogator.conversation_history)

# Run tests
if __name__ == "__main__":
    test_initiate_dialog()
    test_record_guess()
    print("All tests passed.")