from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidgetItem, QLineEdit, QDateTimeEdit, QComboBox, 
                             QMessageBox, QSpinBox, QFrame, QDialog, QFormLayout,
                             QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QDateTime
from shared.styles import TablaNoEditableCSS, FRAME_STYLE, TITULO
from modules.productos.models.promocion_model import PromocionModel
from modules.productos.models.categoria_model import CategoriaModel
from modules.productos.models.producto_model import ProductoModel
from modules.productos.view.inventario_view import TablaNoEditable
from core.database import db
from core.config import *


class PromocionesFrame(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.promo_model = PromocionModel()
        self.crear_interfaz()
        self.cargar_promociones()

    def crear_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # TITULO
        titulo = QLabel("Gestion de Promociones")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(TITULO)
        layout.addWidget(titulo)

        # SECCION 1: CREAR PROMOCION
        form_frame = self.crear_seccion_formulario()
        layout.addWidget(form_frame)

        # SECCION 2: TABLA DE PROMOCIONES
        table_frame = self.crear_seccion_tabla()
        layout.addWidget(table_frame)

        # Cargar datos iniciales
        self.cargar_productos()
        self.cargar_categorias()
        self.cambiar_tipo_aplicacion()

    def crear_seccion_formulario(self):
        form_frame = QFrame()
        form_frame.setStyleSheet(FRAME_STYLE)
        f_layout = QVBoxLayout(form_frame)
        f_layout.setContentsMargins(15, 15, 15, 15)
        f_layout.setSpacing(12)

        # Titulo de seccion
        titulo_crear = QLabel("Crear Nueva Promocion")
        titulo_crear.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin-bottom: 5px;")
        f_layout.addWidget(titulo_crear)

        # Fila 1: Nombre y Descripcion
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        lbl_nombre = QLabel("Nombre:")
        lbl_nombre.setFixedWidth(80)
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre de la promocion")
        self.input_nombre.setMinimumWidth(250)
        
        lbl_desc = QLabel("Descripcion:")
        lbl_desc.setFixedWidth(90)
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Descripcion opcional")
        
        row1.addWidget(lbl_nombre)
        row1.addWidget(self.input_nombre)
        row1.addWidget(lbl_desc)
        row1.addWidget(self.input_desc)
        f_layout.addLayout(row1)

        # Fila 2: Descuento y Fechas
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        lbl_descuento = QLabel("Descuento:")
        lbl_descuento.setFixedWidth(80)
        self.input_descuento = QSpinBox()
        self.input_descuento.setRange(0, 100)
        self.input_descuento.setValue(10)
        self.input_descuento.setSuffix(" %")
        self.input_descuento.setFixedWidth(100)
        
        lbl_inicio = QLabel("Fecha Inicio:")
        lbl_inicio.setFixedWidth(90)
        self.dt_inicio = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_inicio.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.dt_inicio.setCalendarPopup(True)
        
        lbl_fin = QLabel("Fecha Fin:")
        lbl_fin.setFixedWidth(80)
        self.dt_fin = QDateTimeEdit(QDateTime.currentDateTime().addDays(7))
        self.dt_fin.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.dt_fin.setCalendarPopup(True)
        
        row2.addWidget(lbl_descuento)
        row2.addWidget(self.input_descuento)
        row2.addWidget(lbl_inicio)
        row2.addWidget(self.dt_inicio)
        row2.addWidget(lbl_fin)
        row2.addWidget(self.dt_fin)
        row2.addStretch()
        f_layout.addLayout(row2)

        # Fila 3: Tipo de aplicacion (Producto o Categoria)
        row3 = QHBoxLayout()
        row3.setSpacing(15)
        
        lbl_aplicar = QLabel("Aplicar a:")
        lbl_aplicar.setFixedWidth(80)
        lbl_aplicar.setStyleSheet("font-weight: bold;")
        
        self.radio_producto = QRadioButton("Producto")
        self.radio_categoria = QRadioButton("Categoria")
        self.radio_producto.setChecked(True)
        
        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.radio_producto)
        self.btn_group.addButton(self.radio_categoria)
        self.btn_group.buttonClicked.connect(self.cambiar_tipo_aplicacion)
        
        self.combo_selector = QComboBox()
        self.combo_selector.setMinimumWidth(350)
        
        row3.addWidget(lbl_aplicar)
        row3.addWidget(self.radio_producto)
        row3.addWidget(self.radio_categoria)
        row3.addWidget(self.combo_selector)
        row3.addStretch()
        f_layout.addLayout(row3)

        # Boton Crear
        btn_layout = QHBoxLayout()
        btn_crear = QPushButton("Crear Promocion")
        btn_crear.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        btn_crear.setFixedHeight(40)
        btn_crear.setFixedWidth(180)
        btn_crear.clicked.connect(self.crear_promocion)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_crear)
        f_layout.addLayout(btn_layout)
        
        return form_frame

    def crear_seccion_tabla(self):
        table_frame = QFrame()
        table_frame.setStyleSheet(FRAME_STYLE)
        t_layout = QVBoxLayout(table_frame)
        t_layout.setContentsMargins(15, 15, 15, 15)
        t_layout.setSpacing(10)

        titulo_tabla = QLabel("Listado de Promociones")
        titulo_tabla.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        t_layout.addWidget(titulo_tabla)

        self.tabla = TablaNoEditable()
        self.tabla.setStyleSheet(TablaNoEditableCSS)
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Descuento", "Inicio", "Fin", "Estado", "Acciones"])
        self.tabla.setSelectionBehavior(self.tabla.SelectRows)
        self.tabla.setSelectionMode(self.tabla.SingleSelection)
        self.tabla.setAlternatingRowColors(True)
        
        header = self.tabla.horizontalHeader()
        anchos = [60, 300, 100, 180, 180, 100, 280]
        for i, ancho in enumerate(anchos):
            self.tabla.setColumnWidth(i, ancho)
        header.setStretchLastSection(True)
        self.tabla.setMinimumHeight(320)
        
        t_layout.addWidget(self.tabla)
        return table_frame

    def cambiar_tipo_aplicacion(self):
        self.combo_selector.clear()
        
        if self.radio_producto.isChecked():
            self.combo_selector.addItem("-- Seleccionar Producto --", None)
            try:
                pm = ProductoModel()
                df = pm.obtener_todos()
                if hasattr(df, 'iterrows'):
                    for _, row in df.iterrows():
                        nombre = row.get('Nombre', '')
                        id_prod = row.get('ID')
                        if nombre and id_prod:
                            self.combo_selector.addItem(nombre, id_prod)
            except Exception as e:
                print(f"Error cargando productos: {e}")
        else:
            self.combo_selector.addItem("-- Seleccionar Categoria --", None)
            try:
                cm = CategoriaModel()
                df = cm.obtener_todas()
                if not df.empty:
                    for _, row in df.iterrows():
                        nombre_cat = row.get('nombre_categoria', '')
                        id_cat = row.get('id_categoria_productos')
                        if nombre_cat and id_cat:
                            self.combo_selector.addItem(nombre_cat, int(id_cat))
            except Exception as e:
                print(f"Error cargando categorias: {e}")

    def cargar_categorias(self):
        pass

    def cargar_productos(self):
        pass

    def crear_promocion(self):
        nombre = self.input_nombre.text().strip()
        desc = self.input_desc.text().strip()
        pct = int(self.input_descuento.value())
        inicio = self.dt_inicio.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        fin = self.dt_fin.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        
        if not nombre:
            QMessageBox.warning(self, "Validacion", "Ingrese un nombre para la promocion")
            return
        
        if inicio >= fin:
            QMessageBox.warning(self, "Validacion", "La fecha de inicio debe ser anterior a la fecha fin")
            return
        
        # Validar que se haya seleccionado producto o categoria
        id_seleccionado = self.combo_selector.currentData()
        if not id_seleccionado:
            QMessageBox.warning(self, "Validacion", "Seleccione un producto o categoria")
            return
        
        try:
            # Crear promocion
            idp = self.promo_model.crear(nombre, desc, pct, inicio, fin, estado='activa')
            
            # Asignar a producto o categoria
            if self.radio_producto.isChecked():
                self.promo_model.asignar_producto(int(idp), id_seleccionado)
                QMessageBox.information(self, "Exito", f"Promocion creada y asignada al producto")
            else:
                self.promo_model.asignar_categoria(int(idp), int(id_seleccionado))
                QMessageBox.information(self, "Exito", f"Promocion creada y asignada a la categoria")
            
            # Limpiar formulario
            self.input_nombre.clear()
            self.input_desc.clear()
            self.input_descuento.setValue(10)
            self.dt_inicio.setDateTime(QDateTime.currentDateTime())
            self.dt_fin.setDateTime(QDateTime.currentDateTime().addDays(7))
            self.combo_selector.setCurrentIndex(0)
            
            # Recargar tabla
            self.cargar_promociones()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def cargar_promociones(self):
        promos = self.promo_model.obtener_todas()
        self.tabla.setRowCount(len(promos))
        
        for i, p in enumerate(promos):
            # ID
            id_item = QTableWidgetItem(str(p['id_promocion']))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            self.tabla.setItem(i, 0, id_item)

            # Nombre
            nombre_item = QTableWidgetItem(p['nombre'])
            nombre_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            nombre_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 1, nombre_item)

            # Descuento
            desc_item = QTableWidgetItem(str(p['descuento']) + " %")
            desc_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            desc_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 2, desc_item)

            # Fecha Inicio
            inicio_item = QTableWidgetItem(str(p['fecha_inicio']))
            inicio_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            inicio_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 3, inicio_item)

            # Fecha Fin
            fin_item = QTableWidgetItem(str(p['fecha_fin']))
            fin_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            fin_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 4, fin_item)

            # Estado
            estado_item = QTableWidgetItem(p['estado'].capitalize())
            estado_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemNeverHasChildren)
            estado_item.setTextAlignment(Qt.AlignCenter)
            
            # Color segun estado
            if p['estado'] == 'activa':
                estado_item.setBackground(Qt.green)
            elif p['estado'] == 'inactiva':
                estado_item.setBackground(Qt.yellow)
            else:
                estado_item.setBackground(Qt.red)
            
            self.tabla.setItem(i, 5, estado_item)

            # Botones de accion
            btns = QWidget()
            lay = QHBoxLayout(btns)
            lay.setContentsMargins(2, 2, 2, 2)
            lay.setSpacing(5)
            
            # Boton Activar/Desactivar
            btn_act = QPushButton("Activar" if p['estado'] != 'activa' else "Desactivar")
            btn_act.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 6px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            btn_act.setFixedHeight(28)
            btn_act.setFixedWidth(85)
            btn_act.clicked.connect(lambda checked, pid=p['id_promocion'], est=p['estado']: self.toggle_estado(pid, est))
            
            # Boton Editar
            btn_edit = QPushButton("Editar")
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 6px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_edit.setFixedHeight(28)
            btn_edit.setFixedWidth(70)
            btn_edit.clicked.connect(lambda checked, pid=p['id_promocion']: self.editar_promocion(pid))
            
            # Boton Eliminar
            btn_del = QPushButton("Eliminar")
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 6px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            btn_del.setFixedHeight(28)
            btn_del.setFixedWidth(70)
            btn_del.clicked.connect(lambda checked, pid=p['id_promocion']: self.eliminar_promocion(pid))
            
            lay.addWidget(btn_act)
            lay.addWidget(btn_edit)
            lay.addWidget(btn_del)
            self.tabla.setCellWidget(i, 6, btns)

    def toggle_estado(self, id_prom, estado_actual):
        nuevo = 'activa' if estado_actual != 'activa' else 'inactiva'
        try:
            self.promo_model.actualizar_estado(id_prom, nuevo)
            QMessageBox.information(self, "Promocion", f"Estado actualizado a {nuevo}")
            self.cargar_promociones()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def eliminar_promocion(self, id_prom):
        resp = QMessageBox.question(self, "Confirmar", "Eliminar esta promocion?", 
                                    QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        try:
            self.promo_model.eliminar(id_prom)
            QMessageBox.information(self, "Promocion", "Promocion eliminada correctamente")
            self.cargar_promociones()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def editar_promocion(self, id_prom):
        try:
            data = self.promo_model.obtener_por_id(id_prom)
            if not data:
                QMessageBox.warning(self, "Editar", "Promocion no encontrada")
                return
            dlg = EditPromocionDialog(self, self.promo_model, data)
            if dlg.exec_() == QDialog.Accepted:
                self.cargar_promociones()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class EditPromocionDialog(QDialog):
    def __init__(self, parent, promo_model, promocion):
        super().__init__(parent)
        self.setWindowTitle("Editar Promocion")
        self.setMinimumWidth(500)
        self.promo_model = promo_model
        self.promocion = promocion
        self.crear_interfaz()

    def crear_interfaz(self):
        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Campos de edicion
        self.input_nombre = QLineEdit(self.promocion['nombre'])
        self.input_desc = QLineEdit(self.promocion.get('descripcion') or '')
        
        self.input_descuento = QSpinBox()
        self.input_descuento.setRange(0, 100)
        self.input_descuento.setValue(int(float(self.promocion.get('descuento', 0))))
        self.input_descuento.setSuffix(" %")
        
        self.dt_inicio = QDateTimeEdit(QDateTime.fromString(str(self.promocion.get('fecha_inicio')), 'yyyy-MM-dd HH:mm:ss'))
        self.dt_inicio.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.dt_inicio.setCalendarPopup(True)
        
        self.dt_fin = QDateTimeEdit(QDateTime.fromString(str(self.promocion.get('fecha_fin')), 'yyyy-MM-dd HH:mm:ss'))
        self.dt_fin.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.dt_fin.setCalendarPopup(True)
        
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(['activa', 'inactiva'])
        
        current_estado = self.promocion.get('estado') or 'inactiva'
        if current_estado == 'expirada':
            lbl_exp = QLabel("(Expirada)")
            lbl_exp.setStyleSheet('color: #e74c3c; font-weight: bold;')
            layout.addRow('Estado actual:', lbl_exp)
        
        idx = self.combo_estado.findText(current_estado if current_estado in ['activa', 'inactiva'] else 'inactiva')
        if idx >= 0:
            self.combo_estado.setCurrentIndex(idx)

        layout.addRow('Nombre:', self.input_nombre)
        layout.addRow('Descripcion:', self.input_desc)
        layout.addRow('Descuento %:', self.input_descuento)
        layout.addRow('Fecha Inicio:', self.dt_inicio)
        layout.addRow('Fecha Fin:', self.dt_fin)
        layout.addRow('Estado:', self.combo_estado)

        # Categorias asignadas
        assigned_widget = QWidget()
        assigned_layout = QVBoxLayout(assigned_widget)
        assigned_layout.setContentsMargins(0, 0, 0, 0)
        layout.addRow('Categorias asignadas:', assigned_widget)
        self.assigned_cat_layout = assigned_layout

        # Botones
        btn_layout = QHBoxLayout()
        
        btn_cancel = QPushButton('Cancelar')
        btn_cancel.setStyleSheet('background-color: #95a5a6; color: white; padding: 8px; border-radius: 4px;')
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton('Guardar Cambios')
        btn_save.setStyleSheet('background-color: #27ae60; color: white; padding: 8px; border-radius: 4px;')
        btn_save.clicked.connect(self.guardar)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addRow(btn_layout)

        self.load_assigned_categories()

    def guardar(self):
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, 'Validacion', 'El nombre es requerido')
            return
        
        inicio = self.dt_inicio.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        fin = self.dt_fin.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        
        if inicio >= fin:
            QMessageBox.warning(self, 'Validacion', 'La fecha de inicio debe ser anterior a la fecha fin')
            return
        
        try:
            self.promo_model.actualizar(
                int(self.promocion['id_promocion']),
                nombre=nombre,
                descripcion=self.input_desc.text().strip(),
                descuento_pct=int(self.input_descuento.value()),
                fecha_inicio=inicio,
                fecha_fin=fin,
                estado=self.combo_estado.currentText()
            )
            QMessageBox.information(self, 'Exito', 'Promocion actualizada correctamente')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def load_assigned_categories(self):
        try:
            while self.assigned_cat_layout.count():
                item = self.assigned_cat_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()
            
            cats = self.promo_model.obtener_categorias_asignadas(self.promocion['id_promocion'])
            if not cats:
                self.assigned_cat_layout.addWidget(QLabel('Sin categorias asignadas'))
                return
            
            for c in cats:
                row_w = QWidget()
                row_l = QHBoxLayout(row_w)
                row_l.setContentsMargins(0, 0, 0, 0)
                
                lbl = QLabel(c['nombre_categoria'])
                
                btn_quitar = QPushButton('Quitar')
                btn_quitar.setStyleSheet('background-color: #e74c3c; color: white; padding: 4px 8px; border-radius: 3px;')
                btn_quitar.setFixedWidth(70)
                btn_quitar.clicked.connect(lambda _, cid=c['id_categoria_productos']: self.quitar_categoria(cid))
                
                row_l.addWidget(lbl)
                row_l.addStretch()
                row_l.addWidget(btn_quitar)
                self.assigned_cat_layout.addWidget(row_w)
        except Exception as e:
            self.assigned_cat_layout.addWidget(QLabel('Error cargando categorias'))

    def quitar_categoria(self, id_categoria):
        try:
            self.promo_model.remover_categoria(int(self.promocion['id_promocion']), int(id_categoria))
            QMessageBox.information(self, 'Asignacion', 'Categoria removida de la promocion')
            self.load_assigned_categories()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
