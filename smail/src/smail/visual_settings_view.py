
from PyQt5.QtCore import pyqtSlot, QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit, QGridLayout, QPushButton, QVBoxLayout, QSpacerItem, \
QSizePolicy, QFrame, QComboBox

from smail import style
from sconf.configuration.models.global_configuration import GlobalConfiguration
from sconf.configuration.models.sos_configuration import SOSConfiguration
from sconf.configuration.models.smail_configuration import SmailConfiguration
from sconf.ui.convertors.value_convertors import StringValueConvertors
from sconf.ui.styles.global_style_sheets import get_default_label_style, get_default_input_box_style, \
    get_default_dropdown_style, get_default_menu_button_style, get_active_menu_button_style
from sconf.ui.view_models.global_settings_view_model import GlobalViewModel
import smail.smail_confview as smail_confview


class VisualSettingsView(QWidget):
    _globalViewModel: GlobalViewModel
    _globalConfiguration: GlobalConfiguration
    _sosConfiguration: SOSConfiguration

    def __init__(self, global_configuration: GlobalConfiguration,
                 smail_configuration: SmailConfiguration,
                 sos_configuration: SOSConfiguration,
                 data_provider, configuration_writer, stacked_widget
                 ):
    
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.data_provider = data_provider
        self.configuration_writer = configuration_writer
        self.stacked_widget = stacked_widget
        # Menu layout
        self.button_frame = QFrame(self)
        self.button_frame.setStyleSheet(style.get_button_frame_style())
        self.button_frame.setFrameShape(QFrame.StyledPanel)
        self.button_frame.setFixedHeight(130)
        self.button_layout = QHBoxLayout(self.button_frame)
        spacer_left = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_right = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
       # self.button_layout.addItem(spacer_left)

        # Creating the menu buttons
        self.menu_buttons = {
            "Menu1": QPushButton("MENU 1"),
            "X": QPushButton(""),
            "Security": QPushButton("SECURITY"),
            "Visual": QPushButton("VISUAL"),
            "Mail": QPushButton("MAIL")
        }

        # Set up each button with proper sizing and styling
        for name, button in self.menu_buttons.items():
            button.setMinimumSize(244, 107) # Updated size to match Figma
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            if name == "X":
                pixmap_icon = QPixmap("/home/vboxuser/senior-os/sconf/icons/exit.png").scaled(40, 40, Qt.KeepAspectRatio,
                                                                        Qt.SmoothTransformation)
                button.setIconSize(QSize(40, 40))
                button.setIcon(QIcon(pixmap_icon))
            self.button_layout.addWidget(button, alignment=Qt.AlignCenter)
            button.setStyleSheet(style.get_button_style(self.data_provider))

        self.button_layout.setSpacing(10)
        #self.button_layout.addItem(spacer_right)
        self.button_frame.setStyleSheet(style.get_button_frame_style())
        self.main_layout.addWidget(self.button_frame)

        # Create layout for labels and input fields
        self.bottom_frame = QFrame(self)
        self.grid_layout = QGridLayout(self.bottom_frame)
        self.grid_layout.setSpacing(10)
        self._globalConfiguration = global_configuration
        
        self._sosConfiguration = sos_configuration
        self._globalViewModel = GlobalViewModel(global_configuration,  smail_configuration)

        # Labels
        label_alert_color = QLabel("Alert color (in hex)")
        label_highlight_color = QLabel("Highlight color (in hex)")
        label_language = QLabel("Language")


        input_alert_color = QComboBox()
        input_alert_color.addItems(["Black", "Purple", "Red", "Green", "Blue"])
        input_alert_color.setObjectName("alertColor")
        input_alert_color.setCurrentText(
            StringValueConvertors.hex_to_color_name(self._globalConfiguration.alertColor))

        input_highlight_color = QComboBox()
        input_highlight_color.addItems(["Black", "Purple", "Red", "Green", "Blue"])
        input_highlight_color.setObjectName("highlightColor")
        input_highlight_color.setCurrentText(
            StringValueConvertors.hex_to_color_name(self._globalConfiguration.highlightColor))

        combo_language = QComboBox()
        combo_language.addItems(["English", "German", "Czech"])
        combo_language.setObjectName("language")
        combo_language.setCurrentText(
            StringValueConvertors.country_code_to_language(self._globalConfiguration.language))

        # Add widgets to the grid

        self.grid_layout.addWidget(label_alert_color, 0, 0)
        self.grid_layout.addWidget(input_alert_color, 0, 1)

        self.grid_layout.addWidget(label_highlight_color, 1, 0)
        self.grid_layout.addWidget(input_highlight_color, 1, 1)
        
        self.grid_layout.addWidget(label_language, 2, 0)
        self.grid_layout.addWidget(combo_language, 2, 1)

        input_alert_color.currentIndexChanged.connect(self.__on_input_change)
        input_highlight_color.currentIndexChanged.connect(self.__on_input_change)
        combo_language.currentIndexChanged.connect(self.__on_input_change)

        # Set widget layout

        self.main_layout.addWidget(self.bottom_frame)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

        # Apply styling
        self.setStyleSheet(f"""
                            {get_default_label_style()}
                            {get_default_input_box_style()}
                            {get_default_dropdown_style()}
                        """)
        self.bottom_frame.setMinimumSize(1260, 580)
        self.bottom_frame.setStyleSheet("""
                background-color: #FFFFFF;        
                border: 2px solid #000000;                                        
                border-radius: 8px;
                                        """)
        self.button_frame.setStyleSheet(style.get_button_frame_style())
        self.menu_buttons["Menu1"].setStyleSheet(style.get_button_style(self.data_provider))
        self.menu_buttons["X"].setStyleSheet(style.get_button_style(self.data_provider))
        self.menu_buttons["Security"].setStyleSheet(style.get_button_style(self.data_provider))
        self.menu_buttons["Visual"].setStyleSheet(style.get_button_style(self.data_provider, highlight=True))
        self.menu_buttons["Mail"].setStyleSheet(style.get_button_style(self.data_provider))

        self.menu_buttons["X"].clicked.connect(self.terminate_shelp)
        self.menu_buttons["Menu1"].clicked.connect(self.terminate_shelp)
        self.menu_buttons["Security"].clicked.connect(self.show_security_view)
        self.menu_buttons["Visual"].clicked.connect(self.show_visual_view)
        self.menu_buttons["Mail"].clicked.connect(self.show_mail_view)


    def terminate_shelp(self):
        self.configuration_writer.update_configuration(
            configuration=self.data_provider.get_main_configuration()
        )
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.update()
        smail_confview.update_main(self.stacked_widget)
    def show_security_view(self):
        self.configuration_writer.update_configuration(
            configuration=self.data_provider.get_main_configuration()
        )
        self.stacked_widget.setCurrentIndex(1)
        self.stacked_widget.update()
    def show_visual_view(self):
        self.configuration_writer.update_configuration(
            configuration=self.data_provider.get_main_configuration()
        )
        self.stacked_widget.setCurrentIndex(2)
        self.stacked_widget.update()
    def show_mail_view(self):
        self.configuration_writer.update_configuration(
            configuration=self.data_provider.get_main_configuration()
        )
        self.stacked_widget.setCurrentIndex(3)
        self.stacked_widget.update()

    @pyqtSlot()
    def __on_input_change(self):
        sender = self.sender()

        if sender.objectName() == "language" and isinstance(sender, QComboBox):
            print(StringValueConvertors.language_to_country_code(sender.currentText()))
            self._globalViewModel.update_model(sender.objectName(),
                                               StringValueConvertors.language_to_country_code(sender.currentText()))
        elif sender.objectName() == "alertColor" and isinstance(sender, QComboBox):
            print(StringValueConvertors.color_name_to_hex(sender.currentText()))
            self._globalViewModel.update_model(sender.objectName(),
                                               StringValueConvertors.color_name_to_hex(sender.currentText()))
        elif sender.objectName() == "highlightColor" and isinstance(sender, QComboBox):
            print(StringValueConvertors.color_name_to_hex(sender.currentText()))
            self._globalViewModel.update_model(sender.objectName(),
                                               StringValueConvertors.color_name_to_hex(sender.currentText()))
    
    