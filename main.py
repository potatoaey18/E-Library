from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from android.permissions import request_permissions, Permission
from kivy.utils import platform
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import os
import tempfile
from pptx import Presentation
from PIL import Image, ImageDraw, ImageFont 
import io
import fitz
from kivy.config import Config

# Configuration
Config.set('kivy', 'window_icon', '')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '412')
Config.set('graphics', 'height', '732')
Config.set('graphics', 'orientation', 'portrait')

Window.rotation = 0
Window.size = (412, 615)


class MainMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.loading_popup = None
        self.current_navigation_path = ""  # Track current navigation path

        # Orange background
        with self.canvas.before:
            Color(1, 0.6, 0.2, 1)  # Orange
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Top spacer
        self.add_widget(BoxLayout(size_hint=(1, 0.2)))

        # White card - make size_hint responsive instead of fixed width
        self.card = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10),
            size_hint=(0.9, None),
            pos_hint={'center_x': 0.5}
        )
        self.card.bind(minimum_height=self.card.setter('height'))

        with self.card.canvas.before:
            Color(1, 1, 1, 1)  # White
            self.card.rect = RoundedRectangle(
                size=self.card.size,
                pos=self.card.pos,
                radius=[dp(15)]
            )
        self.card.bind(size=self._update_card_bg, pos=self._update_card_bg)

        # Title - use adaptive sizing
        title_label = Label(
            text="Gregor-E Library",
            font_size=self.get_adaptive_font_size(28),
            bold=True,
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=dp(40)
        )
        self.card.add_widget(title_label)

        # Spacer
        self.card.add_widget(BoxLayout(size_hint=(1, None), height=dp(5)))

        # Tagline - use adaptive sizing
        subheading_label = Label(
            text="Your digital library at your fingertips",
            font_size=self.get_adaptive_font_size(14),
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=dp(30)
        )
        self.card.add_widget(subheading_label)

        # Spacer
        self.card.add_widget(BoxLayout(size_hint=(1, None), height=dp(10)))

        # Buttons
        self._add_pill_button("Grade 11", self.show_grade11)
        self._add_pill_button("Grade 12", self.show_grade12)
        self._add_pill_button("About Us", self.show_about_us)

        # Add card to main layout
        self.add_widget(self.card)

        # Bottom spacer
        self.add_widget(BoxLayout(size_hint=(1, 0.2)))

        # Update layout when window size changes
        Window.bind(on_resize=self.on_window_resize)

    def on_window_resize(self, instance, width, height):
        """Handle window resize events to update adaptive layouts"""
        # Update card size based on window dimensions
        self.card.height = self.card.minimum_height

        # Update fonts
        for child in self.card.children:
            if isinstance(child, Label):
                if "Gregor-E Library" in child.text:
                    child.font_size = self.get_adaptive_font_size(28)
                else:
                    child.font_size = self.get_adaptive_font_size(14)
            elif isinstance(child, Button):
                child.font_size = self.get_adaptive_font_size(16)

    def get_adaptive_font_size(self, base_size):
        """Calculate font size based on screen width"""
        # Get the smaller dimension (portrait vs landscape)
        min_dimension = min(Window.width, Window.height)
        # Base calculation for adaptive font size
        # Reference width: 360dp (common phone width)
        reference_width = 360
        return sp(base_size * (min_dimension / reference_width) * 0.7)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_card_bg(self, instance, *args):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def _add_pill_button(self, text, callback):
        btn = Button(
            text=text,
            size_hint=(1, None),
            height=dp(50),  # Increased touch target for mobile
            font_size=self.get_adaptive_font_size(16),
            color=(0, 0, 0, 1),
            background_color=(0, 0, 0, 0)
        )
        btn.bind(on_release=callback)

        with btn.canvas.before:
            Color(0.8, 0.8, 0.8, 1)  # Light gray
            btn.rect = RoundedRectangle(
                size=btn.size,
                pos=btn.pos,
                radius=[dp(25)]  # Larger radius for better look on mobile
            )
        btn.bind(size=self._update_btn_shape, pos=self._update_btn_shape)

        self.card.add_widget(btn)

    def _update_btn_shape(self, btn, *args):
        btn.rect.pos = btn.pos
        btn.rect.size = btn.size

    def show_grade11(self, instance):
        self._show_quarters_popup("Grade 11")

    def show_grade12(self, instance):
        self._show_quarters_popup("Grade 12")

    def _show_quarters_popup(self, title):
        self.current_navigation_path = title

        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self._set_dark_bg(popup_content)

        popup_content.add_widget(Label(
            text=f"{title} - Select Quarter",
            font_size=self.get_adaptive_font_size(20),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        ))

        quarters = ["1st", "2nd", "3rd", "4th"]
        for i, quarter in enumerate(quarters, start=1):
            quarter_button = Button(
                text=f"📖 {quarter} Quarter",
                size_hint=(1, None),
                height=dp(50),  # Increased height for better touch targets
                font_size=self.get_adaptive_font_size(16)
            )
            # Fix: Capture the loop variable i in the lambda function
            quarter_num = i  # Explicitly get the quarter number
            quarter_button.bind(on_release=lambda btn, q=quarter_num:
            self._show_subjects_popup(f"{title} - {quarters[q - 1]} Quarter", q))
            self._style_pill_button(quarter_button, (0.5, 0.5, 0.5, 1), (1, 1, 1, 1))
            popup_content.add_widget(quarter_button)

        close_button = Button(
            text="❌ Close",
            size_hint=(1, None),
            height=dp(50),
            font_size=self.get_adaptive_font_size(16)
        )
        self._style_pill_button(close_button, (0.8, 0.2, 0.2, 1), (1, 1, 1, 1))

        # Make popup responsive with size_hint
        popup = Popup(
            title=title,
            content=popup_content,
            size_hint=(0.95, 0.8),
            title_size=self.get_adaptive_font_size(18)
        )
        close_button.bind(on_release=popup.dismiss)
        popup_content.add_widget(close_button)
        popup.open()

    def _show_subjects_popup(self, title, quarter_num=None):
        # Store current navigation path for later use
        self.current_navigation_path = title

        # Extract quarter from title if not provided
        if quarter_num is None:
            # Gets the '1' from '1st'
            quarter_part = title.split(" - ")[1].split()[0][0]
            quarter_num = int(quarter_part)

        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self._set_dark_bg(popup_content)

        popup_content.add_widget(Label(
            text=f"{title} - Select Subject",
            font_size=self.get_adaptive_font_size(14),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        ))

        # Determine grade from title
        grade = 11 if "Grade 11" in title else 12

        # Get subjects based on grade and quarter
        if grade == 11:
            if quarter_num in (1, 2):
                subjects = [
                    "Oral Comm",
                    "Komunikasyon",
                    "General Mathematics",
                    "Earth Science",
                    "Understanding Culture, Society and Politics",
                    "Personal Development",
                    "PE"
                ]
            else:
                subjects = [
                    "Reading and Writing",
                    "Pagbasa",
                    "21st Century Literature",
                    "Stats and Probability",
                    "PE"
                ]
        else:  # Grade 12
            subjects = [
                "1 - Introduction & Overview",
                "2 - Key Concepts & Theories",
                "3 - Practical Applications",
                "4 - Review and Assessment",
                "5 - Advanced Topics or Follow-Up",
                "6 - Additional Case Studies",
                "7 - Problem-Solving Approaches",
                "8 - Recap and Exam Preparation"
            ]

            subjects = subjects[:5] if quarter_num in (1, 2) else subjects[5:]

        # Create scroll view for subjects
        scroll_height = min(Window.height * 0.5, dp(300))
        scroll_view = ScrollView(size_hint=(1, None), height=scroll_height)
        subjects_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        subjects_layout.bind(minimum_height=subjects_layout.setter('height'))

        for subject in subjects:
            subject_button = Button(
                text=f"📚 {subject}",
                size_hint=(1, None),
                height=dp(50),
                font_size=self.get_adaptive_font_size(12)
            )
            # Capture current subject in lambda
            subject_button.bind(on_release=lambda btn, q=quarter_num, s=subject:
            self._show_weeks_popup(f"{title} - {s}", q, s))
            self._style_pill_button(subject_button, (0.6, 0.6, 0.6, 1), (1, 1, 1, 1))
            subjects_layout.add_widget(subject_button)

        scroll_view.add_widget(subjects_layout)
        popup_content.add_widget(scroll_view)

        # Close button and popup creation remains the same
        close_button = Button(
            text="❌ Close",
            size_hint=(1, None),
            height=dp(50),
            font_size=self.get_adaptive_font_size(12)
        )
        self._style_pill_button(close_button, (0.8, 0.2, 0.2, 1), (1, 1, 1, 1))

        popup = Popup(
            title=title,
            content=popup_content,
            size_hint=(0.95, 0.9),
            title_size=self.get_adaptive_font_size(14)
        )
        close_button.bind(on_release=popup.dismiss)
        popup_content.add_widget(close_button)
        popup.open()

    def _show_weeks_popup(self, title, quarter_num=None, subject=None):
        self.current_navigation_path = title

        # Extract quarter and subject if not provided
        if quarter_num is None:
            title_parts = title.split(" - ")
            quarter_part = title_parts[1].split()[0][0]  # Gets the '1' from '1st'
            quarter_num = int(quarter_part)

        if subject is None:
            subject = title.split(" - ")[-1]

        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self._set_dark_bg(popup_content)

        popup_content.add_widget(Label(
            text=f"{title} - Select Week",
            font_size=self.get_adaptive_font_size(14),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        ))

        # Create scrollable area for weeks
        scroll_height = min(Window.height * 0.6, dp(400))  # Adaptive height
        scroll_view = ScrollView(size_hint=(1, None), height=scroll_height)
        weeks_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        weeks_layout.bind(minimum_height=weeks_layout.setter('height'))

        # Use 8 weeks to match the batch script
        weeks = [f"Week {i}" for i in range(1, 9)]
        for week in weeks:
            week_button = Button(
                text=f"📅 {week}",
                size_hint=(1, None),
                height=dp(50),
                font_size=self.get_adaptive_font_size(14)
            )
            # Fix: Properly capture week number in the lambda
            week_num = int(week.split()[1])
            week_button.bind(on_release=lambda btn, q=quarter_num, s=subject, w=week_num:
            self._show_files_popup(f"{title} - Week {w}", q, s, w))
            self._style_pill_button(week_button, (0.7, 0.7, 0.7, 1), (1, 1, 1, 1))
            weeks_layout.add_widget(week_button)

        scroll_view.add_widget(weeks_layout)
        popup_content.add_widget(scroll_view)

        close_button = Button(
            text="❌ Close",
            size_hint=(1, None),
            height=dp(50),
            font_size=self.get_adaptive_font_size(14)
        )
        self._style_pill_button(close_button, (0.8, 0.2, 0.2, 1), (1, 1, 1, 1))

        # Responsive popup
        popup = Popup(
            title=title,
            content=popup_content,
            size_hint=(0.95, 0.9),
            title_size=self.get_adaptive_font_size(14)
        )
        close_button.bind(on_release=popup.dismiss)
        popup_content.add_widget(close_button)
        popup.open()

    def _show_files_popup(self, title, quarter_num=None, subject=None, week_num=None):
        self.current_navigation_path = title

        # Extract information if not provided
        if any(param is None for param in [quarter_num, subject, week_num]):
            title_parts = title.split(" - ")
            if quarter_num is None:
                quarter_part = title_parts[1].split()[0][0]
                quarter_num = int(quarter_part)

            if subject is None:
                subject = title_parts[2].replace("Subject ", "")

            if week_num is None:
                week_num = int(title_parts[3].split()[1])

        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self._set_dark_bg(popup_content)

        # Use responsive title
        responsive_title = self._get_responsive_title(f"{title} - Select File")

        popup_content.add_widget(Label(
            text=responsive_title,
            font_size=self.get_adaptive_font_size(14),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        ))

        # Use Kivy's app directory for Android compatibility
        from kivy.app import App
        BASE_DIR = os.path.join(App.get_running_app().user_data_dir, "GregorELibrary")

        folder_path = os.path.join(
            BASE_DIR,
            f"Quarter {quarter_num}",
            f"Subject {subject}",
            f"Week {week_num}"
        )

        print(f"Looking for files in: {folder_path}")
        print(f"Quarter: {quarter_num}, Subject: {subject}, Week: {week_num}")

        # Create a scrollable area for files
        scroll_height = min(Window.height * 0.6, dp(400))  # Adaptive height
        scroll_view = ScrollView(size_hint=(1, None), height=scroll_height)
        files_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        files_layout.bind(minimum_height=files_layout.setter('height'))

        files = []
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) 
                     if f.lower().endswith(('.pptx', '.pdf'))]  # Include PDFs

        if files:
            for file in files:
                file_button = Button(
                    text=f"📄 {file}",
                    size_hint=(1, None),
                    height=dp(50),
                    font_size=self.get_adaptive_font_size(14)
                )
                # Fix: Properly capture file name in the lambda
                file_button.bind(on_release=lambda btn, f=file, q=quarter_num, s=subject, w=week_num:
                self._handle_file_selected(f, q, s, w))
                self._style_pill_button(file_button, (0.8, 0.8, 0.8, 1), (1, 1, 1, 1))
                files_layout.add_widget(file_button)
        else:
            files_layout.add_widget(Label(
                text=f"No PowerPoint or PDF files found in:\n{folder_path}",
                font_size=self.get_adaptive_font_size(14),
                color=(1, 1, 1, 1),
                size_hint=(1, None),
                height=dp(80),
                halign='center',
                valign='middle',
                text_size=(Window.width * 0.8, None)
            ))

        scroll_view.add_widget(files_layout)
        popup_content.add_widget(scroll_view)

        # Close button
        close_button = Button(
            text="❌ Close",
            size_hint=(1, None),
            height=dp(50),
            font_size=self.get_adaptive_font_size(14)
        )
        self._style_pill_button(close_button, (0.8, 0.2, 0.2, 1), (1, 1, 1, 1))

        # Responsive popup
        popup = Popup(
            title=title,
            content=popup_content,
            size_hint=(0.95, 0.9),
            title_size=self.get_adaptive_font_size(14)
        )
        close_button.bind(on_release=popup.dismiss)
        popup_content.add_widget(close_button)
        popup.open()

    def _handle_file_selected(self, file_name, quarter_num=None, subject=None, week_num=None):
        from kivy.app import App
        BASE_DIR = os.path.join(App.get_running_app().user_data_dir, "GregorELibrary")

        file_path = os.path.join(
            BASE_DIR,
            f"Quarter {quarter_num}",
            f"Subject {subject}",
            f"Week {week_num}",
            file_name
        )

        print(f"Attempting to access: {file_path}")  # Debug log

        if os.path.exists(file_path):
            try:
                self.loading_popup = self._show_loading_popup()
                
                # Use Clock instead of threading for Android safety
                if file_name.lower().endswith('.pptx'):
                    Clock.schedule_once(lambda dt: self.convert_and_show_ppt(file_path))
                elif file_name.lower().endswith('.pdf'):
                    Clock.schedule_once(lambda dt: self.convert_and_show_pdf(file_path))
                    
            except Exception as e:
                self._show_error_popup("Error", f"Failed to process file: {str(e)}")
                if self.loading_popup:
                    self.loading_popup.dismiss()
        else:
            self._show_error_popup("Error", f"File not found: {file_path}")

    def _show_loading_popup(self):
        """Show a loading popup while processing files."""
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        popup_content.add_widget(Label(
            text="Loading...",
            font_size=self.get_adaptive_font_size(16),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        ))

        popup = Popup(
            title="Processing",
            content=popup_content,
            size_hint=(0.8, 0.4),
            title_size=self.get_adaptive_font_size(16)
        )
        popup.open()
        return popup

    def _show_error_popup(self, title, message):
        """Show an error popup with a given message."""
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        popup_content.add_widget(Label(
            text=message,
            font_size=self.get_adaptive_font_size(14),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(80),
            halign='center',
            valign='middle',
            text_size=(Window.width * 0.8, None)
        ))

        close_button = Button(
            text="Close",
            size_hint=(1, None),
            height=dp(50),
            font_size=self.get_adaptive_font_size(14)
        )
        self._style_pill_button(close_button, (0.8, 0.2, 0.2, 1), (1, 1, 1, 1))
        close_button.bind(on_release=lambda btn: popup.dismiss())

        popup_content.add_widget(close_button)

        popup = Popup(
            title=title,
            content=popup_content,
            size_hint=(0.8, 0.5),
            title_size=self.get_adaptive_font_size(16)
        )
        popup.open()

    def _style_pill_button(self, button, bg_color, text_color):
        """Style a button to look like a pill."""
        button.background_color = bg_color
        button.color = text_color
        with button.canvas.before:
            Color(*bg_color)
            button.rect = RoundedRectangle(
                size=button.size,
                pos=button.pos,
                radius=[dp(25)]
            )
        button.bind(size=self._update_btn_shape, pos=self._update_btn_shape)

    def _get_responsive_title(self, title):
        """Return a shortened title for smaller screens."""
        max_length = int(Window.width / dp(10))  # Adjust based on screen width
        return title if len(title) <= max_length else title[:max_length - 3] + "..."

    def convert_and_show_ppt(self, file_path):
        """Convert PPTX to images and display them."""
        try:
            prs = Presentation(file_path)
            images = []
            for slide in prs.slides:
                img_path = os.path.join(tempfile.gettempdir(), f"slide_{slide.slide_id}.png")
                slide_image = self._extract_slide_image(slide)
                slide_image.save(img_path, "PNG")
                images.append(img_path)

            self._display_images(images)
        except Exception as e:
            self._show_error_popup("Error", f"Failed to convert PPTX: {str(e)}")
        finally:
            if self.loading_popup:
                self.loading_popup.dismiss()

    def convert_and_show_pdf(self, file_path):
        """Convert PDF to images and display them."""
        try:
            pdf_document = fitz.open(file_path)
            images = []
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap()
                img_path = os.path.join(tempfile.gettempdir(), f"page_{page_num + 1}.png")
                pix.save(img_path)
                images.append(img_path)

            self._display_images(images)
        except Exception as e:
            self._show_error_popup("Error", f"Failed to convert PDF: {str(e)}")
        finally:
            if self.loading_popup:
                self.loading_popup.dismiss()

    def _display_images(self, image_paths):
        """Display a list of images in a scrollable popup."""
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        scroll_view = ScrollView(size_hint=(1, 1))
        images_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        images_layout.bind(minimum_height=images_layout.setter('height'))

        for img_path in image_paths:
            img = AsyncImage(source=img_path, size_hint=(1, None), height=dp(400))
            images_layout.add_widget(img)

        scroll_view.add_widget(images_layout)
        popup_content.add_widget(scroll_view)

        close_button = Button(
            text="Close",
            size_hint=(1, None),
            height=dp(50),
            font_size=self.get_adaptive_font_size(14)
        )
        self._style_pill_button(close_button, (0.8, 0.2, 0.2, 1), (1, 1, 1, 1))
        close_button.bind(on_release=lambda btn: popup.dismiss())

        popup_content.add_widget(close_button)

        popup = Popup(
            title="File Content",
            content=popup_content,
            size_hint=(0.95, 0.9),
            title_size=self.get_adaptive_font_size(16)
        )
        popup.open()

    def _extract_slide_image(self, slide):
        """Extract an image from a PPTX slide."""
        # Placeholder for actual implementation
        # You can use libraries like `python-pptx` and `PIL` to render slides as images
        img = Image.new("RGB", (800, 600), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), "Slide Image Placeholder", fill="black")
        return img


class GregorELibraryApp(App):
    def build(self):
        # Request Android permissions
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
            
        Window.bind(on_keyboard=self.on_keyboard)
        return MainMenu()

    def on_keyboard(self, window, key, *args):
        """Handle Android back button."""
        if key == 27:  # Android back button keycode
            return True  # Prevent default behavior
        return False


if __name__ == '__main__':
    GregorELibraryApp().run()
