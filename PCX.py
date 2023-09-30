import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Function to open a PCX file and extract header information
def open_pcx_file():
    global header_data, color_palette, photo, img_label, header_frame, palette_label
    
    # Open a file dialog to select a PCX file
    file_path = filedialog.askopenfilename(filetypes=[("PCX Files", "*.pcx")])

    if file_path:
        # Read PCX file and extract header information
        header_data, color_palette = extract_pcx_header(file_path)
        display_original_image(file_path)
        display_header_info(header_data)
        display_color_palette(color_palette)
        open_button.config(state=tk.DISABLED)
        close_button.config(state=tk.NORMAL)

# Function to close the PCX file information
def close_pcx_file():
    global header_data, color_palette, photo, img_label, header_frame, palette_label

    if photo:
        # Clear and hide the displayed elements
        img_label.config(image='')
        img_label.pack_forget()
        img_info_label.pack_forget()
        header_frame.pack_forget()
        palette_label.config(image='')
        palette_label.pack_forget()
        open_button.config(state=tk.NORMAL)
        close_button.config(state=tk.DISABLED)
        photo = None

# Function to extract PCX file header information and color palette
def extract_pcx_header(file_path):
    header_data = {}
    color_palette = []

    try:
        with open(file_path, "rb") as file:
            # Read and parse PCX header (128 bytes)
            header = file.read(128)

            # Byte 0: Manufacturer (1 byte)
            header_data['Manufacturer'] = int(header[0])

            # Byte 1: Version (1 byte)
            header_data['Version'] = int(header[1])

            # Byte 2: Encoding type (1 byte)
            header_data['Encoding'] = int(header[2])

            # Byte 3: Bits per Pixel (1 byte)
            header_data['BitsPerPixel'] = int(header[3])

            # Bytes 4-11: Image Dimensions (4 bytes each, little-endian)
            header_data['ImageDimensions'] = (
                int.from_bytes(header[4:6], byteorder='little'),
                int.from_bytes(header[6:8], byteorder='little'),
                int.from_bytes(header[8:10], byteorder='little'),
                int.from_bytes(header[10:12], byteorder='little')
            )

            # Bytes 12-13: HDPI (little-endian)
            header_data['HDPI'] = int.from_bytes(header[12:14], byteorder='little')

            # Bytes 14-15: VDPI (little-endian)
            header_data['VDPI'] = int.from_bytes(header[14:16], byteorder='little')

            # Byte 65: Number of Color Planes (1 byte)
            header_data['NumColorPlanes'] = int(header[65])

            # Bytes 66-67: Bytes per Line (2 bytes, little-endian)
            header_data['BytesPerLine'] = int.from_bytes(header[66:68], byteorder='little')

            # Bytes 68-71: Palette Info (2 bytes each, little-endian)
            header_data['PaletteInfo'] = (
                int.from_bytes(header[68:70], byteorder='little'),
                int.from_bytes(header[70:72], byteorder='little')
            )

            # Bytes 16-19: Horizontal and Vertical Screen Size (2 bytes each, little-endian)
            header_data['HorizontalScreenSize'] = int.from_bytes(header[16:18], byteorder='little')
            header_data['VerticalScreenSize'] = int.from_bytes(header[18:20], byteorder='little')

            # Read and parse the color palette
            file.seek(-769, 2)  # Go to the palette data at the end of the file
            palette = file.read(768)  # Read 256 RGB color entries (3 bytes each)
            color_palette = [palette[i:i+3] for i in range(0, len(palette), 3)]  # Split into RGB triples

    except FileNotFoundError:
        print("File not found.")

    return header_data, color_palette

# Function to display the original image
def display_original_image(file_path):
    global photo, img_label, img_info_label

    image = Image.open(file_path)
    photo = ImageTk.PhotoImage(image)
    
    # Display original image
    img_label = tk.Label(root, image=photo)
    img_label.image = photo
    img_label.pack()

    # Label for the original image
    img_info_label = tk.Label(root, text="Original Image")
    img_info_label.pack()

# Function to display header information
def display_header_info(header_data):
    global header_frame

    # Create a frame to enclose header information
    header_frame = tk.Frame(root, borderwidth=2, relief="groove")
    header_frame.pack()

    header_label = tk.Label(header_frame, text="PCX Header Information")
    header_label.pack()

    for key, value in header_data.items():
        info_label = tk.Label(header_frame, text=f"{key}: {value}")
        info_label.pack()

# Function to display the color palette
def display_color_palette(color_palette):
    global palette_label

    # Create a square palette image
    palette_size = int(len(color_palette) ** 0.5)
    palette_image = Image.new("RGB", (palette_size, palette_size))
    pixels = palette_image.load()

    for i in range(palette_size):
        for j in range(palette_size):
            idx = i * palette_size + j
            if idx < len(color_palette):
                r, g, b = color_palette[idx]
                pixels[i, j] = (r, g, b)
            else:
                pixels[i, j] = (0, 0, 0)  # Fill unused cells with black

    # Resize the palette image to make it smaller
    new_size = (palette_size // 2, palette_size // 2)
    palette_image = palette_image.resize(new_size)

    palette_photo = ImageTk.PhotoImage(palette_image)

    # Display the palette image
    palette_label = tk.Label(root, image=palette_photo)
    palette_label.image = palette_photo
    palette_label.pack()

# Create the main GUI window
root = tk.Tk()
root.title("PCX File Viewer")

# Initialize global variables
header_data = {}
color_palette = {}
photo = None
img_label = None
img_info_label = None
header_frame = None
palette_label = None

# Create and configure the "Open PCX File" button
open_button = tk.Button(root, text="Open PCX File", command=open_pcx_file)
open_button.pack()

# Create and configure the "Close PCX File" button (initially disabled)
close_button = tk.Button(root, text="Close PCX File", command=close_pcx_file, state=tk.DISABLED)
close_button.pack()

root.mainloop()
