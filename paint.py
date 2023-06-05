import io
import uuid
from base64 import b64encode

import requests
from PIL import Image
import tkinter as tk
from tkinter import filedialog

API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-5"


def generate_image(prompt: str, inpaint_image_path: str = None, mask_image_path: str = None, count: int = 1) -> list:
    """Generate multiple images from a prompt and perform inpainting if inpaint and mask images are provided.

    Args:
        prompt (str): The prompt to use
        inpaint_image_path (str): The file path of the inpaint image
        mask_image_path (str): The file path of the mask image
        count (int): The number of images to generate

    Returns:
        list: Filenames of the generated images
    """

    headers = {"Authorization": "Bearer <API-Key>"}# Replace YOUR_API_TOKEN with your actual Hugging Face API token
  
    if inpaint_image_path is not None:
        with open(inpaint_image_path, "rb") as image_file:
            image_content = image_file.read()
        encoded_image = b64encode(image_content).decode("utf-8")
    else:
        encoded_image = None

    if mask_image_path is not None:
        with Image.open(mask_image_path) as mask_image:
            if mask_image.mode != "L":
                mask_image = mask_image.convert("L")  # Convert to grayscale if not already
            encoded_mask = image_to_base64(mask_image)
    else:
        encoded_mask = None

    filenames = []
    for _ in range(count):
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "inpaint_image": encoded_image,
                "mask_image": encoded_mask
            },
        )

        if response.ok:
            image = Image.open(io.BytesIO(response.content))
            print(f"Image Generated for prompt: {prompt}")

            filename = f"{str(uuid.uuid4())}.jpg"
            with open(filename, "wb") as image_file:
                image.save(image_file)
            filenames.append(filename)

    return filenames


def image_to_base64(image):
    """Convert an image to base64-encoded string.

    Args:
        image (PIL.Image.Image): The image to convert

    Returns:
        str: The base64-encoded string
    """
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        encoded_image = b64encode(output.getvalue()).decode("utf-8")
    return encoded_image


def browse_inpaint_image():
    """Open a file dialog to select the inpaint image file."""
    inpaint_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
    inpaint_image_entry.delete(0, tk.END)
    inpaint_image_entry.insert(0, inpaint_image_path)


def browse_mask_image():
    """Open a file dialog to select the mask image file."""
    mask_image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
    mask_image_entry.delete(0, tk.END)
    mask_image_entry.insert(0, mask_image_path)


def generate_button_click():
    """Event handler for the Generate button click."""
    prompt_text = prompt_entry.get()
    inpaint_image_path = inpaint_image_entry.get()
    mask_image_path = mask_image_entry.get()
    count_value = count_spinbox.get()

    try:
        count = int(count_value)
        if count <= 0:
            raise ValueError
    except ValueError:
        status_label.config(text="Invalid count value. Please enter a positive integer.")
        return

    filenames = generate_image(prompt_text, inpaint_image_path, mask_image_path, count)
    if filenames:
        status_label.config(text="Images generated and saved:")
        for filename in filenames:
            print(filename)
    else:
        status_label.config(text="Failed to generate images.")


# Create the main window
window = tk.Tk()
window.title("Image Generation and Inpainting")
window.geometry("500x350")

# Prompt Label and Entry
prompt_label = tk.Label(window, text="Prompt:")
prompt_label.pack()
prompt_entry = tk.Entry(window, width=50)
prompt_entry.pack()

# Inpaint Image Label, Entry, and Browse Button
inpaint_image_label = tk.Label(window, text="Inpaint Image (optional):")
inpaint_image_label.pack()
inpaint_image_entry = tk.Entry(window, width=40)
inpaint_image_entry.pack(side=tk.LEFT)
inpaint_image_browse_button = tk.Button(window, text="Browse", command=browse_inpaint_image)
inpaint_image_browse_button.pack(side=tk.LEFT)

# Mask Image Label, Entry, and Browse Button
mask_image_label = tk.Label(window, text="Mask Image (optional):")
mask_image_label.pack()
mask_image_entry = tk.Entry(window, width=40)
mask_image_entry.pack(side=tk.LEFT)
mask_image_browse_button = tk.Button(window, text="Browse", command=browse_mask_image)
mask_image_browse_button.pack(side=tk.LEFT)

# Count Label and Spinbox
count_label = tk.Label(window, text="Number of Images to Generate:")
count_label.pack()
count_spinbox = tk.Spinbox(window, from_=1, to=10)
count_spinbox.pack()

# Generate Button
generate_button = tk.Button(window, text="Generate", command=generate_button_click)
generate_button.pack()

# Status Label
status_label = tk.Label(window, text="")
status_label.pack()

# Start the main loop
window.mainloop()