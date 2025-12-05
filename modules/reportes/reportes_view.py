"""
HUO008 - Reportes de ventas
Como administrador, quiero poder generar reportes de ventas diarias,
semanales y mensuales para analizar el rendimiento del negocio.
				
HUO009 - Productos más vendidos
Como administrador, quiero poder ver qué productos son los más 
vendidos para optimizar la gestión de inventario y compras.
				
HUO010 - Reporte de ganancias y pérdidas	
Como administrador, quiero poder generar un reporte de ganancias 
y pérdidas para evaluar la salud financiera del minimarket.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTabWidget, QDateEdit, QComboBox, QFileDialog, QMessageBox,
                             QTableWidget, QTableWidgetItem, QSizePolicy)
from PyQt5.QtCore import Qt, QDate
from shared.styles import TITULO, TablaNoEditableCSS
from modules.ventas.service.venta_service import VentaService
from modules.reportes.exportador_service import exportar_pdf, exportar_excel
from modules.productos.view.inventario_view import TablaNoEditable
import pandas as pd
from core.database import db

class ReportesFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.venta_service = VentaService()  # Usar Service en vez de Model
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título con estilo moderno
        titulo = QLabel("Reportes y Análisis")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(TITULO)
        layout.addWidget(titulo)

        # Panel de filtros con fondo y bordes
        filtros_widget = QWidget()
        filtros_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        filtros_layout = QHBoxLayout(filtros_widget)
        filtros_layout.setSpacing(10)

        # Estilo para labels
        label_style = """
            QLabel {
                font-weight: bold;
                color: #34495e;
                font-size: 13px;
            }
        """

        # Estilo para date edits y combos
        input_style = """
            QDateEdit, QComboBox {
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                min-width: 200px;
            }
            QDateEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QDateEdit::drop-down, QComboBox::drop-down {
                border: none;
                width: 25px;
            }
        """

        self.fecha_desde = QDateEdit(QDate.currentDate().addDays(-7))
        self.fecha_hasta = QDateEdit(QDate.currentDate())
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_desde.setStyleSheet(input_style)
        self.fecha_hasta.setStyleSheet(input_style)

        # Set minimum allowed date to first sale date if available
        try:
            min_fecha = self._get_min_fecha_venta()
            if min_fecha:
                qmin = QDate(min_fecha.year, min_fecha.month, min_fecha.day)
                self.fecha_desde.setMinimumDate(qmin)
                self.fecha_hasta.setMinimumDate(qmin)
                # If current default desde is before min, move it
                if self.fecha_desde.date() < qmin:
                    self.fecha_desde.setDate(qmin)
        except Exception:
            pass

        lbl_desde = QLabel("Desde:")
        lbl_desde.setStyleSheet(label_style)
        filtros_layout.addWidget(lbl_desde)
        filtros_layout.addWidget(self.fecha_desde)

        lbl_hasta = QLabel("Hasta:")
        lbl_hasta.setStyleSheet(label_style)
        filtros_layout.addWidget(lbl_hasta)
        filtros_layout.addWidget(self.fecha_hasta)

        self.lbl_periodo = QLabel("Periodo:")
        self.lbl_periodo.setStyleSheet(label_style)
        filtros_layout.addWidget(self.lbl_periodo)
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Diario", "Semanal", "Mensual"])
        self.combo_periodo.setStyleSheet(input_style)
        filtros_layout.addWidget(self.combo_periodo)

        filtros_layout.addStretch()

        btn_refresh = QPushButton("Actualizar")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 25px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        btn_refresh.clicked.connect(self.actualizar)
        filtros_layout.addWidget(btn_refresh)
        layout.addWidget(filtros_widget)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                padding: 4px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px 40px;
                margin-right: 3px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d5dbdb;
            }
        """)

        # Tab 1: Ventas por periodo
        self.tab_ventas = QWidget()
        v1 = QVBoxLayout(self.tab_ventas)
        v1.setContentsMargins(15, 15, 15, 15)
        v1.setSpacing(15)
        self.tab_ventas.setMinimumWidth(300)

        # Try to import matplotlib and prepare canvases; if missing, show a helpful label
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
            self._has_mpl = True
        except Exception:
            self._has_mpl = False

        if self._has_mpl:
            self.canvas1 = FigureCanvas(Figure(figsize=(10, 4), facecolor='white'))
            # allow canvas to expand and resize
            self.canvas1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            v1.addWidget(self.canvas1)
            self.placeholder1 = None
        else:
            self.canvas1 = None
            self.placeholder1 = QLabel("Matplotlib no está instalado. Instala: pip install matplotlib")
            self.placeholder1.setStyleSheet('color: red;')
            v1.addWidget(self.placeholder1)
        self.tabs.addTab(self.tab_ventas, "Ventas por periodo")
        # Tabla debajo del gráfico (ventas)
        self.table_ventas = TablaNoEditable()
        self._style_table(self.table_ventas)
        v1.addWidget(self.table_ventas)

        # Tab 2: Productos más vendidos
        self.tab_prod = QWidget()
        v2 = QVBoxLayout(self.tab_prod)
        v2.setContentsMargins(15, 15, 15, 15)
        v2.setSpacing(15)
        if self._has_mpl:
            # make canvas wider and slightly taller so bars have room
            self.canvas2 = FigureCanvas(Figure(figsize=(12, 5), facecolor='white'))
            self.canvas2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            v2.addWidget(self.canvas2)
            self.placeholder2 = None
        else:
            self.canvas2 = None
            self.placeholder2 = QLabel("Matplotlib no está instalado. Instala: pip install matplotlib")
            self.placeholder2.setStyleSheet('color: red;')
            v2.addWidget(self.placeholder2)
        self.tabs.addTab(self.tab_prod, "Productos Top 10")
        # Tabla debajo del gráfico (productos)
        self.table_prod = TablaNoEditable()
        self._style_table(self.table_prod)
        v2.addWidget(self.table_prod)

        # Tab 3: Ganancias y pérdidas
        self.tab_gan = QWidget()
        v3 = QVBoxLayout(self.tab_gan)
        v3.setContentsMargins(15, 15, 15, 15)
        v3.setSpacing(15)
        if self._has_mpl:
            self.canvas3 = FigureCanvas(Figure(figsize=(10, 4), facecolor='white'))
            self.canvas3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            v3.addWidget(self.canvas3)
            self.placeholder3 = None
        else:
            self.canvas3 = None
            self.placeholder3 = QLabel("Matplotlib no está instalado. Instala: pip install matplotlib")
            self.placeholder3.setStyleSheet('color: red;')
            v3.addWidget(self.placeholder3)
        self.tabs.addTab(self.tab_gan, "Ganancias/Pérdidas")
        # Tabla debajo del gráfico (resumen)
        self.table_gan = TablaNoEditable()
        self._style_table(self.table_gan)
        v3.addWidget(self.table_gan)

        # Tab 4: Comprobantes Emitidos
        self.tab_comprobantes = QWidget()
        v4 = QVBoxLayout(self.tab_comprobantes)
        v4.setContentsMargins(15, 15, 15, 15)
        v4.setSpacing(15)
        
        # Leyenda de comprobantes con mejor organización
        leyenda_frame = QWidget()
        leyenda_frame.setStyleSheet("""
            QWidget {
                background-color: #e8f4f8;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        leyenda_layout = QHBoxLayout(leyenda_frame)
        leyenda_layout.setSpacing(20)
        
        # Título de la leyenda
        titulo_leyenda = QLabel("Leyenda:")
        titulo_leyenda.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        leyenda_layout.addWidget(titulo_leyenda)
        
        # Items de leyenda organizados
        items_leyenda = [
            ("🟢 Boleta", "#27ae60"),
            ("🔵 Factura", "#3498db"),
            ("Tarjeta", "#9b59b6"),
            ("Efectivo", "#2ecc71"),
            ("Yape/Plin", "#e74c3c"),
            ("Transferencia", "#f39c12")
        ]
        
        for texto, color in items_leyenda:
            label = QLabel(texto)
            label.setStyleSheet(f"font-size: 13px; color: {color}; font-weight: bold;")
            leyenda_layout.addWidget(label)
        
        leyenda_layout.addStretch()
        v4.addWidget(leyenda_frame)
        
        # Tabla de comprobantes
        self.table_comprobantes = TablaNoEditable()
        self._style_table(self.table_comprobantes)
        v4.addWidget(self.table_comprobantes)
        
        self.tabs.addTab(self.tab_comprobantes, "Comprobantes Emitidos")

        layout.addWidget(self.tabs)

        # show/hide periodo controls depending on active tab
        self.tabs.currentChanged.connect(self._on_tab_changed)
        # set initial visibility (only show for tab index 0)
        try:
            self._on_tab_changed(self.tabs.currentIndex())
        except Exception:
            pass

        # Botones exportar con diseño mejorado
        export_widget = QWidget()
        export_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        h = QHBoxLayout(export_widget)
        h.setSpacing(15)
        h.addStretch()

        btn_export_pdf = QPushButton("Exportar PDF")
        btn_export_pdf.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        btn_export_pdf.clicked.connect(lambda: self.exportar(forma='pdf'))

        btn_export_xlsx = QPushButton("Exportar Excel")
        btn_export_xlsx.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        btn_export_xlsx.clicked.connect(lambda: self.exportar(forma='xlsx'))

        h.addWidget(btn_export_pdf)
        h.addWidget(btn_export_xlsx)
        h.addStretch()
        layout.addWidget(export_widget)

        # Inicializar gráficos
        self.actualizar()

# → Aplicar estilo a las tablas
    def _style_table(self, table):
        table.setStyleSheet(TablaNoEditableCSS)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)

    def _on_tab_changed(self, index: int):
        """Hide periodo controls for tabs other than 'Ventas por periodo' (index 0)."""
        try:
            if index == 0:
                self.lbl_periodo.show()
                self.combo_periodo.show()
            else:
                self.lbl_periodo.hide()
                self.combo_periodo.hide()
        except Exception:
            # ignore if controls not ready
            pass

    def _rango_fechas(self):
        d = self.fecha_desde.date().toPyDate()
        h = self.fecha_hasta.date().toPyDate()
        return d, h

    def _get_min_fecha_venta(self):
        """Return the date of the earliest sale as a datetime.date or None."""
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT MIN(DATE(fecha_venta)) FROM ventas")
            row = cur.fetchone()
            conn.close()
            if row and row[0]:
                from datetime import datetime
                return datetime.strptime(row[0], '%Y-%m-%d').date()
        except Exception:
            return None

    def actualizar(self):
        fecha_desde, fecha_hasta = self._rango_fechas()
        # use ISO date strings for SQLite queries
        fecha_desde_str = fecha_desde.strftime('%Y-%m-%d')
        fecha_hasta_str = fecha_hasta.strftime('%Y-%m-%d')
        periodo = self.combo_periodo.currentText()

        # Tab 1: Ventas por periodo
        try:
            conn = db.get_connection()
            df_v = pd.read_sql_query(
                "SELECT fecha_venta, total_venta, descuento_venta FROM ventas WHERE DATE(fecha_venta) BETWEEN ? AND ? ORDER BY fecha_venta ASC",
                conn, params=[fecha_desde_str, fecha_hasta_str], parse_dates=['fecha_venta']
            )
            conn.close()
        except Exception:
            df_v = pd.DataFrame(columns=['fecha_venta', 'total_venta', 'descuento_venta'])

        if not df_v.empty:
            df_v['fecha_venta'] = pd.to_datetime(df_v['fecha_venta'])
            df_v.set_index('fecha_venta', inplace=True)
            # ensure numeric columns are usable (fill NaN/None)
            df_v['total_venta'] = df_v['total_venta'].fillna(0).astype(float)
            df_v['descuento_venta'] = df_v['descuento_venta'].fillna(0).astype(float)
            # total stored is net after discount; compute gross = total + descuento
            df_v['gross'] = df_v['total_venta'] + df_v['descuento_venta']
            freq = {'Diario': 'D', 'Semanal': 'W', 'Mensual': 'M'}.get(periodo, 'D')
            series = df_v['total_venta'].resample(freq).sum()
        else:
            series = pd.Series([], dtype=float)

        # Draw chart if matplotlib available
        if self._has_mpl and self.canvas1 is not None:
            # Clear entire figure to avoid overlapping axes
            try:
                if hasattr(self.canvas1, 'figure') and self.canvas1.figure:
                    self.canvas1.figure.clear()
                    ax1 = self.canvas1.figure.add_subplot(111)
                else:
                    return  # No figure disponible
            except Exception as e:
                print(f"Error creando gráfico de ventas: {e}")
                return

            if not series.empty:
                # apply date locators/formatters according to granularity
                try:
                    import matplotlib.dates as mdates
                    has_mdates = True
                except Exception:
                    has_mdates = False

                if has_mdates:
                    ax1.xaxis_date()
                    # choose locator/formatter but adapt interval to avoid too many ticks
                    try:
                        # number of aggregated points
                        n_points = len(series.index)
                        if periodo == 'Diario':
                            interval = 1
                            if n_points > 10:
                                import math
                                interval = max(1, math.ceil(n_points / 10))
                            locator = mdates.DayLocator(interval=interval)
                            fmt = mdates.DateFormatter('%d-%b')
                        elif periodo == 'Semanal':
                            interval = 1
                            if n_points > 10:
                                import math
                                interval = max(1, math.ceil(n_points / 10))
                            locator = mdates.WeekdayLocator(byweekday=mdates.MO, interval=interval)
                            fmt = mdates.DateFormatter('%d-%b')
                        else:  # Mensual
                            interval = 1
                            if n_points > 10:
                                import math
                                interval = max(1, math.ceil(n_points / 10))
                            locator = mdates.MonthLocator(interval=interval)
                            fmt = mdates.DateFormatter('%b %Y')
                        ax1.xaxis.set_major_locator(locator)
                        ax1.xaxis.set_major_formatter(fmt)
                    except Exception:
                        pass

                # Plot using the aggregated series that is used for the table
                series.plot(ax=ax1, marker='o', linewidth=2.5, markersize=8,
                          color='#3498db', markerfacecolor='#2980b9',
                          markeredgecolor='white', markeredgewidth=2)

                # Agregar área de relleno bajo la línea
                ax1.fill_between(series.index, series.values, alpha=0.3, color='#3498db')

                ax1.set_title(f"Ventas ({periodo})", fontsize=16, fontweight='bold',
                            color='#2c3e50', pad=20)
                ax1.set_ylabel('Total neto (S/.)', fontsize=12, fontweight='bold', color='#34495e')
                ax1.set_xlabel('Fecha', fontsize=12, fontweight='bold', color='#34495e')

                # Grid más sutil y profesional
                ax1.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7', linewidth=0.8)
                ax1.set_facecolor('#f8f9fa')

                # Mejorar los ticks
                ax1.tick_params(colors='#34495e', labelsize=10)
                for lbl in ax1.get_xticklabels():
                    lbl.set_rotation(45)
                    lbl.set_ha('right')

                # Agregar borde al gráfico
                for spine in ax1.spines.values():
                    spine.set_edgecolor('#bdc3c7')
                    spine.set_linewidth(1.5)
                # Set x-axis limits based on the selected date range so the
                # left/right extremes match the Desde/Hasta controls.
                try:
                    from datetime import datetime, timedelta
                    # fecha_desde and fecha_hasta are date objects from _rango_fechas
                    start_dt = datetime(fecha_desde.year, fecha_desde.month, fecha_desde.day, 0, 0, 0)
                    # include the full 'hasta' day by setting time to 23:59:59, add small padding day
                    end_dt = datetime(fecha_hasta.year, fecha_hasta.month, fecha_hasta.day, 23, 59, 59) + timedelta(days=0)
                    # add a tiny padding (1% of range) so last point isn't on the border
                    try:
                        total_seconds = (end_dt - start_dt).total_seconds()
                        pad = timedelta(seconds=max(1, total_seconds * 0.01))
                        end_dt = end_dt + pad
                    except Exception:
                        pass
                    ax1.set_xlim(start_dt, end_dt)
                except Exception:
                    # if anything goes wrong, skip setting limits
                    pass
            else:
                ax1.text(0.5, 0.5, 'No hay ventas en el rango seleccionado', ha='center')

            try:
                if hasattr(self.canvas1, 'figure') and self.canvas1.figure:
                    self.canvas1.figure.tight_layout()
                    self.canvas1.draw()
            except Exception as e:
                print(f"Error dibujando gráfico: {e}")
        else:
            # Update placeholder text if present
            if getattr(self, 'placeholder1', None) is not None:
                self.placeholder1.setText("Matplotlib no está instalado. Instala: pip install matplotlib")

        # Tab 2: Productos más vendidos (Top 10)
        try:
            conn = db.get_connection()
            query = '''
                SELECT p.nombre_producto as producto_nombre, SUM(dv.cantidad_detalle) as total_vendido, SUM(dv.subtotal_detalle) as ingresos_totales
                FROM detalle_venta dv
                JOIN ventas v ON dv.id_venta = v.id_venta
                JOIN productos p ON dv.id_producto = p.id_producto
                WHERE DATE(v.fecha_venta) BETWEEN ? AND ?
                GROUP BY dv.id_producto, p.nombre_producto
                ORDER BY total_vendido DESC
                LIMIT 10
            '''
            df_p = pd.read_sql_query(query, conn, params=[fecha_desde_str, fecha_hasta_str])
            conn.close()
        except Exception:
            df_p = pd.DataFrame()

        if self._has_mpl and self.canvas2 is not None:
            try:
                if hasattr(self.canvas2, 'figure') and self.canvas2.figure:
                    self.canvas2.figure.clear()
                    ax2 = self.canvas2.figure.add_subplot(111)
                else:
                    return
            except Exception as e:
                print(f"Error creando gráfico de productos: {e}")
                return

            if not df_p.empty:
                names = df_p['producto_nombre'].astype(str).tolist()
                values = df_p['total_vendido'].tolist()
                positions = list(range(len(names)))

                # Crear gradiente de colores del más oscuro al más claro
                colors = ['#1f77b4', '#2980b9', '#3498db', '#5dade2', '#7fb3d5',
                         '#a2c4e0', '#aed6f1', '#d4e6f1', '#e8f4f8', '#f0f8ff']
                bar_colors = colors[:len(names)]

                # draw bars con colores degradados
                bars = ax2.bar(positions, values, color=bar_colors, width=0.7,
                              edgecolor='white', linewidth=2)

                # Agregar valores sobre las barras
                for i, (bar, val) in enumerate(zip(bars, values)):
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(val)}', ha='center', va='bottom',
                            fontweight='bold', fontsize=10, color='#2c3e50')

                ax2.set_xticks(positions)
                # Truncar nombres largos y reducir font size
                truncated_names = [name[:20] + '...' if len(name) > 20 else name for name in names]
                ax2.set_xticklabels(truncated_names, rotation=30, ha='right', fontsize=8)
                ax2.tick_params(axis='x', which='major', labelsize=8, colors='#34495e')
                ax2.tick_params(axis='y', colors='#34495e')

                ax2.set_title('Top 10 Productos más vendidos', fontsize=16,
                            fontweight='bold', color='#2c3e50', pad=20)
                ax2.set_ylabel('Cantidad vendida', fontsize=12, fontweight='bold',
                             color='#34495e')
                ax2.set_xlabel('Productos', fontsize=12, fontweight='bold',
                             color='#34495e')

                # Grid más sutil
                ax2.grid(axis='y', linestyle='--', alpha=0.3, color='#bdc3c7', linewidth=0.8)
                ax2.set_facecolor('#f8f9fa')

                # Mejorar bordes
                for spine in ax2.spines.values():
                    spine.set_edgecolor('#bdc3c7')
                    spine.set_linewidth(1.5)

                # Reducir margen inferior
                try:
                    self.canvas2.figure.subplots_adjust(bottom=0.15, top=0.92)
                except Exception:
                    pass
            else:
                ax2.text(0.5, 0.5, 'No hay datos', ha='center')

            try:
                if hasattr(self.canvas2, 'figure') and self.canvas2.figure:
                    self.canvas2.figure.tight_layout()
                    self.canvas2.draw()
            except Exception as e:
                print(f"Error dibujando gráfico productos: {e}")
        else:
            if getattr(self, 'placeholder2', None) is not None:
                self.placeholder2.setText("Matplotlib no está instalado. Instala: pip install matplotlib")
        # Poblar tabla de productos
        try:
            cols_p = list(df_p.columns)
            # Traducir nombres de columnas
            col_map = {
                'producto_nombre': 'Producto',
                'total_vendido': 'Cantidad Vendida',
                'ingresos_totales': 'Ingresos Totales (S/.)'
            }
            display_cols_p = [col_map.get(c, c) for c in cols_p]

            self.table_prod.setColumnCount(len(cols_p))
            self.table_prod.setRowCount(len(df_p.index))
            self.table_prod.setHorizontalHeaderLabels(display_cols_p)
            
            # Anchos fijos para tabla de productos
            anchos_productos = [400, 180, 200]  # Producto, Cantidad Vendida, Ingresos Totales
            for i, ancho in enumerate(anchos_productos[:len(cols_p)]):
                self.table_prod.setColumnWidth(i, ancho)
            
            for r_idx in range(len(df_p.index)):
                for c, col in enumerate(cols_p):
                    val = df_p.iloc[r_idx][col]
                    item = QTableWidgetItem(str(val))
                    # Alinear números a la derecha y texto al centro
                    if c == 0:  # nombre del producto
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    else:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.table_prod.setItem(r_idx, c, item)
        except Exception:
            # limpiar tabla
            self.table_prod.setRowCount(0)
            self.table_prod.setColumnCount(0)
        try:
            if self.canvas2 and hasattr(self.canvas2, 'figure') and self.canvas2.figure:
                self.canvas2.figure.tight_layout()
                self.canvas2.draw()
        except Exception as e:
            print(f"Error finalizando gráfico productos: {e}")

        # Tab 3: Ganancias y pérdidas (resumen simple)
        if self._has_mpl and self.canvas3 is not None:
            try:
                if hasattr(self.canvas3, 'figure') and self.canvas3.figure:
                    self.canvas3.figure.clear()
                    ax3 = self.canvas3.figure.add_subplot(111)
                else:
                    return
            except Exception as e:
                print(f"Error creando gráfico de ganancias: {e}")
                return

            if not df_v.empty:
                total_net = df_v['total_venta'].sum()
                total_gross = df_v['gross'].sum()
                total_discount = df_v['descuento_venta'].sum()
                labels = ['Bruto', 'Descuentos', 'Neto']
                values = [total_gross, total_discount, total_net]
                colors = ['#27ae60', '#e74c3c', '#3498db']

                bars = ax3.bar(labels, values, color=colors, width=0.6,
                              edgecolor='white', linewidth=2)

                # Agregar valores sobre las barras
                for bar, val in zip(bars, values):
                    height = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2., height,
                            f'${val:.2f}', ha='center', va='bottom',
                            fontweight='bold', fontsize=12, color='#2c3e50')

                ax3.set_title('Resumen de ingresos y descuentos', fontsize=16,
                            fontweight='bold', color='#2c3e50', pad=20)
                ax3.set_ylabel('Monto (S/.)', fontsize=12, fontweight='bold',
                             color='#34495e')

                # Grid más sutil
                ax3.grid(axis='y', linestyle='--', alpha=0.3, color='#bdc3c7', linewidth=0.8)
                ax3.set_facecolor('#f8f9fa')

                # Mejorar ticks
                ax3.tick_params(colors='#34495e', labelsize=11)

                # Mejorar bordes
                for spine in ax3.spines.values():
                    spine.set_edgecolor('#bdc3c7')
                    spine.set_linewidth(1.5)

                # Poblar tabla resumen
                try:
                    df_summary = pd.DataFrame([{
                        'Bruto': f'${total_gross:.2f}',
                        'Descuentos': f'${total_discount:.2f}',
                        'Neto': f'${total_net:.2f}'
                    }])
                    cols_s = list(df_summary.columns)
                    self.table_gan.setColumnCount(len(cols_s))
                    self.table_gan.setRowCount(len(df_summary.index))
                    self.table_gan.setHorizontalHeaderLabels(cols_s)
                    for r_idx in range(len(df_summary.index)):
                        for c, col in enumerate(cols_s):
                            val = df_summary.iloc[r_idx][col]
                            item = QTableWidgetItem(str(val))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.table_gan.setItem(r_idx, c, item)
                    self.table_gan.resizeColumnsToContents()
                    self.table_gan.horizontalHeader().setStretchLastSection(True)
                except Exception:
                    self.table_gan.setRowCount(0)
                    self.table_gan.setColumnCount(0)
            else:
                ax3.text(0.5, 0.5, 'No hay datos para Ganancias/Pérdidas en el rango', ha='center')
                self.table_gan.setRowCount(0)
                self.table_gan.setColumnCount(0)

            try:
                if hasattr(self.canvas3, 'figure') and self.canvas3.figure:
                    self.canvas3.figure.tight_layout()
                    self.canvas3.draw()
            except Exception as e:
                print(f"Error dibujando gráfico ganancias: {e}")
        else:
            if getattr(self, 'placeholder3', None) is not None:
                self.placeholder3.setText("Matplotlib no está instalado. Instala: pip install matplotlib")

        # Store dataframes for export (use non-indexed df for exports)
        try:
            self._df_v = df_v.reset_index()
        except Exception:
            self._df_v = pd.DataFrame()
        self._df_p = df_p if not df_p.empty else pd.DataFrame()

        # Tab 4: Cargar comprobantes emitidos
        try:
            conn = db.get_connection()
            df_comp = pd.read_sql_query("""
                SELECT 
                    c.id_comprobante as ID,
                    c.tipo_comprobante as Tipo,
                    c.serie_comprobante || '-' || c.numero_comprobante as Serie_Numero,
                    c.fecha_emision_comprobante as Fecha_Emision,
                    c.nombre_cliente as Cliente,
                    c.num_documento as DNI,
                    c.razon_social as Razon_Social,
                    c.ruc_emisor as RUC,
                    c.monto_total_comprobante as Monto_Total,
                    v.metodo_pago as Metodo_Pago,
                    c.estado_sunat as Estado_SUNAT
                FROM comprobante c
                INNER JOIN ventas v ON c.id_venta = v.id_venta
                WHERE DATE(c.fecha_emision_comprobante) BETWEEN ? AND ?
                ORDER BY c.fecha_emision_comprobante DESC
            """, conn, params=[fecha_desde_str, fecha_hasta_str])
            conn.close()
        except Exception as e:
            print(f"Error cargando comprobantes: {e}")
            df_comp = pd.DataFrame()
        
        self._df_comp = df_comp
        
        # Poblar tabla de comprobantes con anchos fijos
        if not df_comp.empty:
            cols_comp = ['ID', 'Tipo', 'Serie-Número', 'Fecha Emisión', 'Cliente', 
                        'DNI/RUC', 'Monto Total', 'Método Pago', 'Estado SUNAT']
            self.table_comprobantes.setColumnCount(len(cols_comp))
            self.table_comprobantes.setRowCount(len(df_comp))
            self.table_comprobantes.setHorizontalHeaderLabels(cols_comp)
            
            # Anchos fijos para las columnas
            anchos_comprobantes = [60, 100, 140, 150, 350, 100, 110, 130, 120]
            for i, ancho in enumerate(anchos_comprobantes):
                self.table_comprobantes.setColumnWidth(i, ancho)
            
            for r_idx in range(len(df_comp)):
                # ID
                item = QTableWidgetItem(str(df_comp.iloc[r_idx]['ID']))
                item.setTextAlignment(Qt.AlignCenter)
                self.table_comprobantes.setItem(r_idx, 0, item)
                
                # Tipo con color
                tipo = str(df_comp.iloc[r_idx]['Tipo']).upper()
                item_tipo = QTableWidgetItem(tipo)
                item_tipo.setTextAlignment(Qt.AlignCenter)
                if tipo == 'BOLETA':
                    item_tipo.setForeground(Qt.darkGreen)
                else:
                    item_tipo.setForeground(Qt.blue)
                self.table_comprobantes.setItem(r_idx, 1, item_tipo)
                
                # Serie-Número
                item = QTableWidgetItem(str(df_comp.iloc[r_idx]['Serie_Numero']))
                item.setTextAlignment(Qt.AlignCenter)
                self.table_comprobantes.setItem(r_idx, 2, item)
                
                # Fecha
                fecha_str = str(df_comp.iloc[r_idx]['Fecha_Emision'])[:19]
                item = QTableWidgetItem(fecha_str)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_comprobantes.setItem(r_idx, 3, item)
                
                # Cliente (usar razón social si es factura, nombre si es boleta)
                if tipo == 'FACTURA' and pd.notna(df_comp.iloc[r_idx].get('Razon_Social')):
                    cliente = str(df_comp.iloc[r_idx]['Razon_Social'])
                else:
                    cliente = str(df_comp.iloc[r_idx]['Cliente'])
                item = QTableWidgetItem(cliente)
                self.table_comprobantes.setItem(r_idx, 4, item)
                
                # DNI/RUC
                if tipo == 'FACTURA' and pd.notna(df_comp.iloc[r_idx].get('RUC')):
                    doc = str(df_comp.iloc[r_idx]['RUC'])
                else:
                    doc = str(df_comp.iloc[r_idx]['DNI']) if pd.notna(df_comp.iloc[r_idx].get('DNI')) else '-'
                item = QTableWidgetItem(doc)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_comprobantes.setItem(r_idx, 5, item)
                
                # Monto
                monto = float(df_comp.iloc[r_idx]['Monto_Total'])
                item = QTableWidgetItem(f"S/ {monto:.2f}")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_comprobantes.setItem(r_idx, 6, item)
                
                # Método de pago con color
                metodo = str(df_comp.iloc[r_idx]['Metodo_Pago']).lower()
                item_metodo = QTableWidgetItem(metodo.upper())
                item_metodo.setTextAlignment(Qt.AlignCenter)
                
                # Colorear según método de pago
                if 'tarjeta' in metodo:
                    item_metodo.setForeground(Qt.darkMagenta)
                elif 'efectivo' in metodo:
                    item_metodo.setForeground(Qt.darkGreen)
                elif 'yape' in metodo or 'plin' in metodo:
                    item_metodo.setForeground(Qt.red)
                elif 'transfer' in metodo:
                    item_metodo.setForeground(Qt.darkYellow)
                
                self.table_comprobantes.setItem(r_idx, 7, item_metodo)
                
                # Estado SUNAT
                estado = str(df_comp.iloc[r_idx]['Estado_SUNAT']) if pd.notna(df_comp.iloc[r_idx].get('Estado_SUNAT')) else 'PENDIENTE'
                item = QTableWidgetItem(estado)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_comprobantes.setItem(r_idx, 8, item)
        else:
            self.table_comprobantes.setRowCount(0)
            self.table_comprobantes.setColumnCount(0)

        # Poblar tabla de ventas (df_v may be empty)
        try:
            if not self._df_v.empty:
                cols_v = list(self._df_v.columns)
                # Map internal column names to display titles
                title_map = {'total': 'precio', 'gross': 'total'}
                display_cols = [title_map.get(c, c) for c in cols_v]
                self.table_ventas.setColumnCount(len(cols_v))
                self.table_ventas.setRowCount(len(self._df_v.index))
                self.table_ventas.setHorizontalHeaderLabels(display_cols)
                
                # Anchos fijos para tabla de ventas
                anchos_ventas = [180, 120, 120, 120]  # fecha_venta, total_venta, descuento_venta, gross
                for i, ancho in enumerate(anchos_ventas[:len(cols_v)]):
                    self.table_ventas.setColumnWidth(i, ancho)
                
                for r_idx in range(len(self._df_v.index)):
                    for c, col in enumerate(cols_v):
                        val = self._df_v.iloc[r_idx][col]
                        item = QTableWidgetItem(str(val))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table_ventas.setItem(r_idx, c, item)
            else:
                self.table_ventas.setRowCount(0)
                self.table_ventas.setColumnCount(0)
        except Exception:
            self.table_ventas.setRowCount(0)
            self.table_ventas.setColumnCount(0)

    def exportar(self, forma='pdf'):
        # Export the active tab data
        idx = self.tabs.currentIndex()
        if idx == 0:
            df = self._df_v if hasattr(self, '_df_v') else pd.DataFrame()
            titulo = 'Ventas por periodo'
            default_name = 'ventas_periodo'
        elif idx == 1:
            df = self._df_p if hasattr(self, '_df_p') else pd.DataFrame()
            titulo = 'Productos Top 10'
            default_name = 'productos_top10'
        elif idx == 2:
            # Build a small dataframe summary for ganancias
            if not hasattr(self, '_df_v') or self._df_v.empty:
                df = pd.DataFrame()
            else:
                total_net = self._df_v['total_venta'].sum()
                total_gross = (self._df_v['total_venta'] + self._df_v['descuento_venta']).sum()
                total_discount = self._df_v['descuento_venta'].sum()
                df = pd.DataFrame([{'Bruto': total_gross, 'Descuentos': total_discount, 'Neto': total_net}])
            titulo = 'Ganancias y Pérdidas'
            default_name = 'ganancias_perdidas'
        elif idx == 3:
            # Comprobantes emitidos
            df = self._df_comp if hasattr(self, '_df_comp') else pd.DataFrame()
            titulo = 'Comprobantes Emitidos'
            default_name = 'comprobantes_emitidos'
        else:
            df = pd.DataFrame()
            titulo = 'Reporte'
            default_name = 'reporte'

        if df.empty:
            QMessageBox.information(self, 'Exportar', 'No hay datos para exportar')
            return

        # Ask for filename and attempt export; catch ImportError and show instructions
        try:
            # build descriptive filename including period and date range
            periodo = self.combo_periodo.currentText()
            fecha_desde, fecha_hasta = self._rango_fechas()
            fecha_desde_str = fecha_desde.strftime('%Y-%m-%d')
            fecha_hasta_str = fecha_hasta.strftime('%Y-%m-%d')
            if idx == 0:
                suggested_base = f"{titulo} ({periodo}) de {fecha_desde_str} a {fecha_hasta_str}"
            else:
                suggested_base = f"{titulo} de {fecha_desde_str} a {fecha_hasta_str}"
            # capture chart image from current canvas (if available)
            chart_bytes = None
            try:
                import io
                if idx == 0 and getattr(self, 'canvas1', None) is not None:
                    buf = io.BytesIO()
                    self.canvas1.figure.savefig(buf, format='png', bbox_inches='tight', dpi=150)
                    chart_bytes = buf.getvalue()
                elif idx == 1 and getattr(self, 'canvas2', None) is not None:
                    buf = io.BytesIO()
                    # temporarily reduce xtick label fontsize so product names fit better in export
                    try:
                        fig = self.canvas2.figure
                        if fig.axes:
                            ax = fig.axes[0]
                            orig_sizes = [lbl.get_fontsize() for lbl in ax.get_xticklabels()]
                            for lbl in ax.get_xticklabels():
                                lbl.set_fontsize(max(6, min(lbl.get_fontsize(), 8)))
                    except Exception:
                        orig_sizes = None
                    try:
                        self.canvas2.figure.savefig(buf, format='png', bbox_inches='tight', dpi=150)
                        chart_bytes = buf.getvalue()
                    finally:
                        # restore original sizes
                        try:
                            if orig_sizes is not None and fig.axes:
                                ax = fig.axes[0]
                                for lbl, s in zip(ax.get_xticklabels(), orig_sizes):
                                    lbl.set_fontsize(s)
                        except Exception:
                            pass
                elif idx == 2 and getattr(self, 'canvas3', None) is not None:
                    buf = io.BytesIO()
                    self.canvas3.figure.savefig(buf, format='png', bbox_inches='tight', dpi=150)
                    chart_bytes = buf.getvalue()
            except Exception:
                chart_bytes = None

            if forma == 'pdf':
                path, _ = QFileDialog.getSaveFileName(self, 'Guardar PDF', f'{suggested_base}.pdf', 'PDF Files (*.pdf)')
                if not path:
                    return
                # Apply display title mapping for ventas tab so exported headers match UI
                df_export = df.copy()
                if idx == 0:
                    df_export = df_export.rename(columns={'total': 'precio', 'gross': 'total'})
                exportar_pdf(df_export, path, titulo, chart_bytes=chart_bytes)
                QMessageBox.information(self, 'Exportar', f'PDF guardado en: {path}')
            else:
                path, _ = QFileDialog.getSaveFileName(self, 'Guardar Excel', f'{suggested_base}.xlsx', 'Excel Files (*.xlsx)')
                if not path:
                    return
                df_export = df.copy()
                if idx == 0:
                    df_export = df_export.rename(columns={'total': 'precio', 'gross': 'total'})
                exportar_excel(df_export, path, sheet_name=default_name, chart_bytes=chart_bytes)
                QMessageBox.information(self, 'Exportar', f'Excel guardado en: {path}')
        except ImportError as e:
            # Show a user-friendly message explaining which package is missing
            msg = str(e)
            if 'reportlab' in msg:
                extra = "Para exportar a PDF instala: pip install reportlab"
            elif 'openpyxl' in msg:
                extra = "Para exportar a Excel instala: pip install openpyxl"
            else:
                extra = "Instala las dependencias necesarias: pip install reportlab openpyxl"
            QMessageBox.critical(self, 'Exportar - Dependencia faltante', f"Error exportando: {msg}\n\n{extra}")
        except Exception as e:
            QMessageBox.critical(self, 'Exportar', f'Error exportando: {str(e)}')
