import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt, QSize, QCoreApplication, QProcess
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QGridLayout, QComboBox, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QFrame, QPushButton)

from smail import style
from sconf.configuration.models.global_configuration import GlobalConfiguration
from sconf.configuration.models.smail_configuration import SmailConfiguration
from sconf.ui.components.ui_transformation.transformation import UiElementTransformation
from sconf.ui.convertors.value_convertors import StringValueConvertors
from sconf.ui.convertors.value_validators import Validators
from sconf.ui.styles.global_style_sheets import get_default_label_style, get_default_input_box_style, \
    get_default_dropdown_style, get_default_settings_button_style, get_default_settings_text_edit_style, \
    get_error_label_style, get_default_table_style, get_default_menu_button_style, get_active_menu_button_style
from sconf.ui.view_models.smail_settings_view_model import SmailViewModel
from sconf.ui.view.dialog.table_input_dialog import TablePopup


# TODO: Once initial presentation is done change this to correct binding with the view model
class MailSettingsView(QWidget):
    _smailViewModel: SmailViewModel
    _smailConfiguration: SmailConfiguration
    _globalConfiguration: GlobalConfiguration
    _configurationFolder: str

    def __init__(self, smail_configuration: SmailConfiguration,
                 globalConfiguration: GlobalConfiguration,
                 configurationFolder: str,
                 highlight_color: str,
                    data_provider, configuration_writer, stacked_widget
                ):
        super().__init__()

        self.highlight_color = highlight_color
        self._smailConfiguration = smail_configuration
        self._globalConfiguration = globalConfiguration
        self._smailViewModel = SmailViewModel(smail_configuration, globalConfiguration)
        self._configurationFolder = configurationFolder

        self.main_layout = QVBoxLayout()
        self.data_provider = data_provider
        self.configuration_writer = configuration_writer
        self.stacked_widget = stacked_widget
        # Create layout for labels and input fields
        self.button_frame = QFrame(self)
        self.button_frame.setStyleSheet(style.get_button_frame_style())
        self.button_frame.setFrameShape(QFrame.StyledPanel)
        self.button_layout = QHBoxLayout(self.button_frame)
        spacer_left = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_right = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        #self.button_layout.addItem(spacer_left)
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
            if name == "X":
                pixmap_icon = QPixmap("icons/exit.png").scaled(72, 72, Qt.KeepAspectRatio,
                                                                        Qt.SmoothTransformation)
                button.setIconSize(QSize(100, 100))
                button.setIcon(QIcon(pixmap_icon))
            self.button_layout.addWidget(button, alignment=Qt.AlignCenter)
            button.setStyleSheet(style.get_button_style(self.data_provider))

        self.button_layout.setSpacing(10)
        #self.button_layout.addItem(spacer_right)
        self.button_frame.setStyleSheet(style.get_button_frame_style())
        self.main_layout.addWidget(self.button_frame)

        self.bottom_frame = QFrame(self)
        self.grid_layout = QGridLayout(self.bottom_frame)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setColumnMinimumWidth(0, 261)
        self.grid_layout.setRowStretch(4, 0)

        # Labels
        label_senior_mail = QLabel("Senior email")
        label_senior_password = QLabel("Senior password")
        self.label_email_contact1 = QLabel("Email contact 1")
        self.label_email_contact2 = QLabel("Email contact 2")
        self.label_email_contact3 = QLabel("Email contact 3")
        self.label_email_contact4 = QLabel("Email contact 4")
        self.label_email_contact5 = QLabel("Email contact 5")
        self.label_email_contact6 = QLabel("Email contact 6")

        self.label_error = QLabel()
        self.label_error.setVisible(False)

        # DropDowns and Inputs
        self.senior_mail = QLineEdit(f"{self._smailConfiguration.seniorEmail if self._smailConfiguration.seniorEmail
                                                                           != "" else "Enter seniors email"}")
        self.senior_mail.setObjectName("seniorEmail")

        self.senior_password = QLineEdit(
            f"{self._smailConfiguration.seniorPassword if self._smailConfiguration.seniorPassword
                                                          != "" else "Enter password for seniors email"}")
        self.senior_password.setObjectName("seniorPassword")
        self.senior_password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.email_contact1 = QLineEdit( f"{self._smailConfiguration.emailContactsV2[0]["email1"] if self._smailConfiguration.emailContactsV2[0]["email1"]
                                                                           != "" else "Enter email contact 1"}")
       
        self.email_contact1.setObjectName("email1")

        self.email_contact2 = QLineEdit(f"{self._smailConfiguration.emailContactsV2[1]["email2"] if self._smailConfiguration.emailContactsV2[1]["email2"]
                                                                           != "" else "Enter email contact 2"}")
        self.email_contact2.setObjectName("email2")

        self.email_contact3 = QLineEdit(f"{self._smailConfiguration.emailContactsV2[2]["email3"] if self._smailConfiguration.emailContactsV2[2]["email3"]
                                                                           != "" else "Enter email contact 3"}")
        self.email_contact3.setObjectName("email3")
        self.email_contact4 = QLineEdit(f"{self._smailConfiguration.emailContactsV2[3]["email4"] if self._smailConfiguration.emailContactsV2[3]["email4"]
                                                                           != "" else "Enter email contact 4"}")
        self.email_contact4.setObjectName("email4")

        self.email_contact5 = QLineEdit(f"{self._smailConfiguration.emailContactsV2[4]["email5"] if self._smailConfiguration.emailContactsV2[4]["email5"]
                                                                           != "" else "Enter email contact 5"}")
        self.email_contact5.setObjectName("email5")

        self.email_contact6 = QLineEdit(f"{self._smailConfiguration.emailContactsV2[5]["email6"] if self._smailConfiguration.emailContactsV2[5]["email6"]
                                                                           != "" else "Enter email contact 6"}")
        self.email_contact6.setObjectName("email6")
    

        

        self.grid_layout.addWidget(label_senior_mail, 0, 0)
        self.grid_layout.addWidget(self.senior_mail, 0, 1)

        self.grid_layout.addWidget(label_senior_password, 1, 0)
        self.grid_layout.addWidget(self.senior_password, 1, 1)

        self.grid_layout.addWidget(self.label_email_contact1, 2, 0)
        self.grid_layout.addWidget(self.email_contact1, 2, 1)
        self.grid_layout.addWidget(self.label_email_contact2, 3, 0)
        self.grid_layout.addWidget(self.email_contact2, 3, 1)
        self.grid_layout.addWidget(self.label_email_contact3, 4, 0)
        self.grid_layout.addWidget(self.email_contact3, 4, 1)
        self.grid_layout.addWidget(self.label_email_contact4, 5, 0)
        self.grid_layout.addWidget(self.email_contact4, 5, 1)
        self.grid_layout.addWidget(self.label_email_contact5, 6, 0)
        self.grid_layout.addWidget(self.email_contact5, 6, 1)
        self.grid_layout.addWidget(self.label_email_contact6, 7, 0)
        self.grid_layout.addWidget(self.email_contact6, 7, 1)


        self.senior_mail.textChanged.connect(self.__on_input_change)
        self.senior_password.textChanged.connect(self.__on_input_email_change)
        self.email_contact1.textChanged.connect(lambda: self.__on_input_email_change(0))
        self.email_contact2.textChanged.connect(lambda: self.__on_input_email_change(1))             
        self.email_contact3.textChanged.connect(lambda: self.__on_input_email_change(2))
        self.email_contact4.textChanged.connect(lambda: self.__on_input_email_change(3))
        self.email_contact5.textChanged.connect(lambda: self.__on_input_email_change(4))
        self.email_contact6.textChanged.connect(lambda: self.__on_input_email_change(5))
        self.main_layout.addWidget(self.bottom_frame)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

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
        self.menu_buttons["Visual"].setStyleSheet(style.get_button_style(self.data_provider))
        self.menu_buttons["Mail"].setStyleSheet(style.get_button_style(self.data_provider, highlight=True))

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
        QCoreApplication.quit()
        status = QProcess.startDetached(sys.executable, sys.argv)
        print(status)
    def show_security_view(self):
        self.stacked_widget.setCurrentIndex(1)
        self.stacked_widget.update()
    def show_visual_view(self):
        self.stacked_widget.setCurrentIndex(2)
        self.stacked_widget.update()
    def show_mail_view(self):
        self.stacked_widget.setCurrentIndex(3)
        self.stacked_widget.update()

    @pyqtSlot()
    def __on_input_change(self):
        sender = self.sender()
        if isinstance(sender, QLineEdit):
            self._smailViewModel.update_model(sender.objectName(),
                                              sender.text())
        if isinstance(sender, QComboBox):
            self._smailViewModel.update_model(sender.objectName(),
                                              StringValueConvertors.string_to_bool(sender.currentText()))

        if isinstance(sender, QFileDialog):
            self._smailViewModel.update_model(sender.objectName(),
                                              sender.selectedFiles())

    def __on_input_email_change(self, index):
        sender = self.sender()
        if isinstance(sender, QLineEdit):
            self._smailConfiguration.emailContactsV2[index][sender.objectName()] = sender.text()
            print("Updated email contacts:", sender.objectName())