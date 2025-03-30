import os
import threading
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.clock import Clock

from .widgets import ScrollableLabel, DragDropFileChooser
from ..utils.image_converter import convert_image, ensure_output_directory

# Constants for UI
BLUE_COLOR = (0.2, 0.6, 0.8, 1)
GREEN_COLOR = (0.2, 0.8, 0.2, 1)
TEXT_COLOR = (0.2, 0.2, 0.2, 1)
DEFAULT_FONT_SIZE = '16sp'
TITLE_FONT_SIZE = '28sp'
BUTTON_HEIGHT = 60
DEFAULT_PADDING = [20, 0]

class PngToJpgConverter(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 0
        self.spacing = 0
        
        # Create the UI components
        self._create_header()
        self._create_content_layout()
        
        # File chooser popup
        self.file_chooser_popup = None
        self.selected_files = []
        self.is_batch_mode = False
        
        # Progress popup
        self.progress_popup = None
        self.progress_label = None
        
        # Drag and drop properties
        self.drag_start_pos = None
        self.drag_start_time = None
        self.drag_threshold = 5
        self.drag_time_threshold = 0.2

    def _create_header(self):
        """Create the header section with logo and title."""
        header_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=200,
            padding=0,
            spacing=0
        )
        
        # Logo container with background
        logo_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=170,
            padding=DEFAULT_PADDING
        )
        
        # Logo
        logo = Image(
            source='assets/hendricks-high-resolution-logo-color-on-transparent-background.png',
            size_hint_y=None,
            height=150,
            allow_stretch=True,
            keep_ratio=True
        )
        logo_container.add_widget(logo)
        header_layout.add_widget(logo_container)
        
        # Title with background
        title_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=30,
            padding=DEFAULT_PADDING
        )
        title_container.add_widget(Label(
            text='PNG to JPG Converter',
            size_hint_y=None,
            height=30,
            font_size=TITLE_FONT_SIZE,
            bold=True,
            color=TEXT_COLOR
        ))
        header_layout.add_widget(title_container)
        
        self.add_widget(header_layout)

    def _create_content_layout(self):
        """Create the main content layout with all interactive elements."""
        content_layout = BoxLayout(
            orientation='vertical',
            padding=[20, 0],
            spacing=15
        )
        
        self._add_file_buttons(content_layout)
        self._add_files_display(content_layout)
        self._add_size_inputs(content_layout)
        self._add_output_directory(content_layout)
        self._add_convert_button(content_layout)
        self._add_status_label(content_layout)
        
        self.add_widget(content_layout)

    def _add_file_buttons(self, parent):
        """Add file selection buttons to the parent layout."""
        file_buttons_layout = BoxLayout(
            size_hint_y=None,
            height=BUTTON_HEIGHT,
            spacing=20,
            padding=[10, 0]
        )
        
        # Single file button
        self.single_file_btn = Button(
            text='Select Single File',
            size_hint_x=0.5,
            font_size=DEFAULT_FONT_SIZE,
            background_color=BLUE_COLOR
        )
        self.single_file_btn.bind(on_press=self.show_file_chooser)
        file_buttons_layout.add_widget(self.single_file_btn)
        
        # Batch file button
        self.batch_file_btn = Button(
            text='Select Multiple Files',
            size_hint_x=0.5,
            font_size=DEFAULT_FONT_SIZE,
            background_color=BLUE_COLOR
        )
        self.batch_file_btn.bind(on_press=self.show_file_chooser)
        file_buttons_layout.add_widget(self.batch_file_btn)
        
        parent.add_widget(file_buttons_layout)

    def _add_files_display(self, parent):
        """Add scrollable files display to the parent layout."""
        self.files_label = ScrollableLabel(
            size_hint_y=None,
            height=120,
            do_scroll_x=False,
            do_scroll_y=True
        )
        parent.add_widget(self.files_label)

    def _add_size_inputs(self, parent):
        """Add width and height input fields to the parent layout."""
        size_layout = GridLayout(
            cols=2,
            size_hint_y=None,
            height=120,
            spacing=15,
            padding=[0, 10]
        )
        
        # Width input
        size_layout.add_widget(Label(
            text='Target Width:',
            font_size=DEFAULT_FONT_SIZE
        ))
        self.width_input = TextInput(
            text='',
            multiline=False,
            hint_text='Enter width (optional)',
            font_size=DEFAULT_FONT_SIZE
        )
        size_layout.add_widget(self.width_input)
        
        # Height input
        size_layout.add_widget(Label(
            text='Target Height:',
            font_size=DEFAULT_FONT_SIZE
        ))
        self.height_input = TextInput(
            text='',
            multiline=False,
            hint_text='Enter height (optional)',
            font_size=DEFAULT_FONT_SIZE
        )
        size_layout.add_widget(self.height_input)
        
        parent.add_widget(size_layout)

    def _add_output_directory(self, parent):
        """Add output directory input to the parent layout."""
        output_layout = BoxLayout(
            size_hint_y=None,
            height=BUTTON_HEIGHT,
            spacing=10,
            padding=[0, 10]
        )
        
        output_layout.add_widget(Label(
            text='Output Directory:',
            font_size=DEFAULT_FONT_SIZE
        ))
        
        self.output_path = TextInput(
            text=os.path.expanduser('~/Pictures'),
            size_hint_x=0.7,
            font_size=DEFAULT_FONT_SIZE
        )
        output_layout.add_widget(self.output_path)
        
        parent.add_widget(output_layout)

    def _add_convert_button(self, parent):
        """Add convert button to the parent layout."""
        self.convert_btn = Button(
            text='Convert',
            size_hint_y=None,
            height=BUTTON_HEIGHT,
            font_size='18sp',
            background_color=GREEN_COLOR
        )
        self.convert_btn.bind(on_press=self.convert_files)
        parent.add_widget(self.convert_btn)

    def _add_status_label(self, parent):
        """Add status label to the parent layout."""
        self.status_label = Label(
            text='Ready',
            size_hint_y=None,
            height=40,
            font_size='14sp'
        )
        parent.add_widget(self.status_label)

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        self.drag_start_pos = touch.pos
        self.drag_start_time = Clock.get_time()
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if touch.is_mouse_scrolling:
            return False
        if self.drag_start_pos is None:
            return super().on_touch_up(touch)
            
        drag_distance = (touch.pos[0] - self.drag_start_pos[0])**2 + (touch.pos[1] - self.drag_start_pos[1])**2
        drag_time = Clock.get_time() - self.drag_start_time
        
        if drag_distance < self.drag_threshold**2 and drag_time < self.drag_time_threshold:
            # This was a tap, not a drag
            return super().on_touch_up(touch)
            
        self.drag_start_pos = None
        self.drag_start_time = None
        return super().on_touch_up(touch)

    def show_file_chooser(self, instance):
        """Display file chooser popup for PNG selection."""
        content = BoxLayout(orientation='vertical', padding=10)
        
        # Create file chooser with improved scrolling
        file_chooser = DragDropFileChooser(
            path=os.path.expanduser('~'),
            filters=['*.png'],
            show_hidden=False,
            multiselect=True
        )
        
        # Add buttons
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        select_btn = Button(text='Select')
        select_btn.bind(on_press=lambda x: self.select_files(file_chooser))
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=lambda x: self.file_chooser_popup.dismiss())
        
        button_layout.add_widget(select_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(file_chooser)
        content.add_widget(button_layout)
        
        # Create and show popup
        self.is_batch_mode = instance == self.batch_file_btn
        self.file_chooser_popup = Popup(
            title='Select PNG Files',
            content=content,
            size_hint=(0.9, 0.9)
        )
        self.file_chooser_popup.open()

    def select_files(self, file_chooser):
        """Process file selection from the file chooser."""
        if not hasattr(file_chooser, 'selection'):
            return
            
        if self.is_batch_mode:
            self.selected_files.extend(file_chooser.selection)
        else:
            self.selected_files = file_chooser.selection
        
        # Update files label
        if self.selected_files:
            files_text = f'Selected {len(self.selected_files)} file(s):\n\n'
            for file in self.selected_files:
                files_text += f'• {os.path.basename(file)}\n'
            self.files_label.label.text = files_text
        else:
            self.files_label.label.text = 'No files selected\nDrag and drop files here'
        
        if self.file_chooser_popup:
            self.file_chooser_popup.dismiss()

    def convert_files(self, instance):
        """Start the process of converting PNG files to JPG."""
        if not self.selected_files:
            self.show_error('Please select at least one PNG file')
            return
            
        output_dir = self.output_path.text.strip()
        if not output_dir:
            output_dir = os.path.expanduser('~/Pictures')
            self.output_path.text = output_dir
            
        try:
            ensure_output_directory(output_dir)
        except Exception as e:
            self.show_error(str(e))
            return
        
        # Get target size
        try:
            width = int(self.width_input.text) if self.width_input.text.strip() else None
            height = int(self.height_input.text) if self.height_input.text.strip() else None
        except ValueError:
            self.show_error('Please enter valid numbers for width and height')
            return
        
        # Show progress popup
        self.show_progress_popup()
        
        # Start conversion in a separate thread
        conversion_thread = threading.Thread(
            target=self.convert_files_thread,
            args=(self.selected_files, output_dir, width, height),
            daemon=True  # Allow application to exit even if thread is running
        )
        conversion_thread.start()

    def convert_files_thread(self, files, output_dir, width, height):
        """Background thread to perform file conversion."""
        total_files = len(files)
        successful_conversions = 0
        
        for i, file_path in enumerate(files, 1):
            try:
                # Update progress
                self.update_progress(f'Converting {i}/{total_files}: {os.path.basename(file_path)}')
                
                # Check if file exists
                if not os.path.exists(file_path):
                    self.show_error(f"File not found: {file_path}")
                    continue
                
                # Convert image
                convert_image(file_path, output_dir, width, height)
                successful_conversions += 1
                
            except Exception as e:
                self.show_error(f"Error converting {os.path.basename(file_path)}: {str(e)}")
        
        # Close progress popup and update status
        self.close_progress_popup()
        self.status_label.text = f'Conversion complete! {successful_conversions}/{total_files} files saved to {output_dir}'

    def show_progress_popup(self):
        """Show progress popup during conversion."""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.progress_label = Label(text='Converting files...')
        content.add_widget(self.progress_label)
        
        self.progress_popup = Popup(
            title='Converting Files',
            content=content,
            size_hint=(0.8, 0.3)
        )
        self.progress_popup.open()

    def update_progress(self, text):
        """Update progress popup text."""
        if self.progress_label:
            self.progress_label.text = text

    def close_progress_popup(self):
        """Close the progress popup."""
        if self.progress_popup:
            self.progress_popup.dismiss()
            self.progress_popup = None

    def show_error(self, message):
        """Display error popup with message."""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        content.add_widget(Label(text=message))
        
        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.8, 0.3)
        )
        popup.open() 