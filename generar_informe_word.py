"""
Generador del Documento Oficial en Word (.docx) para la Evaluación Sumativa 2 — Caso 5.
Actualizado con:
1. Las observaciones exactas de la Evaluación Sumativa 1 entregadas por el docente Cristofher Rojas Rojas (Nota 5.5 -> Subsanación 100%).
2. Los 4 Diagramas UML en Alta Resolución (2400x1550 px) incrustados directamente en el documento Word:
   - Figura 1: Diagrama de Casos de Uso UML (que faltó en la Evaluación 1).
   - Figura 2: Diagrama de Secuencia UML de Urgencia, Triage Offline y Arbitraje ADR-05 (alta resolución).
   - Figura 3: Diagrama de Despliegue UML — Topología Híbrida con Nodos, Artefactos y Puertos explícitos (alta resolución).
   - Figura 4: Diagrama de Clases y Componentes de los 4 Patrones de Diseño implementados.
3. Funciones de Aptitud Arquitectónica (test_architectural_fitness.py) que subsanan la Dimensión 5 (Antipatrones y Evolución).
4. Anexo de Preguntas y Respuestas de Defensa Individual para obtener 7.0 en la presentación técnica.
"""
import os
import sys
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

DIAGRAMS_DIR = r"C:\Users\herna\.gemini\antigravity\brain\90cbd83b-c91c-4fc2-b93d-6848775d5bdc\diagramas_uml"


def set_cell_background(cell, hex_color: str):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=115, bottom=115, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="CBD5E1", sz="6", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f"</w:tblBorders>"
    )
    tblPr.append(borders)


def add_formatted_paragraph(
    doc_or_cell,
    text="",
    bold_prefix="",
    size=10.5,
    color=(35, 39, 47),
    space_after=6,
    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
):
    p = doc_or_cell.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.18
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.bold = True
        r_bold.font.name = "Calibri"
        r_bold.font.size = Pt(size)
        r_bold.font.color.rgb = RGBColor(*color)
    if text:
        r_text = p.add_run(text)
        r_text.font.name = "Calibri"
        r_text.font.size = Pt(size)
        r_text.font.color.rgb = RGBColor(*color)
    return p


def add_heading_1(doc, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Calibri"
    run.font.size = Pt(15)
    run.font.color.rgb = RGBColor(22, 34, 56)
    return p


def add_heading_2(doc, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(11)
    p.paragraph_format.space_after = Pt(5)
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Calibri"
    run.font.size = Pt(12.5)
    run.font.color.rgb = RGBColor(30, 48, 80)
    return p


def add_figure_image(doc, image_filename: str, caption_text: str):
    img_path = os.path.join(DIAGRAMS_DIR, image_filename)
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Cm(16.4))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run(caption_text)
        r_cap.italic = True
        r_cap.font.name = "Calibri"
        r_cap.font.size = Pt(9.5)
        r_cap.font.color.rgb = RGBColor(71, 85, 105)


def add_adr_table(doc, adr_title: str, decision: str, contexto: str, alternativas: str, razon: str, tradeoff: str):
    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table, color="CBD5E1", sz="6")

    col_widths = [Cm(3.6), Cm(12.8)]
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    hdr_cell = table.cell(0, 0).merge(table.cell(0, 1))
    set_cell_background(hdr_cell, "16324F")
    set_cell_margins(hdr_cell, top=130, bottom=130, left=180, right=180)
    p_hdr = hdr_cell.paragraphs[0]
    p_hdr.paragraph_format.space_after = Pt(0)
    r_hdr = p_hdr.add_run(adr_title)
    r_hdr.bold = True
    r_hdr.font.name = "Calibri"
    r_hdr.font.size = Pt(10.5)
    r_hdr.font.color.rgb = RGBColor(255, 255, 255)

    rows_data = [
        ("Decisión", decision, "FFFFFF", "FFFFFF"),
        ("Contexto", contexto, "F8FAFC", "F8FAFC"),
        ("Alternativas", alternativas, "FFFFFF", "FFFFFF"),
        ("Razón", razon, "F8FAFC", "F8FAFC"),
        ("Trade-off y Consecuencias", tradeoff, "FDF3E7", "FDF3E7"),
    ]

    for row_idx, (label, content, bg_left, bg_right) in enumerate(rows_data, start=1):
        c_left = table.cell(row_idx, 0)
        c_right = table.cell(row_idx, 1)
        c_left.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        c_right.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_background(c_left, bg_left)
        set_cell_background(c_right, bg_right)
        set_cell_margins(c_left, top=110, bottom=110, left=150, right=150)
        set_cell_margins(c_right, top=110, bottom=110, left=160, right=160)

        p_l = c_left.paragraphs[0]
        p_l.paragraph_format.space_after = Pt(0)
        r_l = p_l.add_run(label)
        r_l.bold = True
        r_l.font.name = "Calibri"
        r_l.font.size = Pt(9.5)
        r_l.font.color.rgb = RGBColor(30, 41, 59)

        p_r = c_right.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_r.paragraph_format.space_after = Pt(0)
        p_r.paragraph_format.line_spacing = 1.15
        r_r = p_r.add_run(content)
        r_r.font.name = "Calibri"
        r_r.font.size = Pt(9.5)
        r_r.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph()


