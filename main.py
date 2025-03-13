from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import os
from kivy.config import Config

Config.set('kivy', 'window_icon', '')
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'orientation', 'portrait')
Window.rotation = 0

Window.rotation = 0
Window.size = (412, 615)

class MainMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.loading_popup = None
        self.current_navigation_path = ""

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
            text=f"Select Quarter",
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
            title='',  # Remove popup title
            content=popup_content,
            size_hint=(0.95, 0.8),
            title_size=0  # Hide title bar
        )
        close_button.bind(on_release=popup.dismiss)
        popup_content.add_widget(close_button)
        popup.open()

    def _show_subjects_popup(self, title, quarter_num=None):
        self.current_navigation_path = title

        # Extract quarter from title if not provided
        if quarter_num is None:
            quarter_part = title.split(" - ")[1].split()[0][0]  # Gets the '1' from '1st'
            quarter_num = int(quarter_part)

        # Reduce padding and spacing in the popup content
        popup_content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))  # Reduced padding and spacing
        self._set_dark_bg(popup_content)

        # Adjust the label size and spacing
        popup_content.add_widget(Label(
            text=f"Select Subject",
            font_size=self.get_adaptive_font_size(14),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(30)  # Reduced height
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

        # Create scroll view for subjects with reduced height
        scroll_height = min(Window.height * 0.6, dp(300))  # Adjusted height
        scroll_view = ScrollView(size_hint=(1, None), height=scroll_height)
        subjects_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))  # Reduced spacing
        subjects_layout.bind(minimum_height=subjects_layout.setter('height'))

        for subject in subjects:
            subject_button = Button(
                text=f"📚 {subject}",
                size_hint=(1, None),
                height=dp(40),  # Reduced button height
                font_size=self.get_adaptive_font_size(12)
            )
            subject_button.bind(on_release=lambda btn, q=quarter_num, s=subject:
            self._show_weeks_popup(f"{title} - {s}", q, s))
            self._style_pill_button(subject_button, (0.6, 0.6, 0.6, 1), (1, 1, 1, 1))
            subjects_layout.add_widget(subject_button)

        scroll_view.add_widget(subjects_layout)
        popup_content.add_widget(scroll_view)

        # Close button with reduced height
        close_button = Button(
            text="❌ Close",
            size_hint=(1, None),
            height=dp(40),  # Reduced height
            font_size=self.get_adaptive_font_size(12)
        )
        self._style_pill_button(close_button, (0.8, 0.2, 0.2, 1), (1, 1, 1, 1))

        # Create and open the popup
        popup = Popup(
            title='',  # Remove popup title
            content=popup_content,
            size_hint=(0.95, 0.8),  # Adjusted size hint
            title_size=0  # Hide title bar
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
            text=f"Select Week",
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
            title='',  # Remove popup title
            content=popup_content,
            size_hint=(0.95, 0.9),
            title_size=0  # Hide title bar
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
                quarter_part = title_parts[1].split()[0][0]  # Gets the '1' from '1st'
                quarter_num = int(quarter_part)

            if subject is None:
                subject = title_parts[2].replace("Subject ", "")

            if week_num is None:
                week_num = int(title_parts[3].split()[1])

        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        self._set_dark_bg(popup_content)

        popup_content.add_widget(Label(
            text=f"Select File",
            font_size=self.get_adaptive_font_size(20),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        ))

        # Create scrollable area for files
        scroll_height = min(Window.height * 0.6, dp(400))  # Adaptive height
        scroll_view = ScrollView(size_hint=(1, None), height=scroll_height)
        files_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        files_layout.bind(minimum_height=files_layout.setter('height'))

        BASE_DIR = "GregorELibrary"

        folder_path = os.path.join(
            BASE_DIR,
            f"Quarter {quarter_num}",
            f"Subject {subject}",
            f"Week {week_num}"
        )

        # Debug output to verify path components
        print(f"Looking for files in: {folder_path}")
        print(f"Quarter: {quarter_num}, Subject: {subject}, Week: {week_num}")

        files = []
        if os.path.exists(folder_path):
            # Include both PPTX and PDF files
            files = [f for f in os.listdir(folder_path)
                     if f.lower().endswith(('.pptx', '.pdf'))]

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
                text=f"No PowerPoint files found in:\n{folder_path}",
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

        close_button = Button(
            text="❌ Close",
            size_hint=(1, None),
            height=dp(50),
            font_size=self.get_adaptive_font_size(14)
        )
        self._style_pill_button(close_button, (0.8, 0.2, 0.2, 1), (1, 1, 1, 1))

        # Use responsive title for popup
        popup = Popup(
            title=self._get_responsive_title(title),
            content=popup_content,
            size_hint=(0.95, 0.9),
            title_size=self.get_adaptive_font_size(14)
        )
        close_button.bind(on_release=popup.dismiss)
        popup_content.add_widget(close_button)
        popup.open()

    def _show_error_popup(self, title, message):
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self._set_dark_bg(popup_content)

        popup_content.add_widget(Label(
            text=message,
            font_size=sp(14),
            color=(1, 1, 1, 1)
        ))

        close_button = Button(
            text="Close",
            size_hint=(1, None),
            height=dp(40),
            font_size=sp(14)
        )
        self._style_pill_button(close_button, (0.8, 0.2, 0.2, 1), (1, 1, 1, 1))

        popup = Popup(title=title, content=popup_content, size_hint=(0.8, 0.4))
        close_button.bind(on_release=popup.dismiss)
        popup_content.add_widget(close_button)
        popup.open()

    def show_about_us(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self._set_dark_bg(popup_content)

        popup_content.add_widget(Label(
            text="About Us",
            font_size=sp(24),
            color=(1, 1, 1, 1)
        ))
        popup_content.add_widget(Label(
            text="We are a team dedicated to providing easy access\n"
                    "to educational resources. Our platform is\n"
                    "designed to help students manage study materials\n"
                    "anytime, anywhere.",
            font_size=sp(14),
            color=(1, 1, 1, 1)
        ))

        close_button = Button(
            text="Close",
            size_hint=(1, None),
            height=dp(40),
            font_size=sp(14)
        )
        self._style_pill_button(close_button, (0.8, 0.2, 0.2, 1), (1, 1, 1, 1))

        popup = Popup(title="About Us", content=popup_content, size_hint=(0.9, 0.9))
        close_button.bind(on_release=popup.dismiss)
        popup_content.add_widget(close_button)
        popup.open()

    def _set_dark_bg(self, layout):
        with layout.canvas.before:
            Color(0, 0, 0, 1)
            layout.bg_rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_bg_rect_popup, pos=self._update_bg_rect_popup)

    def _update_bg_rect_popup(self, layout, *args):
        layout.bg_rect.pos = layout.pos
        layout.bg_rect.size = layout.size

    def _style_pill_button(self, btn, bg_color, text_color):
        btn.background_color = (0, 0, 0, 0)
        btn.color = text_color
        btn.background_normal = ''
        btn.background_down = ''

        with btn.canvas.before:
            Color(*bg_color)
            btn.rect = RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(20)])
        btn.bind(size=self._update_btn_rect, pos=self._update_btn_rect)

    def _update_btn_rect(self, instance, *args):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size


class GregorELibraryApp(App):
    def build(self):
        # Load initial configuration
        Window.bind(on_keyboard=self.on_keyboard)
        return MainMenu()

    def on_keyboard(self, window, key, *args):
        # Disable back button exit
        if key == 27:
            return True
        return False

if __name__ == "__main__":
    GregorELibraryApp().run()
