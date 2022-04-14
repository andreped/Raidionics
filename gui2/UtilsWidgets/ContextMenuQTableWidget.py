from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QMenu, QTableWidget, QAction
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Qt, QSize, Signal, QEvent

from gui2.UtilsWidgets.QCustomIconsPushButton import QCustomIconsPushButton


class ContextMenuQTableWidget(QTableWidget):
    """

    """

    def __init__(self, parent=None):
        super(ContextMenuQTableWidget, self).__init__(parent)
        self.__set_interface()
        self.__set_stylesheets()
        self.__set_connections()

    def __set_interface(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.context_menu = QMenu(self)
        self.display_metadata_action = QAction("Display DICOM metadata")
        self.context_menu.addAction(self.display_metadata_action)
        self.remove_action = QAction("Remove")
        self.context_menu.addAction(self.remove_action)

    def __set_stylesheets(self):
        pass

    def __set_connections(self):
        self.display_metadata_action.triggered.connect(self.__on_display_metadata_triggered)

    def mousePressEvent(self, event):
        """
        """
        if event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())
            if item is not None:
                print('Table Item:', item.row(), item.column())
                self.context_menu.exec_(event.globalPos())
        super(ContextMenuQTableWidget, self).mousePressEvent(event)

    def __on_display_metadata_triggered(self):
        #@TODO. Should emit a Signal with the item pos to know which DICOM series it is.
        pass
