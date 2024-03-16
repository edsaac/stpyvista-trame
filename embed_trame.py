import streamlit as st
import shlex
from subprocess import Popen
import atexit
import socket

def launch_trame(path_script: str):
    
    global trame_component
    
    command = f"/home/adminuser/venv/bin/python {path_script} --port 1234"
    args = shlex.split(command)
    p = Popen(args)

    return p


def close_trame(p: Popen):
    print("Closing trame")
    p.terminate()


def main():

    st.title("Trame within streamlit")

    "### Python `socket` (?)"
    s = socket.socket(
        family = socket.AF_INET,    # (host, port)
        type = socket.SOCK_DGRAM )
    
    s.connect(('8.8.8.8', 1))
    ip, port = s.getsockname()

    print(f"{ip =}, {port =}")
    st.metric("**IP**", ip)
    st.metric("**Port**", port)
    s.close()

    p = launch_trame("trame_example/solution_cone.py")
    atexit.register(close_trame, p)

    st.components.v1.iframe("http://localhost:1234", height=400)
    # trame_component()

if __name__ == "__main__":
    main()
