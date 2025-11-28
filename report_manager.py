"""
Módulo de Generación de Reportes PDF
Maneja toda la lógica de creación de reportes usando reportlab
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os


class PDFGenerator:
    """
    Clase para generar reportes PDF con formato profesional
    """
    
    def __init__(self):
        """Inicializar el generador de PDF"""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Crear estilos personalizados para el PDF"""
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1f538d'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Estilo para información de metadata
        self.styles.add(ParagraphStyle(
            name='MetaInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#999999'),
            spaceAfter=5,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        ))
    
    def generar_reporte_tabla(self, filepath, titulo, columnas, datos):
        """
        Genera un reporte PDF de una tabla específica
        
        Args:
            filepath (str): Ruta completa donde guardar el PDF
            titulo (str): Título del reporte (ej. "Reporte de Máquinas")
            columnas (list): Lista de nombres de columnas
            datos (list): Lista de tuplas con los datos
        
        Returns:
            bool: True si se generó correctamente, False en caso contrario
        """
        try:
            # Crear el documento PDF
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            # Lista para almacenar los elementos del PDF
            elements = []
            
            # === ENCABEZADO ===
            
            # Logo (opcional - emoji como placeholder)
            logo_text = Paragraph("🎮", self.styles['CustomTitle'])
            elements.append(logo_text)
            elements.append(Spacer(1, 12))
            
            # Título principal
            title_text = Paragraph(f"<b>{titulo}</b>", self.styles['CustomTitle'])
            elements.append(title_text)
            
            # Subtítulo con sistema
            subtitle = Paragraph(
                "Sistema de Administración de Máquinas Expendedoras Recreativas",
                self.styles['CustomSubtitle']
            )
            elements.append(subtitle)
            elements.append(Spacer(1, 20))
            
            # Información de generación
            fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            fecha_text = Paragraph(
                f"<b>Fecha de generación:</b> {fecha_generacion}",
                self.styles['MetaInfo']
            )
            elements.append(fecha_text)
            
            total_registros = Paragraph(
                f"<b>Total de registros:</b> {len(datos)}",
                self.styles['MetaInfo']
            )
            elements.append(total_registros)
            elements.append(Spacer(1, 30))
            
            # === TABLA DE DATOS ===
            
            # Preparar datos para la tabla
            # Primera fila: encabezados
            table_data = [columnas]
            
            # Agregar los datos
            for row in datos:
                # Convertir valores None a cadena vacía y limitar longitud
                processed_row = []
                for value in row:
                    if value is None:
                        processed_row.append("")
                    else:
                        # Limitar longitud de texto para que quepa en la tabla
                        str_value = str(value)
                        if len(str_value) > 40:
                            str_value = str_value[:37] + "..."
                        processed_row.append(str_value)
                table_data.append(processed_row)
            
            # Calcular ancho de columnas dinámicamente
            num_columns = len(columnas)
            available_width = 7.0 * inch  # Ancho disponible en la página
            col_width = available_width / num_columns
            
            # Crear la tabla
            table = Table(table_data, colWidths=[col_width] * num_columns)
            
            # Estilo de la tabla
            table_style = TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f538d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Datos
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                
                # Bordes
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1f538d')),
                
                # Alternar colores de filas para mejor legibilidad
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F7F9')]),
            ])
            
            table.setStyle(table_style)
            elements.append(table)
            
            # === PIE DE PÁGINA ===
            elements.append(Spacer(1, 30))
            
            footer_text = Paragraph(
                "© 2025 Proyecto SAMER - Todos los derechos reservados",
                self.styles['MetaInfo']
            )
            elements.append(footer_text)
            
            # Generar el PDF
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"Error al generar PDF: {str(e)}")
            return False
    
    def generar_reporte_general(self, filepath, datos_completos):
        """
        Genera un reporte general con múltiples tablas
        
        Args:
            filepath (str): Ruta completa donde guardar el PDF
            datos_completos (dict): Diccionario con datos de múltiples tablas
                                   {nombre_tabla: (columnas, datos)}
        
        Returns:
            bool: True si se generó correctamente, False en caso contrario
        """
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            elements = []
            
            # === PORTADA ===
            
            # Logo
            logo_text = Paragraph("🎮", self.styles['CustomTitle'])
            elements.append(logo_text)
            elements.append(Spacer(1, 12))
            
            # Título principal
            title_text = Paragraph(
                "<b>REPORTE GENERAL DEL SISTEMA</b>",
                self.styles['CustomTitle']
            )
            elements.append(title_text)
            
            # Subtítulo
            subtitle = Paragraph(
                "Sistema de Administración de Máquinas Expendedoras Recreativas",
                self.styles['CustomSubtitle']
            )
            elements.append(subtitle)
            elements.append(Spacer(1, 40))
            
            # Información de generación
            fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            fecha_text = Paragraph(
                f"<b>Fecha de generación:</b> {fecha_generacion}",
                self.styles['MetaInfo']
            )
            elements.append(fecha_text)
            elements.append(Spacer(1, 60))
            
            # === RESUMEN EJECUTIVO ===
            
            resumen_title = Paragraph(
                "<b>Resumen Ejecutivo</b>",
                self.styles['Heading1']
            )
            elements.append(resumen_title)
            elements.append(Spacer(1, 20))
            
            # Tabla de resumen
            resumen_data = [["Tabla", "Total de Registros"]]
            total_general = 0
            
            for tabla, (columnas, datos) in datos_completos.items():
                num_registros = len(datos)
                total_general += num_registros
                resumen_data.append([tabla, str(num_registros)])
            
            resumen_data.append(["TOTAL", str(total_general)])
            
            resumen_table = Table(resumen_data, colWidths=[4*inch, 2*inch])
            resumen_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f538d')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E3F2FD')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            elements.append(resumen_table)
            elements.append(Spacer(1, 40))
            
            # === SECCIONES DETALLADAS (Cada tabla) ===
            
            for tabla, (columnas, datos) in datos_completos.items():
                # Título de sección
                section_title = Paragraph(
                    f"<b>{tabla}</b>",
                    self.styles['Heading2']
                )
                elements.append(section_title)
                elements.append(Spacer(1, 15))
                
                # Generar tabla con los primeros 20 registros
                table_data = [columnas]
                
                # Limitar a 20 registros para el reporte general
                datos_limitados = datos[:20] if len(datos) > 20 else datos
                
                for row in datos_limitados:
                    processed_row = []
                    for value in row:
                        if value is None:
                            processed_row.append("")
                        else:
                            str_value = str(value)
                            if len(str_value) > 30:
                                str_value = str_value[:27] + "..."
                            processed_row.append(str_value)
                    table_data.append(processed_row)
                
                # Calcular ancho de columnas
                num_columns = len(columnas)
                available_width = 7.0 * inch
                col_width = available_width / num_columns
                
                detail_table = Table(table_data, colWidths=[col_width] * num_columns)
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f538d')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F7F9')]),
                ]))
                
                elements.append(detail_table)
                
                # Nota si hay más registros
                if len(datos) > 20:
                    nota = Paragraph(
                        f"<i>Mostrando 20 de {len(datos)} registros totales</i>",
                        self.styles['MetaInfo']
                    )
                    elements.append(Spacer(1, 5))
                    elements.append(nota)
                
                elements.append(Spacer(1, 30))
            
            # === PIE DE PÁGINA ===
            footer_text = Paragraph(
                "© 2025 Proyecto SAMER - Reporte generado automáticamente",
                self.styles['MetaInfo']
            )
            elements.append(footer_text)
            
            # Generar el PDF
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"Error al generar reporte general: {str(e)}")
            return False


# ============================================================================
# FUNCIONES DE UTILIDAD (ALTERNATIVA A CLASE)
# ============================================================================

def generar_reporte_tabla(filepath, titulo, columnas, datos):
    """
    Función wrapper para generar reporte de tabla individual
    
    Args:
        filepath (str): Ruta completa donde guardar el PDF
        titulo (str): Título del reporte
        columnas (list): Lista de nombres de columnas
        datos (list): Lista de tuplas con los datos
    
    Returns:
        bool: True si se generó correctamente, False en caso contrario
    """
    generator = PDFGenerator()
    return generator.generar_reporte_tabla(filepath, titulo, columnas, datos)


def generar_reporte_general(filepath, datos_completos):
    """
    Función wrapper para generar reporte general
    
    Args:
        filepath (str): Ruta completa donde guardar el PDF
        datos_completos (dict): Diccionario con datos de múltiples tablas
    
    Returns:
        bool: True si se generó correctamente, False en caso contrario
    """
    generator = PDFGenerator()
    return generator.generar_reporte_general(filepath, datos_completos)