import streamlit as st
import shlex
from subprocess import Popen, check_output
import atexit
import socket

def show_config():
    command = "/home/adminuser/venv/bin/streamlit config show"
    args = shlex.split(command)
    output = check_output(args, text=True)
    return output

def get_server_ip():

    s = socket.socket(
        family = socket.AF_INET,    # (host, port)
        type = socket.SOCK_DGRAM )
    
    s.connect(('8.8.8.8', 1))
    ip, port = s.getsockname()

    print(f"{ip =}, {port =}")
    s.close()
    return ip, port

def launch_trame(path_script: str, ip:str):
    command = f"""/home/adminuser/venv/bin/python {path_script}"""
    args = shlex.split(command)
    p = Popen(args)

    return p


def close_trame(p: Popen):
    print("Closing trame")
    p.terminate()


def main():
    st.code(show_config())
    st.title("Trame within streamlit")
    ip, _ = get_server_ip()
    p = launch_trame("trame_example/solution_cone.py", ip)
    atexit.register(close_trame, p)

    st.components.v1.iframe(f"http://{ip}:1234", height=400)
    # trame_component()

    if st.button("Reset trame"):
        p.terminate()
        st.rerun()

if __name__ == "__main__":
    main()
