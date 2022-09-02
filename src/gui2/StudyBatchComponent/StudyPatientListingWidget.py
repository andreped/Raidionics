from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QLabel, QSpacerItem,\
    QGridLayout, QMenu, QAction
from PySide2.QtCore import QSize, Qt, Signal, QPoint
from PySide2.QtGui import QIcon, QPixmap
import os
import logging
from src.gui2.StudyBatchComponent.PatientListingWidgetItem import PatientListingWidgetItem
from src.utils.software_config import SoftwareConfigResources


class StudyPatientListingWidget(QWidget):
    """

    """
    patient_selected = Signal(str)

    def __init__(self, parent=None):
        super(StudyPatientListingWidget, self).__init__()
        self.parent = parent
        self.setFixedWidth((375 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())
        self.setBaseSize(QSize(self.width(), 500))  # Defining a base size is necessary as inner widgets depend on it.
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.study_patient_widgetitems = {}

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.patients_list_scrollarea = QScrollArea()
        self.patients_list_scrollarea.show()
        self.patients_list_scrollarea_layout = QVBoxLayout()
        self.patients_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.patients_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.patients_list_scrollarea.setWidgetResizable(True)
        self.patients_list_scrollarea_dummy_widget = QLabel()
        self.patients_list_scrollarea_layout.setSpacing(0)
        self.patients_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.patients_list_scrollarea_layout.addStretch(1)
        self.patients_list_scrollarea_dummy_widget.setLayout(self.patients_list_scrollarea_layout)
        self.patients_list_scrollarea.setWidget(self.patients_list_scrollarea_dummy_widget)
        self.layout.addWidget(self.patients_list_scrollarea)
        self.__set_interface_listing_header()

    def __set_interface_listing_header(self):
        self.header_layout = QHBoxLayout()
        self.header_patient_label = QLabel("Patient")
        self.header_check_label = QLabel("Visualize")
        self.header_layout.addWidget(self.header_patient_label)
        self.header_layout.addWidget(self.header_check_label)
        self.patients_list_scrollarea_layout.insertLayout(self.patients_list_scrollarea_layout.count() - 1,
                                                          self.header_layout)

    def __set_layout_dimensions(self):
        self.patients_list_scrollarea.setBaseSize(QSize(self.width(), 300))
        self.header_patient_label.setFixedHeight(30)
        self.header_check_label.setFixedHeight(30)

    def __set_connections(self):
        pass

    def __set_stylesheets(self):
        software_ss = SoftwareConfigResources.getInstance().stylesheet_components
        font_color = software_ss["Color7"]
        font_style = 'normal'
        background_color = software_ss["Color5"]
        pressed_background_color = software_ss["Color6"]

        self.setStyleSheet("""
        StudyPatientListingWidget{
        background-color: """ + background_color + """;
        }""")

    def adjustSize(self) -> None:
        items = (self.patients_list_scrollarea_layout.itemAt(i) for i in range(self.patients_list_scrollarea_layout.count()))
        actual_height = 0
        for w in items:
            if (w.__class__ == QHBoxLayout) or (w.__class__ == QVBoxLayout):
                max_height = 0
                sub_items = [w.itemAt(i) for i in range(w.count())]
                for sw in sub_items:
                    if sw.__class__ != QSpacerItem:
                        if sw.wid.sizeHint().height() > max_height:
                            max_height = sw.wid.sizeHint().height()
                actual_height += max_height
            elif w.__class__ == QGridLayout:
                pass
            elif w.__class__ != QSpacerItem:
                size = w.wid.sizeHint()
                actual_height += size.height()
            else:
                pass
        self.patients_list_scrollarea_dummy_widget.setFixedSize(QSize(self.size().width(), actual_height))
        # logging.debug("Study patient listing scroll area size set to {}.\n".format(QSize(self.size().width(),
        #                                                                                  actual_height)))

    def on_patient_imported(self, patient_uid: str) -> None:
        wid = PatientListingWidgetItem(patient_uid=patient_uid, parent=self)
        self.study_patient_widgetitems[patient_uid] = wid
        self.patients_list_scrollarea_layout.insertWidget(self.patients_list_scrollarea_layout.count() - 1, wid)
        wid.patient_selected.connect(self.patient_selected)
        wid.patient_removed.connect(self.on_patient_removed)

    def on_patient_name_edited(self, patient_uid: str, new_name: str) -> None:
        """
        Updates the visible name for the selected patient in the listing, if the patient is part of the study.
        """
        if patient_uid in list(self.study_patient_widgetitems.keys()):
            self.study_patient_widgetitems[patient_uid].patient_uid_label.setText(new_name)

    def on_patient_removed(self, patient_uid):
        self.patients_list_scrollarea_layout.removeWidget(self.study_patient_widgetitems[patient_uid])
        self.study_patient_widgetitems[patient_uid].setParent(None)
        del self.study_patient_widgetitems[patient_uid]
        self.adjustSize()
        self.repaint()

    def on_study_imported(self, study_uid):
        included_patient_uids = SoftwareConfigResources.getInstance().get_study(study_uid).get_included_patients_uids()
        for pid in included_patient_uids:
            self.on_patient_imported(pid)
