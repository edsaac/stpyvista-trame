import streamlit as st
import shlex
from subprocess import Popen, PIPE
import atexit
import os
from pathlib import Path

CLOUDFARE_PATH = Path("./cloudflared-linux-amd64")
if not CLOUDFARE_PATH.exists():
    os.system("wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64")
    os.system("chmod +x cloudflared-linux-amd64")

def run_cloudflared():
    command = "./cloudflared-linux-amd64 tunnel --url http://localhost:12345"
    args = shlex.split(command)
    p = Popen(args, stdout=PIPE, stderr=PIPE, text=True)
    
    while True:
        line = p.stdout.readline()
        if "https" in line and "trycloudflare.com" in line:
            address = line.rpartition("INF")[-1].replace("|","").strip()
            break
        
    return address

def launch_trame(path_script: str):
    command = f"""/home/adminuser/venv/bin/python {path_script} --port 12345"""
    args = shlex.split(command)
    p = Popen(args, stdout=PIPE)
    return p

def close_trame(trame_proc: Popen):
    print("Closing trame")
    trame_proc.terminate()



def main():
    # st.code(show_config())
    st.title("Trame within streamlit")
    
    p = launch_trame("trame_example/solution_cone.py")
    atexit.register(close_trame, p)
        
    if "cloudfared_running" not in st.session_state:
        address = run_cloudflared()
        st.session_state.cloudfared_running = True
    

    st.write(address)
    st.components.v1.iframe(address, height=400)

    # if st.button("Reset trame"):
    #     p.terminate()
    #     st.rerun()

if __name__ == "__main__":
    main()
