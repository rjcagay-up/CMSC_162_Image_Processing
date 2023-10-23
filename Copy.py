# Import necessary libraries
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
# Import necessary libraries
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps, ImageFilter

# Function to open a file based on its type
def open_file(file_type):
    if file_type == "PCX":
        open_pcx_file()
    else:
        upload_display_image()

# Function to close the currently opened file or images
def close_file():
    global current_file_type
    if current_file_type == "PCX":
        close_file_by_type(close_pcx_file)
    else:
        close_all_images()
        close_all_histogram_buttons()

# Function to close the specifically opened PCX file
def close_uploaded_pcx():
    close_file_by_type(close_pcx_file)

# Function to exit the application
def exit_application():
    root.quit()

# Function to close a file by calling a specific close function
def close_file_by_type(close_function):
    close_function()

# Function to open a PCX file
def open_pcx_file():
    # Declare global variables to store various UI elements
    global header_data, color_palette, photo, img_label, img_info_label, header_frame, close_button, palette_canvas

    # Ask user to select a PCX file
    file_path = filedialog.askopenfilename(filetypes=[("PCX Files", "*.pcx")])

    if file_path:
        # Extract header data and color palette from the PCX file
        header_data, color_palette = extract_pcx_header(file_path)
        # Display the original image, header information, color palette, and add related UI elements
        display_original_image(file_path)
        display_header_info(header_data)
        display_color_palette(color_palette)
        close_button.config(state=tk.NORMAL)
        add_histogram_button(file_path)
        add_point_processing_menu(file_path)

# Function to close the specifically opened PCX file
def close_pcx_file():
    # Declare global variables to store various UI elements
    global photo, img_label, img_info_label, header_frame, close_button, palette_canvas

    # Check if a photo exists
    if photo:
        # Clear and hide various UI elements
        img_label.config(image='')
        img_label.pack_forget()
        img_info_label.pack_forget()
        header_frame.pack_forget()
        palette_canvas.pack_forget()
        close_button.config(state=tk.DISABLED)
        # Clear histograms and point processing menu
        close_all_histogram_buttons()
        close_point_processing_menu()
        # Reset photo to None
        photo = None

        # Clear PCX header and color palette information
        global header_data, color_palette
        header_data = {}
        color_palette = []

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
    # Declare global variables to store various UI elements
    global photo, img_label, img_info_label

    # Open the image using PIL
    image = Image.open(file_path)

    # Resize the image to fit within a maximum dimension
    max_dimension = 300
    image.thumbnail((max_dimension, max_dimension))

    # Create a PhotoImage object from the PIL image
    photo = ImageTk.PhotoImage(image)

    # Create a label to display the image
    img_label = tk.Label(root, image=photo)
    img_label.image = photo
    img_label.pack()

    # Create a label to display information about the image
    img_info_label = tk.Label(root, text="Original Image (Resized)")
    img_info_label.pack()

# Function to display header information
def display_header_info(header_data):
    # Declare a global variable to store the header frame
    global header_frame

    # Create a frame to display the header information
    header_frame = tk.Frame(root, borderwidth=2, relief="groove", bg="white")
    header_frame.pack()

    # Create a label for the header information
    header_label = tk.Label(header_frame, text="PCX Header Information", bg="white", font=("Helvetica", 14))
    header_label.pack()

    # Iterate through header data and display each key-value pair
    for key, value in header_data.items():
        info_label = tk.Label(header_frame, text=f"{key}: {value}", bg="white")
        info_label.pack()

