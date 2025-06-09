import os
import subprocess
from typing import Optional

import google.generativeai as genai

# Read API key from api.txt or environment
API_KEY_FILE = "api.txt"


def load_api_key() -> str:
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return os.environ.get("GEMINI_API_KEY", "")


api_key = load_api_key()

if not api_key:
    raise RuntimeError("Gemini API key not found")

# Configure Gemini

genai.configure(api_key=api_key)

# System prompt for the agent
SYSTEM_PROMPT = """
Ты — продвинутый автономный агент на базе Gemini 2.0 Flash. Твои прототипы —
Codex и Manus IM. Ты умеешь читать и изменять файлы, выполнять shell-команды
и запускать Python-код по запросу. Всегда уточняй инструкции пользователя перед
потенциально опасными действиями и сообщай полный вывод команд. Используй стиль
Python и веди историю диалога последовательно. Документация API находится в
файле gemini.txt и лицензирована по CC BY 4.0, примеры кода — под Apache 2.0.
"""

def read_file(path: str) -> str:
    """Return the contents of the given file."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path: str, content: str) -> None:
    """Write content to the given file, overwriting it."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def append_file(path: str, content: str) -> None:
    """Append content to the end of the given file."""
    with open(path, 'a', encoding='utf-8') as f:
        f.write(content)

def execute_command(command: str) -> str:
    """Execute a shell command and return its output."""
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    return proc.stdout


def run_python(code: str) -> str:
    """Execute Python code and return its output."""
    proc = subprocess.run(['python', '-c', code], stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    return proc.stdout

def chat():
    model = genai.GenerativeModel('models/gemini-2.0-flash')
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
        if user_input.startswith('append '):
            parts = user_input.split(' ', 2)
            if len(parts) < 3:
                print('Usage: append <path> <content>')
                continue
            path, content = parts[1], parts[2]
            try:
                append_file(path, content)
                print('Content appended.')
            except Exception as e:
                print('Error appending file:', e)
            continue
        if user_input.startswith('run '):
            cmd = user_input[4:]
            output = execute_command(cmd)
            print(output)
            continue
        if user_input.startswith('python '):
            code = user_input[7:]
            output = run_python(code)
            print(output)
            continue
        response = chat.send_message(user_input)
        print(response.text)

if __name__ == '__main__':
    chat()
