import os
import streamlit as st
import streamlit.components.v1 as components

from pathlib import Path
from time import sleep
from subprocess import check_output, STDOUT
# import shlex

PORT = 12346
CLOUDFLARED_PATH = Path("./cloudflared/cloudflared-linux-amd64")
CONTROL_PANEL= True

in_community_cloud = True
python_executable = "/home/adminuser/venv/bin/python" if in_community_cloud else "python"

def download_cloudflared():
    if not Path("./cloudflared").exists():
        os.system("mkdir cloudflared")
        st.rerun()

    if not CLOUDFLARED_PATH.exists():
        os.system(
            f"wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O {CLOUDFLARED_PATH}"
        )
        os.system(f"chmod 777 {CLOUDFLARED_PATH}")
        st.rerun()

    return True

@st.cache_resource
def launch_trame(path_script: str):
    command = f"""{python_executable} -u {path_script} --server --port {PORT} &"""
    os.system(command)

@st.cache_resource
def launch_cloudflared(dummy: str = "cloud"):
    command = (
        f"./cloudflared/cloudflared-linux-amd64 tunnel --url http://localhost:{PORT} > ./cloudflared/log.txt 2>&1 &"
    )
    os.system(command)

    sleep(5)

    with open("./cloudflared/log.txt") as f:
        for line in f:
            print(line)
            if "https" in line and ".trycloudflare.com" in line:
                address = line.rpartition("INF")[-1].replace("|", "").strip()
                break

    return address

@st.cache_resource
def initialize_server(dummy:str = "cloud"):
    try:
        with open("sentinel.txt") as f:
            address = f.readline()

    except FileNotFoundError:
        download_cloudflared()
        launch_trame("trame_example/grand_canyon.py")
        address = launch_cloudflared()
        
        with open("sentinel.txt", "w") as f:
            f.write(address)
    
    return address

def main():
    #--------------------------------
    # App
    #--------------------------------
    st.set_page_config(
        page_title="Trame in Streamlit",
        page_icon="🧇",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown(
        """
        <style>
        div[data-testid="stAppViewBlockContainer"]{
            padding-top: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🧇 Trame within streamlit")
    address = initialize_server()
    components.iframe(address, height=580)

    if CONTROL_PANEL:
        with st.sidebar:
            if (
                st.text_input("Controls", type="password", label_visibility="collapsed")
                == st.secrets.control_panel
            ):
                st.info(f"Running on {address}")

                if st.button("Clear cache"):
                    st.cache_resource.clear()
                    st.rerun()
                
                with st.form("Run commands"):
                    quick_command = st.text_area("Command")
                    run_command = st.form_submit_button("Run")

                if run_command:
                    task = check_output(
                        # ["bash", "-c", f"\"{quick_command}\""], text=True, stderr=STDOUT
                        f"bash -c \"{quick_command}\"", text=True, stderr=STDOUT, shell=True
                    )
                    st.code(task)


if __name__ == "__main__":
    main()