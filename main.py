import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk

# Updated Constants for UI - Dark mode with red accent
RED_COLOR = "#D32F2F"     # Primary color (red)
BLACK_COLOR = "#121212"   # Secondary color (dark background)
WHITE_COLOR = "#FFFFFF"   # Tertiary color (text/foreground)
DARK_RED_COLOR = "#B71C1C"  # Darker red for button hover
GRAY_COLOR = "#333333"    # For subtle elements
DEFAULT_FONT = ("Arial", 10)
TITLE_FONT = ("Arial", 14, "bold")
BUTTON_HEIGHT = 2
DEFAULT_PADDING = 10

def resize_image(file_path, output_dir, width=None, height=None, output_format=None):
    """
    Resize an image (JPG or PNG) and optionally convert format.
    
    Args:
        file_path (str): Path to the input image file
        output_dir (str): Directory to save the output file
        width (int, optional): Target width for resizing
        height (int, optional): Target height for resizing
        output_format (str, optional): Output format ('JPG' or 'PNG', or None to maintain original)
        
    Returns:
        str: Path to the converted file
    """
    try:
        # Open image
        with Image.open(file_path) as img:
            # Get original format if not converting
            original_format = img.format if not output_format else None
            
            # Convert to RGB if necessary (for RGBA images when saving as JPEG)
            if img.mode in ('RGBA', 'LA') and (output_format == 'JPG' or (not output_format and original_format == 'JPEG')):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB' and img.mode != 'RGBA':
                img = img.convert('RGB')
            
            # Resize if specified
            if width and height:
                img = img.resize((width, height), Image.LANCZOS)
            
            # Determine output filename and format
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            if output_format == 'JPG':
                output_path = os.path.join(output_dir, f"{base_name}.jpg")
                img.save(output_path, 'JPEG', quality=95)
            elif output_format == 'PNG':
                output_path = os.path.join(output_dir, f"{base_name}.png")
                img.save(output_path, 'PNG')
            else:
                # Keep original format
                ext = os.path.splitext(file_path)[1].lower()
                output_path = os.path.join(output_dir, f"{base_name}_resized{ext}")
                if original_format == 'JPEG':
                    img.save(output_path, 'JPEG', quality=95)
                else:
                    img.save(output_path, original_format)
                    
            return output_path
    except Exception as e:
        raise Exception(f'Error processing {file_path}: {str(e)}')

def ensure_output_directory(output_dir):
    """
    Ensure the output directory exists.
    
    Args:
        output_dir (str): Path to the output directory
        
    Raises:
        Exception: If directory creation fails
    """
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            raise Exception(f'Error creating output directory: {str(e)}')

