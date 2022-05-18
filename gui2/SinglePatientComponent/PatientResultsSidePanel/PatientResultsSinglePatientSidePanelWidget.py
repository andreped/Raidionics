from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QLabel
from PySide2.QtCore import QSize, Qt, Signal
import os
from gui2.SinglePatientComponent.PatientResultsSidePanel.SinglePatientResultsWidget import SinglePatientResultsWidget
from utils.software_config import SoftwareConfigResources


class PatientResultsSinglePatientSidePanelWidget(QWidget):
    """
    @FIXME. For enabling a global QEvent catch, have to listen/retrieve from the patient_list_scrollarea_dummy_widget,
    and maybe the SinglePatientResultsWidget if the scroll area is filled.
    """
    patient_selected = Signal(str)  # Unique internal id of the selected patient

    def __init__(self, parent=None):
        super(PatientResultsSinglePatientSidePanelWidget, self).__init__()
        self.parent = parent
        self.setFixedWidth((315 / SoftwareConfigResources.getInstance().get_optimal_dimensions().width()) * self.parent.baseSize().width())
        self.setBaseSize(QSize(self.width(), 500))  # Defining a base size is necessary as inner widgets depend on it.
        self.__set_interface()
        self.__set_layout_dimensions()
        self.__set_connections()
        self.__set_stylesheets()
        self.patient_results_widgets = {}

    def __set_interface(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.patient_list_scrollarea = QScrollArea()
        self.patient_list_scrollarea_layout = QVBoxLayout()
        self.patient_list_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.patient_list_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.patient_list_scrollarea.setWidgetResizable(True)
        self.patient_list_scrollarea_dummy_widget = QLabel()
        self.patient_list_scrollarea_dummy_widget.setStyleSheet("QLabel{background-color:rgb(1, 10, 100);)}")
        self.patient_list_scrollarea_layout.setSpacing(0)
        self.patient_list_scrollarea_layout.setContentsMargins(0, 0, 0, 0)
        self.patient_list_scrollarea_layout.addStretch(1)
        self.patient_list_scrollarea_dummy_widget.setLayout(self.patient_list_scrollarea_layout)
        self.patient_list_scrollarea.setWidget(self.patient_list_scrollarea_dummy_widget)
        self.bottom_layout = QHBoxLayout()
        self.bottom_add_patient_pushbutton = QPushButton("Import patient")
        self.bottom_add_patient_pushbutton.setFixedSize(QSize(80, 30))
        self.bottom_layout.addWidget(self.bottom_add_patient_pushbutton)
        self.layout.addWidget(self.patient_list_scrollarea)
        self.layout.addLayout(self.bottom_layout)

    def __set_layout_dimensions(self):
        # self.patient_list_scrollarea.setBaseSize(QSize(self.width(), 500))
        self.patient_list_scrollarea.setMinimumSize(QSize(self.width(), 300))

    def __set_connections(self):
        self.bottom_add_patient_pushbutton.clicked.connect(self.on_add_new_empty_patient)

    def __set_stylesheets(self):
        # self.overall_label.setStyleSheet("QLabel{background-color:rgb(0, 255, 0);}")
        self.patient_list_scrollarea.setStyleSheet("QScrollArea{background-color:rgb(0, 255, 0);}")
        # self.patient_list_scrollarea_dummy_widget.setStyleSheet("""QLabel{background-color:rgb(0, 128, 0);}""")

    def on_import_data(self):
        """
        In case some patients where imported at the same time as some image for the current patient?
        """
        loaded_patient_uids = list(SoftwareConfigResources.getInstance().patients_parameters.keys())
        for uid in loaded_patient_uids:
            if uid not in list(self.patient_results_widgets.keys()):
                self.add_new_patient(uid)

        if len(self.patient_results_widgets) == 1:
            self.__on_patient_selection(True, list(self.patient_results_widgets.keys())[0])

    def on_import_patient(self, uid: str) -> None:
        """
        A patient result instance is created for the newly imported patient, and appended at the bottom of the
        scroll area with all other already imported patients.
        """
        # @TODO. Which behaviour if only a temp patient opened, should it be deleted?
        self.add_new_patient(uid)

        # A patient is to be displayed at all time
        if len(self.patient_results_widgets) == 1:
            self.__on_patient_selection(True, list(self.patient_results_widgets.keys())[0])

    def add_new_patient(self, patient_name):
        # @TODO. Have to connect signals/slots from each dynamic widget, to enforce the one active patient at all time.
        pat_widget = SinglePatientResultsWidget(patient_name, self)
        pat_widget.setBaseSize(QSize(self.baseSize().width(), self.baseSize().height()))
        # pat_widget.setMaximumSize(QSize(self.baseSize().width(), self.baseSize().height()))
        pat_widget.setMinimumSize(QSize(self.baseSize().width(), int(self.baseSize().height() / 2)))
        pat_widget.populate_from_patient(patient_name)
        self.patient_results_widgets[patient_name] = pat_widget
        self.patient_list_scrollarea_layout.insertWidget(self.patient_list_scrollarea_layout.count() - 1, pat_widget)
        if len(self.patient_results_widgets) == 1:
            pat_widget.manual_header_pushbutton_clicked(True)
        # else:
        #     for i, wid in enumerate(list(self.patient_results_widgets.keys())):
        #         self.patient_results_widgets[wid].manual_header_pushbutton_clicked(False)
        #     pat_widget.manual_header_pushbutton_clicked(True)

        pat_widget.clicked_signal.connect(self.__on_patient_selection)

    def __on_patient_selection(self, state, widget_id):
        # @TODO. Must better handle the interaction between all patient results objects
        for i, wid in enumerate(list(self.patient_results_widgets.keys())):
            if wid != widget_id:
                self.patient_results_widgets[wid].manual_header_pushbutton_clicked(False)
        self.patient_results_widgets[widget_id].header_pushbutton.setEnabled(False)
        SoftwareConfigResources.getInstance().set_active_patient(widget_id)
        # When a patient is selected in the left panel, a visual update of the central/right panel is triggered
        self.patient_selected.emit(widget_id)

    def on_add_new_empty_patient(self):
        uid, error_msg = SoftwareConfigResources.getInstance().add_new_empty_patient("Temp Patient")
        self.add_new_patient(uid)

    def on_standardized_report_imported(self):
        self.patient_results_widgets[SoftwareConfigResources.getInstance().get_active_patient().patient_id].on_standardized_report_imported()
