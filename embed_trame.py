import streamlit as st
import shlex
from subprocess import Popen, PIPE
import atexit
import os
from pathlib import Path

IN_COMMUNITY_CLOUD = True

CLOUDFARED_PATH = Path("./cloudflared/cloudflared-linux-amd64")
PYCOMMAND = "/home/adminuser/venv/bin/python" if IN_COMMUNITY_CLOUD else "python"

if not Path("./cloudflared").exists():
    os.system("mkdir cloudflared")
    st.rerun()

if not CLOUDFARED_PATH.exists():
    os.system(f"wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O {CLOUDFARED_PATH}")
    os.system(f"chmod 777 {CLOUDFARED_PATH}")
    st.rerun()

@st.cache_resource
def launch_cloudflared(dummy:str = "cloud"):
    command = "./cloudflared/cloudflared-linux-amd64 tunnel --url http://localhost:12345"
    args = shlex.split(command)
    p = Popen(args, stdout=PIPE, stderr=PIPE, text=True)
    
    address = "not_found"
    
    for _ in range(50):
        line = p.stderr.readline()
        print(line)
        if "https" in line and "trycloudflare.com" in line:
            address = line.rpartition("INF")[-1].replace("|","").strip()
            break
        
    return p, address

def launch_trame(path_script: str):
    command = f"""{PYCOMMAND} {path_script} --port 12345"""
    args = shlex.split(command)
    p = Popen(args, stdout=PIPE, stderr=PIPE, text=True)
    return p

def close_trame(p_trame: Popen):
    print("Closing trame")
    p_trame.terminate()
    del st.session_state.trame_running

def close_cloudflared(p_cloudflared: Popen):
    print("Closing cloudflared")
    p_cloudflared.terminate()
    del st.session_state.cloudfared_running

def main():
    st.title("Trame within streamlit")
    
    if "cloudfared_running" not in st.session_state:
        p_cloudflared, address = launch_cloudflared()
        atexit.register(close_cloudflared, p_cloudflared)
        st.session_state.cloudfared_running = p_cloudflared

    if "trame_running" not in st.session_state:
        p_trame = launch_trame("trame_example/solution_cone.py")
        atexit.register(close_trame, p_trame)
        st.session_state.trame_running = p_trame
    
    st.write(address)
    st.components.v1.iframe(address, height=400)

    # if st.button("Reset trame"):
    #     p.terminate()
    #     st.rerun()

if __name__ == "__main__":
    main()