class ImageProcessorApp(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, bg=BLACK_COLOR, **kwargs)
        self.master = master
        self.master.title("Image Processor")
        self.master.geometry("800x800")
        self.master.configure(bg=BLACK_COLOR)
        self.pack(fill=tk.BOTH, expand=True)
        
        # Files management
        self.selected_files = []
        self.is_batch_mode = False
        self.operation_mode = tk.StringVar(value="convert")  # Default: convert PNG to JPG
        
        # Create the UI components
        self._create_header()
        self._create_content_layout()
        
        # Configure drag and drop if available
        self._setup_drag_drop()

    def _setup_drag_drop(self):
        """Setup drag and drop if TkinterDnD is available."""
        try:
            self.master.drop_target_register(tk.DND_FILES)
            self.master.dnd_bind('<<Drop>>', self._on_drop)
        except:
            # TkinterDnD might not be available
            pass

    def _create_header(self):
        """Create the header section with logo and title."""
        header_frame = tk.Frame(self, bg=BLACK_COLOR, height=200)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)  # Don't shrink
        
        # Logo container
        logo_container = tk.Frame(header_frame, bg=BLACK_COLOR, height=160)
        logo_container.pack(fill=tk.X, padx=20, pady=0)
        logo_container.pack_propagate(False)
        
        # Logo
        try:
            logo_img = Image.open('assets/hendricks-high-resolution-logo-color-on-transparent-background.png')
            logo_img = logo_img.resize((int(logo_img.width * 150 / logo_img.height), 150), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(logo_container, image=logo_photo, bg=BLACK_COLOR)
            logo_label.image = logo_photo  # Keep reference
            logo_label.pack(pady=5)
        except Exception as e:
            # Fallback if logo can't be loaded
            fallback_label = tk.Label(logo_container, text="Image Processor", font=("Arial", 24, "bold"), 
                                     bg=BLACK_COLOR, fg=RED_COLOR)
            fallback_label.pack(pady=50)
        
        # Title
        title_container = tk.Frame(header_frame, bg=BLACK_COLOR, height=40)
        title_container.pack(fill=tk.X, padx=20, pady=0)
        title_container.pack_propagate(False)
        
        title_label = tk.Label(
            title_container, 
            text="Image Processor", 
            font=TITLE_FONT, 
            fg=WHITE_COLOR,
            bg=BLACK_COLOR
        )
        title_label.pack(pady=5)

    def _create_content_layout(self):
        """Create the main content layout with all interactive elements."""
        content_frame = tk.Frame(self, bg=BLACK_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=0)
        
        # Mode selection
        self._add_mode_selection(content_frame)
        self._add_file_buttons(content_frame)
        self._add_files_display(content_frame)
        self._add_size_inputs(content_frame)
        self._add_output_directory(content_frame)
        self._add_process_button(content_frame)
        self._add_status_label(content_frame)

    def _add_mode_selection(self, parent):
        """Add operation mode selection."""
        mode_frame = tk.LabelFrame(parent, text="Operation Mode", bg=BLACK_COLOR, fg=WHITE_COLOR)
        mode_frame.pack(fill=tk.X, pady=10)
        
        # Create radio buttons for different operation modes
        convert_radio = tk.Radiobutton(
            mode_frame, 
            text="Convert PNG to JPG", 
            variable=self.operation_mode,
            value="convert",
            bg=BLACK_COLOR,
            fg=WHITE_COLOR,
            selectcolor=BLACK_COLOR,
            activebackground=BLACK_COLOR,
            activeforeground=RED_COLOR
        )
        convert_radio.pack(anchor=tk.W, padx=10, pady=5)
        
        resize_jpg_radio = tk.Radiobutton(
            mode_frame, 
            text="Resize JPG files", 
            variable=self.operation_mode,
            value="resize_jpg",
            bg=BLACK_COLOR,
            fg=WHITE_COLOR,
            selectcolor=BLACK_COLOR,
            activebackground=BLACK_COLOR,
            activeforeground=RED_COLOR
        )
        resize_jpg_radio.pack(anchor=tk.W, padx=10, pady=5)

    def _add_file_buttons(self, parent):
        """Add file selection buttons to the parent layout."""
        btn_frame = tk.Frame(parent, bg=BLACK_COLOR)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Configure ttk style for buttons
        style = ttk.Style()
        style.configure('Red.TButton', font=DEFAULT_FONT, background=RED_COLOR)
        
        # Single file button
        self.single_file_btn = tk.Button(
            btn_frame,
            text="Select Single File",
            command=lambda: self.show_file_chooser(False),
            bg=RED_COLOR,
            fg=BLACK_COLOR,
            activebackground=DARK_RED_COLOR,
            activeforeground=BLACK_COLOR
        )
        self.single_file_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Multiple files button
        self.batch_file_btn = tk.Button(
            btn_frame,
            text="Select Multiple Files",
            command=lambda: self.show_file_chooser(True),
            bg=RED_COLOR,
            fg=BLACK_COLOR,
            activebackground=DARK_RED_COLOR,
            activeforeground=BLACK_COLOR
        )
        self.batch_file_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

    def _add_files_display(self, parent):
        """Add scrollable files display to the parent layout."""
        files_frame = tk.LabelFrame(parent, text="Selected Files", bg=BLACK_COLOR, fg=WHITE_COLOR)
        files_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.files_text = ScrolledText(
            files_frame,
            height=6,
            font=DEFAULT_FONT,
            wrap=tk.WORD,
            bg=GRAY_COLOR,
            fg=WHITE_COLOR,
            insertbackground=WHITE_COLOR
        )
        self.files_text.insert(tk.END, "No files selected\nDrag and drop files here or use the buttons above")
        self.files_text.config(state=tk.DISABLED)
        self.files_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add clear button
        clear_btn_frame = tk.Frame(files_frame, bg=BLACK_COLOR)
        clear_btn_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.clear_btn = tk.Button(
            clear_btn_frame,
            text="Clear Selected Files",
            command=self.clear_selected_files,
            bg=RED_COLOR,
            fg=BLACK_COLOR,
            activebackground=DARK_RED_COLOR,
            activeforeground=BLACK_COLOR
        )
        self.clear_btn.pack(side=tk.RIGHT)

    def _add_size_inputs(self, parent):
        """Add width and height input fields to the parent layout."""
        size_frame = tk.LabelFrame(parent, text="Image Size (Optional)", bg=BLACK_COLOR, fg=WHITE_COLOR)
        size_frame.pack(fill=tk.X, pady=10)
        
        # Width input
        width_label = tk.Label(size_frame, text="Target Width:", font=DEFAULT_FONT, bg=BLACK_COLOR, fg=WHITE_COLOR)
        width_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.width_input = tk.Entry(size_frame, font=DEFAULT_FONT, bg=GRAY_COLOR, fg=WHITE_COLOR, insertbackground=WHITE_COLOR)
        self.width_input.insert(0, "")
        self.width_input.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Height input
        height_label = tk.Label(size_frame, text="Target Height:", font=DEFAULT_FONT, bg=BLACK_COLOR, fg=WHITE_COLOR)
        height_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.height_input = tk.Entry(size_frame, font=DEFAULT_FONT, bg=GRAY_COLOR, fg=WHITE_COLOR, insertbackground=WHITE_COLOR)
        self.height_input.insert(0, "")
        self.height_input.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Configure grid
        size_frame.columnconfigure(1, weight=1)

    def _add_output_directory(self, parent):
        """Add output directory input to the parent layout."""
        output_frame = tk.LabelFrame(parent, text="Output Settings", bg=BLACK_COLOR, fg=WHITE_COLOR)
        output_frame.pack(fill=tk.X, pady=10)
        
        # Inner frame for layout
        inner_frame = tk.Frame(output_frame, bg=BLACK_COLOR)
        inner_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Label
        output_label = tk.Label(inner_frame, text="Output Directory:", font=DEFAULT_FONT, bg=BLACK_COLOR, fg=WHITE_COLOR)
        output_label.pack(side=tk.LEFT, padx=5)
        
        # Entry
        self.output_path = tk.Entry(inner_frame, font=DEFAULT_FONT, bg=GRAY_COLOR, fg=WHITE_COLOR, insertbackground=WHITE_COLOR)
        self.output_path.insert(0, os.path.expanduser('~/Pictures'))
        self.output_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Browse button
        browse_btn = tk.Button(
            inner_frame, 
            text="Browse...", 
            command=self.browse_output_dir,
            bg=RED_COLOR,
            fg=BLACK_COLOR,
            activebackground=DARK_RED_COLOR,
            activeforeground=BLACK_COLOR
        )
        browse_btn.pack(side=tk.RIGHT, padx=5)

    def _add_process_button(self, parent):
        """Add process button to the parent layout."""
        convert_frame = tk.Frame(parent, bg=BLACK_COLOR)
        convert_frame.pack(fill=tk.X, pady=10)
        
        self.process_btn = tk.Button(
            convert_frame,
            text="Process",
            font=("Arial", 12, "bold"),
            bg=RED_COLOR,
            fg=BLACK_COLOR,
            activebackground=DARK_RED_COLOR,
            activeforeground=BLACK_COLOR,
            height=2,
            command=self.process_files
        )
        self.process_btn.pack(fill=tk.X, padx=20)

    def _add_status_label(self, parent):
        """Add status label to the parent layout."""
        status_frame = tk.Frame(parent, bg=BLACK_COLOR)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=DEFAULT_FONT,
            bg=BLACK_COLOR,
            fg=WHITE_COLOR
        )
        self.status_label.pack()

    def show_file_chooser(self, is_batch_mode):
        """Display file chooser dialog for image selection."""
        self.is_batch_mode = is_batch_mode
        operation = self.operation_mode.get()
        
        filetypes = []
        if operation == "convert":
            filetypes = [("PNG Files", "*.png")]
            title = "Select PNG Files" if is_batch_mode else "Select PNG File"
        elif operation == "resize_jpg":
            filetypes = [("JPG Files", "*.jpg"), ("JPEG Files", "*.jpeg")]
            title = "Select JPG Files" if is_batch_mode else "Select JPG File"
        
        if is_batch_mode:
            file_paths = filedialog.askopenfilenames(
                title=title,
                filetypes=filetypes
            )
            if file_paths:
                if self.is_batch_mode:
                    self.selected_files.extend(file_paths)
                else:
                    self.selected_files = list(file_paths)
                self._update_files_display()
        else:
            file_path = filedialog.askopenfilename(
                title=title,
                filetypes=filetypes
            )
            if file_path:
                self.selected_files = [file_path]
                self._update_files_display()

    def _on_drop(self, event):
        """Handle drag and drop file events."""
        files = self._parse_drop_data(event.data)
        operation = self.operation_mode.get()
        
        filtered_files = []
        if operation == "convert":
            filtered_files = [f for f in files if f.lower().endswith('.png')]
            if not filtered_files:
                self.show_error("Please drop PNG files only.")
                return
        elif operation == "resize_jpg":
            filtered_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg'))]
            if not filtered_files:
                self.show_error("Please drop JPG files only.")
                return
            
        if self.is_batch_mode:
            self.selected_files.extend(filtered_files)
        else:
            self.selected_files = filtered_files
            
        self._update_files_display()

    def _parse_drop_data(self, data):
        """Parse data from drag and drop event."""
        # Handle different data formats on different platforms
        if os.name == 'nt':  # Windows
            files = data.split('} {')
            for i in range(len(files)):
                if i == 0:
                    files[i] = files[i].replace('{', '')
                if i == len(files) - 1:
                    files[i] = files[i].replace('}', '')
            return files
        else:  # macOS, Linux
            return [data.strip().replace('file://', '').replace('\r\n', '')]

    def _update_files_display(self):
        """Update the files display with selected files."""
        self.files_text.config(state=tk.NORMAL)
        self.files_text.delete(1.0, tk.END)
        
        if self.selected_files:
            files_text = f"Selected {len(self.selected_files)} file(s):\n\n"
            for file in self.selected_files:
                files_text += f"• {os.path.basename(file)}\n"
            self.files_text.insert(tk.END, files_text)
        else:
            self.files_text.insert(tk.END, "No files selected\nDrag and drop files here or use the buttons above")
            
        self.files_text.config(state=tk.DISABLED)

    def browse_output_dir(self):
        """Open dialog to select output directory."""
        directory = filedialog.askdirectory(
            initialdir=self.output_path.get(),
            title="Select Output Directory"
        )
        if directory:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, directory)

    def process_files(self):
        """Start the process of converting or resizing files."""
        if not self.selected_files:
            self.show_error('Please select at least one file')
            return
            
        output_dir = self.output_path.get().strip()
        if not output_dir:
            output_dir = os.path.expanduser('~/Pictures')
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, output_dir)
            
        try:
            ensure_output_directory(output_dir)
        except Exception as e:
            self.show_error(str(e))
            return
        
        # Get target size
        try:
            width = int(self.width_input.get()) if self.width_input.get().strip() else None
            height = int(self.height_input.get()) if self.height_input.get().strip() else None
        except ValueError:
            self.show_error('Please enter valid numbers for width and height')
            return
        
        # Determine operation mode
        operation = self.operation_mode.get()
        
        # Show progress dialog
        self.progress_window = tk.Toplevel(self.master)
        self.progress_window.title("Processing Files")
        self.progress_window.geometry("400x150")
        self.progress_window.resizable(False, False)
        self.progress_window.transient(self.master)
        self.progress_window.grab_set()
        self.progress_window.configure(bg=BLACK_COLOR)
        
        progress_frame = tk.Frame(self.progress_window, padx=20, pady=20, bg=BLACK_COLOR)
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Processing files...",
            font=DEFAULT_FONT,
            bg=BLACK_COLOR,
            fg=WHITE_COLOR
        )
        self.progress_label.pack(pady=10)
        
        # Configure ttk style for progress bar
        style = ttk.Style()
        style.configure("red.Horizontal.TProgressbar", 
                       background=RED_COLOR, 
                       troughcolor=GRAY_COLOR)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=350,
            mode='determinate',
            style="red.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(pady=10, fill=tk.X)
        
        # Start processing in a separate thread
        processing_thread = threading.Thread(
            target=self.process_files_thread,
            args=(self.selected_files, output_dir, width, height, operation),
            daemon=True
        )
        processing_thread.start()

    def process_files_thread(self, files, output_dir, width, height, operation):
        """Background thread to perform file processing."""
        total_files = len(files)
        successful_conversions = 0
        
        for i, file_path in enumerate(files, 1):
            try:
                # Update progress
                progress_percent = int((i-1) / total_files * 100)
                self.update_progress(f"Processing {i}/{total_files}: {os.path.basename(file_path)}", progress_percent)
                
                # Check if file exists
                if not os.path.exists(file_path):
                    self.show_error(f"File not found: {file_path}")
                    continue
                
                # Process image based on operation
                if operation == "convert":
                    # Convert PNG to JPG
                    resize_image(file_path, output_dir, width, height, output_format='JPG')
                    operation_text = "converted"
                elif operation == "resize_jpg":
                    # Resize JPG without conversion
                    resize_image(file_path, output_dir, width, height, output_format=None)
                    operation_text = "resized"
                
                successful_conversions += 1
                
                # Update final progress
                progress_percent = int(i / total_files * 100)
                self.update_progress(f"Processing {i}/{total_files}: {os.path.basename(file_path)}", progress_percent)
                
            except Exception as e:
                self.show_error(f"Error processing {os.path.basename(file_path)}: {str(e)}")
        
        # Close progress window and update status
        self.close_progress_window()
        
        # Update status and clear selected files
        status_text = f'Processing complete! {successful_conversions}/{total_files} files {operation_text} and saved to {output_dir}'
        self.master.after(0, lambda: self._complete_processing(status_text))
        
    def _complete_processing(self, status_text):
        """Update UI after processing is complete and clear selected files."""
        # Update status
        self.status_label.config(text=status_text)
        
        # Clear selected files
        self.selected_files = []
        self._update_files_display()

    def update_progress(self, text, percent):
        """Update progress dialog."""
        self.master.after(0, lambda: self._update_progress_ui(text, percent))

    def _update_progress_ui(self, text, percent):
        """Update the progress UI elements."""
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text=text)
        if hasattr(self, 'progress_bar'):
            self.progress_bar['value'] = percent

    def close_progress_window(self):
        """Close the progress window."""
        self.master.after(0, self._close_progress_window_ui)

    def _close_progress_window_ui(self):
        """Close the progress window from the main thread."""
        if hasattr(self, 'progress_window') and self.progress_window:
            self.progress_window.grab_release()
            self.progress_window.destroy()
            self.progress_window = None

    def show_error(self, message):
        """Display error message box."""
        messagebox.showerror("Error", message)

    def clear_selected_files(self):
        """Clear all selected files."""
        if not self.selected_files:
            return
            
        self.selected_files = []
        self._update_files_display()
        self.status_label.config(text="File selection cleared")


if __name__ == "__main__":
    # Initialize Tk
    root = tk.Tk()
    
    # Try to import TkinterDnD for drag-and-drop support
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
        tk.DND_FILES = "DND_FILES"
    except ImportError:
        # If import fails, just use regular Tk
        print("Note: tkinterdnd2 not available, drag and drop disabled")
        # Define a placeholder for DND_FILES to avoid errors
        tk.DND_FILES = "DND_FILES"  
    
    app = ImageProcessorApp(root)
    root.mainloop()