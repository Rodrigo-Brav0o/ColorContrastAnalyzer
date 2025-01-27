import sys
import colorsys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QSlider, QTabWidget, QFormLayout, QColorDialog, QToolButton,
    QGroupBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor, QPixmap

################################################################################
# Light / Dark stylesheets / Algo bien

LIGHT_STYLESHEET = """
QToolButton {
    border: 1px solid #999;
    border-radius: 10px;
    background-color: #fafafa;
    color: #333;
}
QToolButton:hover {
    background-color: #f0f0f0;
}
QToolTip {
    color: #333;
    background-color: #fafafa;
    border: 1px solid #999;
    padding: 4px;
}
QLineEdit {
    background-color: #fff;
    color: #333;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 2px;
}
QPushButton {
    background-color: #e0e0e0;
    color: #333;
    border: 1px solid #999;
    border-radius: 4px;
    padding: 4px 8px;
}
QPushButton:hover {
    background-color: #d0d0d0;
}
QTabWidget::pane {
    border: 1px solid #ccc;
    background: #f9f9f9;
}
QTabBar::tab {
    background: #eee;
    color: #333;
    padding: 5px;
    border: 1px solid #ccc;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #fff;
    color: #000;
    border-bottom: 1px solid #fff;
}
"""

DARK_STYLESHEET = """
QToolButton {
    border: 1px solid #666;
    border-radius: 10px;
    background-color: #4f4f4f;
    color: #ddd;
}
QToolButton:hover {
    background-color: #666;
}
QToolTip {
    color: #ddd;
    background-color: #2f2f2f;
    border: 1px solid #666;
    padding: 4px;
}
QLineEdit {
    background-color: #3a3a3a;
    color: #ddd;
    border: 1px solid #666;
    border-radius: 4px;
    padding: 2px;
}
QPushButton {
    background-color: #4f4f4f;
    color: #ddd;
    border: 1px solid #666;
    border-radius: 4px;
    padding: 4px 8px;
}
QPushButton:hover {
    background-color: #666;
}
QTabWidget::pane {
    border: 1px solid #444;
    background: #2f2f2f;
}
QTabBar::tab {
    background: #3a3a3a;
    color: #ddd;
    padding: 5px;
    border: 1px solid #444;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #4a4a4a;
    color: #fff;
    border-bottom: 1px solid #4a4a4a;
}
"""

###################################################################
# Contrast calculation / Formulas for the WCAG standarts  