# Function to display the color palette
def display_color_palette(color_palette):
    # Declare a global variable to store the palette canvas
    global palette_canvas

    # Create a canvas to display the color palette
    palette_canvas = tk.Canvas(root, width=100, height=100, bg="white")
    palette_canvas.pack()

    # Calculate the number of rows and columns for the color palette grid
    num_colors = len(color_palette)
    rows = int(num_colors ** 0.5)
    cols = (num_colors + rows - 1) // rows

    # Calculate the size of each cell in the color palette grid
    cell_size = 100 // max(rows, cols)

    # Iterate through the color palette and draw rectangles on the canvas
    for i, color in enumerate(color_palette):
        color_hex = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
        row = i // cols
        col = i % cols
        x_start = col * cell_size
        y_start = row * cell_size
        x_end = x_start + cell_size
        y_end = y_start + cell_size

        # Draw a rectangle for each color in the palette
        for r in range(0, cell_size, 3):
            for c in range(0, cell_size, 3):
                x = x_start + c
                y = y_start + r
                palette_canvas.create_rectangle(x, y, x + 3, y + 3, fill=color_hex, outline=color_hex)

# Function to add a button for displaying the image histogram
def add_histogram_button(image_path):
    # Create a button to show the image histogram
    show_histogram_button = tk.Button(root, text="Show Image Histogram", command=lambda path=image_path: show_image_histogram(path))
    show_histogram_button.pack()

# Function to show the image histogram
def show_image_histogram(image_path):
    # Close existing histograms and display the original image
    close_all_histograms()
    image = Image.open(image_path)
    display_original_image(image_path)

    # Split the image into RGB channels
    red_channel, green_channel, blue_channel = image.split()

    # Display each channel separately along with its histogram
    display_image_channel(red_channel, "Red Channel")
    display_image_channel(green_channel, "Green Channel")
    display_image_channel(blue_channel, "Blue Channel")

    display_histogram(red_channel, "Red Channel Histogram")
    display_histogram(green_channel, "Green Channel Histogram")
    display_histogram(blue_channel, "Blue Channel Histogram")

    image.close()

# Function to display an image channel
def display_image_channel(channel, channel_name):
    # Resize the channel image
    channel.thumbnail((200, 200))
    channel_photo = ImageTk.PhotoImage(channel)

    # Create a label to display the channel image
    channel_label = tk.Label(root, image=channel_photo, text=channel_name, compound=tk.TOP)
    channel_label.image = channel_photo
    channel_label.pack(side=tk.LEFT, padx=10, pady=10)

# Function to display a histogram for an image channel
def display_histogram(channel, histogram_name):
    # Calculate normalized histogram values
    histogram_values = channel.histogram()
    max_value = max(histogram_values)
    normalized_values = [int(value / max_value * 100) for value in histogram_values]

    # Create a canvas to display the histogram
    histogram_canvas = tk.Canvas(root, width=200, height=100, bg="white")
    histogram_canvas.pack()

    # Set the width of each histogram bar
    bar_width = 2

    # Draw rectangles for each value in the normalized histogram
    for i, value in enumerate(normalized_values):
        x_start = i * bar_width
        y_start = 100
        x_end = x_start + bar_width
        y_end = 100 - value
        histogram_canvas.create_rectangle(x_start, y_start, x_end, y_end, fill="black")

    # Create a label to display the histogram name
    histogram_label = tk.Label(root, text=histogram_name)
    histogram_label.pack()

# Function to close all displayed images
def close_all_images():
    for label in img_labels:
        label.destroy()
    img_labels.clear()
    close_all_histograms()
    close_point_processing_menu()
    
    
################################################################################################################################################
# Function to apply an Averaging filter
def apply_averaging_filter(image_path):
    image = Image.open(image_path)
    filtered_image = image.filter(ImageFilter.BLUR)
    create_transformed_image_window(filtered_image, "Averaging Filter")

# Function to apply a Median filter
def apply_median_filter(image_path):
    image = Image.open(image_path)
    filtered_image = image.filter(ImageFilter.MedianFilter)
    create_transformed_image_window(filtered_image, "Median Filter")

# Function to apply Highpass filtering with Laplacian operator
def apply_laplacian_highpass(image_path):
    image = Image.open(image_path)
    filtered_image = image.filter(ImageFilter.FIND_EDGES)
    create_transformed_image_window(filtered_image, "Highpass Filtering with Laplacian Operator")

# Function to apply Unsharp masking
def apply_unsharp_masking(image_path):
    image = Image.open(image_path)
    filtered_image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    create_transformed_image_window(filtered_image, "Unsharp Masking")

