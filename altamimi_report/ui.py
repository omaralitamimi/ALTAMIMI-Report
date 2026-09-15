from __future__ import annotations

import sys
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from . import __app_name__, __version__
from .db import add_report, delete_report, export_csv, init_db, list_reports, update_status
from .utils import PLATFORM_HELP, is_http_url, normalize_url

APP_STYLESHEET = """
QMainWindow, QWidget { background: #12141a; color: #f5f7fb; }
QTabWidget::pane { border: 1px solid #2a2f3a; border-radius: 12px; }
QTabBar::tab { background: #1a1f29; color: #cbd3df; padding: 10px 18px; margin: 2px; border-radius: 8px; }
QTabBar::tab:selected { background: #6d4aff; color: white; }
QLineEdit, QComboBox, QTextEdit, QTableWidget {
    background: #1a1f29; border: 1px solid #333a48; border-radius: 8px; padding: 8px; color: #f5f7fb;
}
QPushButton { background: #2a3140; border: 0; border-radius: 8px; padding: 9px 14px; font-weight: 600; }
QPushButton:hover { background: #394255; }
QPushButton#primary { background: #6d4aff; color: white; }
QPushButton#primary:hover { background: #7a5aff; }
QPushButton#danger { background: #7a2d3b; color: white; }
QFrame#card { background: #171b23; border: 1px solid #262c37; border-radius: 14px; }
QHeaderView::section { background: #202632; color: #f5f7fb; padding: 8px; border: 0; }
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        init_db()
        self.setWindowTitle(f"{__app_name__} — v{__version__}")
        self.resize(1050, 700)
        self.setMinimumSize(860, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        self._build_ui()
        self.refresh_history()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(16)

        title = QLabel("ALTAMIMI Report")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        subtitle = QLabel("مساعد عام لتنظيم البلاغات وفتح الروابط الرسمية — بدون تخزين كلمات مرور وبدون إرسال جماعي")
        subtitle.setStyleSheet("color:#aeb7c6;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_new_report_tab(), "بلاغ جديد")
        self.tabs.addTab(self._build_history_tab(), "السجل")
        self.tabs.addTab(self._build_about_tab(), "حول الأداة")
        layout.addWidget(self.tabs, 1)
        self.setCentralWidget(root)
        self.statusBar().showMessage("جاهز")

    def _card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        return frame

    def _build_new_report_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(14)

        card = self._card()
        form = QFormLayout(card)
        form.setContentsMargins(18, 18, 18, 18)
        form.setSpacing(12)

        self.platform = QComboBox()
        self.platform.addItems(["Facebook", "Instagram", "X / Twitter", "TikTok", "أخرى"])
        self.target_url = QLineEdit()
        self.target_url.setPlaceholderText("https://...")
        self.reason = QComboBox()
        self.reason.addItems([
            "محتوى مزعج / Spam",
            "انتحال شخصية",
            "احتيال أو خداع",
            "مضايقة أو تنمّر",
            "خطاب كراهية",
            "محتوى جنسي أو عُري",
            "تهديد أو عنف",
            "سبب آخر",
        ])
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("ملاحظات أو وصف مختصر للحالة...")
        self.notes.setMaximumHeight(120)

        form.addRow("المنصة:", self.platform)
        form.addRow("رابط الحساب/الصفحة/المنشور:", self.target_url)
        form.addRow("سبب البلاغ:", self.reason)
        form.addRow("ملاحظات:", self.notes)
        layout.addWidget(card)

        info = QLabel(
            "الأداة لا ترسل البلاغ تلقائيًا. تفتح الهدف في متصفحك، وأنت تُكمل البلاغ من واجهة المنصة نفسها. "
            "هذا يجعل المشروع مناسبًا للنشر العام على GitHub ويمنع إساءة الاستخدام."
        )
        info.setWordWrap(True)
        info.setStyleSheet("background:#171b23;border:1px solid #2b3340;border-radius:10px;padding:12px;color:#bfc8d5;")
        layout.addWidget(info)

        buttons = QHBoxLayout()
        open_btn = QPushButton("فتح الهدف في المتصفح")
        open_btn.setObjectName("primary")
        open_btn.clicked.connect(self.open_target)
        help_btn = QPushButton("فتح مركز مساعدة المنصة")
        help_btn.clicked.connect(self.open_help)
        draft_btn = QPushButton("حفظ كمسودة")
        draft_btn.clicked.connect(lambda: self.save_record("مسودة"))
        done_btn = QPushButton("تسجيله كمُرسل يدويًا")
        done_btn.clicked.connect(lambda: self.save_record("تم الإرسال يدويًا"))

        buttons.addWidget(open_btn)
        buttons.addWidget(help_btn)
        buttons.addStretch(1)
        buttons.addWidget(draft_btn)
        buttons.addWidget(done_btn)
        layout.addLayout(buttons)
        layout.addStretch(1)
        return page

    def _build_history_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 18, 14, 14)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "التاريخ", "المنصة", "الرابط", "السبب", "الملاحظات", "الحالة"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        layout.addWidget(self.table, 1)

        buttons = QHBoxLayout()
        refresh = QPushButton("تحديث")
        refresh.clicked.connect(self.refresh_history)
        mark = QPushButton("تغيير الحالة إلى مُراجع")
        mark.clicked.connect(self.mark_reviewed)
        delete = QPushButton("حذف المحدد")
        delete.setObjectName("danger")
        delete.clicked.connect(self.delete_selected)
        export = QPushButton("تصدير CSV")
        export.clicked.connect(self.export_history)
        buttons.addWidget(refresh)
        buttons.addWidget(mark)
        buttons.addWidget(export)
        buttons.addStretch(1)
        buttons.addWidget(delete)
        layout.addLayout(buttons)
        return page

    def _build_about_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(22, 24, 22, 22)
        heading = QLabel("ALTAMIMI Report")
        heading.setFont(QFont("Arial", 20, QFont.Bold))
        body = QLabel(
            "الإصدار 1.0.0\n\n"
            "مشروع مفتوح المصدر لتنظيم البلاغات، حفظ سجل محلي، وفتح الهدف ومركز مساعدة المنصة.\n\n"
            "الخصوصية: لا يخزن بريدك أو كلمة المرور، ولا يرسل بيانات إلى خادم خارجي. قاعدة البيانات محفوظة محليًا على جهاز المستخدم.\n\n"
            "حدود الاستخدام: لا يحتوي على بلاغات جماعية، تدوير بروكسيات، anti-detection، أو تجاوز أنظمة المنصات.\n\n"
            "الترخيص: MIT"
        )
        body.setWordWrap(True)
        body.setStyleSheet("color:#c6ceda;font-size:14px;")
        layout.addWidget(heading)
        layout.addWidget(body)
        layout.addStretch(1)
        return page

    def _validated_url(self) -> str | None:
        url = normalize_url(self.target_url.text())
        if not is_http_url(url):
            QMessageBox.warning(self, "رابط غير صالح", "أدخل رابطًا صحيحًا يبدأ بـ http:// أو https://")
            return None
        self.target_url.setText(url)
        return url

    def open_target(self) -> None:
        url = self._validated_url()
        if not url:
            return
        QDesktopServices.openUrl(QUrl(url))
        self.statusBar().showMessage("تم فتح الرابط في المتصفح")

    def open_help(self) -> None:
        platform = self.platform.currentText()
        url = PLATFORM_HELP.get(platform)
        if not url:
            webbrowser.open("https://www.google.com/search?q=social+media+reporting+help")
            return
        QDesktopServices.openUrl(QUrl(url))

    def save_record(self, status: str) -> None:
        url = self._validated_url()
        if not url:
            return
        add_report(
            platform=self.platform.currentText(),
            target_url=url,
            reason=self.reason.currentText(),
            notes=self.notes.toPlainText().strip(),
            status=status,
        )
        self.refresh_history()
        self.statusBar().showMessage("تم حفظ السجل")
        QMessageBox.information(self, "تم", "تم حفظ السجل محليًا بنجاح.")

    def refresh_history(self) -> None:
        records = list_reports()
        self.table.setRowCount(len(records))
        for row_idx, r in enumerate(records):
            values = [r.id, r.created_at, r.platform, r.target_url, r.reason, r.notes, r.status]
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignVCenter | (Qt.AlignRight if col_idx != 0 else Qt.AlignCenter))
                self.table.setItem(row_idx, col_idx, item)

    def _selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "اختر سجلًا", "اختر صفًا من السجل أولًا.")
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def mark_reviewed(self) -> None:
        report_id = self._selected_id()
        if report_id is None:
            return
        update_status(report_id, "مُراجع")
        self.refresh_history()

    def delete_selected(self) -> None:
        report_id = self._selected_id()
        if report_id is None:
            return
        answer = QMessageBox.question(self, "تأكيد الحذف", "هل تريد حذف هذا السجل؟")
        if answer == QMessageBox.Yes:
            delete_report(report_id)
            self.refresh_history()

    def export_history(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "تصدير السجل", "ALTAMIMI_reports.csv", "CSV (*.csv)")
        if not path:
            return
        export_csv(Path(path))
        QMessageBox.information(self, "تم", "تم تصدير السجل بنجاح.")


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    window = MainWindow()
    window.show()
    raise SystemExit(app.exec())
