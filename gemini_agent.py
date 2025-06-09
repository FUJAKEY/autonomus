import os
import subprocess
import google.generativeai as genai

# Read API key from api.txt
API_KEY_FILE = 'api.txt'
if os.path.exists(API_KEY_FILE):
    with open(API_KEY_FILE, 'r') as f:
        api_key = f.read().strip()
else:
    api_key = os.environ.get('GEMINI_API_KEY')

if not api_key:
    raise RuntimeError('Gemini API key not found')

# Configure Gemini

genai.configure(api_key=api_key)

# System prompt for the agent
SYSTEM_PROMPT = '''Вы — автономный агент Gemini 2.0 Flash. У вас есть доступ к файловой
системе и командной строке. Вы можете читать и изменять файлы, выполнять shell-команды
и возвращать результат пользователю. Всегда действуйте уверенно и последовательно.
Используйте Python-подобный синтаксис для примеров кода. Запрашивайте у пользователя
четкие инструкции. Документация Gemini API взята из файла gemini.txt и распространяется
по лицензии Creative Commons Attribution 4.0, кодовые примеры — по лицензии Apache 2.0.
'''

def read_file(path: str) -> str:
    """Return the contents of the given file."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path: str, content: str) -> None:
    """Write content to the given file, overwriting it."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def execute_command(command: str) -> str:
    """Execute a shell command and return its output."""
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    return proc.stdout

def chat():
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[{'role': 'system', 'parts': [SYSTEM_PROMPT]}])
    while True:
        try:
            user_input = input('>>> ')
        except EOFError:
            break
        if user_input.strip() in {'exit', 'quit'}:
            break
        if user_input.startswith('read '):
            path = user_input[5:].strip()
            try:
                content = read_file(path)
                print(content)
            except Exception as e:
                print('Error reading file:', e)
            continue
        if user_input.startswith('write '):
            parts = user_input.split(' ', 2)
            if len(parts) < 3:
                print('Usage: write <path> <content>')
                continue
            path, content = parts[1], parts[2]
            try:
                write_file(path, content)
                print('File written.')
            except Exception as e:
                print('Error writing file:', e)
            continue
        if user_input.startswith('run '):
            cmd = user_input[4:]
            output = execute_command(cmd)
            print(output)
            continue
        response = chat.send_message(user_input)
        print(response.text)

if __name__ == '__main__':
    chat()