# Function to apply High boost filtering
def apply_high_boost_filter(image_path, amplification_param):
    image = Image.open(image_path)
    blurred_image = image.filter(ImageFilter.BLUR)
    high_boost_image = Image.blend(image, blurred_image, alpha=amplification_param)
    create_transformed_image_window(high_boost_image, f"High Boost Filter (Amplification: {amplification_param})")

# Function to apply Gradient: Sobel or Prewitt magnitude operator
def apply_gradient_operator(image_path, operator_type):
    image = Image.open(image_path).convert('L')  # Convert to grayscale
    if operator_type == "Sobel":
        gradient_image = image.filter(ImageFilter.FIND_EDGES)
    elif operator_type == "Prewitt":
        gradient_image = image.filter(ImageFilter.CONTOUR)
    else:
        return
    create_transformed_image_window(gradient_image, f"Gradient: {operator_type} Magnitude Operator")
    
    

# Add buttons for each new function in the GUI
def add_filter_buttons(image_path):
    tk.Button(root, text="Averaging Filter", command=lambda: apply_averaging_filter(image_path)).pack(pady=5)
    tk.Button(root, text="Median Filter", command=lambda: apply_median_filter(image_path)).pack(pady=5)
    tk.Button(root, text="Highpass Filtering (Laplacian)", command=lambda: apply_laplacian_highpass(image_path)).pack(pady=5)
    tk.Button(root, text="Unsharp Masking", command=lambda: apply_unsharp_masking(image_path)).pack(pady=5)

    amplification_label = tk.Label(root, text="High Boost Amplification:")
    amplification_label.pack(pady=5)
    amplification_scale = tk.Scale(root, from_=1, to=3, resolution=0.1, orient=tk.HORIZONTAL, length=200)
    amplification_scale.pack(pady=5)
    tk.Button(root, text="High Boost Filtering", command=lambda: apply_high_boost_filter(image_path, amplification_scale.get())).pack(pady=5)

    tk.Button(root, text="Sobel Gradient Operator", command=lambda: apply_gradient_operator(image_path, "Sobel")).pack(pady=5)
    tk.Button(root, text="Prewitt Gradient Operator", command=lambda: apply_gradient_operator(image_path, "Prewitt")).pack(pady=5)
    
    
    
#################################################################################################################################################

# Function to close all displayed histograms
def close_all_histograms():
    # Destroy all widgets related to histograms and histogram buttons
    for widget in root.winfo_children():
        if widget.winfo_class() == 'Canvas' or widget.winfo_class() == 'Label' or widget.winfo_class() == 'Button':
            widget.destroy()

# Function to close all histogram buttons
def close_all_histogram_buttons():
    # Destroy all histogram buttons
    for widget in root.winfo_children():
        if widget.winfo_class() == 'Button':
            widget.destroy()

# Function to add a menu for point processing methods
def add_point_processing_menu(image_path):
    # Declare global variables for point processing menu and variable
    global point_processing_menu, point_processing_var

    # Create a StringVar to store the selected method
    point_processing_var = tk.StringVar()
    point_processing_var.set("Point Processing Methods")

    # Create an OptionMenu for point processing methods
    point_processing_menu = tk.OptionMenu(root, point_processing_var, "Select Method", "Grayscale Transformation", "Negative Transformation", "Thresholding", "Gamma Transformation")
    point_processing_menu.pack(side=tk.RIGHT, padx=10, pady=10)

    # Set a trace to handle selection changes in the point processing menu
    point_processing_var.trace('w', lambda *args: handle_point_processing_selection(image_path))

# Function to close the point processing menu
def close_point_processing_menu():
    point_processing_menu.destroy()

# Function to handle the selection of a point processing method
def handle_point_processing_selection(image_path):
    # Get the selected method from the menu
    selected_method = point_processing_var.get()

    # Call the corresponding function based on the selected method
    if selected_method == "Grayscale Transformation":
        grayscale_transformation(image_path)
    elif selected_method == "Negative Transformation":
        negative_transformation(image_path)
    elif selected_method == "Thresholding":
        manual_thresholding(image_path, threshold_scale.get())
    elif selected_method == "Gamma Transformation":
        gamma_transformation(image_path, gamma_scale.get())

