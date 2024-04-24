import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageChops
import numpy as np
from io import BytesIO

# Set Streamlit page configuration to wide mode
st.set_page_config(layout="wide")

def load_image(image_path):
    return Image.open(image_path).convert('RGBA')

def merge_images(base_image, overlay_image, opacity=0.5):
    overlay_image = overlay_image.resize(base_image.size, Image.Resampling.LANCZOS)
    merged_image = Image.blend(base_image.convert('RGBA'), overlay_image.convert('RGBA'), opacity)
    return merged_image

def resize_image(image, max_width=1200, max_height=800):
    width_ratio = max_width / image.width
    height_ratio = max_height / image.height
    ratio = min(width_ratio, height_ratio)
    new_width = int(image.width * ratio)
    new_height = int(image.height * ratio)
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized_image

def process_drawing(overlay_image, drawing_data):
    drawing_image = Image.fromarray(np.uint8(drawing_data)).convert('RGBA')
    drawing_image = drawing_image.resize(overlay_image.size, Image.Resampling.LANCZOS)
    drawing_array = np.array(drawing_image)

    # Masks need to be adapted to the size of the overlay image
    add_mask = (drawing_array[:, :, 0] == 0) & (drawing_array[:, :, 1] == 255) & (drawing_array[:, :, 2] == 0)
    subtract_mask = (drawing_array[:, :, 0] == 255) & (drawing_array[:, :, 1] == 0) & (drawing_array[:, :, 2] == 0)

    # Create a white image to add
    add_image = Image.new("RGBA", overlay_image.size, (255, 255, 255, 255))
    add_image.putalpha(Image.fromarray((add_mask * 255).astype(np.uint8)))

    # Create a mask for subtraction (will be used to clear regions)
    subtract_image = Image.new("RGBA", overlay_image.size, (0, 0, 0, 0))
    subtract_image.putalpha(Image.fromarray((subtract_mask * 255).astype(np.uint8)))

    # Combine images: first apply add_mask then subtract_mask
    modified_overlay_image = Image.alpha_composite(overlay_image, add_image)
    modified_overlay_image = ImageChops.subtract(modified_overlay_image, subtract_image)

    return modified_overlay_image
def main():
    st.title("Interactive Image Editing with Add and Subtract Modes")

    base_image_path = "D6.try.jpg"
    overlay_image_path = "mask.jpeg"
    base_image = load_image(base_image_path)
    overlay_image = load_image(overlay_image_path)

    merged_image = merge_images(base_image, overlay_image, opacity=0.5)
    fitted_image = resize_image(merged_image)

    drawing_mode = st.selectbox("Drawing Mode", ["Add", "Subtract"])
    color = "#00FF00" if drawing_mode == "Add" else "#FF0000"

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # Transparent fill color
        stroke_width=10,
        stroke_color=color,  # Green for Add, Red for Subtract
        background_color='',
        background_image=fitted_image,
        update_streamlit=True,
        width=fitted_image.width,
        height=fitted_image.height,
        drawing_mode='freedraw',
        key="canvas"
    )

    if st.button("Save Changes"):
        if canvas_result.image_data is not None:
            modified_overlay_image = process_drawing(overlay_image, canvas_result.image_data)
            bytes_io = BytesIO()
            modified_overlay_image.save(bytes_io, format='PNG')
            image_bytes = bytes_io.getvalue()

            st.download_button(
                label="Download Final Image",
                data=image_bytes,
                file_name="final_modified_image.png",
                mime="image/png"
            )

if __name__ == "__main__":
    main()
