from core.config import THEME_COLOR

TablaNoEditableCSS = """
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #e0e0e0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: black;
                font-weight: bold;
            }
            QTableWidget::item:hover {
                background-color: #9CCDF0;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                border: 2px solid #ddd;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QScrollBar:vertical{
                border: none;
                background: #E3E3E3;
                width: 12 px;
                margin: 0px;
            }
            QScrollBar::handle:vertical{
                background: #ccc;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover{
                background: #999;
            }
            QScrollBar:horizontal {
                border: none;
                background: #E3E3E3;
                height: 12px;
                margin: 0px;
            }

            QScrollBar::handle:horizontal {
                background: #ccc;
                min-width: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #999;
            }
        """

FRAME_STYLE = """QFrame { background-color: #f0f0f0; border-radius: 3px; }"""

TITULO = f"""
        QLabel {{
            color: {THEME_COLOR};
            font-size: 25px;
            font-weight: bold;
            font-family: Roboto;
            margin-bottom: 10px;
            }}
        """