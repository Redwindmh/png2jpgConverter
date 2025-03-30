from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock

class ScrollableLabel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(
            text='No files selected\nDrag and drop files here',
            size_hint_y=None,
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        self.label.bind(texture_size=self.label.setter('size'))
        self.add_widget(self.label)

class DragDropFileChooser(FileChooserListView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drag_start_pos = None
        self.drag_start_time = None
        self.drag_threshold = 5  # pixels
        self.drag_time_threshold = 0.2  # seconds
        
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