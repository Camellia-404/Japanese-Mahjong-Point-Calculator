# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(800, 700)
        self.chk_dealer = QCheckBox(Form)
        self.chk_dealer.setObjectName(u"chk_dealer")
        self.chk_dealer.setGeometry(QRect(30, 30, 88, 24))
        self.chk_tsumo = QCheckBox(Form)
        self.chk_tsumo.setObjectName(u"chk_tsumo")
        self.chk_tsumo.setGeometry(QRect(30, 50, 88, 24))
        self.chk_riichi = QCheckBox(Form)
        self.chk_riichi.setObjectName(u"chk_riichi")
        self.chk_riichi.setGeometry(QRect(30, 70, 88, 24))
        self.btn_calculate = QPushButton(Form)
        self.btn_calculate.setObjectName(u"btn_calculate")
        self.btn_calculate.setGeometry(QRect(620, 580, 121, 41))
        self.lbl_result = QLabel(Form)
        self.lbl_result.setObjectName(u"lbl_result")
        self.lbl_result.setGeometry(QRect(160, 50, 331, 111))
        self.frame_palette = QFrame(Form)
        self.frame_palette.setObjectName(u"frame_palette")
        self.frame_palette.setGeometry(QRect(60, 270, 681, 300))
        self.frame_palette.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_palette.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame_palette)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame_hand = QFrame(Form)
        self.frame_hand.setObjectName(u"frame_hand")
        self.frame_hand.setGeometry(QRect(80, 180, 661, 80))
        self.frame_hand.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_hand.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_dora = QFrame(Form)
        self.frame_dora.setObjectName(u"frame_dora")
        self.frame_dora.setGeometry(QRect(540, 90, 201, 80))
        self.frame_dora.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_dora.setFrameShadow(QFrame.Shadow.Raised)
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(60, 580, 551, 41))
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.radio_hand = QRadioButton(self.groupBox)
        self.radio_hand.setObjectName(u"radio_hand")
        self.radio_hand.setChecked(True)

        self.horizontalLayout.addWidget(self.radio_hand)

        self.radio_dora = QRadioButton(self.groupBox)
        self.radio_dora.setObjectName(u"radio_dora")

        self.horizontalLayout.addWidget(self.radio_dora)

        self.radio_ankan = QRadioButton(self.groupBox)
        self.radio_ankan.setObjectName(u"radio_ankan")

        self.horizontalLayout.addWidget(self.radio_ankan)

        self.radio_minkan = QRadioButton(self.groupBox)
        self.radio_minkan.setObjectName(u"radio_minkan")

        self.horizontalLayout.addWidget(self.radio_minkan)

        self.radio_chi = QRadioButton(self.groupBox)
        self.radio_chi.setObjectName(u"radio_chi")

        self.horizontalLayout.addWidget(self.radio_chi)

        self.radio_pon = QRadioButton(self.groupBox)
        self.radio_pon.setObjectName(u"radio_pon")

        self.horizontalLayout.addWidget(self.radio_pon)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(521, 90, 16, 81))
        self.label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label.setAutoFillBackground(True)
        self.label.setWordWrap(True)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(60, 180, 16, 81))
        self.label_2.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_2.setAutoFillBackground(True)
        self.label_2.setWordWrap(True)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.chk_dealer.setText(QCoreApplication.translate("Form", u"\u89aa", None))
        self.chk_tsumo.setText(QCoreApplication.translate("Form", u"\u30c4\u30e2", None))
        self.chk_riichi.setText(QCoreApplication.translate("Form", u"\u30ea\u30fc\u30c1", None))
        self.btn_calculate.setText(QCoreApplication.translate("Form", u"\u8a08\u7b97", None))
        self.lbl_result.setText("")
        self.groupBox.setTitle("")
        self.radio_hand.setText(QCoreApplication.translate("Form", u"\u624b\u724c\u9078\u629e", None))
        self.radio_dora.setText(QCoreApplication.translate("Form", u"\u30c9\u30e9\u9078\u629e", None))
        self.radio_ankan.setText(QCoreApplication.translate("Form", u"\u6697\u69d3", None))
        self.radio_minkan.setText(QCoreApplication.translate("Form", u"\u660e\u69d3", None))
        self.radio_chi.setText(QCoreApplication.translate("Form", u"\u30c1\u30fc", None))
        self.radio_pon.setText(QCoreApplication.translate("Form", u"\u30dd\u30f3", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u30c9\u30e9", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u624b\u724c", None))
    # retranslateUi