# Function for point processing: Grayscale Transformation
def grayscale_transformation(image_path):
    image = Image.open(image_path).convert('L')  # Convert to grayscale
    create_transformed_image_window(image, "Grayscale Transformation")

# Function for point processing: Negative Transformation
def negative_transformation(image_path):
    image = Image.open(image_path)
    neg_image = ImageOps.invert(image)
    create_transformed_image_window(neg_image, "Negative Transformation")

# Function for point processing: Black/White via Manual Thresholding
def manual_thresholding(image_path, threshold):
    image = Image.open(image_path).convert('L')  # Convert to grayscale
    threshold_image = image.point(lambda p: 255 if p > threshold else 0)
    create_transformed_image_window(threshold_image, f"Thresholding (Threshold={threshold})")

# Function for point processing: Power-law (Gamma) Transformation
def gamma_transformation(image_path, gamma):
    image = Image.open(image_path).convert('L')  # Convert to grayscale
    gamma_image = image.point(lambda p: int(p ** gamma))
    create_transformed_image_window(gamma_image, f"Gamma Transformation (Gamma={gamma})")

    
# Function to create a new window for displaying transformed images
def create_transformed_image_window(image, label_text):
    # Create a new Toplevel window
    transformed_window = tk.Toplevel(root)
    transformed_window.title(label_text)

# Function to create a new window for displaying transformed images
def create_transformed_image_window(image, label_text):
    # Create a new Toplevel window
    transformed_window = tk.Toplevel(root)
    transformed_window.title(label_text)

    # Display the transformed image in the new window
    image.thumbnail((300, 300))
    img_widget = ImageTk.PhotoImage(image)

    img_label = tk.Label(transformed_window, image=img_widget, text=label_text, compound=tk.TOP)
    img_label.image = img_widget
    img_label.pack(side=tk.LEFT, padx=10, pady=10)

# UI for point processing methods
def add_point_processing_ui(image_path):
    frame = tk.Frame(root, bg="white", bd=2, relief="groove")
    frame.pack(side=tk.RIGHT, padx=10, pady=10)

    tk.Label(frame, text="Point Processing Methods", font=("Helvetica", 14), bg="white").pack()

    tk.Button(frame, text="Grayscale Transformation", command=lambda: grayscale_transformation(image_path)).pack(pady=5)
    tk.Button(frame, text="Negative Transformation", command=lambda: negative_transformation(image_path)).pack(pady=5)

    global threshold_scale, gamma_scale

    threshold_label = tk.Label(frame, text="Threshold (0-255):", bg="white")
    threshold_label.pack(pady=5)

    threshold_scale = tk.Scale(frame, from_=0, to=255, orient=tk.HORIZONTAL, length=200)
    threshold_scale.pack(pady=5)

    tk.Button(frame, text="Thresholding", command=lambda: manual_thresholding(image_path, threshold_scale.get())).pack(pady=5)

    gamma_label = tk.Label(frame, text="Gamma (0.1-3.0):", bg="white")
    gamma_label.pack(pady=5)

    gamma_scale = tk.Scale(frame, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, length=200)
    gamma_scale.pack(pady=5)

    tk.Button(frame, text="Gamma Transformation", command=lambda: gamma_transformation(image_path, gamma_scale.get())).pack(pady=5)

# List to store image labels
img_labels = []

