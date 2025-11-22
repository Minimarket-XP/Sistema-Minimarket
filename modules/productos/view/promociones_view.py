from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit, QDateTimeEdit,
                             QComboBox, QMessageBox, QSpinBox, QGroupBox, QCompleter)
from PyQt5.QtCore import Qt, QDateTime
from modules.productos.models.promocion_model import PromocionModel
from core.database import db


class PromocionesFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prom_model = PromocionModel()
        self.init_ui()
        self.cargar_promociones()

    def init_ui(self):
        layout = QVBoxLayout(self)
        titulo = QLabel("Promociones")
        titulo.setStyleSheet("font-size:20px; font-weight:bold;")
        layout.addWidget(titulo)
        # Form crear promocion (más claro y vertical)
        form = QGroupBox("Crear nueva promoción")
        form.setStyleSheet("QGroupBox{font-weight:bold; padding:8px;} QGroupBox::title{subcontrol-origin: margin; left: 8px;}" )
        f_layout = QVBoxLayout(form)

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
        btn_crear.setStyleSheet("background-color:#2ecc71; color:white; padding:8px; font-weight:bold;")
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
        layout.addWidget(form)

        # Asignaciones rápidas (producto por nombre con autocompletado)
        assign_box = QGroupBox("Asignar promoción")
        assign_box.setStyleSheet("QGroupBox{padding:8px;} QGroupBox::title{font-weight:bold;}" )
        a_layout = QHBoxLayout(assign_box)
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
        a_layout.addWidget(self.input_prom_id)
        a_layout.addWidget(QLabel("Producto:"))
        a_layout.addWidget(self.input_producto)
        a_layout.addWidget(btn_asign_prod)
        a_layout.addWidget(self.combo_categoria)
        a_layout.addWidget(btn_asign_cat)
        layout.addWidget(assign_box)

        # Tabla de promociones
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Descuento%", "Inicio", "Fin", "Estado", "Acciones"])
        layout.addWidget(self.tabla)

        # cargar productos para autocompletar
        self.cargar_productos()

    def cargar_categorias(self):
        self.combo_categoria.clear()
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT id_categoria_productos, nombre_categoria FROM categoria_productos ORDER BY nombre_categoria')
            rows = cur.fetchall()
            conn.close()
            self.combo_categoria.addItem("-- Seleccionar --", None)
            for r in rows:
                self.combo_categoria.addItem(r[1], r[0])
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
        """Carga lista de productos para autocompletado (nombre->id)."""
        try:
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id_producto, nombre_producto FROM productos ORDER BY nombre_producto")
            rows = cur.fetchall()
            conn.close()
            self.product_name_to_id = {
                (r[1].strip() if r[1] else ''): r[0] for r in rows
            }
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
            self.tabla.setItem(i, 0, QTableWidgetItem(str(p['id_promocion'])))
            self.tabla.setItem(i, 1, QTableWidgetItem(p['nombre']))
            self.tabla.setItem(i, 2, QTableWidgetItem(str(p['descuento'])))
            self.tabla.setItem(i, 3, QTableWidgetItem(str(p['fecha_inicio'])))
            self.tabla.setItem(i, 4, QTableWidgetItem(str(p['fecha_fin'])))
            self.tabla.setItem(i, 5, QTableWidgetItem(p['estado']))
            # Acciones: activar/desactivar, eliminar
            btns = QWidget()
            from PyQt5.QtWidgets import QHBoxLayout
            lay = QHBoxLayout(btns)
            lay.setContentsMargins(0,0,0,0)
            btn_act = QPushButton("Activar" if p['estado'] != 'activa' else "Desactivar")
            btn_act.clicked.connect(lambda checked, pid=p['id_promocion'], est=p['estado']: self.toggle_estado(pid, est))
            btn_del = QPushButton("Eliminar")
            btn_del.clicked.connect(lambda checked, pid=p['id_promocion']: self.eliminar_promocion(pid))
            lay.addWidget(btn_act)
            lay.addWidget(btn_del)
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
                # intentar buscar por LIKE en la BD (primer resultado)
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("SELECT id_producto FROM productos WHERE nombre_producto LIKE ? LIMIT 1", (f"%{prod_text}%",))
                r = cur.fetchone()
                conn.close()
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
