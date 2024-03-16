import streamlit as st
import shlex
from subprocess import Popen, PIPE
import atexit
import os
from pathlib import Path

CLOUDFARE_PATH = Path("./cloudflared-linux-amd64")
if not CLOUDFARE_PATH.exists():
    os.system("wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64")
    os.system("chmod +x cloudflared-linux-amd64")

def run_cloudflared():
    command = "nohup ./cloudflared-linux-amd64 tunnel --url http://localhost:12345 &"
    args = shlex.split(command)
    p = Popen(args)
    return p

def launch_trame(path_script: str):
    command = f"""/home/adminuser/venv/bin/python {path_script} --port 12345"""
    args = shlex.split(command)
    p = Popen(args, stdout=PIPE)
    return p

def close_trame(trame_proc: Popen):
    print("Closing trame")
    trame_proc.terminate()

def get_address():
    command = """grep -o 'https://.*\.trycloudflare.com' nohup.out | head -n 1 | xargs -I {} echo "{}" > address.txt"""
    os.system(command)
    with open("address.txt") as f:
        address = f.read()

    return address

def main():
    # st.code(show_config())
    st.title("Trame within streamlit")
    
    p = launch_trame("trame_example/solution_cone.py")
    atexit.register(close_trame, p)
        
    if "cloudfared_running" not in st.session_state:
        run_cloudflared()
        st.session_state.cloudfared_running = True
    

    adresss = get_address()
    st.write(adresss)
    st.components.v1.iframe(adresss, height=400)

    # if st.button("Reset trame"):
    #     p.terminate()
    #     st.rerun()

if __name__ == "__main__":
    main()