# Function to upload and display images
def upload_display_image():
    # Define file types for image selection
    file_types = [
        ('JPG Files', '*.jpg'),
        ('PNG Files', '*.png'),
        ('Bitmap Files', '*.bmp'),
        ('Tag Image File Format Files', '*.tiff'),
        ('All Files', '*.*')
    ]

    # Ask the user to select one or more image files
    select_files = filedialog.askopenfilenames(multiple=True, filetypes=file_types)

    # Process each selected image file
    for file_path in select_files:
        # Open the image using PIL
        image = Image.open(file_path)
        # Resize the image to fit within a maximum dimension
        image.thumbnail((500, 500))

        # Create a PhotoImage object from the PIL image
        img_widget = ImageTk.PhotoImage(image)

        # Create a label to display the image
        img_label = tk.Label(root, image=img_widget, bg="white")
        img_label.image = img_widget
        img_label.pack(side=tk.LEFT, padx=10, pady=10)

        # Append the label to the list for later reference
        img_labels.append(img_label)
        # Add a button to display the histogram and UI for point processing
        add_histogram_button(file_path)
        add_point_processing_ui(file_path)
        
        # Add a button to display the histogram and UI for point processing
        add_histogram_button(file_path)
        add_point_processing_ui(file_path)
        add_filter_buttons(file_path)

        # Close the image file
        image.close()

# Function to create the main application window
# Function to create the main application window
def create_main_window():
    # Declare global variables for various UI elements
    global root, current_file_type, header_data, color_palette, photo, img_label, img_info_label, header_frame, palette_canvas, img_labels, point_processing_menu, point_processing_var, threshold_scale, gamma_scale

    # Create the main Tkinter window
    root = tk.Tk()
    root.title("File Viewer")
    root.configure(bg="light gray")

    # Initialize various variables
    header_data = {}
    color_palette = {}
    photo = None
    img_label = None
    img_info_label = None
    header_frame = None
    palette_canvas = None
    img_labels = []
    current_file_type = None
    point_processing_menu = None
    point_processing_var = None
    threshold_scale = None
    gamma_scale = None

    # Create the menu bar
    menu = tk.Menu(root)
    root.config(menu=menu)

    # Create the "File" menu
    file_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="File", menu=file_menu)

    # Add commands to the "File" menu
    file_menu.add_command(label="Open PCX File", command=lambda: open_file("PCX"), compound=tk.LEFT, image=None)
    file_menu.add_command(label="Upload Image", command=lambda: open_file("Image"), compound=tk.LEFT, image=None)
    file_menu.add_separator()
    file_menu.add_command(label="Close File", command=close_file, compound=tk.LEFT, image=None)
    file_menu.add_command(label="Close Uploaded PCX", command=close_uploaded_pcx, compound=tk.LEFT, image=None)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=exit_application, compound=tk.LEFT, image=None)

    # Start the Tkinter main loop
    root.mainloop()

# Function to add filtering buttons on the right side of the GUI
def add_filter_buttons(image_path):
    frame = tk.Frame(root, bg="white", bd=2, relief="groove")
    frame.pack(side=tk.RIGHT, padx=10, pady=10)

    tk.Label(frame, text="Filtering Methods", font=("Helvetica", 14), bg="white").pack()

    tk.Button(frame, text="Averaging Filter", command=lambda: apply_averaging_filter(image_path)).pack(pady=5)
    tk.Button(frame, text="Median Filter", command=lambda: apply_median_filter(image_path)).pack(pady=5)
    tk.Button(frame, text="Highpass Filtering (Laplacian)", command=lambda: apply_laplacian_highpass(image_path)).pack(pady=5)
    tk.Button(frame, text="Unsharp Masking", command=lambda: apply_unsharp_masking(image_path)).pack(pady=5)

    amplification_label = tk.Label(frame, text="High Boost Amplification:", bg="white")
    amplification_label.pack(pady=5)
    amplification_scale = tk.Scale(frame, from_=1, to=3, resolution=0.1, orient=tk.HORIZONTAL, length=200)
    amplification_scale.pack(pady=5)
    tk.Button(frame, text="High Boost Filtering", command=lambda: apply_high_boost_filter(image_path, amplification_scale.get())).pack(pady=5)

    tk.Button(frame, text="Sobel Gradient Operator", command=lambda: apply_gradient_operator(image_path, "Sobel")).pack(pady=5)
    tk.Button(frame, text="Prewitt Gradient Operator", command=lambda: apply_gradient_operator(image_path, "Prewitt")).pack(pady=5)
    
# Call the function to create the main application window
create_main_window()
