"""Exportador de datos a PDF y Excel.
Usa reportlab para PDF y openpyxl para Excel.
"""
import io
import os
import tempfile
import pandas as pd


def exportar_pdf(dataframe: pd.DataFrame, filename: str, titulo: str = "Reporte", chart_bytes: bytes = None):
    """Exporta el DataFrame a PDF usando reportlab. Lanza ImportError con mensaje claro si falta la dependencia."""
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.platypus import Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError as e:
        raise ImportError("Falta la dependencia 'reportlab'. Instálala: pip install reportlab") from e

    buffer = io.BytesIO()
    # Use landscape orientation for wider charts/tables
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(titulo, styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Prepare a display-friendly copy of the dataframe (format dates/numbers)
    df_display = dataframe.copy()
    try:
        # Format datetime-like columns (common name 'fecha')
        for col in df_display.columns:
            if 'fecha' in col.lower():
                try:
                    df_display[col] = pd.to_datetime(df_display[col]).dt.strftime('%Y-%m-%d %H:%M')
                except Exception:
                    pass
        # Format numeric columns as currency with 2 decimals (prefix S/)
        num_cols = df_display.select_dtypes(include=['number']).columns.tolist()
        for nc in num_cols:
            df_display[nc] = df_display[nc].apply(lambda x: f"S/{x:,.2f}")
    except Exception:
        df_display = dataframe.copy()

    # If chart image bytes provided, insert image first (scaled to fit page)
    if chart_bytes:
        try:
            img_buf = io.BytesIO(chart_bytes)
            # attempt to get image size using PIL to preserve aspect ratio and fit within page
            try:
                from PIL import Image as PILImage
                img_buf.seek(0)
                pil_img = PILImage.open(img_buf)
                img_w, img_h = pil_img.size  # pixels
                # compute aspect ratio and scale to fit within doc.width x doc.height (both in points)
                aspect = img_h / float(img_w) if img_w else 1.0
                draw_w = doc.width
                draw_h = draw_w * aspect
                if draw_h > doc.height:
                    draw_h = doc.height
                    draw_w = draw_h / aspect if aspect else draw_w
                img_buf = io.BytesIO(chart_bytes)
                img = RLImage(img_buf, width=draw_w, height=draw_h)
            except Exception:
                # If PIL not available or fails, scale to doc.width and let reportlab handle
                img_buf = io.BytesIO(chart_bytes)
                img = RLImage(img_buf, width=doc.width)
            elements.append(img)
            elements.append(Spacer(1, 12))
        except Exception:
            # If embedding fails, continue without image
            pass

    if df_display.empty:
        elements.append(Paragraph("No hay datos", styles['Normal']))
    else:
        # Convertir dataframe a lista de listas
        data = [list(df_display.columns)] + df_display.values.tolist()
        table = Table(data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        elements.append(table)

    doc.build(elements)


def exportar_excel(dataframe: pd.DataFrame, filename: str, sheet_name: str = 'Sheet1', chart_bytes: bytes = None):
    """Exporta el DataFrame a Excel usando openpyxl engine. Lanza ImportError con mensaje claro si falta openpyxl."""
    try:
        import openpyxl  # noqa: F401
    except ImportError as e:
        raise ImportError("Falta la dependencia 'openpyxl'. Instálala: pip install openpyxl") from e

    # Basic export without chart
    def _write_without_chart(startrow=None, chart_tmpfile=None):
        # Prepare a formatted copy for excel
        df_out = dataframe.copy()
        try:
            for col in df_out.columns:
                if 'fecha' in col.lower():
                    try:
                        df_out[col] = pd.to_datetime(df_out[col]).dt.strftime('%Y-%m-%d %H:%M')
                    except Exception:
                        pass
            num_cols = df_out.select_dtypes(include=['number']).columns.tolist()
            for nc in num_cols:
                df_out[nc] = df_out[nc].apply(lambda x: f"S/{x:,.2f}")
        except Exception:
            df_out = dataframe.copy()

        kwargs = {}
        if startrow is not None:
            kwargs['startrow'] = startrow
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_out.to_excel(writer, sheet_name=sheet_name, index=False, **kwargs)

        # If chart file provided, insert it using openpyxl after writer has closed
        if chart_tmpfile:
            from openpyxl import load_workbook
            from openpyxl.drawing.image import Image as XLImage
            wb = load_workbook(filename)
            ws = wb[sheet_name]
            img = XLImage(chart_tmpfile)
            ws.add_image(img, 'A1')
            wb.save(filename)

    # By default, write data starting at row 15 so there is room for the chart
    if chart_bytes:
        # create a temporary file for the PNG image
        tmp = None
        try:
            tmpf = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            tmpf.write(chart_bytes)
            tmpf.close()
            tmp = tmpf.name
            _write_without_chart(startrow=15, chart_tmpfile=tmp)
        finally:
            if tmp and os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except Exception:
                    pass
    else:
        _write_without_chart(startrow=15)
