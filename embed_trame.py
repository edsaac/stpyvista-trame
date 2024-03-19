import streamlit as st
import shlex
from subprocess import Popen, PIPE
import atexit
import os
from pathlib import Path
from collections import namedtuple
from time import sleep

CF_Connection = namedtuple("CF_Connection", ["process", "address"])
PORT = 12444

IN_COMMUNITY_CLOUD = True
PYCOMMAND = "/home/adminuser/venv/bin/python" if IN_COMMUNITY_CLOUD else "python"

CLOUDFLARED_PATH = Path("./cloudflared/cloudflared-linux-amd64")
TRAME_APP_PATH = "./trame_example/grand_canyon.py"

if not Path("./cloudflared").exists():
    os.system("mkdir cloudflared")
    st.rerun()

if not CLOUDFLARED_PATH.exists():
    os.system(f"wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O {CLOUDFLARED_PATH}")
    os.system(f"chmod 777 {CLOUDFLARED_PATH}")
    st.rerun()

@st.cache_resource
def launch_cloudflared(dummy:str = "cloud"):
    command = f"./cloudflared/cloudflared-linux-amd64 tunnel --url http://localhost:{PORT}"
    args = shlex.split(command)
    p = Popen(args, stdout=PIPE, stderr=PIPE, text=True)
    
    address = "not_found"
    sleep(2)
    
    for _ in range(50):
        line = p.stderr.readline()
        print(line)
        if "https" in line and ".trycloudflare.com" in line:
            address = line.rpartition("INF")[-1].replace("|","").strip()
            break
        
    return CF_Connection(p, address)

@st.cache_resource
def launch_trame(path_script: str):
    command = f"""{PYCOMMAND} {path_script} --server --port {PORT}"""
    args = shlex.split(command)
    p = Popen(args, stdout=PIPE, stderr=PIPE, text=True)
    
    return p

def close_all(p_trame: Popen, p_cloudflared: Popen):
    close_trame(p_trame)
    close_cloudflared(p_cloudflared)
    st.rerun()

def close_trame(p_trame: Popen):
    print("Closing trame")
    p_trame.terminate()
    del st.session_state.trame_running

def close_cloudflared(p_cloudflared: Popen):
    print("Closing cloudflared")
    p_cloudflared.terminate()
    del st.session_state.cloudflared

def main():
    st.title("Trame within streamlit")
    
    if "cloudflared" not in st.session_state:
        cloudflared = launch_cloudflared()
        atexit.register(close_cloudflared, cloudflared.process)
        st.session_state.cloudflared = cloudflared
    
    if "trame_running" not in st.session_state:
        p_trame = launch_trame(TRAME_APP_PATH)
        atexit.register(close_trame, p_trame)
        st.session_state.trame_running = p_trame

        for _ in range(20):
            st.sidebar.text(p_trame.stdout.readline())
        
        for _ in range(20):
            st.sidebar.text(p_trame.stderr.readline())

    st.write(st.session_state.cloudflared.address)
    st.components.v1.iframe(st.session_state.cloudflared.address, height=400)

    if st.button("Reset trame", on_click=st.cache_resource.clear):
        close_all(st.session_state.cloudflared.process, st.session_state.trame_running)
        

if __name__ == "__main__":
    main()