def linearize(c):
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def relative_luminance(r, g, b):     #linearize formula
    R = linearize(r)
    G = linearize(g)
    B = linearize(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def contrast_ratio(hex_fg, hex_bg):
    fg_short = hex_fg[:7]  # ejemp:  "#RRGGBB"
    bg_short = hex_bg[:7]

    fr = int(fg_short[1:3], 16) / 255.0         #normal formula for hex to rbg 
    fg_ = int(fg_short[3:5], 16) / 255.0
    fb = int(fg_short[5:7], 16) / 255.0

    br = int(bg_short[1:3], 16) / 255.0
    bg__ = int(bg_short[3:5], 16) / 255.0
    bb = int(bg_short[5:7], 16) / 255.0

    L1 = relative_luminance(fr, fg_, fb)       #Luminance formula
    L2 = relative_luminance(br, bg__, bb)
    if L2 > L1:
        L1, L2 = L2, L1

    return (L1 + 0.05) / (L2 + 0.05)

def check_conformance(ratio):
    return {
        "AA (Normal Text)": "Pass" if ratio >= 4.5 else "Fail",
        "AA (Large Text)": "Pass" if ratio >= 3.0 else "Fail",
        "AAA (Normal Text)": "Pass" if ratio >= 7.0 else "Fail"
    }


# Color conversion helpers / Making sure the colors look correctly

def rgb_to_hex(r, g, b, a=1.0):
    r_i = max(0, min(int(r*255), 255))         #cambiar rgb colors to hex 
    g_i = max(0, min(int(g*255), 255))
    b_i = max(0, min(int(b*255), 255))
    a_i = max(0, min(int(a*255), 255))
    if a_i >= 255:
        return f"#{r_i:02X}{g_i:02X}{b_i:02X}"
    else:
        return f"#{r_i:02X}{g_i:02X}{b_i:02X}{a_i:02X}"

def hex_to_hsv(hex_color):
    hex_color = hex_color.strip('#')
    if len(hex_color) < 6:
        raise ValueError("Invalid hex color.")
    r = int(hex_color[0:2], 16)/255.0
    g = int(hex_color[2:4], 16)/255.0
    b = int(hex_color[4:6], 16)/255.0
    a = 1.0
    if len(hex_color) == 8:
        a = int(hex_color[6:8], 16)/255.0

    import colorsys
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return (h, s, v, a)

def hsv_to_hex(h, s, v, a=1.0):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return rgb_to_hex(r, g, b, a)

def hex_to_rgba_str(hex_color):    #setting a color or a bg in CSS
    
    hex_color = hex_color.strip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    a = 255
    if len(hex_color) == 8:
        a = int(hex_color[6:8], 16)
    return f"rgba({r},{g},{b},{a/255:.2f})"


#########################################################################
# Main widget

class ContrastCheckerWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ColorContrast")

        
        self.custom_colors = []          #it will store to 16 custom colors

        
        self.last_ratio = None               #it will track the lastest ratio for it to generate recommendatonin

        self.fg_h = 0.0
        self.fg_s = 1.0
        self.fg_v = 1.0
        self.fg_a = 1.0

        self.bg_h = 0.0
        self.bg_s = 1.0
        self.bg_v = 1.0
        self.bg_a = 1.0

        self.is_dark_mode = False

        ##################################################################
        # FG Input
        
        self.fg_label = QLabel("Foreground Hex:")
        self.fg_input = QLineEdit("#FF0000")
        self.fg_input.textChanged.connect(self.ensure_hash_prefix_in_fg)
        self.fg_input.textChanged.connect(self.on_fg_input_changed)
        self.fg_pick_btn = QPushButton("Pick")                                     #boton para seleccionar color
        self.fg_pick_btn.clicked.connect(self.pick_fg_color)

        fg_input_layout = QHBoxLayout()
        fg_input_layout.addWidget(self.fg_input)
        fg_input_layout.addWidget(self.fg_pick_btn)

        ####################################################################
        # FG sliders
        
        self.fg_tab = QWidget()
        self.hue_slider_fg = self.create_hue_slider()
        self.sat_slider_fg = self.create_slider()
        self.bri_slider_fg = self.create_slider()
        self.opa_slider_fg = self.create_slider()

        self.hue_slider_fg.valueChanged.connect(self.on_fg_hue_changed)           #chnages automatically 
        self.sat_slider_fg.valueChanged.connect(self.on_fg_saturation_changed)
        self.bri_slider_fg.valueChanged.connect(self.on_fg_brightness_changed)
        self.opa_slider_fg.valueChanged.connect(self.on_fg_opacity_changed)

        hue_help_fg = self.create_help_button("Hue slider.\n0..360°.\nControls color angle.")        #range from all sliders / how are thez supposed to work
        sat_help_fg = self.create_help_button("Saturation slider.\n0..100.\n0=gray, 100=vivid.")
        bri_help_fg = self.create_help_button("Brightness slider.\n0..100.\n0=black, 100=bright.")
        opa_help_fg = self.create_help_button("Opacity slider.\n0..100.\n0=transparent, 100=opaque.")

        hue_layout_fg = QHBoxLayout()               #que aparezca en la app
        hue_layout_fg.addWidget(self.hue_slider_fg)
        hue_layout_fg.addWidget(hue_help_fg)

        sat_layout_fg = QHBoxLayout()
        sat_layout_fg.addWidget(self.sat_slider_fg)
        sat_layout_fg.addWidget(sat_help_fg)

        bri_layout_fg = QHBoxLayout()
        bri_layout_fg.addWidget(self.bri_slider_fg)
        bri_layout_fg.addWidget(bri_help_fg)

        opa_layout_fg = QHBoxLayout()
        opa_layout_fg.addWidget(self.opa_slider_fg)
        opa_layout_fg.addWidget(opa_help_fg)

        fg_form = QFormLayout()                     #text on top of the slider 
        fg_form.addRow("Hue", hue_layout_fg)
        fg_form.addRow("Saturation", sat_layout_fg)
        fg_form.addRow("Brightness", bri_layout_fg)
        fg_form.addRow("Opacity", opa_layout_fg)
        self.fg_tab.setLayout(fg_form)

        #####################################################################
        # BACKGROUND INPUT
        
        self.bg_label = QLabel("Background Hex:")
        self.bg_input = QLineEdit("#FFFFFF")
        self.bg_input.textChanged.connect(self.ensure_hash_prefix_in_bg)
        self.bg_input.textChanged.connect(self.on_bg_input_changed)
        self.bg_pick_btn = QPushButton("Pick")
        self.bg_pick_btn.clicked.connect(self.pick_bg_color)

        bg_input_layout = QHBoxLayout()
        bg_input_layout.addWidget(self.bg_input)
        bg_input_layout.addWidget(self.bg_pick_btn)

        #################################################################
        # BG Sliders
        
        self.bg_tab = QWidget()                             #basicamente lo mismo que el FG
        self.hue_slider_bg = self.create_hue_slider()
        self.sat_slider_bg = self.create_slider()
        self.bri_slider_bg = self.create_slider()
        self.opa_slider_bg = self.create_slider()

        self.hue_slider_bg.valueChanged.connect(self.on_bg_hue_changed)
        self.sat_slider_bg.valueChanged.connect(self.on_bg_saturation_changed)
        self.bri_slider_bg.valueChanged.connect(self.on_bg_brightness_changed)
        self.opa_slider_bg.valueChanged.connect(self.on_bg_opacity_changed)

        hue_help_bg = self.create_help_button("Hue slider.\n0..360°.\nControls color angle.")
        sat_help_bg = self.create_help_button("Saturation slider.\n0..100.\n0=gray, 100=vivid.")
        bri_help_bg = self.create_help_button("Brightness slider.\n0..100.\n0=black, 100=bright.")
        opa_help_bg = self.create_help_button("Opacity slider.\n0..100.\n0=transparent, 100=opaque.")

        hue_layout_bg = QHBoxLayout()
        hue_layout_bg.addWidget(self.hue_slider_bg)
        hue_layout_bg.addWidget(hue_help_bg)

        sat_layout_bg = QHBoxLayout()
        sat_layout_bg.addWidget(self.sat_slider_bg)
        sat_layout_bg.addWidget(sat_help_bg)

        bri_layout_bg = QHBoxLayout()
        bri_layout_bg.addWidget(self.bri_slider_bg)
        bri_layout_bg.addWidget(bri_help_bg)

        opa_layout_bg = QHBoxLayout()
        opa_layout_bg.addWidget(self.opa_slider_bg)
        opa_layout_bg.addWidget(opa_help_bg)

        bg_form = QFormLayout()
        bg_form.addRow("Hue", hue_layout_bg)
        bg_form.addRow("Saturation", sat_layout_bg)
        bg_form.addRow("Brightness", bri_layout_bg)
        bg_form.addRow("Opacity", opa_layout_bg)
        self.bg_tab.setLayout(bg_form)

        #######################################################################
        # TAB widget
        
        self.tab_widget = QTabWidget()                    # que aparezca en la app
        self.tab_widget.addTab(self.fg_tab, "Foreground")
        self.tab_widget.addTab(self.bg_tab, "Background")

        #########################################################################
        # Preview area
        
        self.preview_label = QLabel("Sample Text")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(300, 150)
        
        
        self.preview_label.setAutoFillBackground(True)        #makessure that the label paints its own BG

        self.preview_text_input = QLineEdit("Sample Text")
        self.preview_text_input.textChanged.connect(self.update_preview)          #it connects so it can update if there is any change

        self.preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self.preview_label)
        self.preview_group.setLayout(preview_layout)

        ############################################################################
        # Upload image
        
        self.upload_image_group = QGroupBox("Upload Image")               #todo lo que es upload image, mensaje de error, center text, making sure its clickeable
        self.upload_image_label = QLabel("No image uploaded")
        self.upload_image_label.setAlignment(Qt.AlignCenter)
        self.upload_image_label.setStyleSheet("border: 1px solid #ccc;")
        self.upload_image_label.setFixedSize(300, 250)
        self.upload_image_button = QPushButton("Upload Image")
        self.upload_image_button.clicked.connect(self.upload_image)

        upload_image_layout = QVBoxLayout()
        upload_image_layout.addWidget(self.upload_image_label)
        upload_image_layout.addWidget(self.upload_image_button)
        self.upload_image_group.setLayout(upload_image_layout)

        #########################################################################
        # Top layout (FG + BG Hex)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.fg_label)
        top_layout.addLayout(fg_input_layout)
        top_layout.addWidget(self.bg_label)
        top_layout.addLayout(bg_input_layout)

        ########################################################################v
        # Middle Layout (Tabs + Preview + Upload)
        
        middle_layout = QHBoxLayout()            #que tenga buen tamano / que este en lado correcto etc.
        self.tab_widget.setMinimumWidth(250)
        self.tab_widget.setMinimumHeight(300)
        self.preview_group.setMinimumWidth(350)
        self.preview_group.setMinimumHeight(250)

        middle_layout.addWidget(self.tab_widget, 1)
        middle_layout.addWidget(self.preview_group, 2)

        right_side_layout = QVBoxLayout()
        right_side_layout.addWidget(self.upload_image_group)

        middle_layout.addLayout(right_side_layout, 2)

        #####################################################################
        # Text Input layout (Preview text)
        
        text_input_layout = QHBoxLayout()
        text_input_layout.addWidget(QLabel("Preview text:"))
        text_input_layout.addWidget(self.preview_text_input)

        ###################################################################
        # Bottom layout (Calc Contrast + Recommendation + Theme)
        
        self.calculate_button = QPushButton("Calculate Contrast")                #para cosa que tenga su nombre, el tamano correcto y que este conectado correctamente
        self.calculate_button.setFixedSize(130, 36)
        self.calculate_button.clicked.connect(self.calculate_wcw_contrast)

        self.result_label = QLabel("Result will appear here")
        self.result_label.setFixedWidth(300)

        self.toggle_theme_btn = QPushButton("Dark Mode")
        self.toggle_theme_btn.setFixedSize(90, 28)
        self.toggle_theme_btn.clicked.connect(self.toggleTheme)

        self.recommendation_button = QPushButton("Recommendation")
        self.recommendation_button.setFixedSize(130, 36)
        self.recommendation_button.clicked.connect(self.handle_recommendation)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.calculate_button)
        buttons_layout.addWidget(self.recommendation_button)

        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(buttons_layout)
        bottom_layout.addWidget(self.result_label)
        bottom_layout.addWidget(self.toggle_theme_btn)

        ######################################################################
        # Main layout
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(text_input_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

        
        self.on_fg_input_changed()     #Initialize from defaults
        self.on_bg_input_changed()
        self.update_preview()

    ########################################
    # Recommendation
    
    def handle_recommendation(self):
        if self.last_ratio is None:
            QMessageBox.information(self, "Recommendation", "No contrast ratio calculated yet.")
            return

        ratio = self.last_ratio
        if ratio < 3.0:
            msg = (
                f"Your contrast ratio is only {ratio:.2f}, which is quite low.\n\n"
                "Try making the background lighter or the foreground darker.\n"
                "Consider increasing the saturation or brightness difference."
            )
        elif ratio < 4.5:
            msg = (
                f"Your contrast ratio is {ratio:.2f}, which doesn't meet AA for normal text.\n\n"
                "Try adjusting the background/foreground to increase contrast.\n"
                "For example, make the BG brighter or the FG color bolder."
            )
        elif ratio < 7.0:
            msg = (
                f"Your contrast ratio is {ratio:.2f}, which meets AA for normal text,\n"
                "but not AAA. If you want AAA, you need 7.0 or higher.\n"
                "You could try a slightly darker or brighter color to bump the ratio."
            )
        else:
            msg = (
                f"Great! Your contrast ratio is {ratio:.2f} which meets AAA.\n\n"
                "You have excellent contrast, so you should be set.\n"
                "If you want a different aesthetic, you can still tweak hue/sat."
            )

        QMessageBox.information(self, "Recommendation", msg)

    ###############################################################################################
    # Custom Colors / mas focus
    
    def add_custom_color(self, color: QColor):
        
        for existing in self.custom_colors:             # Up to 16 different  custom colors
            if existing.rgb() == color.rgb():
                return
        if len(self.custom_colors) >= 16:
            self.custom_colors.pop(0)
        self.custom_colors.append(color)

    def setup_color_dialog(self, initial: QColor) -> QColorDialog:
        dialog = QColorDialog(self)
        dialog.setOption(QColorDialog.ShowAlphaChannel, False)
        dialog.setCurrentColor(initial)
        for i, c in enumerate(self.custom_colors):
            dialog.setCustomColor(i, c.rgb())
        return dialog

    #####################################################################
    # Upload Image / mas focus 

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(
                self.upload_image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.upload_image_label.setPixmap(pixmap)
            self.upload_image_label.setText("")
        else:
            self.upload_image_label.setText("No image uploaded")

    ############################################################################
    # Sliders / Help 
    
    def create_slider(self):        #simbol of ? for what each slider does and size and the values etc.
        s = QSlider(Qt.Horizontal)
        s.setRange(0, 100)
        s.setValue(100)
        return s

    def create_hue_slider(self):
        s = QSlider(Qt.Horizontal)
        s.setRange(0, 360)
        s.setValue(0)
        return s

    def create_help_button(self, tooltip_text):
        btn = QToolButton()
        btn.setText("?")
        btn.setToolTip(tooltip_text)
        btn.setFixedSize(20, 20)
        font = QFont()
        font.setBold(True)
        btn.setFont(font)
        return btn

    #######################################################################
    # Toggling Light/Dark mode
    
    def toggleTheme(self):
        app = QApplication.instance()
        if not app:
            return

        if not self.is_dark_mode:                                   #el mejor cambio que pude haber hecho, tengo sueno
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.Window, QColor(45, 45, 45))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
            dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
            dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(90, 150, 240))
            dark_palette.setColor(QPalette.HighlightedText, Qt.black)

            app.setStyle("Fusion")
            app.setPalette(dark_palette)
            app.setStyleSheet(DARK_STYLESHEET)
            self.toggle_theme_btn.setText("Light Mode")
            self.is_dark_mode = True
        else:
            light_palette = QPalette()
            light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
            light_palette.setColor(QPalette.WindowText, Qt.black)
            light_palette.setColor(QPalette.Base, Qt.white)
            light_palette.setColor(QPalette.AlternateBase, QColor(225, 225, 225))
            light_palette.setColor(QPalette.ToolTipBase, Qt.white)
            light_palette.setColor(QPalette.ToolTipText, Qt.black)
            light_palette.setColor(QPalette.Text, Qt.black)
            light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
            light_palette.setColor(QPalette.ButtonText, Qt.black)
            light_palette.setColor(QPalette.BrightText, Qt.red)
            light_palette.setColor(QPalette.Link, QColor(0, 120, 215))
            light_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
            light_palette.setColor(QPalette.HighlightedText, Qt.white)

            app.setStyle("Fusion")
            app.setPalette(light_palette)
            app.setStyleSheet(LIGHT_STYLESHEET)
            self.toggle_theme_btn.setText("Dark Mode")
            self.is_dark_mode = False

    ########################################################################################
    # Force "#" in line edits
    
    def ensure_hash_prefix_in_fg(self):                     # just making sure the # is alsways there, other wise it wont be hex
        txt = self.fg_input.text()
        if not txt.startswith("#"):
            self.fg_input.blockSignals(True)
            self.fg_input.setText("#" + txt.replace("#", ""))
            self.fg_input.blockSignals(False)

    def ensure_hash_prefix_in_bg(self):
        txt = self.bg_input.text()
        if not txt.startswith("#"):
            self.bg_input.blockSignals(True)
            self.bg_input.setText("#" + txt.replace("#", ""))
            self.bg_input.blockSignals(False)

    #################################################################################
    # Color Pickers
    
    def pick_fg_color(self):                           #making sure u are clickking for FG and the correct formulas are applyed otherwise the  colors wont appear
        txt = self.fg_input.text().strip()
        if len(txt) >= 7 and txt.startswith("#"):
            try:
                base_rgb = txt[:7]
                r = int(base_rgb[1:3], 16)
                g = int(base_rgb[3:5], 16)
                b = int(base_rgb[5:7], 16)
                initial = QColor(r, g, b)
            except ValueError:
                initial = QColor(255,255,255)
        else:
            initial = QColor(255,255,255)

        dialog = self.setup_color_dialog(initial)
        if dialog.exec() == QColorDialog.Accepted:
            color = dialog.selectedColor()
            self.add_custom_color(color)
            hex_str = f"#{color.red():02X}{color.green():02X}{color.blue():02X}"
            self.fg_input.blockSignals(True)
            self.fg_input.setText(hex_str)
            self.fg_input.blockSignals(False)
            self.on_fg_input_changed()

    def pick_bg_color(self):                            #lo mismo pero para BG, making sure the formulas are correctly applyed and the colors accepted 
        txt = self.bg_input.text().strip()
        if len(txt) >= 7 and txt.startswith("#"):
            try:
                base_rgb = txt[:7]
                r = int(base_rgb[1:3], 16)
                g = int(base_rgb[3:5], 16)
                b = int(base_rgb[5:7], 16)
                initial = QColor(r, g, b)
            except ValueError:
                initial = QColor(255,255,255)
        else:
            initial = QColor(255,255,255)

        dialog = self.setup_color_dialog(initial)
        if dialog.exec() == QColorDialog.Accepted:
            color = dialog.selectedColor()
            self.add_custom_color(color)
            hex_str = f"#{color.red():02X}{color.green():02X}{color.blue():02X}"
            self.bg_input.blockSignals(True)
            self.bg_input.setText(hex_str)
            self.bg_input.blockSignals(False)
            self.on_bg_input_changed()

    ############################################################################
    # FG: line edit to -> HSV
    
    def on_fg_input_changed(self):
        txt = self.fg_input.text().strip()
        if len(txt) < 7:
            return
        try:
            h, s, v, a = hex_to_hsv(txt)
            self.fg_h, self.fg_s, self.fg_v, self.fg_a = h, s, v, a

            self.hue_slider_fg.blockSignals(True)
            self.hue_slider_fg.setValue(int(h * 360))
            self.hue_slider_fg.blockSignals(False)

            self.sat_slider_fg.blockSignals(True)
            self.sat_slider_fg.setValue(int(s * 100))
            self.sat_slider_fg.blockSignals(False)

            self.bri_slider_fg.blockSignals(True)
            self.bri_slider_fg.setValue(int(v * 100))
            self.bri_slider_fg.blockSignals(False)

            self.opa_slider_fg.blockSignals(True)
            self.opa_slider_fg.setValue(int(a * 100))
            self.opa_slider_fg.blockSignals(False)

            self.update_preview()
        except ValueError:
            pass

    def on_fg_hue_changed(self, val):
        self.fg_h = val / 360.0
        self.write_fg_line_edit()
        self.update_preview()

    def on_fg_saturation_changed(self, val):
        self.fg_s = val / 100.0
        self.write_fg_line_edit()
        self.update_preview()

    def on_fg_brightness_changed(self, val):
        self.fg_v = val / 100.0
        self.write_fg_line_edit()
        self.update_preview()

    def on_fg_opacity_changed(self, val):
        self.fg_a = val / 100.0
        self.write_fg_line_edit()
        self.update_preview()

    def write_fg_line_edit(self):
        new_hex = hsv_to_hex(self.fg_h, self.fg_s, self.fg_v, self.fg_a)
        self.fg_input.blockSignals(True)
        self.fg_input.setText(new_hex)
        self.fg_input.blockSignals(False)

    #########################################################################
    # BG: line edit to -> HSV
    
    def on_bg_input_changed(self):
        txt = self.bg_input.text().strip()
        if len(txt) < 7:
            return
        try:
            h, s, v, a = hex_to_hsv(txt)
            self.bg_h, self.bg_s, self.bg_v, self.bg_a = h, s, v, a

            self.hue_slider_bg.blockSignals(True)
            self.hue_slider_bg.setValue(int(h * 360))
            self.hue_slider_bg.blockSignals(False)

            self.sat_slider_bg.blockSignals(True)
            self.sat_slider_bg.setValue(int(s * 100))
            self.sat_slider_bg.blockSignals(False)

            self.bri_slider_bg.blockSignals(True)
            self.bri_slider_bg.setValue(int(v * 100))
            self.bri_slider_bg.blockSignals(False)

            self.opa_slider_bg.blockSignals(True)
            self.opa_slider_bg.setValue(int(a * 100))
            self.opa_slider_bg.blockSignals(False)

            self.update_preview()
        except ValueError:
            pass

    def on_bg_hue_changed(self, val):
        self.bg_h = val / 360.0
        self.write_bg_line_edit()
        self.update_preview()

    def on_bg_saturation_changed(self, val):
        self.bg_s = val / 100.0
        self.write_bg_line_edit()
        self.update_preview()

    def on_bg_brightness_changed(self, val):
        self.bg_v = val / 100.0
        self.write_bg_line_edit()
        self.update_preview()

    def on_bg_opacity_changed(self, val):
        self.bg_a = val / 100.0
        self.write_bg_line_edit()
        self.update_preview()

    def write_bg_line_edit(self):
        new_hex = hsv_to_hex(self.bg_h, self.bg_s, self.bg_v, self.bg_a)
        self.bg_input.blockSignals(True)
        self.bg_input.setText(new_hex)
        self.bg_input.blockSignals(False)

    ##################################################################################
    # Live Preview
    
    def update_preview(self):
        fg_hex = hsv_to_hex(self.fg_h, self.fg_s, self.fg_v, self.fg_a)    #makes sure that  the preview  shows exactly the user specified FG and BG colors,unaffected by Dark and Light mode 
        bg_hex = hsv_to_hex(self.bg_h, self.bg_s, self.bg_v, self.bg_a)

        fg_css = hex_to_rgba_str(fg_hex)
        bg_css = hex_to_rgba_str(bg_hex)

        custom_text = self.preview_text_input.text().strip()
        if not custom_text:
            custom_text = " "

        self.preview_label.setStyleSheet(                             # Directly override the labe style sheet, ignoring D/L mode
            f"QLabel {{ color: {fg_css}; background-color: {bg_css}; border: 1px solid #444; }}"
        )

        self.preview_label.setText(custom_text)

    #######################################################################################
    # Calculate and display WCAG contrast
    
    def calculate_wcw_contrast(self):
        fg_hex = hsv_to_hex(self.fg_h, self.fg_s, self.fg_v, self.fg_a)
        bg_hex = hsv_to_hex(self.bg_h, self.bg_s, self.bg_v, self.bg_a)

        if self.fg_a < 0.2 and self.bg_a < 0.2:
            self.result_label.setText(self._styled_fail_card("Both FG & BG < 20% opacity"))               #si opacity es menor a20% error para FG y BG
            self.last_ratio = None
            return
        elif self.fg_a < 0.2:
            self.result_label.setText(self._styled_fail_card("Foreground < 20% opacity"))
            self.last_ratio = None
            return
        elif self.bg_a < 0.2:
            self.result_label.setText(self._styled_fail_card("Background < 20% opacity"))
            self.last_ratio = None
            return

        try:
            ratio = contrast_ratio(fg_hex, bg_hex)
            self.last_ratio = ratio
                                                                
            results = check_conformance(ratio)                   #lo que saldria en los resultados una vez que termine los calculos
            c1_normal = results.get("AA (Normal Text)", "Fail")
            c1_large = results.get("AA (Large Text)", "Fail")
            c2_normal = results.get("AAA (Normal Text)", "Fail")
            c2_large = c2_normal
            c3_nt = "Pass" if ratio >= 3.0 else "Fail"

            results_criteria = [
                {
                    "title": "1.4.3 (AA) Minimum Contrast",
                    "regular": c1_normal,
                    "large": c1_large
                },
                {
                    "title": "1.4.6 (AAA) Enhanced Contrast",
                    "regular": c2_normal,
                    "large": c2_large
                },
                {
                    "title": "1.4.11 Non-text Contrast (AA)",
                    "regular": c3_nt,
                    "large": c3_nt
                }
            ]

            html_output = self.build_wcag_tiles_html(ratio, results_criteria)
            self.result_label.setText(html_output)

        except ValueError as e:
            self.result_label.setText(self._styled_fail_card(f"Error: {str(e)}"))
            self.last_ratio = None

    def _styled_fail_card(self, msg):                #que los resultados seas un poco mejor visualmente
        if self.is_dark_mode:
            bg = "#333"
            txt = "#eee"
            fail_color = "salmon"
        else:
            bg = "#f4f4f4"
            txt = "#333"
            fail_color = "red"
        return f"""
        <div style="max-width:350px; background:{bg}; color:{txt};
                    border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.15);
                    font-family:Arial,sans-serif; padding:14px; margin:10px;">
          <h3 style="margin:0 0 8px 0; font-size:1.1em;">
            <span style="color:{fail_color}; margin-right:6px;">✖</span>
            Fail
          </h3>
          <div>{msg}</div>
        </div>
        """

    def build_wcag_tiles_html(self, ratio, criteria_list):           #again making sure it loks goods 
        if self.is_dark_mode:
            grid_bg = "#333"
            tile_bg = "#444"
            text_color = "#eee"
            pass_color = "lime"
            fail_color = "salmon"
        else:
            grid_bg = "#f9f9f9"
            tile_bg = "#fff"
            text_color = "#333"
            pass_color = "#2e7d32"
            fail_color = "#d32f2f"

        html = f"""
        <div style="
          max-width:600px; 
          background:{grid_bg};
          border-radius:8px;
          box-shadow:0 2px 5px rgba(0,0,0,0.15);
          font-family:Arial,sans-serif;
          color:{text_color};
          padding:16px;
          margin:10px;">
          
          <h3 style="margin-top:0; margin-bottom:14px; font-size:1.2em;">
            WCAG Criteria – Contrast ratio: {ratio:.2f}
          </h3>

          <div style="
            display:flex;
            flex-wrap:wrap;
            gap:10px;">
        """

        def passfail_html(label, status):         #yes or no icons
            if status.lower() == "pass":
                icon = "✔"
                color = pass_color
            elif status.lower() == "fail":
                icon = "✖"
                color = fail_color
            else:
                icon = "?"
                color = text_color
            return f"""
            <div style="margin:3px 0; display:flex; align-items:center;">
              <span style="color:{color}; margin-right:6px;">{icon}</span>
              <span>{label}: {status}</span>
            </div>
            """

        for crit in criteria_list:
            ctitle = crit.get("title", "Criterion")
            reg_status = crit.get("regular", "N/A")
            larg_status = crit.get("large", "N/A")

            html += f"""
            <div style="
              background:{tile_bg};
              border-radius:6px;
              box-shadow:0 1px 3px rgba(0,0,0,0.2);
              padding:12px;
              min-width:160px;">
              <h4 style="margin-top:0; margin-bottom:8px; font-size:1em;">
                {ctitle}
              </h4>
              {passfail_html("Regular Text", reg_status)}
              {passfail_html("Large Text", larg_status)}
            </div>
            """

        html += """
          </div> <!-- end .flex-wrap -->
        </div> <!-- end outer card -->
        """
        return html


#########################################################################################
# Main

if __name__ == "__main__":                  #making sure it converst into a window or app with 900 x 500 size
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    app.setStyleSheet(LIGHT_STYLESHEET)        # Start in light mode by default

    window = ContrastCheckerWidget()
    window.resize(900, 500)
    window.show()
    sys.exit(app.exec())
