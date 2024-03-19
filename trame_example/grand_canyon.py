from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, html
from trame.widgets import vuetify as vuetify

import pyvista as pv

# from PIL import Image
import rasterio
import numpy as np

# Always set PyVista to plot off screen with Trame
pv.OFF_SCREEN = True
PATH_TO_DEM = "trame_example/clipped_colorado.tif"

def create_plotter():

    with rasterio.open(PATH_TO_DEM) as im:
        elevation = im.read(1)  ## Assuming data in first band
        width = im.width
        height = im.height
        print(width, height)

    # Create mesh grid
    x = np.arange(width)
    y = np.arange(height)
    xx, yy = np.meshgrid(x, y)
    z = np.zeros_like(xx)

    print(f"{np.min(elevation)}, {np.max(elevation)}")
    # Generate surface
    surface = (
        pv.StructuredGrid(xx, yy, z)
        .triangulate()
        .extract_surface()
        .smooth()
    )

    surface["elevation"] = elevation.T.flatten()
    warped = surface.warp_by_scalar("elevation", factor=0.05)

    # Assemble plotter
    plotter = pv.Plotter()

    plotter.add_mesh(
        warped,
        scalars="elevation",
        cmap="gist_earth",
        show_edges=False,
        name="colorado",
        show_scalar_bar=False,
    )

    # Zooming and camera configs
    plotter.view_isometric()

    return plotter

server = get_server(client_type = "vue2")
state, ctrl = server.state, server.controller

pl = create_plotter()
actor = pl.actors["colorado"]
lut = actor.mapper.lookup_table

# When color change, execute fn
@state.change("color")
def bg_color(color, **kwargs):
    pl.set_background(color)
    ctrl.view_update()

@state.change("visible")
def mesh_visible(visible, **kwargs):
    actor.visibility = visible
    ctrl.view_update()

@state.change("colormap")
def change_colormap(colormap, **kwargs):
    lut.apply_cmap(colormap)
    ctrl.view_update()


with SinglePageWithDrawerLayout(server, show_drawer=False, width="15%") as layout:
# with SinglePageLayout(server, toolbar_title="🌄 Grand Canyon") as layout:
    
    layout.title.set_text("🌄 Grand Canyon")

    with layout.drawer:
        with vuetify.VTooltip(right=True):
            with vuetify.Template(v_slot_activator='{ on, attrs }'):
                with html.Div(v_on='on', v_bind='attrs'):   
                    vuetify.VColorPicker(
                        label="Background color",
                        v_model=("color", "#dddddd"),
                        outlined=True,
                        hide_inputs=True,
                    )
            html.Span("Change background")


    with layout.toolbar:
        vuetify.VSpacer()
        
        vuetify.VSelect(
            label="Colormap",
            v_model=("colormap", "terrain"),
            items=("array_list", ["viridis", "terrain", "coolwarm"]),
            hide_details=True,
            dense=True,
            outlined=True,
            style="max-width: 250px",
        )

        vuetify.VSpacer()

        with vuetify.VTooltip(bottom=True):
            with vuetify.Template(v_slot_activator='{ on, attrs }'):
                with html.Div(v_on='on', v_bind='attrs'):
                    vuetify.VCheckbox(
                        label="Show model",
                        v_model=("visible", True),
                        dense=True,
                        hide_details=True,
                        outlined=True,
                    )
            html.Span("Show or hide the mesh")

    with layout.content:
        view = vtk.VtkLocalView(pl.ren_win)  ## Fails for lut cmap
        ctrl.view_update = view.update
        

if __name__ == "__main__":
    server.start(open_browser=False, show_connection_info=True)