import pyvista as pv
from pyvista.plotting import Plotter

import asyncio
import streamlit as st 
from streamlit.components.v1 import declare_component
import nest_asyncio
import threading

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vtk, client, trame

pv.OFF_SCREEN = True
pv.start_xvfb()
nest_asyncio.apply()

def basic_plotter():
    plotter = pv.Plotter()

    ## Create a mesh with a cube
    mesh = pv.Sphere(center=(0, 0, 0))

    ## Add some scalar field associated to the mesh
    mesh["myscalar"] = mesh.points[:, 2] * mesh.points[:, 0]
    mesh.set_active_scalars("myscalar")

    ## Add mesh to the plotter
    plotter.add_mesh(mesh, cmap="bwr", line_width=1, label="sphere")
    plotter.add_title("My sphere", color="black", font_size=14)

    ## Final touches
    plotter.view_isometric()
    plotter.background_color = "lightgray"

    return plotter

class TrameApp:

    def __init__(self, plotter:Plotter) -> None:
        
        self.server = get_server(client_type="vue2")
        state, ctrl = self.server.state, self.server.controller  # noqa

        with SinglePageLayout(self.server, show_drawer=False, height="500px") as layout:
        
            ## Layout
            with layout.content:
                view = vtk.VtkLocalView(plotter.ren_win)
                ctrl.view_update = view.update

            ## Streamlit component configuration
            js = "console.log('First message!');\n"

            with open("./streamlit-trame-component-lib.js") as f:
                js += f.read()

            ctrl.swap = client.JSEval(exec=js).exec
            trame.ClientTriggers(mounted=ctrl.swap)

    async def async_run(self):
        
        if not self.server.running:
            self.cor = self.server.start(
                port=12346,
                open_browser=False,
                thread=True,
                show_connection_info=True,
                exec_mode="coroutine",
                disable_logging=True,
                timeout=0,
            )
        
            loop = asyncio.new_event_loop()
            self.task = loop.create_task(self.cor, name="st_trame")
            print("Create task running")
            
            loop.run_forever()  # This is blocking

        await self.server.ready

    def run(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(self.async_run())
        return

def main():

    st_trame = declare_component("trame", url="http://localhost:12346")
    st.title("streamlit-trame")
    
    pl = basic_plotter()
    print("Build plotter")

    tmap = TrameApp(pl)
    print("Get server and coroutine")

    st_trame(key="my_trame")
    print("Create component")    

    threading.Thread(target=tmap.run).start()

if __name__ == "__main__":
    main()