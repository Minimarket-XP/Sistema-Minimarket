from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidgetItem, QLineEdit, QDateTimeEdit,
                             QComboBox, QMessageBox, QSpinBox, QGroupBox, QCompleter, QDialog)
from PyQt5.QtCore import Qt, QDateTime
from modules.productos.models.promocion_model import PromocionModel
from modules.productos.models.categoria_model import CategoriaModel
from modules.productos.models.producto_model import ProductoModel
from modules.productos.view.inventario_view import TablaNoEditable
from core.database import db

# Estilos reutilizables (coincidir con estilo de gestión de devoluciones)
FRAME_STYLE = """QFrame { background-color: #f0f0f0; border-radius: 3px; }"""
TABLE_STYLE = """
            QTableWidget {
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #e0e0e0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                border: 1px solid #ddd;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QScrollBar:vertical {
                background: #ecf0f1;
                width: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
"""


class PromocionesFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prom_model = PromocionModel()
        self.init_ui()
        self.cargar_promociones()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(10)

        titulo = QLabel("Promociones")
        titulo.setAlignment(Qt.AlignLeft)
        titulo.setStyleSheet("font-size:22px; font-weight:bold; color: #1f618d;")
        layout.addWidget(titulo)
        # Form crear promocion (más claro y vertical)
        # Panel superior: crear promoción
        from PyQt5.QtWidgets import QFrame
        form_frame = QFrame()
        form_frame.setStyleSheet(FRAME_STYLE)
        f_layout = QVBoxLayout(form_frame)
        form_frame.setContentsMargins(10,10,10,10)

        title_box = QLabel("Crear nueva promoción")
        title_box.setStyleSheet("font-weight:bold; margin-bottom:6px;")
        f_layout.addWidget(title_box)

        row1 = QHBoxLayout()
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre promoción")
        self.input_nombre.setMinimumWidth(240)
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Descripción")
        row1.addWidget(self.input_nombre)
        row1.addWidget(self.input_desc)

        row2 = QHBoxLayout()
        self.input_descuento = QSpinBox()
        self.input_descuento.setRange(0, 100)
        self.input_descuento.setValue(10)
        self.input_descuento.setSuffix(" %")
        self.dt_inicio = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_inicio.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.dt_fin = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_fin.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        btn_crear = QPushButton("Crear promoción")
        btn_crear.setStyleSheet(f"""
            QPushButton {{
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 18px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{ background-color: #27ae60; }}
        """)
        btn_crear.setFixedHeight(36)
        btn_crear.setFixedWidth(160)
        btn_crear.clicked.connect(self.crear_promocion)
        row2.addWidget(QLabel("Descuento:"))
        row2.addWidget(self.input_descuento)
        row2.addWidget(QLabel("Inicio:"))
        row2.addWidget(self.dt_inicio)
        row2.addWidget(QLabel("Fin:"))
        row2.addWidget(self.dt_fin)
        row2.addWidget(btn_crear)

        f_layout.addLayout(row1)
        f_layout.addLayout(row2)
        layout.addWidget(form_frame)

        # Asignaciones rápidas (producto por nombre con autocompletado)
        # Panel asignaciones rápidas
        assign_frame = QFrame()
        assign_frame.setStyleSheet(FRAME_STYLE)
        assign_vlayout = QVBoxLayout(assign_frame)
        assign_frame.setContentsMargins(10,10,10,10)

        # Título del bloque de asignación
        lbl_assign_title = QLabel("Asignar promoción")
        lbl_assign_title.setStyleSheet("font-weight:bold; margin-bottom:6px; color: #1f618d;")
        assign_vlayout.addWidget(lbl_assign_title)
        a_layout = QHBoxLayout()

        self.input_prom_id = QLineEdit()
        self.input_prom_id.setPlaceholderText("ID promoción")
        self.input_producto = QLineEdit()
        self.input_producto.setPlaceholderText("Buscar producto por nombre...")
        self.combo_categoria = QComboBox()
        self.cargar_categorias()
        btn_asign_prod = QPushButton("Asignar a producto")
        btn_asign_prod.setStyleSheet("background-color:#3498db; color:white;")
        btn_asign_prod.clicked.connect(self.asignar_producto)
        btn_asign_cat = QPushButton("Asignar a categoría")
        btn_asign_cat.setStyleSheet("background-color:#f39c12; color:white;")
        btn_asign_cat.clicked.connect(self.asignar_categoria)

        a_layout.addWidget(QLabel("Promoción ID:"))
        self.input_prom_id.setFixedWidth(140)
        a_layout.addWidget(self.input_prom_id)
        a_layout.addWidget(QLabel("Producto:"))
        self.input_producto.setFixedWidth(380)
        a_layout.addWidget(self.input_producto)
        btn_asign_prod.setFixedHeight(40)
        btn_asign_prod.setFixedWidth(160)
        btn_asign_prod.setStyleSheet("background-color:#2980b9; color:white; font-weight:bold; border-radius:6px;")
        a_layout.addWidget(btn_asign_prod)
        self.combo_categoria.setFixedWidth(220)
        a_layout.addWidget(self.combo_categoria)
        btn_asign_cat.setFixedHeight(40)
        btn_asign_cat.setFixedWidth(160)
        btn_asign_cat.setStyleSheet("background-color:#d35400; color:white; font-weight:bold; border-radius:6px;")
        a_layout.addWidget(btn_asign_cat)
        a_layout.addStretch()
        assign_vlayout.addLayout(a_layout)
        layout.addWidget(assign_frame)

        # Panel tabla
        table_frame = QFrame()
        table_frame.setStyleSheet(FRAME_STYLE)
        t_layout = QVBoxLayout(table_frame)
        t_layout.setContentsMargins(10,10,10,10)

        self.tabla = TablaNoEditable()
        self.tabla.setStyleSheet(TABLE_STYLE)
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Descuento%", "Inicio", "Fin", "Estado", "Acciones"])
        # Configuración similar a devoluciones
        self.tabla.setSelectionBehavior(self.tabla.SelectRows)
        self.tabla.setSelectionMode(self.tabla.SingleSelection)
        self.tabla.setAlternatingRowColors(True)
        header = self.tabla.horizontalHeader()
        # Anchos: ID pequeño, Nombre amplio, Descuento, Inicio, Fin, Estado, Acciones
        anchos = [60, 550, 100, 180, 180, 100, 240]
        for i, ancho in enumerate(anchos):
            try:
                self.tabla.setColumnWidth(i, ancho)
            except Exception:
                pass
        header.setStretchLastSection(False)
        self.tabla.setMinimumHeight(240)
        t_layout.addWidget(self.tabla)
        layout.addWidget(table_frame)

        # cargar productos para autocompletar y categorías
        self.cargar_productos()
        self.cargar_categorias()

    def cargar_categorias(self):
        self.combo_categoria.clear()
        try:
            self.combo_categoria.addItem("-- Seleccionar --", None)
            cm = CategoriaModel()
            df = cm.obtener_todas()
            if not df.empty:
                for _, row in df.iterrows():
                    self.combo_categoria.addItem(row['nombre_categoria'], int(row['id_categoria_productos']))
        except Exception as e:
            print("Error cargando categorías:", e)

    def crear_promocion(self):
        nombre = self.input_nombre.text().strip()
        desc = self.input_desc.text().strip()
        pct = int(self.input_descuento.value())
        inicio = self.dt_inicio.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        fin = self.dt_fin.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        if not nombre:
            QMessageBox.warning(self, "Validación", "Ingresa un nombre para la promoción")
            return
        if inicio >= fin:
            QMessageBox.warning(self, "Validación", "La fecha de inicio debe ser anterior a la fecha fin")
            return
        try:
            idp = self.prom_model.crear(nombre, desc, pct, inicio, fin, estado='activa')
            QMessageBox.information(self, "Éxito", f"Promoción creada: {idp}")
            self.cargar_promociones()
            # recargar productos por si se mostró id_prom en pantalla
            self.cargar_productos()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def cargar_productos(self):
        """Carga lista de productos para autocompletado (nombre->id) usando el modelo."""
        try:
            pm = ProductoModel()
            df = pm.obtener_todos()
            # df tiene columna "Nombre" y en la estructura original el ID está en "ID"
            self.product_name_to_id = {}
            if hasattr(df, 'iterrows'):
                for _, row in df.iterrows():
                    name = (row.get('Nombre') or '').strip()
                    pid = row.get('ID')
                    if name:
                        self.product_name_to_id[name] = pid
            nombres = list(self.product_name_to_id.keys())
            completer = QCompleter(nombres)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.input_producto.setCompleter(completer)
        except Exception as e:
            print("Error cargando productos para autocompletar:", e)

    def cargar_promociones(self):
        promos = self.prom_model.obtener_todas()
        self.tabla.setRowCount(len(promos))
        for i, p in enumerate(promos):
            id_item = QTableWidgetItem(str(p['id_promocion']))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            self.tabla.setItem(i, 0, id_item)

            nombre_item = QTableWidgetItem(p['nombre'])
            nombre_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            nombre_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 1, nombre_item)

            desc_item = QTableWidgetItem(str(p['descuento']))
            desc_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            desc_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 2, desc_item)

            inicio_item = QTableWidgetItem(str(p['fecha_inicio']))
            inicio_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            inicio_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 3, inicio_item)

            fin_item = QTableWidgetItem(str(p['fecha_fin']))
            fin_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            fin_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 4, fin_item)

            estado_item = QTableWidgetItem(p['estado'])
            estado_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            estado_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 5, estado_item)

            # Acciones: activar/desactivar, editar, eliminar
            btns = QWidget()
            from PyQt5.QtWidgets import QHBoxLayout
            lay = QHBoxLayout(btns)
            lay.setContentsMargins(0,0,0,0)
            btn_act = QPushButton("Activar" if p['estado'] != 'activa' else "Desactivar")
            btn_act.setStyleSheet("background-color:#7f8c8d; color:white; padding:6px; border-radius:4px;")
            btn_act.setFixedHeight(28)
            btn_act.setFixedWidth(90)
            btn_act.clicked.connect(lambda checked, pid=p['id_promocion'], est=p['estado']: self.toggle_estado(pid, est))
            btn_edit = QPushButton("Editar")
            btn_edit.setStyleSheet("background-color:#3498db; color:white; padding:6px; border-radius:4px;")
            btn_edit.setFixedHeight(28)
            btn_edit.setFixedWidth(80)
            btn_edit.clicked.connect(lambda checked, pid=p['id_promocion']: self.editar_promocion(pid))
            btn_del = QPushButton("Eliminar")
            btn_del.setStyleSheet("background-color:#e74c3c; color:white; padding:6px; border-radius:4px;")
            btn_del.setFixedHeight(28)
            btn_del.setFixedWidth(80)
            btn_del.clicked.connect(lambda checked, pid=p['id_promocion']: self.eliminar_promocion(pid))
            lay.addWidget(btn_act)
            lay.addWidget(btn_edit)
            lay.addWidget(btn_del)
            lay.setSpacing(6)
            self.tabla.setCellWidget(i, 6, btns)

    def toggle_estado(self, id_prom, estado_actual):
        nuevo = 'activa' if estado_actual != 'activa' else 'inactiva'
        try:
            self.prom_model.actualizar_estado(id_prom, nuevo)
            QMessageBox.information(self, "Promoción", f"Estado actualizado a {nuevo}")
            self.cargar_promociones()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def eliminar_promocion(self, id_prom):
        resp = QMessageBox.question(self, "Confirmar", "¿Eliminar promoción?", QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        try:
            self.prom_model.eliminar(id_prom)
            QMessageBox.information(self, "Promoción", "Promoción eliminada")
            self.cargar_promociones()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def editar_promocion(self, id_prom):
        try:
            data = self.prom_model.obtener_por_id(id_prom)
            if not data:
                QMessageBox.warning(self, "Editar", "Promoción no encontrada")
                return
            dlg = EditPromocionDialog(self, self.prom_model, data)
            if dlg.exec_() == QDialog.Accepted:
                self.cargar_promociones()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def asignar_producto(self):
        id_prom = self.input_prom_id.text().strip()
        prod_text = self.input_producto.text().strip()
        if not id_prom or not prod_text:
            QMessageBox.warning(self, "Validación", "Proporciona ID promoción y producto")
            return
        # Resolver nombre -> id_producto si corresponde
        id_producto = None
        try:
            # si el texto coincide con un nombre conocido
            if hasattr(self, 'product_name_to_id') and prod_text in self.product_name_to_id:
                id_producto = self.product_name_to_id[prod_text]
            else:
                # intentar buscar por LIKE en la BD (primer resultado) usando helper
                r = db.fetchone("SELECT id_producto FROM productos WHERE nombre_producto LIKE ? LIMIT 1", (f"%{prod_text}%",))
                if r:
                    id_producto = r[0]

            if not id_producto:
                QMessageBox.warning(self, "Validación", "No se encontró el producto especificado")
                return

            self.prom_model.asignar_producto(int(id_prom), id_producto)
            QMessageBox.information(self, "Asignación", f"Promoción {id_prom} asignada a producto {id_producto}")
            # limpiar campo producto
            self.input_producto.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def asignar_categoria(self):
        id_prom = self.input_prom_id.text().strip()
        id_cat = self.combo_categoria.currentData()
        if not id_prom or not id_cat:
            QMessageBox.warning(self, "Validación", "Proporciona ID promoción y selecciona categoría")
            return
        try:
            self.prom_model.asignar_categoria(int(id_prom), int(id_cat))
            QMessageBox.information(self, "Asignación", "Promoción asignada a la categoría")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class EditPromocionDialog(QDialog):
    def __init__(self, parent, prom_model, promocion):
        super().__init__(parent)
        self.setWindowTitle("Editar promoción")
        self.prom_model = prom_model
        self.promocion = promocion
        self.init_ui()

    def init_ui(self):
        from PyQt5.QtWidgets import QFormLayout
        layout = QFormLayout(self)
        self.input_nombre = QLineEdit(self.promocion['nombre'])
        self.input_desc = QLineEdit(self.promocion.get('descripcion') or '')
        self.input_descuento = QSpinBox()
        self.input_descuento.setRange(0, 100)
        self.input_descuento.setValue(int(float(self.promocion.get('descuento', 0))))
        self.dt_inicio = QDateTimeEdit(QDateTime.fromString(str(self.promocion.get('fecha_inicio')), 'yyyy-MM-dd HH:mm:ss'))
        self.dt_inicio.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.dt_fin = QDateTimeEdit(QDateTime.fromString(str(self.promocion.get('fecha_fin')), 'yyyy-MM-dd HH:mm:ss'))
        self.dt_fin.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.combo_estado = QComboBox()
        # No permitir seleccionar 'expirada' manualmente desde el diálogo de edición
        self.combo_estado.addItems(['activa','inactiva'])
        # Si la promoción ya está expirada, mostrarla pero deshabilitar la opción de seleccionar 'expirada'
        current_estado = self.promocion.get('estado') or 'inactiva'
        if current_estado == 'expirada':
            # mostrar 'expirada' en la UI pero no como opción en el combo; mostrar etiqueta aparte
            lbl_exp = QLabel("(Expirada)")
            lbl_exp.setStyleSheet('color:#e74c3c; font-weight:bold;')
            layout.addRow('', lbl_exp)
        idx = self.combo_estado.findText(current_estado if current_estado in ['activa','inactiva'] else 'inactiva')
        if idx >= 0:
            self.combo_estado.setCurrentIndex(idx)

        layout.addRow('Nombre:', self.input_nombre)
        layout.addRow('Descripción:', self.input_desc)
        layout.addRow('Descuento %:', self.input_descuento)
        layout.addRow('Fecha inicio:', self.dt_inicio)
        layout.addRow('Fecha fin:', self.dt_fin)
        layout.addRow('Estado:', self.combo_estado)

        # Mostrar categorías asignadas y permitir quitar una específica
        assigned_widget = QWidget()
        assigned_layout = QVBoxLayout(assigned_widget)
        assigned_layout.setContentsMargins(0,0,0,0)
        layout.addRow('Categorías asignadas:', assigned_widget)
        self.assigned_cat_layout = assigned_layout

        # Guardar botón
        btn_save = QPushButton('Guardar')
        btn_save.setStyleSheet('background-color:#2ecc71; color:white;')
        btn_save.clicked.connect(self.guardar)
        layout.addRow(btn_save)

        # Cargar la lista de categorías asignadas
        self.load_assigned_categories()

    def guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, 'Validación', 'Nombre requerido')
            return
        inicio = self.dt_inicio.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        fin = self.dt_fin.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        if inicio >= fin:
            QMessageBox.warning(self, 'Validación', 'Fecha inicio debe ser anterior a fecha fin')
            return
        try:
            self.prom_model.actualizar(
                int(self.promocion['id_promocion']),
                nombre=nombre,
                descripcion=self.input_desc.text().strip(),
                descuento_pct=int(self.input_descuento.value()),
                fecha_inicio=inicio,
                fecha_fin=fin,
                estado=self.combo_estado.currentText()
            )
            QMessageBox.information(self, 'Éxito', 'Promoción actualizada')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def load_assigned_categories(self):
        """Carga y muestra las categorías asignadas a la promoción en el diálogo."""
        # limpiar layout
        try:
            while self.assigned_cat_layout.count():
                item = self.assigned_cat_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()
            cats = self.prom_model.obtener_categorias_asignadas(self.promocion['id_promocion'])
            if not cats:
                self.assigned_cat_layout.addWidget(QLabel('(Sin categorías asignadas)'))
                return
            for c in cats:
                row_w = QWidget()
                row_l = QHBoxLayout(row_w)
                row_l.setContentsMargins(0,0,0,0)
                lbl = QLabel(c['nombre_categoria'])
                btn_quitar = QPushButton('Quitar')
                btn_quitar.setStyleSheet('background-color:#e74c3c; color:white;')
                btn_quitar.setFixedWidth(80)
                btn_quitar.clicked.connect(lambda _, cid=c['id_categoria_productos']: self.quitar_categoria(cid))
                row_l.addWidget(lbl)
                row_l.addStretch()
                row_l.addWidget(btn_quitar)
                self.assigned_cat_layout.addWidget(row_w)
        except Exception as e:
            # mostrar error mínimo
            self.assigned_cat_layout.addWidget(QLabel('Error cargando categorías'))

    def quitar_categoria(self, id_categoria):
        try:
            self.prom_model.remover_categoria(int(self.promocion['id_promocion']), int(id_categoria))
            QMessageBox.information(self, 'Asignación', 'Categoría removida de la promoción')
            self.load_assigned_categories()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
    
