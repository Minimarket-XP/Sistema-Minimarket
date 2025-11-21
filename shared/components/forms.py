## Formularios y componentes reutilizables

import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QFileDialog, 
                             QMessageBox, QInputDialog, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from core.config import *
from shared.helpers import cargar_categorias, cargar_tipos_corte, cargar_tipos_productos, cargar_unidades_medida, validar_numero

class ProductoForm(QDialog):    
    def __init__(self, parent, title="Producto", producto_data=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(520, 510)
        self.setModal(True)
        
        self.parent = parent
        self.producto_data = producto_data
        
        self.img_path = ""
        self.entries = {}

        self.crearInterfaz()
        self._cargar_datos_si_existe()
    
    def _cargar_datos_si_existe(self):
        """Carga datos del producto si existe"""
        if self.producto_data is not None:
            # Verificar si es pandas Series o dict y tiene datos
            if hasattr(self.producto_data, 'empty'):
                if not self.producto_data.empty:
                    self.llenarCampos()
            elif self.producto_data:  # Para dict u otros tipos
                self.llenarCampos()
    
    def crearInterfaz(self): # → Interfaz del formulario
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título dinámico
        titulo = self._get_titulo()
        titulo_label = self._crear_titulo_label(titulo)
        main_layout.addWidget(titulo_label)
        
        # Campos de entrada optimizados
        self._crear_campos_entrada(main_layout)
        
        # Categoría y tipo de corte
        self._crear_comboboxes(main_layout)
        
        # Selección de imagen
        self._crear_seccion_imagen(main_layout)
        
        # Botones
        self._crear_botones(main_layout)
    
    def _get_titulo(self): #→ Determina el título del formulario
        es_modificar = False
        if self.producto_data is not None:
            if hasattr(self.producto_data, 'empty'):
                es_modificar = not self.producto_data.empty
            else:
                es_modificar = bool(self.producto_data)
        return "Modificar Producto" if es_modificar else "Registrar Producto"
    
    def _crear_titulo_label(self, titulo): # → Label del título
        titulo_label = QLabel(titulo)
        titulo_label.setAlignment(Qt.AlignCenter)
        titulo_label.setStyleSheet(f"""
            QLabel {{
                color: {THEME_COLOR};
                font-size: 18px;
                font-weight: bold;
                font-family: Arial;
                margin-bottom: 10px;
            }}
        """)
        return titulo_label
    
    def _crear_campos_entrada(self, main_layout): # → Crea los campos de entrada
        campos = [("Nombre", ""), ("Precio", "0"), ("Stock inicial", "0"), ("Stock Mínimo", "0")]
        
        for label, default in campos:
            campo_layout = QHBoxLayout()
            
            label_widget = QLabel(label + ":")
            label_widget.setFixedWidth(100)
            label_widget.setStyleSheet("font-weight: bold; color: #333;")
            
            entry = self._crear_line_edit(default)
            self.entries[label] = entry
            
            campo_layout.addWidget(label_widget)
            campo_layout.addWidget(entry)
            main_layout.addLayout(campo_layout)
    
    def _crear_line_edit(self, default_value, entry=None): # → QLineEdit con estilos
        entry = QLineEdit()
        entry.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #4285F4;
            }
        """)
        
        if self.producto_data is None or (hasattr(self.producto_data, 'empty') and self.producto_data.empty):
            entry.setText(default_value)
        
        return entry
    
    def _crear_comboboxes(self, main_layout): # → Crea comboboxes de categoría, tipo y unidad
        # Categoría
        categoria_layout = QHBoxLayout()
        categoria_label = QLabel("Categoría:")
        categoria_label.setFixedWidth(100)
        categoria_label.setStyleSheet("font-weight: bold; color: #333;")

        self.categoria_cb = QComboBox()
        self.categoria_cb.addItems(cargar_categorias())
        self.categoria_cb.setStyleSheet(self._get_combobox_style())
        
        btn_nueva_categoria = self._crear_boton_secundario("Nueva...", self.agregarCategoriasRapido)
        
        categoria_layout.addWidget(categoria_label)
        categoria_layout.addWidget(self.categoria_cb)
        categoria_layout.addWidget(btn_nueva_categoria)
        main_layout.addLayout(categoria_layout)
        
        # Tipo de producto
        tipo_layout = QHBoxLayout()
        tipo_label = QLabel("Tipo:")
        tipo_label.setFixedWidth(100)
        tipo_label.setStyleSheet("font-weight: bold; color: #333;")

        self.tipo_cb = QComboBox()
        self.tipo_cb.addItems(cargar_tipos_productos())
        self.tipo_cb.setStyleSheet(self._get_combobox_style())
        
        tipo_layout.addWidget(tipo_label)
        tipo_layout.addWidget(self.tipo_cb)
        main_layout.addLayout(tipo_layout)
        
        # Unidad de medida
        unidad_layout = QHBoxLayout()
        unidad_label = QLabel("Unidad:")
        unidad_label.setFixedWidth(100)
        unidad_label.setStyleSheet("font-weight: bold; color: #333;")

        self.unidad_cb = QComboBox()
        self.unidad_cb.addItems(cargar_unidades_medida())
        self.unidad_cb.setStyleSheet(self._get_combobox_style())
        
        unidad_layout.addWidget(unidad_label)
        unidad_layout.addWidget(self.unidad_cb)
        main_layout.addLayout(unidad_layout)
        
        # Tipo de corte (opcional para carnes)
        corte_layout = QHBoxLayout()
        self.corte_label = QLabel("Tipo de Corte:")
        self.corte_label.setFixedWidth(100)
        self.corte_label.setStyleSheet("font-weight: bold; color: #333;")

        self.corte_cb = QComboBox()
        self.corte_cb.addItems(cargar_tipos_corte())
        self.corte_cb.setStyleSheet(self._get_combobox_style())
        
        corte_layout.addWidget(self.corte_label)
        corte_layout.addWidget(self.corte_cb)
        main_layout.addLayout(corte_layout)

        # Ocultar inicialmente el tipo de corte y su label
        self.corte_label.hide()
        self.corte_cb.hide()

        # Conectar la señal para mostrar/ocultar según categoría
        self.categoria_cb.currentTextChanged.connect(self.mostrarOcultarTipoCorte)

    def _crear_seccion_imagen(self, main_layout):
        """Crea la sección de selección de imagen"""
        imagen_layout = QHBoxLayout()
        imagen_label = QLabel("Imagen (opcional):")
        imagen_label.setFixedWidth(130)
        imagen_label.setStyleSheet("font-weight: bold; color: #333;")
        
        btn_seleccionar = self._crear_boton_info("Seleccionar", self.seleccionarImagen)
        
        self.img_info_label = QLabel("")
        self.img_info_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        
        imagen_layout.addWidget(imagen_label)
        imagen_layout.addWidget(btn_seleccionar)
        imagen_layout.addWidget(self.img_info_label)
        main_layout.addLayout(imagen_layout)
        
        # Vista previa de imagen
        self.imagen_viewer = ImagenViewer()
        main_layout.addWidget(self.imagen_viewer)
    
    def _crear_botones(self, main_layout):
        """Crea los botones de acción"""
        botones_layout = QHBoxLayout()
        
        btn_cancelar = self._crear_boton_secundario("Cancelar", self.reject)
        btn_guardar = self._crear_boton_primario("Guardar", self.validarYGuardar)
        
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(btn_guardar)
        main_layout.addLayout(botones_layout)
    
    def _get_combobox_style(self):
        """Retorna el estilo para comboboxes"""
        return """
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QComboBox:focus {
                border: 2px solid #4285F4;
            }
        """
    
    def _crear_boton_secundario(self, texto, funcion):
        """Crea un botón con estilo secundario"""
        boton = QPushButton(texto)
        boton.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        boton.clicked.connect(funcion)
        return boton
    
    def _crear_boton_info(self, texto, funcion):
        """Crea un botón con estilo info"""
        boton = QPushButton(texto)
        boton.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        boton.clicked.connect(funcion)
        return boton
    
    def _crear_boton_primario(self, texto, funcion):
        """Crea un botón con estilo primario"""
        boton = QPushButton(texto)
        boton.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #0056b3;
            }}
        """)
        boton.clicked.connect(funcion)
        return boton
    
    def llenarCampos(self):
        if self.producto_data is None or self.producto_data.empty:
            return
        
        # Llenar campos de texto
        self.entries["Nombre"].setText(str(self.producto_data.get("Nombre", "")))
        self.entries["Precio"].setText(str(self.producto_data.get("Precio", "")))
        self.entries["Stock inicial"].setText(str(self.producto_data.get("Stock", "")))
        self.entries["Stock Mínimo"].setText(str(self.producto_data.get("Stock Mínimo", 1)))
        
        # Establecer categoría y tipo de corte
        categoria = str(self.producto_data.get("Categoría", ""))
        # Buscar y seleccionar categoría
        categoria_index = self.categoria_cb.findText(categoria)
        if categoria_index >= 0:
            self.categoria_cb.setCurrentIndex(categoria_index)

        if categoria == "carnes":
            tipo_corte = str(self.producto_data.get("Tipo de Corte", ""))
            # Buscar y seleccionar tipo de corte
            corte_index = self.corte_cb.findText(tipo_corte)
            if corte_index >= 0:
                self.corte_cb.setCurrentIndex(corte_index)

        # Establecer imagen
        imagen_actual = self.producto_data.get("Imagen", "")
        if imagen_actual and os.path.exists(imagen_actual):
            self.img_path = imagen_actual
            self.img_info_label.setText(os.path.basename(imagen_actual))
    
    def agregarCategoriasRapido(self):
        nueva_categoria, ok = QInputDialog.getText(self, "Nueva Categoría", 
                                                  "Ingrese el nombre de la nueva categoría:")
        
        if ok and nueva_categoria.strip():
            nueva_categoria = nueva_categoria.strip()
            try:
                # Agregar a la base de datos
                from core.database import db
                db.execute_query("INSERT OR IGNORE INTO categorias (nombre, descripcion) VALUES (?, ?)", 
                               (nueva_categoria, f"Categoría {nueva_categoria}"))
                
                # Recargar las categorías en el dropdown
                categorias_actualizadas = cargar_categorias()
                self.categoria_cb.clear()
                self.categoria_cb.addItems(categorias_actualizadas)
                
                # Seleccionar la nueva categoría
                categoria_index = self.categoria_cb.findText(nueva_categoria)
                if categoria_index >= 0:
                    self.categoria_cb.setCurrentIndex(categoria_index)
                
                QMessageBox.information(self, "Éxito", f"Categoría '{nueva_categoria}' agregada correctamente.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo agregar la categoría: {e}")
    
    def seleccionarImagen(self):
        file_dialog = QFileDialog()
        path, _ = file_dialog.getOpenFileName(self, "Seleccionar imagen", "", 
                                            "Imágenes (*.png *.jpg *.jpeg *.gif *.bmp)")
        if path:
            self.img_path = path
            self.img_info_label.setText(os.path.basename(path))
    
    def validarDatos(self):
        nombre = self.entries["Nombre"].text().strip()
        categoria = self.categoria_cb.currentText().strip()
        
        if not nombre:
            QMessageBox.critical(self, "Error", "El nombre del producto es obligatorio.")
            return None
        
        if not categoria:
            QMessageBox.critical(self, "Error", "Debes seleccionar una categoría del dropdown.")
            return None
        
        # Validar campos numéricos
        precio, precio_valido = validar_numero(self.entries["Precio"].text())
        stock, stock_valido = validar_numero(self.entries["Stock inicial"].text(), "int")
        stock_min, stock_min_valido = validar_numero(self.entries["Stock Mínimo"].text(), "int")
        
        if not precio_valido or precio <= 0:
            QMessageBox.critical(self, "Error", "El precio debe ser mayor que S/0.00")
            return None
        
        if not stock_valido or stock <= 0:
            QMessageBox.critical(self, "Error", "El stock debe ser un número mayor que 0.")
            return None

        if not stock_min_valido or stock_min <= 0:
            QMessageBox.critical(self, "Error", "El stock mínimo debe ser un número entero valido mayor que 0.")
            return None
        
        return {
            "Nombre": nombre,
            "Categoría": categoria,
            "Tipo de Corte": self.corte_cb.currentText().strip(),
            "Precio": precio,
            "Stock": stock,
            "Stock Mínimo": stock_min,
            "imagen_origen": self.img_path if self.img_path else None
        }

    def guardar(self):
        raise NotImplementedError("Debe implementarse en la clase hija")

    def mostrarOcultarTipoCorte(self, categoria): #
        """Muestra u oculta el campo de tipo de corte según la categoría"""
        if categoria.lower() == "carne" or categoria.lower() == "carnes":
            self.corte_label.show()
            self.corte_cb.show()
        else:
            self.corte_label.hide()
            self.corte_cb.hide()
            self.corte_cb.setCurrentIndex(0)  # Resetear selección

class ImagenViewer(QLabel):
    def __init__(self, parent = None, **kwargs):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f8f9fa;
                min-height: 200px;
                max-height: 200px;
                margin: 10px;
            }
        """)
        self.imagen_actual = None
    
    def mostrarImagen(self, ruta_imagen, tamaño=(200, 200)):
        try:
            # Limpiar imagen anterior primero
            self.limpiar()
            
            if ruta_imagen and os.path.exists(ruta_imagen):
                pixmap = QPixmap(ruta_imagen)
                # Verificar que el pixmap no sea nulo antes de escalar
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(tamaño[0], tamaño[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.setPixmap(scaled_pixmap)
                    self.imagen_actual = scaled_pixmap
                else:
                    self.limpiar()
            else:
                self.limpiar()
        except Exception as e:
            # Solo imprimir si es un error real, no de imagen que no existe
            if "doesn't exist" not in str(e):
                print(f"Error al cargar imagen: {e}")
            self.limpiar()
    
    def limpiar(self):
        self.clear()
        self.setText("Vista previa de imagen")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f8f9fa;
                min-height: 200px;
                max-height: 200px;
                margin: 10px;
                color: #6c757d;
                font-size: 14px;
            }
        """)
        self.imagen_actual = None