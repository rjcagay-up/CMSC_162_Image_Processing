import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def open_file(file_type):
    # Function to handle the file opening based on file type
    if file_type == "PCX":
        open_pcx_file()
    else:
        upload_display_image()

def close_file():
    # Function to handle closing the file based on the current file type
    global current_file_type
    if current_file_type == "PCX":
        close_file_by_type(close_pcx_file)
    else:
        close_images()

def close_uploaded_pcx():
    # Function to close an uploaded PCX file
    close_file_by_type(close_pcx_file)

def exit_application():
    # Function to exit the application
    root.quit()

def close_file_by_type(close_function):
    # Function to close a file using a specific close function
    close_function()

def open_pcx_file():
    # Function to open a PCX file and display its information
    global header_data, color_palette, photo, img_label, img_info_label, header_frame, close_button, palette_canvas

    # Open a file dialog to select a PCX file
    file_path = filedialog.askopenfilename(filetypes=[("PCX Files", "*.pcx")])

    if file_path:
        # Read PCX file and extract header information
        header_data, color_palette = extract_pcx_header(file_path)
        display_original_image(file_path)
        display_header_info(header_data)
        display_color_palette(color_palette)
        close_button.config(state=tk.NORMAL)

# Function to close the PCX file information
def close_pcx_file():
    global photo, img_label, img_info_label, header_frame, close_button, palette_canvas

    if photo:
        # Clear and hide the displayed elements
        img_label.config(image='')
        img_label.pack_forget()
        img_info_label.pack_forget()
        header_frame.pack_forget()
        palette_canvas.pack_forget()
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
            header_data['Bits per pixel'] = int(header[3])

            # Bytes 4-11: Image Dimensions (4 bytes each, little-endian)
            header_data['Image Dimensions'] = (
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
            header_data['Number of Color Planes'] = int(header[65])

            # Bytes 66-67: Bytes per Line (2 bytes, little-endian)
            header_data['Bytes per Line'] = int.from_bytes(header[66:68], byteorder='little')

            # Bytes 68-71: Palette Info (2 bytes each, little-endian)
            header_data['Palette Information'] = (
                int.from_bytes(header[68:70], byteorder='little'),
                int.from_bytes(header[70:72], byteorder='little')
            )

            # Bytes 16-19: Horizontal and Vertical Screen Size (2 bytes each, little-endian)
            header_data['Horizontal Screen Size'] = int.from_bytes(header[16:18], byteorder='little')
            header_data['Vertical Screen Size'] = int.from_bytes(header[18:20], byteorder='little')

            # Read and parse the color palette
            file.seek(-769, 2)  # Go to the palette data at the end of the file
            palette = file.read(768)  # Read 256 RGB color entries (3 bytes each)
            color_palette = [palette[i:i + 3] for i in range(0, len(palette), 3)]  # Split into RGB triples

    except FileNotFoundError:
        print("File not found.")

    return header_data, color_palette

# Function to display the original image
def display_original_image(file_path):
    global photo, img_label, img_info_label

    # Open the image
    image = Image.open(file_path)

    # Resize the image to a smaller size
    max_dimension = 300  # Set the maximum dimension (width or height) for the displayed image
    image.thumbnail((max_dimension, max_dimension))

    # Create a PhotoImage object from the resized image
    photo = ImageTk.PhotoImage(image)

    # Display the resized image
    img_label = tk.Label(root, image=photo)
    img_label.image = photo
    img_label.pack()

    # Label for the original image
    img_info_label = tk.Label(root, text="Original Image (Resized)")
    img_info_label.pack()

# Function to display header information
def display_header_info(header_data):
    global header_frame

    # Create a frame to enclose header information
    header_frame = tk.Frame(root, borderwidth=2, relief="groove", bg="white")
    header_frame.pack()

    header_label = tk.Label(header_frame, text="PCX Header Information", bg="white", font=("Helvetica", 14))
    header_label.pack()

    for key, value in header_data.items():
        info_label = tk.Label(header_frame, text=f"{key}: {value}", bg="white")
        info_label.pack()

def display_color_palette(color_palette):
    global palette_canvas

    # Create a canvas for color palette
    palette_canvas = tk.Canvas(root, width=150, height=150, bg="white")
    palette_canvas.pack()

    # Calculate the number of rows and columns for the color palette
    num_colors = len(color_palette)
    rows = int(num_colors ** 0.5)
    cols = (num_colors + rows - 1) // rows

    # Calculate the cell size
    cell_size = 100 // max(rows, cols)

    # Draw color squares in the canvas
    for i, color in enumerate(color_palette):
        # Convert the color values from the file to hexadecimal
        color_hex = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
        row = i // cols
        col = i % cols
        x_start = col * cell_size
        y_start = row * cell_size
        x_end = x_start + cell_size
        y_end = y_start + cell_size

        # Draw a rectangle with a more granular representation of colors
        for r in range(0, cell_size, 3):
            for c in range(0, cell_size, 3):
                x = x_start + c
                y = y_start + r
                palette_canvas.create_rectangle(x, y, x + 3, y + 3, fill=color_hex, outline=color_hex)

# Create a list to keep track of displayed image labels
img_labels = []

def upload_display_image():
    # Function to upload and display multiple images
    # allowed file types for image files
    file_types = [
        ('JPG Files', '*.jpg'),
        ('PNG Files', '*.png'),
        ('Bitmap Files', '*.bmp'),
        ('Tag Image File Format Files', '*.tiff'),
        ('All Files', '*.*')
    ]

    # for selecting files 
    select_files = filedialog.askopenfilenames(multiple=True, filetypes=file_types)

    # Calculate the center of the UI
    center_row = root.winfo_reqheight() // 2
    center_column = root.winfo_reqwidth() // 2

    for file_path in select_files:
        # Open the image file
        image = Image.open(file_path)

        # Resize the image 
        image.thumbnail((350, 500))

        # displaying the image in Tkinter
        img_widget = ImageTk.PhotoImage(image)

        # Create a label to display the image
        img_label = tk.Label(root, image=img_widget, bg="white")
        img_label.image = img_widget
        img_label.pack(side=tk.LEFT, padx=10, pady=10)  # Use side, padx, and pady to center-align

        # append the image label 
        img_labels.append(img_label)

        # executing close function 
        image.close()

# close function 
def close_images():
    # Function to close all displayed images
    for label in img_labels:
        label.destroy()  # Destroy the label widget
    img_labels.clear()  # Clear the list of labels

def create_main_window():
    # Function to create the main window
    global root, current_file_type

    root = tk.Tk()
    root.title("File Viewer")
    root.configure(bg="light gray")

    # Initialize global variables
    header_data = {}
    color_palette = {}
    photo = None
    img_label = None
    img_info_label = None
    header_frame = None
    palette_canvas = None
    img_labels = []

    current_file_type = None

    # Create and configure the File menu
    menu = tk.Menu(root)
    root.config(menu=menu)

    file_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="File", menu=file_menu)

    # Configure the file menu
    file_menu.add_command(label="Open PCX File", command=lambda: open_file("PCX"), compound=tk.LEFT, image=None)
    file_menu.add_command(label="Upload Image", command=lambda: open_file("Image"), compound=tk.LEFT, image=None)
    file_menu.add_separator()
    file_menu.add_command(label="Close File", command=close_file, compound=tk.LEFT, image=None)
    file_menu.add_command(label="Close Uploaded PCX", command=close_uploaded_pcx, compound=tk.LEFT, image=None)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=exit_application, compound=tk.LEFT, image=None)

    root.mainloop()

# Run the main window creation function
create_main_window()
