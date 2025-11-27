
import argparse
import os
import subprocess

def parse_lean_to_repl(lean):
    replaced_newlines = lean.replace("\n", "\\n")
    cmd_string = f'{{ "cmd": "{replaced_newlines}" }}'
    return cmd_string

def execute_lean(repl_json, working_directory='.'):
    # maybe add a optional to specify where the repl compiler is located, if not in current directory
    repl_cmd = subprocess.run(['lake', 'exe', 'repl'], input=repl_json, stdout=subprocess.PIPE, encoding='utf-8', cwd=working_directory)
    return repl_cmd.stdout

def compile_lean(lean_script, working_directory='.'):
    command_line_string = parse_lean_to_repl(lean_script)
    return execute_lean(command_line_string, working_directory)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='execute_lean',
        description='takes a lean script as single String and executes it by using lean4 repl')
    parser.add_argument('lean_script', type=str, help='the lean script to execute, must be a String')
    parser.add_argument('-w', '--working_directory', type=str, default='.', required=False, help='the directory of the repl compiler')
    args = parser.parse_args()
    # the only validate input should be a lean script, so maybe validate the input
    print(compile_lean(args.lean_script, args.working_directory))