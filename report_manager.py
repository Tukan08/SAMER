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
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para evitar conflictos con tkinter
import matplotlib.pyplot as plt
import io
from collections import defaultdict


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

    
    def generar_reporte_recaudacion(self, filepath, datos_tabla, datos_graficos, meses_solicitados):
        """
        Genera un reporte PDF especializado para Recaudación con gráficos estadísticos
        
        Args:
            filepath (str): Ruta completa donde guardar el PDF
            datos_tabla (tuple): (columnas, filas) de la tabla Recaudacion
            datos_graficos (list): Lista de tuplas (Mes, Ubicacion, TotalRecaudado)
            meses_solicitados (int): Número de meses solicitados por el usuario
        
        Returns:
            bool: True si se generó correctamente, False en caso contrario
        """
        try:
            # Configurar estilo de matplotlib
            plt.style.use('ggplot')
            
            # Crear el documento PDF
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            elements = []
            
            # === ENCABEZADO ===
            logo_text = Paragraph("🎮", self.styles['CustomTitle'])
            elements.append(logo_text)
            elements.append(Spacer(1, 12))
            
            title_text = Paragraph(
                f"<b>Reporte Estadístico de Recaudación</b>",
                self.styles['CustomTitle']
            )
            elements.append(title_text)
            
            subtitle = Paragraph(
                "Sistema de Administración de Máquinas Expendedoras Recreativas",
                self.styles['CustomSubtitle']
            )
            elements.append(subtitle)
            elements.append(Spacer(1, 20))
            
            # Información del reporte
            fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            fecha_text = Paragraph(
                f"<b>Fecha de generación:</b> {fecha_generacion}",
                self.styles['MetaInfo']
            )
            elements.append(fecha_text)
            
            periodo_text = Paragraph(
                f"<b>Período analizado:</b> Últimos {meses_solicitados} mes(es)",
                self.styles['MetaInfo']
            )
            elements.append(periodo_text)
            elements.append(Spacer(1, 30))
            
            # === GENERAR GRÁFICOS ===
            
            if not datos_graficos:
                elements.append(Paragraph(
                    "<b>No hay datos disponibles para generar gráficos</b>",
                    self.styles['Normal']
                ))
            else:
                # Organizar datos por mes y ubicación
                datos_por_mes = defaultdict(lambda: defaultdict(float))
                meses_unicos = set()
                ubicaciones_unicas = set()
                
                for mes, ubicacion, total in datos_graficos:
                    datos_por_mes[mes][ubicacion] = float(total)
                    meses_unicos.add(mes)
                    ubicaciones_unicas.add(ubicacion)
                
                meses_ordenados = sorted(list(meses_unicos))
                ubicaciones_ordenadas = sorted(list(ubicaciones_unicas))
                
                # === CASO 1: Un solo mes - Gráfico de barras simple ===
                if meses_solicitados == 1 or len(meses_ordenados) == 1:
                    section_title = Paragraph(
                        "<b>Recaudación del Mes Actual</b>",
                        self.styles['Heading1']
                    )
                    elements.append(section_title)
                    elements.append(Spacer(1, 15))
                    
                    # Crear gráfico de barras
                    fig, ax = plt.subplots(figsize=(8, 5))
                    
                    mes_actual = meses_ordenados[0] if meses_ordenados else "N/A"
                    ubicaciones = []
                    montos = []
                    
                    for ubicacion in ubicaciones_ordenadas:
                        ubicaciones.append(ubicacion)
                        montos.append(datos_por_mes[mes_actual].get(ubicacion, 0))
                    
                    bars = ax.bar(ubicaciones, montos, color='#1f538d', alpha=0.8)
                    ax.set_xlabel('Ubicaciones', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Dinero Recaudado ($)', fontsize=12, fontweight='bold')
                    ax.set_title(f'Recaudación por Ubicación - {mes_actual}', 
                                fontsize=14, fontweight='bold')
                    ax.grid(axis='y', alpha=0.3)
                    
                    # Rotar etiquetas si hay muchas ubicaciones
                    if len(ubicaciones) > 4:
                        plt.xticks(rotation=45, ha='right')
                    
                    # Agregar valores sobre las barras
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'${height:,.0f}',
                               ha='center', va='bottom', fontsize=9)
                    
                    plt.tight_layout()
                    
                    # Guardar en buffer
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                    img_buffer.seek(0)
                    plt.close(fig)
                    
                    # Agregar al PDF
                    img = Image(img_buffer, width=6*inch, height=3.75*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 30))
                
                # === CASO 2: Múltiples meses - Gráficos de barras + tendencia ===
                else:
                    # Gráficos de barras por mes
                    section_title = Paragraph(
                        "<b>Recaudación Mensual por Ubicación</b>",
                        self.styles['Heading1']
                    )
                    elements.append(section_title)
                    elements.append(Spacer(1, 15))
                    
                    for mes in meses_ordenados:
                        # Crear gráfico de barras para este mes
                        fig, ax = plt.subplots(figsize=(7, 4))
                        
                        ubicaciones = []
                        montos = []
                        
                        for ubicacion in ubicaciones_ordenadas:
                            ubicaciones.append(ubicacion)
                            montos.append(datos_por_mes[mes].get(ubicacion, 0))
                        
                        bars = ax.bar(ubicaciones, montos, color='#1f538d', alpha=0.8)
                        ax.set_xlabel('Ubicaciones', fontsize=11, fontweight='bold')
                        ax.set_ylabel('Dinero Recaudado ($)', fontsize=11, fontweight='bold')
                        ax.set_title(f'Recaudación - {mes}', fontsize=12, fontweight='bold')
                        ax.grid(axis='y', alpha=0.3)
                        
                        if len(ubicaciones) > 4:
                            plt.xticks(rotation=45, ha='right')
                        
                        # Valores sobre barras
                        for bar in bars:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height,
                                   f'${height:,.0f}',
                                   ha='center', va='bottom', fontsize=8)
                        
                        plt.tight_layout()
                        
                        img_buffer = io.BytesIO()
                        plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight')
                        img_buffer.seek(0)
                        plt.close(fig)
                        
                        img = Image(img_buffer, width=5*inch, height=2.85*inch)
                        elements.append(img)
                        elements.append(Spacer(1, 15))
                    
                    elements.append(Spacer(1, 20))
                    
                    # Gráfico de líneas de tendencia
                    section_title = Paragraph(
                        "<b>Tendencia de Recaudación por Ubicación</b>",
                        self.styles['Heading1']
                    )
                    elements.append(section_title)
                    elements.append(Spacer(1, 15))
                    
                    fig, ax = plt.subplots(figsize=(8, 5))
                    
                    # Colores para cada ubicación
                    colores = plt.cm.tab10(range(len(ubicaciones_ordenadas)))
                    
                    for idx, ubicacion in enumerate(ubicaciones_ordenadas):
                        meses_labels = []
                        valores = []
                        
                        for mes in meses_ordenados:
                            meses_labels.append(mes)
                            valores.append(datos_por_mes[mes].get(ubicacion, 0))
                        
                        ax.plot(meses_labels, valores, marker='o', linewidth=2,
                               label=ubicacion, color=colores[idx])
                    
                    ax.set_xlabel('Mes', fontsize=12, fontweight='bold')
                    ax.set_ylabel('Dinero Recaudado ($)', fontsize=12, fontweight='bold')
                    ax.set_title('Evolución de Recaudación por Ubicación',
                                fontsize=14, fontweight='bold')
                    ax.legend(loc='best', fontsize=9)
                    ax.grid(True, alpha=0.3)
                    
                    if len(meses_ordenados) > 6:
                        plt.xticks(rotation=45, ha='right')
                    
                    plt.tight_layout()
                    
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                    img_buffer.seek(0)
                    plt.close(fig)
                    
                    img = Image(img_buffer, width=6*inch, height=3.75*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 30))
            
            # === TABLA DE DATOS ===
            section_title = Paragraph(
                "<b>Datos Detallados de Recaudación</b>",
                self.styles['Heading1']
            )
            elements.append(section_title)
            elements.append(Spacer(1, 15))
            
            columnas, filas = datos_tabla
            
            # Preparar datos para la tabla
            table_data = [columnas]
            for row in filas:
                processed_row = []
                for value in row:
                    if value is None:
                        processed_row.append("")
                    else:
                        str_value = str(value)
                        if len(str_value) > 40:
                            str_value = str_value[:37] + "..."
                        processed_row.append(str_value)
                table_data.append(processed_row)
            
            # Calcular ancho de columnas
            num_columns = len(columnas)
            available_width = 7.0 * inch
            col_width = available_width / num_columns
            
            table = Table(table_data, colWidths=[col_width] * num_columns)
            table.setStyle(TableStyle([
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
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
                 [colors.white, colors.HexColor('#F5F7F9')]),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 30))
            
            # Pie de página
            footer_text = Paragraph(
                "© 2025 Proyecto SAMER - Reporte Estadístico Generado Automáticamente",
                self.styles['MetaInfo']
            )
            elements.append(footer_text)
            
            # Generar el PDF
            doc.build(elements)
            
            # Limpiar matplotlib
            plt.close('all')
            
            return True
            
        except Exception as e:
            print(f"Error al generar reporte de recaudación: {str(e)}")
            import traceback
            traceback.print_exc()
            # Asegurar limpieza en caso de error
            plt.close('all')
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

def generar_reporte_recaudacion(filepath, datos_tabla, datos_graficos, meses_solicitados):
    """
    Función wrapper para generar reporte estadístico de recaudación
    
    Args:
        filepath (str): Ruta completa donde guardar el PDF
        datos_tabla (tuple): Tupla (columnas, filas) de la tabla Recaudacion
        datos_graficos (list): Lista de tuplas (Mes, Ubicacion, TotalRecaudado)
        meses_solicitados (int): Número de meses solicitados
    
    Returns:
        bool: True si se generó correctamente, False en caso contrario
    """
    generator = PDFGenerator()
    return generator.generar_reporte_recaudacion(filepath, datos_tabla, datos_graficos, meses_solicitados)
