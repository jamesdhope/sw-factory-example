import argparse

def reverse_string(input_string):
    """
    Reverses the given input string.

    Parameters:
    input_string (str): The string to be reversed.

    Returns:
    str: The reversed string.
    """
    if not input_string:
        raise ValueError("The input string cannot be empty.")
    return input_string[::-1]

def main():
    parser = argparse.ArgumentParser(description='Reverse a given string.')
    parser.add_argument('string', type=str, nargs='?', help='The string to reverse')

    args = parser.parse_args()

    if args.string:
        # Direct string input from command line argument
        print("Reversed string:", reverse_string(args.string))
    else:
        # Prompt the user to enter a string
        user_input = input("Enter a string to reverse: ")
        print("Reversed string:", reverse_string(user_input))

if __name__ == "__main__":
    main()
