import code
import subprocess

def run_code(codes):
    interpreter = code.InteractiveInterpreter()
    interpreter.runcode(codes)

def run_code_from_file(fileName):
    subprocess.Popen(['python', fileName])

def start_pydoc():
    port = '1234'
    return subprocess.Popen(['pydoc', '-p', port]), ('http://127.0.0.1:' + port + '/')