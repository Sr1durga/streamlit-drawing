# import streamlit as st
# from streamlit_drawable_canvas import st_canvas
# from PIL import Image
# import numpy as np
# from io import BytesIO

# # Set Streamlit page configuration to wide mode
# st.set_page_config(layout="wide")

# def load_image(image_path):
#     return Image.open(image_path).convert('RGBA')

# def merge_images(base_image, overlay_image, opacity=0.5):
#     # Resize overlay image to match the base image size
#     overlay_image = overlay_image.resize(base_image.size, Image.Resampling.LANCZOS)
#     # Blend images with opacity
#     merged_image = Image.blend(base_image.convert('RGBA'), overlay_image.convert('RGBA'), opacity)
#     return merged_image

# def resize_image(image, max_width=1200, max_height=800):
#     # Calculate ratios to maintain aspect ratio
#     width_ratio = max_width / image.width
#     height_ratio = max_height / image.height
#     ratio = min(width_ratio, height_ratio)
#     # Calculate new dimensions
#     new_width = int(image.width * ratio)
#     new_height = int(image.height * ratio)
#     # Resize image
#     resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
#     return resized_image

# def main():
#     st.title("Interactive Image Drawing")

#     # Load images
#     base_image_path = "/Users/sridurgakrithivasan/streamlit-drawing/D6.try.jpg"
#     overlay_image_path = "/Users/sridurgakrithivasan/streamlit-drawing/mask.jpeg"
#     base_image = load_image(base_image_path)
#     overlay_image = load_image(overlay_image_path)

#     # Merge and resize images
#     merged_image = merge_images(base_image, overlay_image, opacity=0.5)
#     fitted_image = resize_image(merged_image)

#     # Drawing canvas setup
#     canvas_result = st_canvas(
#         fill_color="rgba(255, 255, 255, 0)",  # Transparent fill color
#         stroke_width=10,
#         stroke_color="#FFFFFF",  # White stroke color
#         background_color='',
#         background_image=fitted_image,
#         update_streamlit=True,
#         width=fitted_image.width,
#         height=fitted_image.height,
#         drawing_mode='freedraw',
#         key='canvas'
#     )

#     # Handle canvas image data and prepare for download
#     if canvas_result.image_data is not None:
#         drawing_image = Image.fromarray(np.uint8(canvas_result.image_data)).convert('RGBA')
#         final_image = Image.alpha_composite(fitted_image.convert('RGBA'), drawing_image)

#         # Convert result_image into PNG format bytes
#         bytes_io = BytesIO()
#         final_image.save(bytes_io, format='PNG')
#         image_bytes = bytes_io.getvalue()

#         # Download button for the resulting image
#         st.download_button(
#             label="Download Image",
#             data=image_bytes,
#             file_name="final_overlay_drawing.png",
#             mime="image/png"
#         )

# if __name__ == "__main__":
#     main()
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
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
    # Convert drawing data to numpy array
    drawing_array = np.array(drawing_data)

    # Generate a mask from the drawing
    # Assuming drawing is made in white, extract all channels assuming they're similar (greyscale)
    drawing_mask = np.all(drawing_array[:, :, :3] == 255, axis=-1).astype(np.uint8) * 255

    # Resize overlay image to match drawing size
    overlay_resized = overlay_image.resize((drawing_array.shape[1], drawing_array.shape[0]), Image.Resampling.LANCZOS)
    overlay_array = np.array(overlay_resized)

    # Extract alpha channel or assume all white if not present
    if overlay_array.shape[2] == 4:
        mask = overlay_array[:, :, 3]
    else:
        mask = np.full((overlay_array.shape[0], overlay_array.shape[1]), 255, dtype=np.uint8)

    # Subtract drawing mask from the original mask
    new_mask = mask.astype(int) - drawing_mask.astype(int)
    new_mask = np.clip(new_mask, 0, 255).astype(np.uint8)

    # Update the alpha channel of the overlay image
    overlay_array[:, :, 3] = new_mask

    # Create a new image from the modified array
    modified_overlay_image = Image.fromarray(overlay_array, 'RGBA')
    return modified_overlay_image

def main():
    st.title("Interactive Image Drawing")

    base_image_path = "D6.try.jpg"
    overlay_image_path = "mask.jpeg"
    base_image = load_image(base_image_path)
    overlay_image = load_image(overlay_image_path)

    merged_image = merge_images(base_image, overlay_image, opacity=0.5)
    fitted_image = resize_image(merged_image)

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=10,
        stroke_color="#FFFFFF",
        background_color='',
        background_image=fitted_image,
        update_streamlit=True,
        width=fitted_image.width,
        height=fitted_image.height,
        drawing_mode='freedraw',
        key='canvas'
    )

    if canvas_result.image_data is not None:
        modified_overlay_image = process_drawing(overlay_image, canvas_result.image_data)
        
        bytes_io = BytesIO()
        modified_overlay_image.save(bytes_io, format='PNG')
        image_bytes = bytes_io.getvalue()

        st.download_button(
            label="Download Modified Overlay Image",
            data=image_bytes,
            file_name="modified_overlay_image.png",
            mime="image/png"
        )

if __name__ == "__main__":
    main()
