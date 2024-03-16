import streamlit as st
import shlex
from subprocess import Popen
import atexit
import socket

def get_server_ip():

    s = socket.socket(
        family = socket.AF_INET,    # (host, port)
        type = socket.SOCK_DGRAM )
    
    s.connect(('8.8.8.8', 1))
    ip, port = s.getsockname()

    print(f"{ip =}, {port =}")
    s.close()
    return ip, port

def launch_trame(path_script: str):
    
    ip, _ = get_server_ip()

    command = f"/home/adminuser/venv/bin/python {path_script} --port 1234 --host {ip:!s}"
    args = shlex.split(command)
    p = Popen(args)

    return p


def close_trame(p: Popen):
    print("Closing trame")
    p.terminate()


def main():

    st.title("Trame within streamlit")



    p = launch_trame("trame_example/solution_cone.py")
    atexit.register(close_trame, p)

    st.components.v1.iframe("http://localhost:1234", height=400)
    # trame_component()

if __name__ == "__main__":
    main()
