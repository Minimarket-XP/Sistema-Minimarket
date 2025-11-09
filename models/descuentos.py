"""
Módulo de descuentos - operaciones sobre carritos
"""
from typing import List, Tuple


class AplicarDescuento:
    @staticmethod
    def _validar_porcentaje(pct: float):
        try:
            pct = float(pct)
        except Exception:
            raise ValueError("Porcentaje inválido")
        if pct < 0 or pct > 100:
            raise ValueError("El porcentaje debe estar entre 0 y 100")
        return pct

    @staticmethod
    def _validar_monto(monto: float):
        try:
            monto = float(monto)
        except Exception:
            raise ValueError("Monto inválido")
        if monto < 0:
            raise ValueError("El monto no puede ser negativo")
        return monto

    @staticmethod
    def aplicar_descuento_producto(carrito: List[dict], producto_id: str, porcentaje: float) -> Tuple[List[dict], float]:
        """Aplica un porcentaje de descuento a un producto específico en el carrito.

        Devuelve (carrito_modificado, monto_descuento_total)
        """
        porcentaje = AplicarDescuento._validar_porcentaje(porcentaje)
        descuento_total = 0.0
        for item in carrito:
            if str(item.get('id')) == str(producto_id):
                orig_total = float(item.get('total', 0))
                descuento = orig_total * (porcentaje / 100.0)
                nuevo_total = max(0.0, orig_total - descuento)
                item['total'] = round(nuevo_total, 2)
                # registrar descuento por línea
                item['descuento'] = round(descuento, 2)
                descuento_total += round(descuento, 2)
                break
        return carrito, round(descuento_total, 2)

    @staticmethod
    def aplicar_descuento_total(carrito: List[dict], porcentaje: float) -> Tuple[List[dict], float]:
        """Aplica un porcentaje a todo el carrito distribuyéndolo proporcionalmente a los subtotales.

        Devuelve (carrito_modificado, monto_descuento_total)
        """
        porcentaje = AplicarDescuento._validar_porcentaje(porcentaje)
        subtotal_total = sum(float(item.get('total', 0)) for item in carrito)
        if subtotal_total <= 0:
            return carrito, 0.0

        descuento_total = 0.0
        for item in carrito:
            item_sub = float(item.get('total', 0))
            descuento = item_sub * (porcentaje / 100.0)
            new_total = round(max(0.0, item_sub - descuento), 2)
            # No registrar descuento por línea para descuentos globales; dejar None
            item['descuento'] = None
            item['total'] = new_total
            descuento_total += round(descuento, 2)

        # Ajuste por redondeo: asegurar que descuento_total no exceda diferencia
        return carrito, round(descuento_total, 2)

    @staticmethod
    def aplicar_descuento_fijo(carrito: List[dict], monto: float) -> Tuple[List[dict], float]:
        """Aplica un monto fijo de descuento repartido proporcionalmente entre los items.

        Devuelve (carrito_modificado, monto_descuento_total)
        """
        monto = AplicarDescuento._validar_monto(monto)
        subtotal_total = sum(float(item.get('total', 0)) for item in carrito)
        if subtotal_total <= 0:
            return carrito, 0.0

        monto_aplicable = min(monto, subtotal_total)
        descuento_total = 0.0
        # Repartir proporcionalmente
        for item in carrito:
            item_sub = float(item.get('total', 0))
            proportion = item_sub / subtotal_total if subtotal_total > 0 else 0
            descuento = round(monto_aplicable * proportion, 2)
            new_total = round(max(0.0, item_sub - descuento), 2)
            # No registrar descuento por línea para descuentos globales; dejar None
            item['descuento'] = None
            item['total'] = new_total
            descuento_total += descuento

        # Ajuste por redondeo: si quedó diferencia, restarla del primer item
        diff = round(monto_aplicable - descuento_total, 2)
        if abs(diff) >= 0.01 and carrito:
            # restar la diferencia del primer item
            first = carrito[0]
            prev_total = float(first.get('total', 0))
            first['total'] = round(max(0.0, prev_total - diff), 2)
            # no registrar descuento por línea (global)
            first['descuento'] = None
            descuento_total = round(descuento_total + diff, 2)

        return carrito, round(descuento_total, 2)

    @staticmethod
    def aplicar_descuento_por_tipo(carrito: List[dict], campo: str, valor: str, porcentaje: float) -> Tuple[List[dict], float]:
        """Aplica un porcentaje de descuento a todos los items cuyo campo (p. ej. 'categoria' o 'tipo_corte') coincida con valor.

        Devuelve (carrito_modificado, monto_descuento_total)
        """
        porcentaje = AplicarDescuento._validar_porcentaje(porcentaje)
        descuento_total = 0.0
        for item in carrito:
            # usar llaves normales en los items (guardamos 'categoria' y 'tipo_corte')
            if str(item.get(campo, '')).strip().lower() == str(valor).strip().lower():
                item_sub = float(item.get('total', item.get('base_total', 0)))
                descuento = item_sub * (porcentaje / 100.0)
                item['total'] = round(max(0.0, item_sub - descuento), 2)
                descuento_total += round(descuento, 2)

        return carrito, round(descuento_total, 2)

