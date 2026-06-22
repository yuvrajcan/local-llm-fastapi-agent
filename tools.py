from langchain_core.tools import tool
import os

@tool
def write_local_file(filename: str, content: str) -> str:
    """
    Creates a new text file on the local computer and writes the specified content into it.
    Use this tool whenever the user asks you to write, save, or create a file.
    """
    try:
        # Save the file in the current directory
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Success! The file '{filename}' was created and saved to the disk."
    except Exception as e:
        return f"Error creating file: {str(e)}"

# A list of tools we will eventually pass to the LLM
agent_tools = [write_local_file]