# Technical Specification: String Reversing Tool

## Objective
Create a simple Python script that takes user input and reverses the provided string.

## Requirements
- **User Input**: The script must prompt the user to enter a string.
- **String Reversal**: The script should reverse the entered string.
- **Output**: Display the reversed string to the user.
- **Language**: The implementation must use Python.

## Functional Components
1. **Input Handling**:
   - Use Python's input function to take a string from the user.
2. **String Reversal Logic**:
   - Reverse the string using slicing or a loop.
3. **Output Display**:
   - Print the reversed string to the console.

## Non-functional Requirements
- **Usability**: The script should be easy to run and understand.
- **Compatibility**: Must be compatible with Python 3.

## Assumptions
- The input will be a single line of text.
- The script will run in a console environment.

## Future Considerations
- Handle exceptions or errors if a user provides unexpected input types, though this is not required for the current version.

## Testing
- Test the script with various strings to ensure accurate reversal.
- Consider edge cases such as empty strings and single-character strings.