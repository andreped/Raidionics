from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication
from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QIcon, QPixmap
import os

from gui2.UtilsWidgets.QCollapsibleGroupBox import QCollapsibleGroupBox
from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton
from gui2.SinglePatientComponent.LayersInteractorSidePanel.LayersInteractorAtlasCollapsibleGroupBox import LayersInteractorAtlasCollapsibleGroupBox

from utils.software_config import SoftwareConfigResources


class LayersInteractorAtlasesWidget(QCollapsibleGroupBox):
    """

    """
    atlas_view_toggled = Signal(str, bool)

    def __init__(self, parent=None):
        super(LayersInteractorAtlasesWidget, self).__init__("Structures", self, header_style='left')
        self.set_header_icons(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../Images/arrow_right_icon.png'),
                              QSize(20, 20),
                              os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                           '../../Images/arrow_down_icon.png'),
                              QSize(20, 20), side='left')
        self.parent = parent
        self.volumes_widget = {}
        self.__set_interface()
        self.__set_stylesheets()

    def __set_interface(self):
        self.content_label_layout.addStretch(1)

    def __set_stylesheets(self):
        self.content_label.setStyleSheet("QLabel{background-color:rgb(255,0,255);}")

    def adjustSize(self):
        actual_height = 0
        for w in self.volumes_widget:
            size = self.volumes_widget[w].sizeHint()
            actual_height += size.height()
        self.content_label.setFixedSize(QSize(self.size().width(), actual_height))

    def reset(self):
        """

        """
        for w in list(self.volumes_widget):
            self.content_label_layout.removeWidget(self.volumes_widget[w])
            self.volumes_widget[w].deleteLater()
            self.volumes_widget.pop(w)
        self.header_pushbutton.setChecked(False)
        self.header_pushbutton.clicked.emit()

    def on_volume_view_toggled(self, volume_uid, state):
        """
        @TODO. Might not be necessary, don't care about uid and state, just that the current annotations must be removed
        """
        self.reset()
        self.on_import_data()
        # for k in list(self.volumes_widget.keys()):
        #     wid = self.volumes_widget[k]
        #     self.content_label_layout.removeWidget(wid)
        #     self.volumes_widget.pop(k)

    # def on_annotation_volume_import(self, uid):

    def on_patient_view_toggled(self, patient_uid):
        active_patient = SoftwareConfigResources.getInstance().patients_parameters[patient_uid]
        # @TODO. Should not load all annotations, but only the ones of the current MRI volume
        # Or we should display all annotations regardless, and group them under their respective MRI parents.
        # In addition, there will be another groupbox somewhere to specify if we use the raw patient space, the
        # co-registered patient space, or the MNI space for displaying.
        for volume_id in list(active_patient.annotation_volumes.keys()):
            if not volume_id in list(self.volumes_widget.keys()):
                self.on_import_volume(volume_id)
        self.adjustSize()  # To force a repaint of the layout with the new elements

    def on_import_volume(self, volume_id):
        volume_widget = LayersInteractorAtlasCollapsibleGroupBox(uid=volume_id, parent=self)
        self.volumes_widget[volume_id] = volume_widget
        self.content_label_layout.insertWidget(self.content_label_layout.count() - 1, volume_widget)

        # On-the-fly signals/slots connection for the newly created QWidget
        volume_widget.header_pushbutton.clicked.connect(self.adjustSize)
        volume_widget.right_clicked.connect(self.on_visibility_clicked)
        # Triggers a repaint with adjusted size for the layout
        self.adjustSize()

    def on_visibility_clicked(self, uid, state):
        self.atlas_view_toggled.emit(uid, state)