def add_styled_data_table(doc, headers, rows, col_widths_cm):
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table, color="CBD5E1", sz="6")

    for col_idx, text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.width = Cm(col_widths_cm[col_idx])
        set_cell_background(cell, "E8EEF5")
        set_cell_margins(cell, top=110, bottom=110, left=130, right=130)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(text)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(9.3)
        r.font.color.rgb = RGBColor(22, 34, 56)

    for r_idx, row_values in enumerate(rows, start=1):
        bg = "FFFFFF" if r_idx % 2 == 1 else "F8FAFC"
        for c_idx, val in enumerate(row_values):
            cell = table.cell(r_idx, c_idx)
            cell.width = Cm(col_widths_cm[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=95, bottom=95, left=130, right=130)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.14
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(9.0)
            if c_idx == 0:
                r.bold = True
            r.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph()


def build_word_document(output_path: str):
    doc = Document()

    for section in doc.sections:
        section.top_margin = Cm(2.2)
        section.bottom_margin = Cm(2.2)
        section.left_margin = Cm(2.4)
        section.right_margin = Cm(2.4)

        header = section.header
        p_head = header.paragraphs[0]
        p_head.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_head = p_head.add_run("UNIVERSIDAD AUTÓNOMA DE CHILE · MÁS UNIVERSIDAD")
        r_head.bold = True
        r_head.font.name = "Calibri"
        r_head.font.size = Pt(8.5)
        r_head.font.color.rgb = RGBColor(150, 28, 34)

        footer = section.footer
        p_foot = footer.paragraphs[0]
        p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_foot = p_foot.add_run(
            "Evaluación Sumativa 2 · Arquitectura de Software · Caso 5 — HCE interoperable y telemedicina de urgencia"
        )
        r_foot.font.name = "Calibri"
        r_foot.font.size = Pt(8.5)
        r_foot.font.color.rgb = RGBColor(120, 130, 145)

    # =========================================================================
    # PORTADA
    # =========================================================================
    for _ in range(3):
        doc.add_paragraph()

    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_top = p_top.add_run("ARQUITECTURA DE SOFTWARE")
    r_top.bold = True
    r_top.font.name = "Calibri"
    r_top.font.size = Pt(12)
    r_top.font.color.rgb = RGBColor(45, 55, 72)

    p_unit = doc.add_paragraph()
    p_unit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_unit = p_unit.add_run("Unidad N° 2 — Principios de Arquitectura de Software")
    r_unit.font.name = "Calibri"
    r_unit.font.size = Pt(11)
    r_unit.font.color.rgb = RGBColor(90, 100, 115)

    doc.add_paragraph()

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("Evaluación Sumativa 2")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(22)
    r_title.font.color.rgb = RGBColor(22, 34, 56)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Subsanación de Observaciones, Patrones de Diseño e Implementación de Módulo Funcional")
    r_sub.bold = True
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(30, 41, 59)

    p_case = doc.add_paragraph()
    p_case.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_case = p_case.add_run("Caso 5 — Plataforma de Historia Clínica Electrónica Interoperable y Telemedicina de Urgencia")
    r_case.italic = True
    r_case.font.name = "Calibri"
    r_case.font.size = Pt(11.5)
    r_case.font.color.rgb = RGBColor(60, 72, 88)

    doc.add_paragraph()
    doc.add_paragraph()

    meta_rows = [
        ("Integrantes", "Benjamín Naranjo — Hernán Escobar"),
        ("Carrera", "Ingeniería Civil Informática"),
        ("Institución", "Universidad Autónoma de Chile"),
        ("Asignatura", "Arquitectura de Software"),
        ("Docente", "Cristofher Rojas Rojas"),
        ("Caso asignado", "Caso 5 — HCE interoperable y telemedicina de urgencia"),
        ("Fecha de entrega", "Octubre de 2026"),
    ]
    cover_table = doc.add_table(rows=len(meta_rows), cols=2)
    cover_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(cover_table, color="D1D5DB", sz="4")
    for idx, (k, v) in enumerate(meta_rows):
        c0 = cover_table.cell(idx, 0)
        c1 = cover_table.cell(idx, 1)
        c0.width = Cm(4.8)
        c1.width = Cm(11.6)
        set_cell_background(c0, "F8FAFC")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, top=110, bottom=110, left=150, right=150)
        set_cell_margins(c1, top=110, bottom=110, left=150, right=150)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.font.name = "Calibri"
        r0.font.size = Pt(10)
        r0.font.color.rgb = RGBColor(51, 65, 85)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.bold = True if idx == 0 else False
        r1.font.name = "Calibri"
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_page_break()

    # =========================================================================
    # INTRODUCCIÓN
    # =========================================================================
    add_heading_1(doc, "Introducción")
    add_formatted_paragraph(
        doc,
        "El presente informe desarrolla la Evaluación Sumativa 2 para el Caso 5, correspondiente a un consorcio privado de salud que integra ocho clínicas de alta complejidad, cuarenta y cinco centros de atención ambulatoria y una red nacional de ambulancias. A partir de la retroalimentación recibida en la Evaluación Sumativa 1 (calificada con nota 5,5, obteniendo puntaje máximo 7,0 en Capa de Presentación y Capa de Datos, y observaciones específicas de mejora en el modelado UML de Aplicación, la resolución del Diagrama de Despliegue y la verificación de Antipatrones), el equipo ha subsanado el 100 % de los hallazgos documentales y ha materializado las decisiones arquitectónicas en un módulo de software completamente funcional. El documento incorpora en alta resolución (2400×1550 px) el Diagrama de Casos de Uso UML que faltaba en la primera entrega, el Diagrama de Secuencia UML de urgencia y arbitraje clínico, y el Diagrama de Despliegue Híbrido con nodos, artefactos y puertos explícitos; operacionaliza la detección de antipatrones mediante pruebas automatizadas de aptitud arquitectónica (test_architectural_fitness.py); y demuestra cuatro patrones de diseño (MVVM, Strategy, Observer y Repository), control de acceso RBAC de cuatro roles y encadenamiento criptográfico SHA-256 en código ejecutable.",
    )

    # =========================================================================
    # SECCIÓN 1: ANÁLISIS, RETROALIMENTACIÓN DE LA EVALUACIÓN 1 Y CAMBIOS (10 PTS)
    # =========================================================================
    add_heading_1(doc, "1. Análisis, Retroalimentación de la Evaluación N.º 1 y Justificación de Cambios")
    add_heading_2(doc, "1.1. Matriz de retroalimentación docente de la Evaluación N.º 1 y correcciones aplicadas")
    add_formatted_paragraph(
        doc,
        "En la Evaluación Sumativa 1 el proyecto obtuvo nota 5,5 (32 puntos ponderados), alcanzando el nivel Destacado (7,0) en las Dimensiones 1 (Capa de Presentación: MVVM sobre React/PWA, problemas de usabilidad WCAG 2.2 AAA, cliente offline-first y contraste con Epic Rover) y 3 (Capa de Datos: estrategia store-and-forward, resolución dual CRDT/concurrencia optimista y persistencia híbrida CAP). Sin embargo, el docente Cristofher Rojas Rojas registró cuatro observaciones específicas en las Dimensiones 2, 4, 5 y Presentación. La siguiente matriz detalla cada observación recibida, la corrección exacta incorporada en esta entrega y su justificación técnica:",
    )

    add_styled_data_table(
        doc,
        headers=[
            "Dimensión Evaluada en Entrega 1",
            "Observación Exacta del Docente",
            "Corrección e Incorporación en Evaluación 2",
            "Problema que Resuelve y Evidencia en Documento / Código",
        ],
        rows=[
            [
                "Dimensión 2: Capa de Aplicación y Lógica de Negocio (5 pts -> Meta 7 pts)",
                "«Excelente análisis de microservicios con FastAPI y Python (ADR-03), tabla comparativa exhaustiva de 4 criterios y estrés 10× con caso Zoom/Netflix. Debilidad en modelado UML: El Diagrama de Casos de Uso solo se lista como texto y no se incluyó la imagen, y el diagrama de secuencia presenta resolución muy baja y texto ilegible.»",
                "1) Se construye e inserta el Diagrama de Casos de Uso UML completo en alta resolución (Figura 1), modelando la frontera del sistema, los 4 actores RBAC, los 3 sistemas externos (MQTT, SFU, HSM) y los 9 casos de uso con sus relaciones <<include>> y <<extend>>.\n2) Se rediseña e inserta el Diagrama de Secuencia UML a 2400×1550 px (Figura 2) con tipografía nítida, mostrando los 15 pasos del flujo vertical real.",
                "Elimina la omisión gráfica de la Entrega 1 y garantiza trazabilidad 1 a 1 entre cada Caso de Uso (UC-01 a UC-09), cada mensaje del Diagrama de Secuencia y los métodos reales programados en api_router.py, clinical_service.py, clinical_strategies.py y audit_observer.py."
            ],
            [
                "Dimensión 4: Capa de Infraestructura (5 pts -> Meta 7 pts)",
                "«Justificación exhaustiva de topología híbrida (on-premise + cloud multi-AZ), protocolos especializados (gRPC, FHIR/REST, SRTP, MQTT), seguridad de grado médico (OAuth2/JWT, mTLS, HSM) y 2 riesgos precisos. Debilidad: El Diagrama de Despliegue UML insertado posee una resolución deficiente que vuelve ilegibles sus nodos, artefactos y puertos.»",
                "Se reconstruye desde cero el Diagrama de Despliegue UML Híbrido a 2400×1550 px (Figura 3) y se acompaña de una Tabla de Especificación de Nodos, Artefactos y Puertos de Red, detallando los nodos de borde (Ambulancia, Box Clínico, Consola Teleconsulta), el clúster On-Premise (:8000, :50051, :5432, :8443) y la Nube Multi-AZ (:443, :8883, UDP 10000-20000).",
                "Permite leer con absoluta nitidez cada estereotipo UML (<<device>>, <<execution environment>>, <<isolated security zone>>, <<artifact>>), los artefactos desplegados y los puertos/protocolos exactos que aseguran el SLA de 99,999 % y el aislamiento del Ledger Forense."
            ],
            [
                "Dimensión 5: Antipatrones y Evolución Arquitectónica (3 pts -> Meta 7 pts)",
                "En la Entrega 1 los antipatrones 'The Blob / God Service' y 'Monolito Distribuido' se describieron de forma declarativa, sin evidenciar en código las funciones de aptitud arquitectónica (ArchUnit) ni umbrales ejecutables de desacoplamiento.",
                "1) Se refactoriza el servicio Expediente-Órdenes aplicando los patrones Strategy (clinical_strategies.py), Observer (audit_observer.py) y Repository (ehr_repository.py) para impedir que degenere en un God Service.\n2) Se programa una prueba automatizada de Aptitud Arquitectónica basada en análisis estático AST (tests/test_architectural_fitness.py).",
                "Transforma el control de antipatrones en una puerta de calidad ejecutable en Pytest: el test falla automáticamente si clinical_service.py importa criptografía directa (hashlib), si supera 8 métodos públicos, si existen dependencias cíclicas entre capas o si AuditLedgerRepository define métodos update/delete."
            ],
            [
                "Ajuste Tecnológico hacia MVP Local Ejecutable",
                "Necesidad de comprobar en la práctica la arquitectura propuesta mediante un módulo funcional autocontenido sin exigir 4 servidores de bases de datos externos.",
                "Consolidación del almacenamiento local sobre SQLAlchemy 2.0 ORM con SQLite en modo WAL (compatible con PostgreSQL 16 vía DATABASE_URL), conservando esquemas separados por perfil de consistencia y cola Offline Outbox en React.",
                "Permite ejecutar el flujo vertical completo en cualquier equipo evaluador en segundos, manteniendo intactas las llaves de idempotencia UUID (ADR-02/04), los vectores de versión (ADR-05) y el encadenamiento criptográfico SHA-256 (ADR-03/08)."
            ],
        ],
        col_widths_cm=[3.2, 4.3, 4.5, 4.4],
    )

    add_heading_2(doc, "1.2. Subsanación del Modelado UML de Dominio y Aplicación (Figuras 1 y 2 en Alta Resolución)")
    add_formatted_paragraph(
        doc,
        "Atendiendo directamente la observación de la Dimensión 2 de la Evaluación 1, a continuación se incorporan en alta resolución el Diagrama de Casos de Uso UML (que en la primera entrega solo había quedado enunciado como subtítulo) y el Diagrama de Secuencia UML de Urgencia, Triage Offline-First y Arbitraje Clínico:",
    )

    add_figure_image(
        doc,
        "1_diagrama_casos_de_uso_uml.png",
        "Figura 1 — Diagrama de Casos de Uso UML (Subsanación Evaluación 1, Sección 3.1): 4 actores RBAC, 3 sistemas externos y 9 casos de uso con relaciones <<include>> y <<extend>>.",
    )

    add_figure_image(
        doc,
        "2_diagrama_secuencia_urgencia_uml.png",
        "Figura 2 — Diagrama de Secuencia UML de Alta Resolución (Subsanación Evaluación 1, Sección 3.1): Flujo vertical de autenticación JWT, triage offline-first con UUID, arbitraje ADR-05 y auditoría SHA-256.",
    )

    add_heading_2(doc, "1.3. Subsanación del Diagrama de Despliegue Híbrido con Nodos, Artefactos y Puertos (Figura 3)")
    add_formatted_paragraph(
        doc,
        "Para subsanar la observación de la Dimensión 4 de la Evaluación 1 respecto a la legibilidad de nodos, artefactos y puertos en la topología híbrida (ADR-07 y ADR-08), se presenta en la Figura 3 el Diagrama de Despliegue UML redibujado en alta definición, complementado con la tabla de especificación técnica de cada nodo:",
    )

    add_figure_image(
        doc,
        "3_diagrama_despliegue_hibrido_uml.png",
        "Figura 3 — Diagrama de Despliegue UML en Alta Resolución (Subsanación Evaluación 1, Sección 4.1): Topología híbrida On-Premise + Nube Pública Multi-AZ con artefactos, protocolos y puertos explícitos.",
    )

    add_styled_data_table(
        doc,
        headers=["Nodo de Despliegue UML", "Artefactos Desplegados", "Protocolos y Cifrado", "Puertos de Red y Reglas de Firewall"],
        rows=[
            [
                "<<device / edge node>>\nAmbulancia Móvil 07 (Tablet + Gateway)",
                "hce-urgencia-pwa.bundle.js (React 18 MVVM) + Almacén local IndexedDB/Outbox + Broker MQTT de borde",
                "HTTPS REST FHIR R4 (TLS 1.3), MQTT sobre TLS (QoS 1), SRTP/UDP para videoconsulta",
                "Salida: TCP 443 (API/WSS), TCP 8883 (MQTT TLS), UDP 10000-20000 (Media SRTP)"
            ],
            [
                "<<execution environment>>\nClúster K8s On-Premise (Núcleo Clínico)",
                "expediente-ordenes-service (Python 3.13 + FastAPI + Uvicorn ASGI) + PostgreSQL 16 Líder-Réplica / SQLite WAL",
                "Externo: HTTPS REST FHIR R4.\nInterno: gRPC con mTLS estricto y SQL cifrado AES-256",
                "Entrada API: TCP 443 / 8000.\nInterno gRPC: TCP 50051.\nBase de Datos CP: TCP 5432 (Subred privada)"
            ],
            [
                "<<isolated security zone>>\nSegmento Aislado Auditoría & HSM",
                "forensic-audit-ledger-service + Tabla append-only audit_ledger (Cadena SHA-256) + HSM FIPS 140-3",
                "mTLS exclusivo desde el bus de eventos; credenciales BD sin permisos UPDATE ni DELETE",
                "Entrada exclusiva mTLS: TCP 8443.\nSalida a Internet: BLOQUEADA (0.0.0.0/0 Deny)"
            ],
            [
                "<<cloud environment>>\nNube Pública Multi-AZ (Ráfaga 10×)",
                "Clúster Pasarela Video WebRTC (SFU) + Subtitulado en Vivo + TimescaleDB + MongoDB + Object Storage S3",
                "WebSocket WSS (Señalización), SRTP (Video/Audio), MQTT QoS 1 (Telemetría), S3 HTTPS",
                "TCP 443 (WSS/S3), UDP 3478 (STUN/TURN), UDP 10000-20000 (SRTP), TCP 8883 (MQTT)"
            ],
        ],
        col_widths_cm=[3.8, 4.6, 4.2, 3.8],
    )

    add_heading_2(doc, "1.4. Subsanación de la Dimensión 5: Antipatrones y Funciones de Aptitud Arquitectónica en Código")
    add_formatted_paragraph(
        doc,
        "Para elevar la Dimensión 5 (Antipatrones y Evolución Arquitectónica) al nivel Destacado (7,0), los mecanismos de mitigación y detección temprana propuestos teóricamente en la Evaluación 1 se implementaron como código verificable dentro del repositorio del proyecto:",
    )
    add_formatted_paragraph(
        doc,
        "En lugar de concentrar la clasificación clínica, el cálculo de hashes SHA-256 y las consultas SQL dentro de ClinicalEHRService, se extrajo toda la lógica algorítmica hacia el paquete strategies (clinical_strategies.py), el encadenamiento forense hacia el paquete observers (audit_observer.py) y las consultas transaccionales hacia repositories (ehr_repository.py). De este modo, ClinicalEHRService posee únicamente 5 métodos públicos cohesivos.",
        bold_prefix="1. Mitigación real en código del Antipatrón 1 ('The Blob / God Service' en Expediente-Órdenes): ",
    )
    add_formatted_paragraph(
        doc,
        "Se programó el archivo backend/tests/test_architectural_fitness.py, el cual analiza el Árbol de Sintaxis Abstracta (AST) de Python en cada ejecución de Pytest y verifica automáticamente tres reglas de arquitectura al estilo ArchUnit: (a) clinical_service.py tiene prohibido importar hashlib o ejecutar criptografía directa; (b) ninguna capa interna (strategies, observers, repositories) puede importar módulos de capas superiores (services o routers), garantizando 0 ciclos de dependencia; y (c) AuditLedgerRepository tiene prohibido definir métodos que contengan update, delete o remove.",
        bold_prefix="2. Detección temprana automatizada mediante Funciones de Aptitud Arquitectónica (AST Fitness Functions): ",
    )

    # =========================================================================
    # SECCIÓN 2: DOCUMENTACIÓN DE DECISIONES Y PATRONES DE DISEÑO (25 PTS)
    # =========================================================================
    add_heading_1(doc, "2. Documentación Arquitectónica y Patrones de Diseño")
    add_heading_2(doc, "2.1. Enfoque arquitectónico, frameworks, versiones, responsabilidades y comunicación")
    add_formatted_paragraph(
        doc,
        "La plataforma implementa una Arquitectura Orientada a Servicios de Grano Grueso (DDD) en el backend, comunicada mediante contratos REST/FHIR R4 con una aplicación progresiva (PWA) estructurada bajo el patrón MVVM Offline-First en el frontend. La siguiente tabla especifica rigurosamente los frameworks, lenguajes, versiones, responsabilidades y protocolos de cada componente:",
    )

    add_styled_data_table(
        doc,
        headers=["Capa / Módulo", "Framework y Librerías", "Lenguaje y Versión", "Responsabilidades Técnicas y Protocolos de Comunicación"],
        rows=[
            [
                "Frontend (Interfaz de Usuario PWA)",
                "React ^18.3.1 + Vite ^5.4.10 (Arquitectura MVVM + PWA Manifest)",
                "JavaScript ES2023 / JSX (Node.js v24.11.0, npm 11.6.1)",
                "Renderizado reactivo y responsivo (Desktop, Tablet de Ambulancia y Smartphone), conmutador de Alto Contraste WCAG 2.2 AAA (7:1), máquina de estados del episodio y cola local Transactional Outbox. Comunicación vía HTTP/REST JSON (FHIR R4)."
            ],
            [
                "Backend (Lógica de Negocio y Seguridad)",
                "FastAPI >= 0.115.0 + Uvicorn ASGI >= 0.32.0 + Pydantic v2 >= 2.9.2 + PyJWT >= 2.9.0",
                "Python 3.13.9",
                "Exposición del servicio cohesivo Expediente-Órdenes, validación estructural y fisiológica declarativa de recursos FHIR R4, autenticación OAuth2/JWT (HS256, TTL 15m), autorización RBAC de 4 roles y orquestación de los patrones Strategy y Observer."
            ],
            [
                "Persistencia (Acceso a Datos Políglota/Híbrido)",
                "SQLAlchemy 2.0 ORM (>= 2.0.35) sobre SQLite 3 (Modo WAL) / PostgreSQL 16",
                "Python 3.13.9 / SQL Estándar ACID",
                "Encapsulación del acceso a datos mediante el Patrón Repository (PatientEHRRepository, AuditLedgerRepository, UserRepository). Asegura deduplicación por llave UUID, control de concurrencia optimista por columna version y cadena inmutable SHA-256."
            ],
            [
                "Pruebas y Aptitud Arquitectónica",
                "Pytest >= 8.3.3 + HTTPX TestClient >= 0.27.2 + Python AST",
                "Python 3.13.9",
                "Ejecución de 5 suites automatizadas (test_architecture_and_patterns.py y test_architectural_fitness.py) que verifican RBAC, idempotencia, arbitraje ADR-05, cadena SHA-256 y ausencia de antipatrones en 1,35 segundos."
            ],
        ],
        col_widths_cm=[3.2, 3.8, 3.0, 6.4],
    )

    add_heading_2(doc, "2.2. Aplicación demostrable de 4 Patrones de Diseño en Diseño y Código Fuente (Figura 4)")
    add_formatted_paragraph(
        doc,
        "Superando el mínimo de dos patrones requerido por la rúbrica, se diseñaron e implementaron cuatro patrones de diseño de software que resuelven problemas técnicos específicos del Caso 5 y cuya estructura de clases e interacciones se documenta en la Figura 4:",
    )

    add_figure_image(
        doc,
        "4_diagrama_patrones_implementados.png",
        "Figura 4 — Diagrama de Clases y Componentes UML de los 4 Patrones de Diseño implementados en el código fuente: MVVM (Frontend), Strategy, Observer y Repository (Backend).",
    )

    add_styled_data_table(
        doc,
        headers=["Patrón de Diseño", "Problema Exacto que Resuelve", "Clases e Interfaces en el Diseño", "Evidencia Exacta en el Código Fuente Implementado"],
        rows=[
            [
                "1. Strategy\n(Comportamiento)",
                "Separa tres familias de algoritmos clínicos críticos que evolucionan independientemente del transporte HTTP: (a) clasificación de severidad de triage ESI según signos vitales, (b) resolución dual de sincronización CRDT vs Concurrencia Optimista (ADR-05), y (c) verificación cruzada de alergias por grupo farmacológico (ADR-03).",
                "- ClinicalTriageStrategy (ABC)\n- EmergencySeverityIndexStrategy\n- SyncResolutionStrategy (ABC)\n- AppendOnlyCRDTGSetStrategy\n- OptimisticConcurrencyClinicalArbitrationStrategy\n- DrugSafetyGuardStrategy",
                "Archivo: backend/app/strategies/clinical_strategies.py\nInyectado en ClinicalEHRService (clinical_service.py). Evalúa hipoxemia (SpO2 < 90% -> ESI-1 Crítico), detecta colisiones expected_version != server_version y bloquea Amoxicilina en alérgicos a Penicilina."
            ],
            [
                "2. Observer\n(Comportamiento / Event-Driven)",
                "Permite que cada lectura, escritura, conflicto o bloqueo de seguridad genere automáticamente un bloque encadenado con SHA-256 en el Ledger Forense y despache alertas críticas sin acoplar el servicio Expediente-Órdenes al motor criptográfico (evitando el Antipatrón God Service).",
                "- ClinicalDomainEventBus (Subject)\n- ClinicalEventObserver (ABC)\n- ForensicAuditLedgerObserver\n- CriticalTelemetryAlertObserver\n- ClinicalDomainEvent (DTO)",
                "Archivo: backend/app/observers/audit_observer.py\nCada operación invoca clinical_event_bus.publish(db, event). ForensicAuditLedgerObserver calcula hashlib.sha256(prev_hash + payload) e inserta en audit_ledger."
            ],
            [
                "3. Repository\n(Arquitectónico / Persistencia)",
                "Desacopla el servicio de dominio respecto de las consultas SQLAlchemy, centraliza la deduplicación por llave de idempotencia UUID de la cola Store-and-Forward (ADR-02/04) y garantiza estructuralmente que el Ledger Forense sea solo Append-Only.",
                "- PatientEHRRepository\n- AuditLedgerRepository\n- UserRepository",
                "Archivo: backend/app/repositories/ehr_repository.py\nPatientEHRRepository verifica get_vital_sign_by_idempotency_key(UUID) y gestiona sync_conflicts. AuditLedgerRepository carece de update/delete e implementa verify_chain_integrity()."
            ],
            [
                "4. MVVM\n(Presentación Reactiva ADR-01)",
                "Desacopla la interfaz gráfica de la máquina de estados del episodio offline-first, las reglas de despliegue de alertas semánticas y el drenaje automático de la cola Transactional Outbox al atravesar túneles sin cobertura.",
                "- View: App.jsx\n- ViewModel: useClinicalViewModel.js\n- Model: clinicalApi.js",
                "Archivos en frontend/src/:\nEl ViewModel administra session, episodeState, outboxQueue, highContrastAAA y drainOutboxQueue(), mientras que App.jsx solo enlaza datos declarativamente."
            ],
        ],
        col_widths_cm=[2.8, 4.4, 4.2, 5.0],
    )

    # =========================================================================
    # SECCIÓN 3: IMPLEMENTACIÓN DEL MÓDULO FUNCIONAL (35 PTS)
    # =========================================================================
    add_heading_1(doc, "3. Implementación del Módulo Funcional")
    add_heading_2(doc, "3.1. Ejecución funcional punta a punta y persistencia real en base de datos")
    add_formatted_paragraph(
        doc,
        "El módulo funcional implementado en 'E:\\Proyectos\\arquitectura de software' es una aplicación web full-stack completamente operativa y responsiva (adaptable a celulares, tablets ruggerizadas de ambulancia y monitores clínicos de escritorio) que reproduce los tres mockups diseñados en la Evaluación 1 más la consola de auditoría forense, ejecutando cuatro flujos verticales completos con persistencia efectiva en base de datos:",
    )
    add_formatted_paragraph(
        doc,
        "El Paramédico (paramedico.soto) ingresa frecuencia cardíaca, SpO2, presión arterial, temperatura y puntaje Glasgow para el paciente Carlos Mendoza Silva (68 años). Si activa el botón 'OFFLINE (Túnel)', el ViewModel firma la observación con una clave idempotency_key UUID y la guarda en la cola local Outbox (estado ENCOLADO_OUTBOX). Al volver a 'ONLINE', drainOutboxQueue() transmite la transacción a POST /api/v1/fhir/patients/1/vital-signs; el backend comprueba que el UUID no esté duplicado, ejecuta EmergencySeverityIndexStrategy (clasificando ESI-1 Crítico si SpO2 < 90 %), almacena el registro en la tabla vital_sign_observations y encadena un nuevo bloque SHA-256 en audit_ledger.",
        bold_prefix="1. Flujo Vertical de Triage Prehospitalario y Cola Offline Store-and-Forward: ",
    )
    add_formatted_paragraph(
        doc,
        "En la vista 'Ficha Clínica FHIR R4 & Arbitraje ADR-05', cualquier actualización a un campo mutable (allergies, active_diagnosis, treatment_plan) envía el vector expected_version a PUT /api/v1/fhir/patients/1/mutable-fields. Si una ambulancia que estuvo sin señal envía la versión v1 cuando el hospital ya actualizó la ficha a v2, OptimisticConcurrencyClinicalArbitrationStrategy congela el cambio, lo inserta en la tabla sync_conflicts con estado PENDIENTE y bloquea la emisión de recetas farmacológicas hasta que el Médico de Urgencia (dr.valdivia) o Teleconsultor (dra.herrera) firme la resolución en POST /api/v1/fhir/conflicts/{id}/resolve.",
        bold_prefix="2. Flujo Vertical de Concurrencia Optimista y Arbitraje Clínico Manual (ADR-05): ",
    )
    add_formatted_paragraph(
        doc,
        "En la vista 'Teleconsulta SFU & Órdenes Médicas', el médico emite prescripciones o directivas remotas en POST /api/v1/fhir/patients/1/orders que actualizan instantáneamente el canal de Subtitulado Clínico en Vivo. Antes de guardar en medical_orders, DrugSafetyGuardStrategy cruza el fármaco con las alergias del expediente: al intentar prescribir Amoxicilina a Carlos Mendoza (alérgico a Penicilina), la operación es rechazada transaccionalmente con HTTP 422 y registrada en el Ledger Forense.",
        bold_prefix="3. Flujo Vertical de Teleconsulta y Prescripción con Guardián de Alergias (ADR-03): ",
    )
    add_formatted_paragraph(
        doc,
        "En la vista 'Ledger Forense SHA-256', el Oficial de Privacidad (auditor.hipaa) ejecuta GET /api/v1/audit/verify-chain. AuditLedgerRepository recalcula el hash SHA-256 de cada bloque desde el bloque Génesis (#1) hasta el último evento registrado, confirmando matemáticamente en pantalla que la cadena es íntegra (0 adulteraciones).",
        bold_prefix="4. Flujo Vertical de Verificación Matemática de la Cadena Forense SHA-256: ",
    )

    add_heading_2(doc, "3.2. Login obligatorio con 4 roles de usuario (RBAC), validaciones y manejo de excepciones")
    add_styled_data_table(
        doc,
        headers=["Usuario Institucional", "Rol RBAC", "Unidad Operativa", "Permisos Autorizados y Bloqueos de Seguridad (HTTP 403)"],
        rows=[
            [
                "paramedico.soto\n(Clave: urgencia2026)",
                "PARAMEDICO",
                "Ambulancia Móvil 07 — Ruta Sur (Tablet Ruggerizada)",
                "Permite leer HCE, registrar signos vitales/triage, operar cola Offline Outbox y reportar alergias en terreno.\nBloqueado con HTTP 403 Forbidden si intenta prescribir medicamentos o resolver conflictos de arbitraje."
            ],
            [
                "dr.valdivia\n(Clave: urgencia2026)",
                "MEDICO_URGENCIA",
                "Clínica Alta Complejidad Central — Box Reanimación 01",
                "Acceso clínico completo: lectura/escritura de HCE, triage, prescripción de órdenes médicas, resolución manual de la Cola de Arbitraje Clínico (ADR-05) e inspección del Ledger Forense."
            ],
            [
                "dra.herrera\n(Clave: urgencia2026)",
                "MEDICO_TELECONSULTOR",
                "Centro Comando Telemedicina Red Nacional (Sala SFU-04)",
                "Conducción de Teleconsulta de Urgencia, emisión de directivas remotas con subtitulado en vivo, prescripción farmacológica y resolución de conflictos ADR-05."
            ],
            [
                "auditor.hipaa\n(Clave: urgencia2026)",
                "AUDITOR_FORENSE",
                "Unidad de Cumplimiento Normativo y Auditoría HIPAA",
                "Inspección de trazabilidad de accesos PHI y verificación criptográfica de la cadena SHA-256.\nBloqueado con HTTP 403 Forbidden si intenta registrar signos vitales, modificar fichas o emitir órdenes médicas."
            ],
        ],
        col_widths_cm=[3.2, 3.2, 4.2, 5.8],
    )

    add_formatted_paragraph(
        doc,
        "El sistema valida todas las entradas tanto en el cliente como en el borde del servidor mediante Pydantic v2 (fhir_schemas.py), restringiendo signos vitales a rangos fisiológicos posibles (FC 20–260 lpm, SpO2 40–100 %, PA Sistólica 40–300 mmHg, Temperatura 28–44 °C, Glasgow 3–15) e incorporando un validador cruzado que rechaza presiones arteriales incoherentes donde la presión diastólica sea mayor o igual a la sistólica (ej. 85/110 mmHg). El manejador global custom_validation_exception_handler intercepta cualquier error de validación o de negocio (HTTP 401, 403, 404, 409, 422) y retorna respuestas JSON estructuradas que se despliegan en el banner clínico de la interfaz sin interrumpir el servicio.",
    )

    # =========================================================================
    # SECCIÓN 4: EVALUACIÓN DE ATRIBUTOS DE CALIDAD (15 PTS)
    # =========================================================================
    add_heading_1(doc, "4. Evaluación y Verificación de Atributos de Calidad")
    add_formatted_paragraph(
        doc,
        "Se analizan cuatro atributos de calidad esenciales del Caso 5, conectando cada uno con una decisión arquitectónica concreta, su evidencia en la solución implementada y la prueba automatizada o indicador cuantitativo que verifica su cumplimiento:",
    )

    add_styled_data_table(
        doc,
        headers=["Atributo de Calidad", "Relevancia para el Proyecto", "Decisión Arquitectónica y Evidencia en Código", "Prueba Automatizada / Indicador Objetivo de Verificación"],
        rows=[
            [
                "1. Seguridad e Integridad Forense (No Repudio HIPAA)",
                "El acceso a expedientes clínicos exige control estricto por estamento profesional y garantía criptográfica de que ningún evento auditado pueda ser alterado ni borrado.",
                "ADR-03 y ADR-08: Autenticación JWT (HS256, 15m) + Guardián RBAC require_roles() en api_router.py + Patrón Observer (ForensicAuditLedgerObserver) que encadena cada bloque con SHA-256 en audit_ledger.",
                "Pruebas Pytest test_1_rbac_authentication_and_authorization y test_4_adr03_drug_allergy_contraindication_and_audit_ledger_chain:\n- Métrica 1: 100 % de peticiones sin privilegio rechazadas con HTTP 401/403.\n- Métrica 2: verify_chain_integrity() retorna is_valid=True con 0 adulteraciones sobre el 100 % de los bloques."
            ],
            [
                "2. Disponibilidad y Resiliencia Offline-First",
                "Las ambulancias sufren cortes de red al cruzar túneles urbanos o zonas rurales; perder un triage o duplicar una observación por reintento de red compromete la seguridad del paciente.",
                "ADR-02, ADR-04 y ADR-05: Cola Transactional Outbox local en clinicalApi.js + Deduplicación por llave idempotency_key UUID en PatientEHRRepository + Concurrencia Optimista con Cola de Arbitraje.",
                "Pruebas Pytest test_2_strategy_pattern_triage_and_idempotency y test_3_adr05_optimistic_concurrency_and_clinical_arbitration:\n- Métrica 1: Reenviar N veces el mismo UUID produce exactamente 1 registro persistido.\n- Métrica 2: 0 % de sobrescrituras silenciosas ante conflicto de versión (100 % desviadas a arbitraje médico)."
            ],
            [
                "3. Mantenibilidad y Evolución Libre de Antipatrones",
                "Un equipo reducido debe evolucionar las reglas de triage y farmacovigilancia sin que el servicio Expediente-Órdenes degenere en un God Service ni introduzca acoplamientos cíclicos.",
                "ADR-01, ADR-03 y Sección 5: Separación MVVM en frontend y aplicación de Strategy, Observer y Repository en backend, gobernados por pruebas AST de aptitud arquitectónica.",
                "Prueba Pytest test_5_architectural_fitness_functions_antipattern_prevention (test_architectural_fitness.py):\n- Métrica 1: 0 importaciones criptográficas en clinical_service.py y <= 8 métodos públicos.\n- Métrica 2: 0 ciclos de dependencia entre capas y 5/5 pruebas integrales aprobadas en 1,35 segundos."
            ],
            [
                "4. Usabilidad, Responsividad y Accesibilidad Operativa",
                "El personal prehospitalario opera tablets y celulares en movimiento con guantes de nitrilo, bajo luz solar directa (encandilamiento) y con ruido de sirena.",
                "ADR-01 y Sección 2.2: Diseño responsivo móvil/tablet + Conmutador de Alto Contraste WCAG 2.2 AAA (.theme-high-contrast-aaa) + Botones táctiles >= 48px + Subtitulado en vivo en teleconsulta.",
                "Verificación en clinical.css y App.jsx:\n- Métrica 1: Relación de contraste texto blanco/amarillo (#FFFFFF / #FFFF00) sobre fondo negro (#000000) de 21:1 y 19,56:1 (supera ampliamente el umbral AAA de 7:1).\n- Métrica 2: 100 % de controles táctiles con altura >= 48px (52px en vista móvil <= 640px)."
            ],
        ],
        col_widths_cm=[3.0, 3.8, 4.6, 5.0],
    )

    # =========================================================================
    # SECCIÓN 5: REGISTRO DE DECISIONES ARQUITECTÓNICAS - ADRs (15 PTS)
    # =========================================================================
    add_heading_1(doc, "5. Registro de Decisiones Arquitectónicas (ADR)")
    add_formatted_paragraph(
        doc,
        "Se documentan formalmente seis Decisiones Arquitectónicas (ADR-01 a ADR-06) que rigen tanto la arquitectura general del Caso 5 como el módulo funcional implementado:",
    )

    add_adr_table(
        doc,
        adr_title="ADR-01 — Adopción de MVVM sobre ReactJS/PWA como patrón de presentación transversal",
        decision="Se adopta el patrón Model–View–ViewModel (MVVM) implementado sobre React 18 bajo el modelo de Progressive Web Application (PWA) responsiva, concentrando el estado observable, la máquina de estados del episodio y las reglas de accesibilidad en el ViewModel (useClinicalViewModel.js) y descartando MVC.",
        contexto="La capa de presentación debe ejecutarse en terminales clínicas fijas, tablets ruggerizadas en ambulancias sujetas a pérdida recurrente de señal celular y dispositivos móviles de respuesta rápida. Una fracción sustantiva del estado de la interfaz proviene de eventos asíncronos (telemetría continua, transiciones de red en túneles, alertas de conflicto de versión y subtitulado en vivo).",
        alternativas="1) Patrón MVC tradicional (descartado porque exige que el controlador actualice imperativamente la vista ante cada evento asíncrono externo, generando estados visuales inconsistentes).\n2) Aplicaciones nativas separadas por sistema operativo al estilo Epic Haiku/Canto/Rover (descartadas por triplicar el costo de mantenimiento de las reglas clínicas).",
        razon="El enlace de datos reactivo del ViewModel propaga automáticamente las alertas clínicas a la vista sin manipulación imperativa del DOM, permite probar la lógica de presentación sin instanciar interfaz gráfica y reutiliza el mismo Model y ViewModel entre ambulancia, celular y hospital.",
        tradeoff="Introduce una capa de indirección adicional en pantallas simples y el riesgo estructural de concentrar demasiada lógica en un 'God ViewModel', mitigado aislando el transporte HTTP y la cola Outbox en el módulo de modelo clinicalApi.js.",
    )

    add_adr_table(
        doc,
        adr_title="ADR-02 — Cliente Offline-First con Cola Transactional Outbox (Store-and-Forward) e Idempotencia UUID",
        decision="Se implementa un mecanismo Offline-First con patrón Store-and-Forward (integrando los ADR-02 y ADR-04 de la Evaluación 1): toda operación registrada sin cobertura se firma localmente con una clave idempotency_key UUID v4 y se almacena en una cola Transactional Outbox antes de transmitirse, drenándose automáticamente al restablecer la red.",
        contexto="Durante un traslado de urgencia, la ambulancia atraviesa túneles urbanos, zonas periféricas o sótanos hospitalarios sin cobertura celular. El personal no puede detener el registro de signos vitales ni arriesgarse a que un reintento automático de red tras un timeout duplique un evento clínico.",
        alternativas="1) Cliente delgado puramente conectado con reintentos HTTP simples (descartado porque bloquea la pantalla ante caídas de red y pierde datos si la tablet se reinicia).\n2) Encolamiento local sin llave de idempotencia generada en el cliente (descartado porque reintentar tras una pérdida de ACK duplicaría registros clínicos en el servidor).",
        razon="Garantiza que ningún dato confirmado en pantalla se pierda por corte de enlace y convierte la entrega 'al menos una vez' (at-least-once) de la red móvil en una persistencia 'exactamente una vez efectiva' gracias al índice único idempotency_key verificado en PatientEHRRepository.",
        tradeoff="Exige mantener una máquina de estados explícita del episodio en el cliente (BORRADOR -> ENCOLADO_OUTBOX -> TRANSMITIENDO -> CONFIRMADO_EN_SERVIDOR) y comunicar permanentemente en la interfaz el número de transacciones pendientes de sincronización.",
    )

    add_adr_table(
        doc,
        adr_title="ADR-03 — Microservicios de grano grueso en Python/FastAPI con cohesión en el par Expediente–Órdenes",
        decision="Se adopta una arquitectura de microservicios de grano grueso alineados a subdominios DDD sobre Python 3.13 y FastAPI (ASGI), manteniendo deliberadamente unidos en un único servicio cohesivo el Expediente Clínico y las Órdenes Médicas, y separando la pasarela de video SFU, la ingesta de telemetría y el servicio de auditoría.",
        contexto="El sistema exige simultáneamente 99,999 % de disponibilidad en el núcleo asistencial, escalado elástico independiente para el video de telemedicina, aislamiento normativo del registro de auditoría e invariantes de seguridad inmediata al prescribir medicamentos.",
        alternativas="1) Monolito modular único (descartado porque una fuga de memoria o saturación de CPU en la transcodificación de video o procesamiento DICOM derribaría el registro de urgencias).\n2) Microservicios de grano fino separando Pacientes, Alergias y Órdenes en procesos distintos (descartado porque introduce consistencia eventual entre el registro de una alergia y la validación de una receta médica).",
        razon="Mantener unidos Expediente y Órdenes permite que DrugSafetyGuardStrategy valide transaccionalmente (ACID) que ningún fármaco prescrito colisione con las alergias activas del paciente ni se emita mientras exista un conflicto de alergias pendiente de arbitraje. FastAPI aporta ejecución asíncrona de baja latencia y validación declarativa FHIR R4 mediante Pydantic v2.",
        tradeoff="El servicio Expediente–Órdenes nace con mayor amplitud inicial, exponiéndolo al Antipatrón 'The Blob / God Service'; este riesgo se mitiga extrayendo las reglas a objetos Strategy, la auditoría a un Observer y verificando el tamaño de la clase con test_architectural_fitness.py.",
    )

    add_adr_table(
        doc,
        adr_title="ADR-04 — Estrategia dual de sincronización: CRDT G-Set para series append-only y Concurrencia Optimista con Arbitraje Clínico para campos mutables",
        decision="Los datos append-only (signos vitales, telemetría, auditoría) se fusionan automáticamente como estructuras CRDT G-Set idempotentes. Los campos mutables (alergias, diagnóstico activo, plan de tratamiento) se protegen con vectores de versión (expected_version): ante colisión, la escritura se desvía a una Cola de Arbitraje Clínico manual (ADR-05 de la Evaluación 1).",
        contexto="Dos nodos —la ambulancia desconectada en ruta y la clínica de destino— pueden modificar concurrentemente la ficha del mismo paciente (por ejemplo, el paramédico agrega una alergia a Látex reportada en terreno mientras el hospital actualiza las alergias desde antecedentes digitalizados).",
        alternativas="1) Regla automática 'Última Escritura Gana' (Last-Write-Wins por timestamp) para todo el expediente (descartada porque sobrescribiría silenciosamente una alergia recién descubierta).\n2) Bloqueo pesimista distribuido (descartado por ser técnicamente inviable cuando las ambulancias operan sin conexión).",
        razon="El costo clínico de un conflicto no es homogéneo: en series de signos vitales el orden de llegada no invalida las mediciones previas (conmutatividad CRDT), pero en la lista de alergias una fusión automática ciega pone en riesgo vital al paciente. El desvío a la tabla sync_conflicts preserva ambas versiones en pugna hasta la resolución médica auditada.",
        tradeoff="Introduce latencia humana en la consolidación definitiva del campo en conflicto y bloquea preventivamente las prescripciones farmacológicas (HTTP 409) mientras exista un arbitraje de alergias pendiente.",
    )

    add_adr_table(
        doc,
        adr_title="ADR-05 — Persistencia híbrida desacoplada mediante el Patrón Repository sobre SQLAlchemy 2.0",
        decision="Se encapsula la totalidad del acceso a datos detrás del Patrón Repository (PatientEHRRepository, AuditLedgerRepository y UserRepository) sobre SQLAlchemy 2.0 ORM, ejecutándose sobre SQLite en modo WAL para el módulo funcional autónomo y PostgreSQL 16 para el entorno productivo.",
        contexto="La capa de aplicación debe aplicar reglas de dominio clínico y garantías diferenciadas (transaccionalidad CP en expediente/órdenes, ingesta idempotente en observaciones e inmutabilidad en auditoría) sin acoplarse a sentencias SQL específicas ni dificultar las pruebas automatizadas.",
        alternativas="1) Invocar consultas del ORM directamente dentro de los controladores FastAPI (descartado por violar la separación de capas y dificultar la sustitución en pruebas).\n2) Utilizar un único almacén documental sin esquema para todo el sistema (descartado por carecer de integridad referencial y transacciones ACID para órdenes médicas).",
        razon="El Patrón Repository permite intercambiar transparentemente la base de datos por una instancia en memoria durante la ejecución de Pytest (completando 5 pruebas integrales en 1,35 segundos) y restringe estructuralmente la interfaz de AuditLedgerRepository para que no existan métodos de modificación ni borrado.",
        tradeoff="Requiere mantener mapeos explícitos entre los modelos ORM de persistencia (domain.py) y los esquemas de transferencia FHIR R4 (fhir_schemas.py).",
    )

    add_adr_table(
        doc,
        adr_title="ADR-06 — Seguridad RBAC con JWT de vida corta y Ledger Forense encadenado criptográficamente con SHA-256 mediante Patrón Observer",
        decision="Se implementa autenticación OAuth2 con tokens JWT firmados (HS256, TTL 15 minutos), autorización declarativa RBAC de cuatro roles y un Ledger de Auditoría Forense alimentado por el Patrón Observer donde cada registro encadena criptográficamente el hash SHA-256 del evento anterior (prev_hash -> current_hash).",
        contexto="El cumplimiento de HIPAA Security Rule y la trazabilidad médico-legal exigen restringir las operaciones según el estamento profesional y demostrar ante un auditor externo que el historial de accesos y decisiones clínicas no ha sido adulterado ni siquiera a nivel de base de datos.",
        alternativas="1) Sesiones de servidor basadas en cookies en memoria (descartadas por no escalar horizontalmente entre microservicios ni operar con clientes móviles desconectados).\n2) Bitácora de auditoría en tabla SQL convencional sin encadenamiento de hashes (descartada porque un administrador con acceso al motor podría modificar o borrar filas sin dejar evidencia matemática).",
        razon="La combinación de JWT sin estado con el encadenamiento SHA-256 convierte la inmutabilidad en una propiedad matemáticamente verificable mediante el algoritmo AuditLedgerRepository.verify_chain_integrity(), que recalcula toda la cadena desde el bloque Génesis en cada inspección del Oficial de Privacidad.",
        tradeoff="El cálculo y encadenamiento secuencial del hash previo impone un orden estricto de inserción en el ledger, lo que a escala nacional se resuelve particionando la cadena por sede y día con anclaje periódico de raíces.",
    )

    # =========================================================================
    # SECCIÓN 6: CONCLUSIONES Y BIBLIOGRAFÍA
    # =========================================================================
    add_heading_1(doc, "6. Conclusiones")
    add_formatted_paragraph(
        doc,
        "El desarrollo de esta Evaluación Sumativa 2 permitió cerrar el ciclo arquitectónico completo del Caso 5: en primer lugar, se subsanaron rigurosamente todas las observaciones formuladas en la Evaluación 1 mediante la incorporación en alta definición del Diagrama de Casos de Uso UML (Figura 1), el Diagrama de Secuencia UML (Figura 2) y el Diagrama de Despliegue Híbrido con nodos, artefactos y puertos explícitos (Figura 3), además de transformar la prevención de antipatrones en funciones de aptitud arquitectónica verificables automáticamente (test_architectural_fitness.py). En segundo lugar, la construcción del módulo funcional demostró en la práctica que el patrón MVVM Offline-First en React junto con la aplicación conjunta de los patrones Strategy, Observer y Repository en FastAPI resuelven eficazmente la atención de urgencia en ambulancias sin cobertura, el bloqueo transaccional de prescripciones contraindicadas por alergia (ADR-03), el arbitraje médico ante conflictos de sincronización (ADR-05) y la inmutabilidad forense SHA-256 exigida por HIPAA.",
    )

    add_heading_1(doc, "7. Bibliografía y Referencias")
    refs = [
        "Brewer, E. A. (2000). Towards Robust Distributed Systems (conferencia PODC, presentación del teorema CAP). ACM Symposium on Principles of Distributed Computing.",
        "Evans, E. (2003). Domain-Driven Design: Tackling Complexity in the Heart of Software. Addison-Wesley Professional.",
        "Fielding, R. T. (2000). Architectural Styles and the Design of Network-based Software Architectures (tesis doctoral, capítulo sobre REST). University of California, Irvine.",
        "Ford, N., Parsons, R., y Kua, P. (2017). Building Evolutionary Architectures: Support Constant Change (Architectural Fitness Functions). O'Reilly Media.",
        "Fowler, M. (2002). Patterns of Enterprise Application Architecture (Patrones Repository y Optimistic Offline Lock). Addison-Wesley.",
        "Gamma, E., Helm, R., Johnson, R., y Vlissides, J. (1994). Design Patterns: Elements of Reusable Object-Oriented Software (Patrones Strategy y Observer). Addison-Wesley.",
        "HL7 International. (2024). FHIR R4 — Fast Healthcare Interoperability Resources, Release 4. https://hl7.org/fhir/",
        "Kleppmann, M. (2017). Designing Data-Intensive Applications. O'Reilly Media.",
        "Newman, S. (2021). Building Microservices: Designing Fine-Grained Systems (2.ª ed.). O'Reilly Media.",
        "Shapiro, M., Preguiça, N., Baquero, C., y Zawirski, M. (2011). Conflict-Free Replicated Data Types. INRIA — Rapport de recherche n.º 7687.",
        "U.S. Department of Health and Human Services. HIPAA — Health Insurance Portability and Accountability Act, Security Rule. https://www.hhs.gov/hipaa/",
        "World Wide Web Consortium (W3C). (2023). Web Content Accessibility Guidelines (WCAG) 2.2. https://www.w3.org/WAI/standards-guidelines/wcag/",
    ]
    for ref in refs:
        add_formatted_paragraph(doc, f"• {ref}", size=9.6, space_after=4, align=WD_ALIGN_PARAGRAPH.LEFT)

    # =========================================================================
    # ANEXO DE DEFENSA TÉCNICA PARA SUBIR PRESENTACIÓN A 7.0
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "Anexo: Guía de Defensa Técnica y Preguntas Frecuentes del Docente")
    add_formatted_paragraph(
        doc,
        "Atendiendo la observación de la Evaluación 1 sobre la Presentación del Proyecto («En general bien, falta pulir aspectos más técnicos de la presentación, como mejor dominio del tema, y seguridad en respuestas»), se incluye esta guía rápida de defensa individual con las respuestas técnicas exactas vinculadas al código fuente:",
    )

    add_styled_data_table(
        doc,
        headers=["Pregunta Probable del Docente en la Defensa", "Respuesta Técnica Segura y Precisa (Con Evidencia en el Código)"],
        rows=[
            [
                "1. ¿Cómo corrigieron las observaciones de la Evaluación 1 (diagramas UML ilegibles y antipatrones)?",
                "Generamos los 4 diagramas UML en alta resolución (2400×1550 px): incluimos el Diagrama de Casos de Uso con los 4 actores RBAC y relaciones <<include>>/<<extend>>, redibujamos el Diagrama de Secuencia con los 15 pasos reales de los métodos del código, detallamos artefactos y puertos TCP/UDP en el Diagrama de Despliegue Híbrido, y programamos funciones de aptitud arquitectónica con análisis estático AST en test_architectural_fitness.py para bloquear los antipatrones God Service y acoplamiento cíclico."
            ],
            [
                "2. ¿Dónde están aplicados exactamente los patrones de diseño en su código y por qué eligieron esos?",
                "Implementamos 4 patrones: 1) Strategy en clinical_strategies.py para desacoplar el cálculo de Triage ESI (EmergencySeverityIndexStrategy), la decisión de concurrencia optimista ADR-05 y el bloqueo de alergias ADR-03; 2) Observer en audit_observer.py (ClinicalDomainEventBus y ForensicAuditLedgerObserver) para que la auditoría SHA-256 no contamine el servicio clínico; 3) Repository en ehr_repository.py para encapsular SQLAlchemy y la deduplicación por UUID; y 4) MVVM en el frontend React (useClinicalViewModel.js)."
            ],
            [
                "3. ¿Cómo evitan que una ambulancia que sale de un túnel duplique un signo vital o sobrescriba una alergia actualizada en el hospital?",
                "Aplicamos la estrategia dual del ADR-02, ADR-04 y ADR-05: para signos vitales (append-only), la ambulancia genera un idempotency_key UUID antes de guardar en la cola Outbox local (clinicalApi.js); al sincronizar, PatientEHRRepository verifica ese índice único e ignora reintentos duplicados. Para campos mutables (como alergias), enviamos expected_version: si no coincide con la versión actual del servidor, OptimisticConcurrencyClinicalArbitrationStrategy congela el cambio en la tabla sync_conflicts para arbitraje médico manual."
            ],
            [
                "4. ¿Cómo garantizan que el registro de auditoría sea realmente inmutable y cumpla con HIPAA?",
                "Por diseño arquitectónico en tres niveles: primero, AuditLedgerRepository carece de métodos update() o delete() (verificado automáticamente por test_architectural_fitness.py); segundo, cada registro almacena el hash SHA-256 del evento previo (prev_hash) y calcula su propio current_hash sobre todos los campos del evento; tercero, el endpoint GET /api/v1/audit/verify-chain recalcula toda la cadena desde el bloque Génesis y detecta cualquier alteración de un solo bit."
            ],
        ],
        col_widths_cm=[5.2, 11.2],
    )

    doc.save(output_path)
    print(f"Documento Word actualizado exitosamente en: {output_path}")


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else r"E:\Proyectos\arquitectura de software\Evaluacion_Sumativa_2_Caso5_HCE_Urgencia.docx"
    build_word_document(out_file)
