"""
Generador de Diagramas UML de Alta Resolución (300 DPI) para corregir las observaciones de la Evaluación 1:
1. Diagrama de Casos de Uso UML (que faltó / quedó cortado en la Evaluación 1).
2. Diagrama de Secuencia UML de Urgencia, Triage Offline-First y Arbitraje ADR-05 (legible a 300 DPI).
3. Diagrama de Componentes y Clases de Patrones (MVVM + Strategy + Observer + Repository).
4. Diagrama de Despliegue UML — Topología Híbrida con Nodos, Artefactos y Puertos explícitos (legible a 300 DPI).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_DIR = r"E:\Proyectos\arquitectura de software\diagramas_uml"
os.makedirs(OUT_DIR, exist_ok=True)


def draw_box(ax, x, y, w, h, title, body_lines=None, bg="#F8FAFC", border="#1E3A8A", title_bg=None, title_color="#0F172A", fontsize=9.5, body_fontsize=8.5):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.6,
        edgecolor=border,
        facecolor=bg,
        zorder=2,
    )
    ax.add_patch(box)

    if title_bg:
        header_h = min(0.055, h * 0.34)
        hdr = FancyBboxPatch(
            (x, y + h - header_h), w, header_h,
            boxstyle="round,pad=0.008,rounding_size=0.015",
            linewidth=1.2,
            edgecolor=border,
            facecolor=title_bg,
            zorder=3,
        )
        ax.add_patch(hdr)
        ax.text(
            x + w / 2, y + h - header_h / 2,
            title,
            ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=title_color,
            zorder=4,
        )
        content_top = y + h - header_h - 0.015
    else:
        ax.text(
            x + w / 2, y + (h * 0.72 if body_lines else h / 2),
            title,
            ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=title_color,
            zorder=4,
        )
        content_top = y + h * 0.50

    if body_lines:
        text_str = "\n".join(body_lines)
        ax.text(
            x + w / 2, (y + content_top) / 2,
            text_str,
            ha="center", va="center",
            fontsize=body_fontsize, color="#1E293B",
            linespacing=1.32,
            zorder=4,
        )


def draw_arrow(ax, x1, y1, x2, y2, label="", color="#1E3A8A", style="->", dashed=False, rad=0.0, fontsize=8.2):
    ls = "--" if dashed else "-"
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style,
        mutation_scale=14,
        linewidth=1.5,
        linestyle=ls,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        zorder=5,
    )
    ax.add_patch(arrow)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + (0.018 if rad == 0 else rad * 0.12)
        ax.text(
            mx, my, label,
            ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color="#0F172A",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#CBD5E1", alpha=0.95),
            zorder=6,
        )


# =============================================================================
# 1. DIAGRAMA DE CASOS DE USO UML (Corrección Observación Cap. 3.1 Evaluación 1)
# =============================================================================
def generate_use_case_diagram():
    fig, ax = plt.subplots(figsize=(14, 9.2), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Título
    ax.text(
        0.5, 0.965,
        "DIAGRAMA DE CASOS DE USO UML — PLATAFORMA HCE INTEROPERABLE Y TELEMEDICINA DE URGENCIA (CASO 5)",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color="#0F172A"
    )
    ax.text(
        0.5, 0.935,
        "Corrección Evaluación 1 (Sección 3.1): Frontera del Sistema, 4 Actores RBAC, Sistemas Externos y Relaciones <<include>> / <<extend>>",
        ha="center", va="center", fontsize=9.5, color="#475569"
    )

    # Frontera del sistema
    sys_box = FancyBboxPatch(
        (0.22, 0.06), 0.56, 0.84,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        linewidth=2.2, edgecolor="#16324F", facecolor="#F8FAFC", zorder=1
    )
    ax.add_patch(sys_box)
    ax.text(
        0.50, 0.875,
        "<<System Boundary>>\nNúcleo HCE Interoperable FHIR R4 & Telemedicina de Urgencia",
        ha="center", va="center", fontsize=10.5, fontweight="bold", color="#16324F", zorder=3
    )

    # Actores Primarios (Izquierda: RBAC)
    actors_left = [
        (0.09, 0.76, "«Actor RBAC»\nParamédico / TENS\n(paramedico.soto)\n[Ambulancia Móvil 07]"),
        (0.09, 0.54, "«Actor RBAC»\nMédico de Urgencia\n(dr.valdivia)\n[Clínica Destino]"),
        (0.09, 0.32, "«Actor RBAC»\nMédico Teleconsultor\n(dra.herrera)\n[Sala WebRTC SFU]"),
        (0.09, 0.12, "«Actor RBAC»\nAuditor Forense HIPAA\n(auditor.hipaa)\n[Oficial Privacidad OPD]"),
    ]
    for ax_x, ax_y, label in actors_left:
        draw_box(ax, ax_x - 0.08, ax_y - 0.065, 0.16, 0.13, label, bg="#EFF6FF", border="#1D4ED8", fontsize=8.8)

    # Actores Secundarios / Sistemas Externos (Derecha)
    actors_right = [
        (0.91, 0.72, "«Sistema Externo»\nMonitor Multiparámetro\nAmbulancia (MQTT QoS 1)"),
        (0.91, 0.46, "«Sistema Externo»\nClúster Video SFU\n(WebRTC / SRTP UDP)"),
        (0.91, 0.20, "«Sistema Externo»\nHSM & Ledger Forense\nSHA-256 Append-Only"),
    ]
    for ax_x, ax_y, label in actors_right:
        draw_box(ax, ax_x - 0.08, ax_y - 0.06, 0.16, 0.12, label, bg="#FEF3C7", border="#B45309", fontsize=8.6)

    # Casos de Uso dentro del Sistema
    use_cases = [
        ("UC-01", 0.36, 0.78, "UC-01: Autenticar Sesión\nOAuth2/JWT (15m) + RBAC"),
        ("UC-02", 0.36, 0.65, "UC-02: Registrar Signos Vitales\ny Triage ESI (Strategy)"),
        ("UC-03", 0.64, 0.65, "UC-03: Encolar en Outbox Local\nOffline-First con UUID (ADR-02)"),
        ("UC-04", 0.36, 0.51, "UC-04: Consultar y Actualizar\nFicha Clínica FHIR R4"),
        ("UC-05", 0.64, 0.51, "UC-05: Resolver Conflicto en\nCola Arbitraje Clínico (ADR-05)"),
        ("UC-06", 0.36, 0.36, "UC-06: Emitir Orden Médica /\nDirectiva Teleconsulta SFU"),
        ("UC-07", 0.64, 0.36, "UC-07: Validar Alergias Cruzadas\nTransaccionalmente (ADR-03)"),
        ("UC-08", 0.36, 0.18, "UC-08: Verificar Cadena Hash\nSHA-256 del Ledger Forense"),
        ("UC-09", 0.64, 0.18, "UC-09: Registrar Evento Inmutable\n(ForensicAuditLedgerObserver)"),
    ]

    uc_coords = {}
    for code, cx, cy, text in use_cases:
        uc_coords[code] = (cx, cy)
        ellipse = mpatches.Ellipse(
            (cx, cy), width=0.24, height=0.095,
            facecolor="#FFFFFF", edgecolor="#0F766E" if "UC-07" in code or "UC-09" in code else "#1E3A8A",
            linewidth=1.7, zorder=3
        )
        ax.add_patch(ellipse)
        ax.text(cx, cy, text, ha="center", va="center", fontsize=8.3, fontweight="bold", color="#0F172A", zorder=4)

    # Asociaciones Actor -> Caso de Uso
    draw_arrow(ax, 0.17, 0.76, 0.24, 0.78, "", color="#1D4ED8")
    draw_arrow(ax, 0.17, 0.74, 0.24, 0.65, "", color="#1D4ED8")
    draw_arrow(ax, 0.17, 0.71, 0.24, 0.52, "", color="#1D4ED8")

    draw_arrow(ax, 0.17, 0.55, 0.24, 0.64, "", color="#1D4ED8")
    draw_arrow(ax, 0.17, 0.54, 0.24, 0.51, "", color="#1D4ED8")
    draw_arrow(ax, 0.17, 0.51, 0.24, 0.37, "", color="#1D4ED8")
    draw_arrow(ax, 0.17, 0.52, 0.52, 0.51, "", color="#1D4ED8")

    draw_arrow(ax, 0.17, 0.34, 0.24, 0.50, "", color="#1D4ED8")
    draw_arrow(ax, 0.17, 0.32, 0.24, 0.36, "", color="#1D4ED8")
    draw_arrow(ax, 0.17, 0.33, 0.52, 0.50, "", color="#1D4ED8")

    draw_arrow(ax, 0.17, 0.13, 0.24, 0.18, "", color="#1D4ED8")

    # Relaciones <<include>> y <<extend>> internas
    draw_arrow(ax, 0.52, 0.65, 0.48, 0.65, "«extend»\n[Sin Red / Túnel]", color="#B45309", dashed=True, fontsize=7.6)
    draw_arrow(ax, 0.52, 0.51, 0.48, 0.51, "«extend»\n[v_cliente != v_servidor]", color="#DC2626", dashed=True, fontsize=7.6)
    draw_arrow(ax, 0.48, 0.36, 0.52, 0.36, "«include»", color="#0F766E", dashed=True, fontsize=7.8)
    draw_arrow(ax, 0.48, 0.18, 0.52, 0.18, "«include»", color="#0F766E", dashed=True, fontsize=7.8)
    draw_arrow(ax, 0.64, 0.31, 0.64, 0.23, "«include»\n(Observer)", color="#0F766E", dashed=True, fontsize=7.6)

    # Sistemas externos
    draw_arrow(ax, 0.83, 0.72, 0.48, 0.67, "Telemetría", color="#B45309")
    draw_arrow(ax, 0.48, 0.35, 0.83, 0.46, "SRTP / Subtítulos", color="#B45309")
    draw_arrow(ax, 0.76, 0.18, 0.83, 0.20, "SHA-256 Chain", color="#B45309")

    out_path = os.path.join(OUT_DIR, "1_diagrama_casos_de_uso_uml.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path


# =============================================================================
# 2. DIAGRAMA DE SECUENCIA UML DE ALTA RESOLUCIÓN (Corrección Cap. 3.1 Eval 1)
# =============================================================================
def generate_sequence_diagram():
    fig, ax = plt.subplots(figsize=(14.5, 9.5), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5, 0.968,
        "DIAGRAMA DE SECUENCIA UML — FLUJO VERTICAL DE URGENCIA, ARBITRAJE ADR-05 Y AUDITORÍA SHA-256",
        ha="center", va="center", fontsize=12, fontweight="bold", color="#0F172A"
    )
    ax.text(
        0.5, 0.94,
        "Corrección Evaluación 1 (Sección 3.1): Interacción legible extremo a extremo entre MVVM, FastAPI, Patrones y Persistencia",
        ha="center", va="center", fontsize=9.3, color="#475569"
    )

    participants = [
        (0.08, "Actor RBAC\n(Paramédico /\nMédico)"),
        (0.22, "View & ViewModel\n(App.jsx +\nuseClinicalVM)"),
        (0.36, "Outbox Model\n(clinicalApi.js\nUUID Queue)"),
        (0.50, "FastAPI Router\n& Guardián RBAC\n(api_router.py)"),
        (0.64, "Servicio Dominio\n& Patrón Strategy\n(clinical_service)"),
        (0.78, "Patrón Repository\nSQLAlchemy ACID\n(ehr_repository)"),
        (0.92, "Patrón Observer\nLedger SHA-256\n(audit_observer)"),
    ]

    for px, title in participants:
        draw_box(ax, px - 0.062, 0.84, 0.124, 0.075, title, bg="#16324F", border="#0F172A", title_color="#FFFFFF", fontsize=8.3)
        ax.plot([px, px], [0.06, 0.84], linestyle="--", color="#94A3B8", linewidth=1.3, zorder=1)

    steps = [
        (0.79, 0.08, 0.22, "1. POST /auth/login (credenciales + nodo ambulancia)", "#1D4ED8", False),
        (0.75, 0.22, 0.50, "2. Valida hash contraseña y emite JWT HS256 (TTL=15m, Offline=72h)", "#1D4ED8", False),
        (0.71, 0.50, 0.92, "3. publish(AUTH_LOGIN_SUCCESS) -> Encadena Bloque SHA-256 #N", "#0F766E", False),
        (0.64, 0.08, 0.22, "4. Ingresa Signos Vitales Críticos (FC=124, SpO2=87%, PA=90/56, T=38.8°C)", "#B45309", False),
        (0.60, 0.22, 0.36, "5. [En Túnel Offline] enqueueOutboxTransaction(idempotency_key=UUID)", "#B45309", True),
        (0.55, 0.36, 0.50, "6. [Reconecta 5G] drainOutboxQueue() -> POST /vital-signs (Bearer JWT + UUID)", "#1D4ED8", False),
        (0.50, 0.50, 0.64, "7. Verifica RBAC [PARAMEDICO/MEDICO] y valida rangos Pydantic v2", "#1D4ED8", False),
        (0.45, 0.64, 0.78, "8. get_vital_sign_by_idempotency_key(UUID) -> Previene duplicados", "#1E3A8A", False),
        (0.40, 0.64, 0.64, "9. EmergencySeverityIndexStrategy.evaluate() -> Clasifica [ESI-1 Crítico]", "#DC2626", False),
        (0.35, 0.64, 0.78, "10. save_vital_sign_observation() en tabla vital_sign_observations", "#1E3A8A", False),
        (0.30, 0.64, 0.92, "11. publish(TRIAGE_VITAL_SIGNS_RECORDED) -> SHA-256(prev_hash + payload)", "#0F766E", False),
        (0.24, 0.22, 0.50, "12. PUT /mutable-fields (allergies, expected_version=1 vs server_version=2)", "#DC2626", False),
        (0.19, 0.50, 0.78, "13. [Colisión ADR-05] create_sync_conflict(status='PENDIENTE') + Bloquea Recetas", "#DC2626", False),
        (0.14, 0.50, 0.78, "14. Médico resuelve arbitraje (POST /conflicts/{id}/resolve) -> Sube a versión v3", "#0F766E", False),
        (0.09, 0.50, 0.92, "15. GET /audit/verify-chain -> Recalcula todos los hashes SHA-256 (is_valid=True)", "#0F766E", False),
    ]

    for y, x1, x2, text, col, is_dashed in steps:
        if x1 == x2:
            # Self-call
            ax.plot([x1, x1 + 0.04, x1 + 0.04, x1], [y + 0.01, y + 0.01, y - 0.01, y - 0.01], color=col, linewidth=1.6)
            ax.text(
                x1 + 0.045, y, text,
                ha="left", va="center", fontsize=8.2, fontweight="bold", color=col,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#FEF2F2", edgecolor=col)
            )
        else:
            draw_arrow(ax, x1, y, x2, y, label=text, color=col, dashed=is_dashed, fontsize=8.0)

    out_path = os.path.join(OUT_DIR, "2_diagrama_secuencia_urgencia_uml.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path


# =============================================================================
# 3. DIAGRAMA DE DESPLIEGUE UML — TOPOLOGÍA HÍBRIDA LEGIBLE (Corrección Cap. 4.1)
# =============================================================================
def generate_deployment_diagram():
    fig, ax = plt.subplots(figsize=(14.5, 9.2), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5, 0.965,
        "DIAGRAMA DE DESPLIEGUE UML — TOPOLOGÍA HÍBRIDA ON-PREMISE + NUBE MULTI-AZ (ADR-07 Y ADR-08)",
        ha="center", va="center", fontsize=12, fontweight="bold", color="#0F172A"
    )
    ax.text(
        0.5, 0.935,
        "Corrección Evaluación 1 (Sección 4.1): Especificación legible en 300 DPI de Nodos, Artefactos, Protocolos, Cifrado y Puertos",
        ha="center", va="center", fontsize=9.3, color="#475569"
    )

    # 1. Nodos de Borde y Clientes (Arriba)
    draw_box(
        ax, 0.03, 0.62, 0.28, 0.27,
        "«device / edge node»\nAmbulancia Móvil 07 (Tablet + Gateway)",
        [
            "• Artefacto: hce-pwa-client (React 18 MVVM)",
            "• Almacén Local: IndexedDB / Outbox AES-256",
            "• Periférico: Monitor Signos Vitales (MQTT)",
            "• Credencial Offline Firmada (TTL: 72 horas)",
            "• Puertos Salida: TCP 443 (HTTPS), UDP 10000-20000"
        ],
        bg="#EFF6FF", border="#1D4ED8", title_bg="#1E3A8A", title_color="#FFFFFF", fontsize=9.0, body_fontsize=8.2
    )

    draw_box(
        ax, 0.36, 0.62, 0.28, 0.27,
        "«device / workstation»\nEstación Clínica / Box Reanimación",
        [
            "• Artefacto: hce-pwa-client (React 18 / Vite)",
            "• Vistas: Ficha FHIR R4, Arbitraje ADR-05",
            "• Visor de Estudios DICOM & Receta Electrónica",
            "• Autenticación: OAuth2 + JWT (TTL: 15 min)",
            "• Puerto Salida: TCP 443 (TLS 1.3 Estricto)"
        ],
        bg="#EFF6FF", border="#1D4ED8", title_bg="#1E3A8A", title_color="#FFFFFF", fontsize=9.0, body_fontsize=8.2
    )

    draw_box(
        ax, 0.69, 0.62, 0.28, 0.27,
        "«device / telemedicine station»\nConsola Comando Teleconsulta & Auditoría",
        [
            "• Artefacto: hce-telemed-console (PWA)",
            "• Flujo Multimedia: WebRTC / SRTP + Subtítulos",
            "• Consola Oficial Privacidad (Auditor HIPAA)",
            "• Verificación Criptográfica Cadena SHA-256",
            "• Puertos: TCP 443 (WSS/HTTPS), UDP 3478 (STUN/TURN)"
        ],
        bg="#EFF6FF", border="#1D4ED8", title_bg="#1E3A8A", title_color="#FFFFFF", fontsize=9.0, body_fontsize=8.2
    )

    # 2. Centro de Datos On-Premise del Consorcio (Abajo Izquierda - Soberanía del Dato y SLA 99.999%)
    draw_box(
        ax, 0.03, 0.06, 0.52, 0.45,
        "«execution environment» Centro de Datos On-Premise Consorcio (Clúster Kubernetes HA — SLA 99,999%)",
        [],
        bg="#F1F5F9", border="#0F172A", title_bg="#16324F", title_color="#FFFFFF", fontsize=9.2
    )

    draw_box(
        ax, 0.05, 0.27, 0.23, 0.16,
        "«artifact» Servicio Expediente-Órdenes",
        [
            "• Python 3.13 + FastAPI (Uvicorn ASGI)",
            "• Patrones: Strategy, Observer, Repository",
            "• Contratos Externos: REST FHIR R4 (:8000)",
            "• Tráfico Interno: gRPC / mTLS (:50051)"
        ],
        bg="#FFFFFF", border="#1E3A8A", fontsize=8.5, body_fontsize=7.8
    )

    draw_box(
        ax, 0.30, 0.27, 0.23, 0.16,
        "«database» Núcleo Transaccional CP",
        [
            "• Motor: PostgreSQL 16 HA / SQLite WAL",
            "• Tablas: patients, medical_orders, conflicts",
            "• Cifrado en Reposo: AES-256 (HSM Keys)",
            "• Puerto Interno Aislado: TCP 5432"
        ],
        bg="#FFFFFF", border="#1E3A8A", fontsize=8.5, body_fontsize=7.8
    )

    draw_box(
        ax, 0.05, 0.08, 0.48, 0.15,
        "«isolated security zone» Segmento Aislado de Auditoría Forense & HSM (Sin Ruta a Internet — ADR-03 / ADR-08)",
        [
            "• Artefacto: forensic-audit-ledger-service + Tabla Append-Only audit_ledger (Cadena Hash SHA-256)",
            "• Credenciales BD: INSERT & SELECT únicamente (Permisos UPDATE y DELETE revocados por rol de motor)",
            "• custodia de llaves criptográficas en Hardware Security Module (HSM FIPS 140-3) · Puerto mTLS: TCP 8443"
        ],
        bg="#FEF2F2", border="#DC2626", fontsize=8.5, body_fontsize=7.8
    )

    # 3. Nube Pública Multi-AZ (Abajo Derecha - Elasticidad de Ráfaga 10x / 20x)
    draw_box(
        ax, 0.59, 0.06, 0.38, 0.45,
        "«cloud environment» Nube Pública Multi-AZ HIPAA-Eligible (Componentes de Ráfaga 10×)",
        [],
        bg="#FFFBEB", border="#B45309", title_bg="#92400E", title_color="#FFFFFF", fontsize=9.2
    )

    draw_box(
        ax, 0.61, 0.27, 0.34, 0.16,
        "«artifact» Clúster Pasarela Video WebRTC (SFU) + Subtitulado",
        [
            "• Autoescalado Horizontal por Sesiones Activas (Zoom-style)",
            "• Señalización: WebSocket TLS (TCP 443) | Media: SRTP (UDP 10000-20000)",
            "• Servicio Desacoplado de Subtitulado Clínico en Vivo (Sección 2.2 #2)"
        ],
        bg="#FFFFFF", border="#B45309", fontsize=8.5, body_fontsize=7.8
    )

    draw_box(
        ax, 0.61, 0.08, 0.34, 0.15,
        "«database» Ingestor Telemetría (TimescaleDB) & Almacén DICOM (S3)",
        [
            "• Broker MQTT (TLS TCP 8883, QoS 1) -> Series Temporales TimescaleDB",
            "• Documentos FHIR Variables (MongoDB :27017) & Objetos DICOM Cifrados (S3 :443)"
        ],
        bg="#FFFFFF", border="#B45309", fontsize=8.5, body_fontsize=7.8
    )

    # Enlaces de Red y Protocolos
    draw_arrow(ax, 0.17, 0.62, 0.17, 0.43, "HTTPS REST FHIR R4 (TLS 1.3 :443)\n+ Outbox Sync UUID", color="#1D4ED8")
    draw_arrow(ax, 0.50, 0.62, 0.22, 0.43, "HTTPS / OAuth2 JWT (:443)", color="#1D4ED8")
    draw_arrow(ax, 0.83, 0.62, 0.78, 0.43, "WSS (:443) + SRTP (UDP)", color="#B45309")
    draw_arrow(ax, 0.24, 0.62, 0.72, 0.23, "MQTT QoS 1 (:8883)", color="#0F766E")
    draw_arrow(ax, 0.28, 0.35, 0.30, 0.35, "SQL / ACID\n(:5432)", color="#0F172A")
    draw_arrow(ax, 0.17, 0.27, 0.17, 0.23, "Evento SHA-256\n(mTLS :8443)", color="#DC2626")
    draw_arrow(ax, 0.55, 0.35, 0.59, 0.35, "Enlace Privado\nmTLS / VPN HA", color="#0F766E", style="<->")

    out_path = os.path.join(OUT_DIR, "3_diagrama_despliegue_hibrido_uml.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path


# =============================================================================
# 4. DIAGRAMA DE CLASES Y COMPONENTES DE PATRONES DE DISEÑO (300 DPI)
# =============================================================================
def generate_patterns_diagram():
    fig, ax = plt.subplots(figsize=(14, 8.5), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5, 0.96,
        "DIAGRAMA DE ARQUITECTURA Y PATRONES DE DISEÑO IMPLEMENTADOS EN EL CÓDIGO FUENTE",
        ha="center", va="center", fontsize=12, fontweight="bold", color="#0F172A"
    )
    ax.text(
        0.5, 0.928,
        "Trazabilidad directa con los archivos del proyecto: MVVM (Frontend) + Strategy, Observer y Repository (Backend)",
        ha="center", va="center", fontsize=9.3, color="#475569"
    )

    # Frontend MVVM
    draw_box(
        ax, 0.03, 0.54, 0.27, 0.33,
        "Patrón 4: MVVM + Outbox (Frontend React)",
        [
            "• View (frontend/src/App.jsx):",
            "  4 Vistas Clínicas + WCAG 2.2 AAA (7:1)",
            "• ViewModel (useClinicalViewModel.js):",
            "  Estado Observable + Máquina Episodio",
            "• Model (clinicalApi.js):",
            "  Cliente FHIR R4 + Cola Outbox UUID"
        ],
        bg="#EFF6FF", border="#1D4ED8", title_bg="#1E3A8A", title_color="#FFFFFF", fontsize=9.0, body_fontsize=8.2
    )

    # Servicio Central
    draw_box(
        ax, 0.36, 0.54, 0.28, 0.33,
        "Núcleo Cohesivo (ADR-03)",
        [
            "• Router + RBAC (api_router.py):",
            "  JWT HS256 (15m) + require_roles()",
            "• Servicio (clinical_service.py):",
            "  ClinicalEHRService",
            "  Orquesta Triage, Arbitraje ADR-05,",
            "  Órdenes Médicas y Auditoría"
        ],
        bg="#F8FAFC", border="#0F172A", title_bg="#16324F", title_color="#FFFFFF", fontsize=9.0, body_fontsize=8.2
    )

    # Patrón Strategy
    draw_box(
        ax, 0.70, 0.54, 0.27, 0.33,
        "Patrón 1: Strategy (clinical_strategies.py)",
        [
            "• ClinicalTriageStrategy (ABC):",
            "  -> EmergencySeverityIndexStrategy",
            "• SyncResolutionStrategy (ADR-05):",
            "  -> AppendOnlyCRDTGSetStrategy",
            "  -> OptimisticConcurrencyArbitration",
            "• DrugSafetyGuardStrategy (ADR-03)"
        ],
        bg="#ECFDF5", border="#059669", title_bg="#065F46", title_color="#FFFFFF", fontsize=9.0, body_fontsize=8.2
    )

    # Patrón Observer
    draw_box(
        ax, 0.08, 0.10, 0.38, 0.32,
        "Patrón 2: Observer (backend/app/observers/audit_observer.py)",
        [
            "• Subject: ClinicalDomainEventBus (subscribe / publish)",
            "• Evento: ClinicalDomainEvent (dataclass inmutable)",
            "• Suscriptor 1: ForensicAuditLedgerObserver",
            "  Calcula SHA-256(seq | actor | rol | acción | prev_hash)",
            "• Suscriptor 2: CriticalTelemetryAlertObserver (Código Rojo)"
        ],
        bg="#FEF2F2", border="#DC2626", title_bg="#991B1B", title_color="#FFFFFF", fontsize=9.0, body_fontsize=8.2
    )

    # Patrón Repository
    draw_box(
        ax, 0.54, 0.10, 0.38, 0.32,
        "Patrón 3: Repository (backend/app/repositories/ehr_repository.py)",
        [
            "• PatientEHRRepository: Persistencia ACID, deduplicación",
            "  por idempotency_key UUID y Cola Arbitraje sync_conflicts",
            "• AuditLedgerRepository: Estructuralmente Append-Only",
            "  (sin update/delete) + verify_chain_integrity() SHA-256",
            "• UserRepository: Gestión de 4 perfiles RBAC"
        ],
        bg="#FFFBEB", border="#D97706", title_bg="#92400E", title_color="#FFFFFF", fontsize=9.0, body_fontsize=8.2
    )

    draw_arrow(ax, 0.30, 0.70, 0.36, 0.70, "REST FHIR R4", color="#1D4ED8")
    draw_arrow(ax, 0.64, 0.70, 0.70, 0.70, "Inyecta Strategy", color="#059669")
    draw_arrow(ax, 0.45, 0.54, 0.30, 0.42, "Publica Eventos (Desacoplado)", color="#DC2626")
    draw_arrow(ax, 0.55, 0.54, 0.68, 0.42, "Acceso a Datos ACID", color="#D97706")
    draw_arrow(ax, 0.46, 0.26, 0.54, 0.26, "Persiste Bloque SHA-256", color="#991B1B")

    out_path = os.path.join(OUT_DIR, "4_diagrama_patrones_implementados.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    p1 = generate_use_case_diagram()
    p2 = generate_sequence_diagram()
    p3 = generate_deployment_diagram()
    p4 = generate_patterns_diagram()
    print("Diagramas generados a 300 DPI:")
    for p in (p1, p2, p3, p4):
        print(" ->", p)
