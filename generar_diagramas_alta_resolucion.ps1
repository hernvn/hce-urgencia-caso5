param(
    [string]$OutDir = "C:\Users\herna\.gemini\antigravity\brain\90cbd83b-c91c-4fc2-b93d-6848775d5bdc\diagramas_uml"
)
Add-Type -AssemblyName System.Drawing

if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
}

function New-Canvas([int]$W = 2400, [int]$H = 1550) {
    $bmp = New-Object System.Drawing.Bitmap($W, $H)
    $bmp.SetResolution(96, 96)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.PageUnit = [System.Drawing.GraphicsUnit]::Pixel
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $g.Clear([System.Drawing.Color]::White)
    return @{ Bitmap = $bmp; Graphics = $g }
}

function Get-Color([string]$Hex) {
    return [System.Drawing.ColorTranslator]::FromHtml($Hex)
}

function New-PxFont([string]$Family, [float]$PxSize, [System.Drawing.FontStyle]$Style = [System.Drawing.FontStyle]::Regular) {
    return New-Object System.Drawing.Font($Family, $PxSize, $Style, [System.Drawing.GraphicsUnit]::Pixel)
}

function Draw-Card($g, [float]$x, [float]$y, [float]$w, [float]$h, [string]$title, [string[]]$lines, [string]$bgHex='#F8FAFC', [string]$borderHex='#1E3A8A', [string]$headerBgHex='#16324F', [string]$headerTextHex='#FFFFFF', [float]$titlePx=20, [float]$bodyPx=17, [float]$hdrHeight=52) {
    $bgBrush = New-Object System.Drawing.SolidBrush((Get-Color $bgHex))
    $borderPen = New-Object System.Drawing.Pen((Get-Color $borderHex), 2.5)
    $g.FillRectangle($bgBrush, $x, $y, $w, $h)

    $hdrH = if ($lines -and $lines.Count -gt 0) { $hdrHeight } else { [Math]::Min($hdrHeight, $h) }
    if ($headerBgHex -ne '') {
        $hdrBrush = New-Object System.Drawing.SolidBrush((Get-Color $headerBgHex))
        $g.FillRectangle($hdrBrush, $x, $y, $w, $hdrH)
        $hdrBrush.Dispose()
    }
    $g.DrawRectangle($borderPen, $x, $y, $w, $h)

    $titleFont = New-PxFont 'Segoe UI' $titlePx ([System.Drawing.FontStyle]::Bold)
    $titleBrush = New-Object System.Drawing.SolidBrush((Get-Color $headerTextHex))
    $sfCenter = New-Object System.Drawing.StringFormat
    $sfCenter.Alignment = [System.Drawing.StringAlignment]::Center
    $sfCenter.LineAlignment = [System.Drawing.StringAlignment]::Center
    $rectTitle = New-Object System.Drawing.RectangleF(($x + 8), ($y + 4), ($w - 16), ($hdrH - 8))
    $g.DrawString($title, $titleFont, $titleBrush, $rectTitle, $sfCenter)

    if ($lines -and $lines.Count -gt 0) {
        $bodyFont = New-PxFont 'Segoe UI' $bodyPx ([System.Drawing.FontStyle]::Regular)
        $bodyBrush = New-Object System.Drawing.SolidBrush((Get-Color '#0F172A'))
        $sfLeft = New-Object System.Drawing.StringFormat
        $sfLeft.Alignment = [System.Drawing.StringAlignment]::Near
        $sfLeft.LineAlignment = [System.Drawing.StringAlignment]::Near
        $bodyText = [string]::Join("`r`n", $lines)
        $rectBody = New-Object System.Drawing.RectangleF(($x + 16), ($y + $hdrH + 12), ($w - 32), ($h - $hdrH - 20))
        $g.DrawString($bodyText, $bodyFont, $bodyBrush, $rectBody, $sfLeft)
        $bodyFont.Dispose()
        $bodyBrush.Dispose()
        $sfLeft.Dispose()
    }

    $bgBrush.Dispose()
    $borderPen.Dispose()
    $titleFont.Dispose()
    $titleBrush.Dispose()
    $sfCenter.Dispose()
}

function Draw-UseCaseEllipse($g, [float]$cx, [float]$cy, [float]$rx, [float]$ry, [string]$text, [string]$borderHex='#1E3A8A', [string]$bgHex='#FFFFFF') {
    $x = $cx - $rx
    $y = $cy - $ry
    $w = $rx * 2
    $h = $ry * 2
    $bgBrush = New-Object System.Drawing.SolidBrush((Get-Color $bgHex))
    $pen = New-Object System.Drawing.Pen((Get-Color $borderHex), 2.5)
    $g.FillEllipse($bgBrush, $x, $y, $w, $h)
    $g.DrawEllipse($pen, $x, $y, $w, $h)

    $font = New-PxFont 'Segoe UI' 16 ([System.Drawing.FontStyle]::Bold)
    $brush = New-Object System.Drawing.SolidBrush((Get-Color '#0F172A'))
    $sf = New-Object System.Drawing.StringFormat
    $sf.Alignment = [System.Drawing.StringAlignment]::Center
    $sf.LineAlignment = [System.Drawing.StringAlignment]::Center
    $rect = New-Object System.Drawing.RectangleF(($x + 18), ($y + 10), ($w - 36), ($h - 20))
    $g.DrawString($text, $font, $brush, $rect, $sf)

    $bgBrush.Dispose(); $pen.Dispose(); $font.Dispose(); $brush.Dispose(); $sf.Dispose()
}

function Draw-Arrow($g, [float]$x1, [float]$y1, [float]$x2, [float]$y2, [string]$label='', [string]$hex='#1E3A8A', [bool]$dashed=$false, [float]$labelOffsetY=0) {
    $pen = New-Object System.Drawing.Pen((Get-Color $hex), 2.5)
    if ($dashed) {
        $pen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash
    }
    $cap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap(6, 6, $true)
    $pen.CustomEndCap = $cap
    $g.DrawLine($pen, $x1, $y1, $x2, $y2)

    if ($label -ne '') {
        $mx = ($x1 + $x2) / 2
        $my = (($y1 + $y2) / 2) + $labelOffsetY
        $font = New-PxFont 'Segoe UI' 15 ([System.Drawing.FontStyle]::Bold)
        $size = $g.MeasureString($label, $font)
        $bx = $mx - ($size.Width / 2) - 8
        $by = $my - ($size.Height / 2) - 4
        $bw = $size.Width + 16
        $bh = $size.Height + 8
        $bBrush = New-Object System.Drawing.SolidBrush((Get-Color '#FFFFFF'))
        $bPen = New-Object System.Drawing.Pen((Get-Color $hex), 1.8)
        $g.FillRectangle($bBrush, $bx, $by, $bw, $bh)
        $g.DrawRectangle($bPen, $bx, $by, $bw, $bh)
        $tBrush = New-Object System.Drawing.SolidBrush((Get-Color '#0F172A'))
        $g.DrawString($label, $font, $tBrush, ($bx + 8), ($by + 4))
        $font.Dispose(); $bBrush.Dispose(); $bPen.Dispose(); $tBrush.Dispose()
    }
    $pen.Dispose(); $cap.Dispose()
}

function Draw-TitleBanner($g, [string]$title, [string]$subtitle) {
    $hdrBrush = New-Object System.Drawing.SolidBrush((Get-Color '#16324F'))
    $g.FillRectangle($hdrBrush, 0, 0, 2400, 110)
    $f1 = New-PxFont 'Segoe UI' 28 ([System.Drawing.FontStyle]::Bold)
    $f2 = New-PxFont 'Segoe UI' 19 ([System.Drawing.FontStyle]::Regular)
    $wBrush = New-Object System.Drawing.SolidBrush((Get-Color '#FFFFFF'))
    $sBrush = New-Object System.Drawing.SolidBrush((Get-Color '#CBD5E1'))
    $g.DrawString($title, $f1, $wBrush, 40, 20)
    $g.DrawString($subtitle, $f2, $sBrush, 40, 64)
    $hdrBrush.Dispose(); $f1.Dispose(); $f2.Dispose(); $wBrush.Dispose(); $sBrush.Dispose()
}

# =============================================================================
# 1. DIAGRAMA DE CASOS DE USO UML
# =============================================================================
$c1 = New-Canvas 2400 1550
$g = $c1.Graphics
Draw-TitleBanner $g 'DIAGRAMA DE CASOS DE USO UML - PLATAFORMA HCE INTEROPERABLE Y TELEMEDICINA DE URGENCIA (CASO 5)' 'Correccion Evaluacion 1 (Seccion 3.1): Frontera del Sistema, 4 Actores RBAC, Sistemas Externos y Relaciones <<include>> / <<extend>>'

Draw-Card $g 490 135 1420 1370 '<<System Boundary>> Plataforma Centralizada HCE Interoperable FHIR R4 y Telemedicina de Urgencia' @() '#F8FAFC' '#16324F' '#16324F' '#FFFFFF' 20 16 54

Draw-Card $g 35 200 400 220 '<<Actor RBAC>> Paramedico / TENS' @(
    'Usuario: paramedico.soto',
    'Nodo: Ambulancia Movil 07 (Tablet)',
    '- Captura signos vitales y triage ESI',
    '- Opera cola Offline Outbox en tuneles'
) '#EFF6FF' '#1D4ED8' '#1E3A8A' '#FFFFFF' 19 16 46

Draw-Card $g 35 500 400 220 '<<Actor RBAC>> Medico de Urgencia' @(
    'Usuario: dr.valdivia',
    'Nodo: Clinica Alta Complejidad Central',
    '- Consulta y actualiza Ficha FHIR R4',
    '- Resuelve Arbitraje ADR-05 y prescribe'
) '#EFF6FF' '#1D4ED8' '#1E3A8A' '#FFFFFF' 19 16 46

Draw-Card $g 35 800 400 220 '<<Actor RBAC>> Medico Teleconsultor' @(
    'Usuario: dra.herrera',
    'Nodo: Sala Comando SFU-04 Nacional',
    '- Conduce videoconsulta SRTP/WebRTC',
    '- Emite directivas con subtitulado en vivo'
) '#EFF6FF' '#1D4ED8' '#1E3A8A' '#FFFFFF' 19 16 46

Draw-Card $g 35 1100 400 220 '<<Actor RBAC>> Auditor Forense HIPAA' @(
    'Usuario: auditor.hipaa',
    'Nodo: Consola Aislada de Cumplimiento',
    '- Inspecciona trazabilidad de accesos PHI',
    '- Verifica matematicamente cadena SHA-256'
) '#FEF2F2' '#DC2626' '#991B1B' '#FFFFFF' 19 16 46

Draw-Card $g 1965 250 400 220 '<<Sistema Externo>> Monitor Vitales' @(
    'Equipamiento Embarcado Ambulancia',
    '- Protocolo: MQTT sobre TLS (QoS 1)',
    '- Envia rafagas de FC, SpO2, PA y Temp'
) '#FFFBEB' '#B45309' '#92400E' '#FFFFFF' 19 16 46

Draw-Card $g 1965 640 400 220 '<<Sistema Externo>> Cluster Video SFU' @(
    'Nube Publica Multi-AZ (Autoescalable)',
    '- Senalizacion: WebSocket TLS (:443)',
    '- Medio: SRTP sobre UDP + Subtitulado'
) '#FFFBEB' '#B45309' '#92400E' '#FFFFFF' 19 16 46

Draw-Card $g 1965 1030 400 220 '<<Sistema Externo>> Modulo HSM y Ledger' @(
    'Segmento de Red Aislado On-Premise',
    '- Custodia claves AES-256 y raices SHA-256',
    '- Credenciales Append-Only (Sin DELETE)'
) '#FEF2F2' '#DC2626' '#991B1B' '#FFFFFF' 19 16 46

Draw-UseCaseEllipse $g 820 300 260 72 "UC-01: Autenticar Sesion Institucional`r`nOAuth2/JWT (15m) + Credencial Offline (72h)" '#1E3A8A' '#FFFFFF'
Draw-UseCaseEllipse $g 820 520 260 72 "UC-02: Registrar Signos Vitales y`r`nClasificar Triage ESI (Patron Strategy)" '#1E3A8A' '#FFFFFF'
Draw-UseCaseEllipse $g 1580 520 260 72 "UC-03: Encolar en Outbox Local`r`nStore-and-Forward con UUID (ADR-02/04)" '#B45309' '#FFFBEB'
Draw-UseCaseEllipse $g 820 755 260 72 "UC-04: Consultar y Actualizar Ficha`r`nClinica Interoperable HL7 FHIR R4" '#1E3A8A' '#FFFFFF'
Draw-UseCaseEllipse $g 1580 755 260 72 "UC-05: Desviar y Resolver Conflicto en`r`nCola de Arbitraje Clinico (ADR-05)" '#DC2626' '#FEF2F2'
Draw-UseCaseEllipse $g 820 990 260 72 "UC-06: Emitir Orden Medica / Directiva`r`nde Teleconsulta con Subtitulado" '#1E3A8A' '#FFFFFF'
Draw-UseCaseEllipse $g 1580 990 260 72 "UC-07: Verificar Alergias Cruzadas`r`nTransaccionalmente (Invariante ADR-03)" '#059669' '#ECFDF5'
Draw-UseCaseEllipse $g 820 1235 260 72 "UC-08: Auditar y Verificar Integridad`r`nMatematica de Cadena SHA-256" '#991B1B' '#FEF2F2'
Draw-UseCaseEllipse $g 1580 1235 260 72 "UC-09: Encadenar Evento Forense`r`nInmutable (Patron Observer SHA-256)" '#059669' '#ECFDF5'

Draw-Arrow $g 435 290 560 300 '' '#1D4ED8'
Draw-Arrow $g 435 330 560 510 '' '#1D4ED8'
Draw-Arrow $g 435 370 560 735 '' '#1D4ED8'

Draw-Arrow $g 435 585 560 535 '' '#1D4ED8'
Draw-Arrow $g 435 610 560 755 '' '#1D4ED8'
Draw-Arrow $g 435 650 560 975 '' '#1D4ED8'
Draw-Arrow $g 435 630 1320 755 '' '#DC2626'

Draw-Arrow $g 435 890 560 770 '' '#1D4ED8'
Draw-Arrow $g 435 920 560 990 '' '#1D4ED8'
Draw-Arrow $g 435 905 1320 770 '' '#DC2626'

Draw-Arrow $g 435 1210 560 1235 '' '#991B1B'

Draw-Arrow $g 1320 520 1080 520 '<<extend>> [En Tunel Offline]' '#B45309' $true
Draw-Arrow $g 1320 755 1080 755 '<<extend>> [v_cli != v_srv]' '#DC2626' $true
Draw-Arrow $g 1080 990 1320 990 '<<include>> (Obligatorio)' '#059669' $true
Draw-Arrow $g 1080 1235 1320 1235 '<<include>>' '#059669' $true
Draw-Arrow $g 1580 1062 1580 1163 '<<include>> (Observer)' '#059669' $true

Draw-Arrow $g 1965 360 1080 500 'MQTT QoS 1' '#B45309' $false -25
Draw-Arrow $g 1080 960 1965 750 'SRTP / WSS' '#B45309' $false 25
Draw-Arrow $g 1840 1235 1965 1140 'SHA-256' '#991B1B'

$p1 = Join-Path $OutDir '1_diagrama_casos_de_uso_uml.png'
$c1.Bitmap.Save($p1, [System.Drawing.Imaging.ImageFormat]::Png)
$c1.Graphics.Dispose(); $c1.Bitmap.Dispose()

# =============================================================================
# 2. DIAGRAMA DE SECUENCIA UML DE URGENCIA Y ARBITRAJE
# =============================================================================
$c2 = New-Canvas 2400 1550
$g = $c2.Graphics
Draw-TitleBanner $g 'DIAGRAMA DE SECUENCIA UML - FLUJO VERTICAL DE URGENCIA, OUTBOX OFFLINE, ARBITRAJE ADR-05 Y AUDITORIA' 'Correccion Evaluacion 1 (Seccion 3.1): Secuencia de alta resolucion con participantes, firmas de metodos y retornos'

$cols = @(
    @{ X = 190;  Title = "Actor Clinico RBAC`r`n(Paramedico / Medico)" },
    @{ X = 540;  Title = "View + ViewModel`r`n(App.jsx / useClinicalVM)" },
    @{ X = 890;  Title = "Outbox Model Local`r`n(clinicalApi.js UUID)" },
    @{ X = 1240; Title = "FastAPI Router y RBAC`r`n(api_router.py)" },
    @{ X = 1590; Title = "ClinicalEHRService y`r`nPatron Strategy" },
    @{ X = 1940; Title = "PatientEHRRepository`r`n(SQLAlchemy ACID)" },
    @{ X = 2250; Title = "AuditLedgerObserver`r`n(Cadena SHA-256)" }
)

foreach ($c in $cols) {
    Draw-Card $g ($c.X - 150) 135 300 84 $c.Title @() '#16324F' '#0F172A' '#16324F' '#FFFFFF' 17 15 84
    $dashPen = New-Object System.Drawing.Pen((Get-Color '#94A3B8'), 2)
    $dashPen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash
    $g.DrawLine($dashPen, $c.X, 220, $c.X, 1490)
    $dashPen.Dispose()
}

$seqSteps = @(
    @{ Y = 275; X1 = 190;  X2 = 540;  Text = '1. Selecciona perfil RBAC e inicia sesion (loginWithCredentials)'; Col = '#1D4ED8'; Dash = $false },
    @{ Y = 355; X1 = 540;  X2 = 1240; Text = '2. POST /api/v1/auth/login -> Verifica hash y emite JWT HS256 (TTL=15m)'; Col = '#1D4ED8'; Dash = $false },
    @{ Y = 435; X1 = 1240; X2 = 2250; Text = '3. publish(AUTH_LOGIN_SUCCESS) -> Calcula SHA-256(prev_hash + payload)'; Col = '#059669'; Dash = $false },
    @{ Y = 515; X1 = 190;  X2 = 540;  Text = '4. Registra Triage Critico (FC=124, SpO2=87%, PA=90/56 mmHg, T=38.8 C)'; Col = '#B45309'; Dash = $false },
    @{ Y = 595; X1 = 540;  X2 = 890;  Text = '5. [Modo Tunel Offline] enqueueOutboxTransaction(idempotency_key=UUID)'; Col = '#B45309'; Dash = $true },
    @{ Y = 675; X1 = 890;  X2 = 1240; Text = '6. [Recupera Red 5G] drainOutboxQueue() -> POST /vital-signs (Bearer JWT + UUID)'; Col = '#1D4ED8'; Dash = $false },
    @{ Y = 755; X1 = 1240; X2 = 1590; Text = '7. require_roles([PARAMEDICO, MEDICO]) + Validacion fisiologica Pydantic v2'; Col = '#1D4ED8'; Dash = $false },
    @{ Y = 835; X1 = 1590; X2 = 1940; Text = '8. get_vital_sign_by_idempotency_key(UUID) -> Garantiza Cero Duplicados'; Col = '#1E3A8A'; Dash = $false },
    @{ Y = 915; X1 = 1590; X2 = 1940; Text = '9. EmergencySeverityIndexStrategy.evaluate() -> Clasifica [ESI-1 Critico] y guarda'; Col = '#DC2626'; Dash = $false },
    @{ Y = 995; X1 = 1590; X2 = 2250; Text = '10. publish(TRIAGE_VITAL_SIGNS_RECORDED) -> Inserta eslabon SHA-256 en audit_ledger'; Col = '#059669'; Dash = $false },
    @{ Y = 1080; X1 = 540; X2 = 1240; Text = '11. PUT /mutable-fields (allergies, expected_version=1 vs servidor v2)'; Col = '#DC2626'; Dash = $false },
    @{ Y = 1165; X1 = 1240; X2 = 1940; Text = '12. [Colision ADR-05] OptimisticConcurrencyStrategy -> Crea SyncConflict PENDIENTE'; Col = '#DC2626'; Dash = $false },
    @{ Y = 1250; X1 = 540; X2 = 1240; Text = '13. Intento de recetar Amoxicilina -> Bloqueado HTTP 409/422 (DrugSafetyGuardStrategy)'; Col = '#DC2626'; Dash = $true },
    @{ Y = 1335; X1 = 540; X2 = 1940; Text = '14. Medico firma conciliacion (POST /conflicts/{id}/resolve) -> Actualiza ficha a v3'; Col = '#059669'; Dash = $false },
    @{ Y = 1420; X1 = 1240; X2 = 2250; Text = '15. GET /audit/verify-chain -> Recalcula cadena desde bloque Genesis (0 adulteraciones)'; Col = '#059669'; Dash = $false }
)

foreach ($s in $seqSteps) {
    Draw-Arrow $g $s.X1 $s.Y $s.X2 $s.Y $s.Text $s.Col $s.Dash
}

$p2 = Join-Path $OutDir '2_diagrama_secuencia_urgencia_uml.png'
$c2.Bitmap.Save($p2, [System.Drawing.Imaging.ImageFormat]::Png)
$c2.Graphics.Dispose(); $c2.Bitmap.Dispose()

# =============================================================================
# 3. DIAGRAMA DE DESPLIEGUE UML — TOPOLOGÍA HÍBRIDA LEGIBLE
# =============================================================================
$c3 = New-Canvas 2400 1550
$g = $c3.Graphics
Draw-TitleBanner $g 'DIAGRAMA DE DESPLIEGUE UML - TOPOLOGIA HIBRIDA ON-PREMISE + NUBE MULTI-AZ (ADR-07 Y ADR-08)' 'Correccion Evaluacion 1 (Seccion 4.1): Nodos de Hardware/K8s, Artefactos Desplegados, Protocolos y Puertos en Alta Resolucion'

Draw-Card $g 45 140 730 370 '<<device / edge node>> Ambulancia Movil 07 (Tablet + Gateway Borde)' @(
    '- Artefacto UI: hce-urgencia-pwa.bundle.js (React 18 MVVM Offline-First)',
    '- Persistencia Local: IndexedDB + Cola Transactional Outbox Cifrada AES-256',
    '- Credencial de Operacion Offline firmada por Nodo de Borde (TTL: 72 horas)',
    '- Equipamiento Medico: Monitor Multiparametro conectado por Broker MQTT local',
    '- Accesibilidad: Tema Alto Contraste Exterior WCAG 2.2 AAA (7:1) y Botones >= 48dp',
    '- Puertos Salientes: TCP 443 (HTTPS/REST FHIR), TCP 8883 (MQTT TLS), UDP 10000-20000'
) '#EFF6FF' '#1D4ED8' '#1E3A8A' '#FFFFFF' 19 16 48

Draw-Card $g 835 140 730 370 '<<device / workstation>> Terminal Clinica Hospitalaria (Box Reanimacion)' @(
    '- Artefacto UI: hce-urgencia-pwa.bundle.js (Ejecutado sobre Chromium / Edge)',
    '- Modulos: Ficha Clinica Interoperable HL7 FHIR R4 + Visor Estudios DICOM',
    '- Control de Concurrencia: Consola de Arbitraje Clinico Manual (ADR-05)',
    '- Farmacovigilancia: Prescripcion Electronica con verificacion de alergias',
    '- Autenticacion: OAuth2 + Token JWT de vida corta (TTL: 15 minutos)',
    '- Puertos Salientes: TCP 443 (HTTPS TLS 1.3 Estricto)'
) '#EFF6FF' '#1D4ED8' '#1E3A8A' '#FFFFFF' 19 16 48

Draw-Card $g 1625 140 730 370 '<<device / console>> Estacion Comando Teleconsulta y Auditoria HIPAA' @(
    '- Artefacto UI: hce-telemed-auditor-console (React 18 PWA)',
    '- Telemedicina: Cliente WebRTC SRTP con reconexion ICE Restart (120 seg)',
    '- Accesibilidad Auditiva: Canal de Subtitulado Clinico en Vivo (Seccion 2.2 #2)',
    '- Consola Oficial de Privacidad (OPD): Verificador matematico de cadena SHA-256',
    '- Control de Acceso: Rol MEDICO_TELECONSULTOR y Rol AUDITOR_FORENSE',
    '- Puertos Salientes: TCP 443 (WSS/HTTPS), UDP 3478 (STUN/TURN), UDP 10000-20000'
) '#EFF6FF' '#1D4ED8' '#1E3A8A' '#FFFFFF' 19 16 48

Draw-Card $g 45 640 1370 865 '<<execution environment>> Centro de Datos Institucional On-Premise (Cluster Kubernetes HA - SLA 99,999%)' @() '#F1F5F9' '#0F172A' '#16324F' '#FFFFFF' 20 16 52

Draw-Card $g 80 720 620 350 '<<artifact>> Microservicio Cohesivo Expediente-Ordenes' @(
    '- Runtime: Python 3.13.9 + FastAPI + Uvicorn ASGI (:8000)',
    '- Patrones: Strategy (Triage/Sync), Observer, Repository',
    '- Contratos Externos: API REST JSON HL7 FHIR R4 (TCP 443/8000)',
    '- Comunicacion Interna: gRPC / Protocol Buffers sobre mTLS (:50051)',
    '- Validacion Borde: Esquemas declarativos Pydantic v2'
) '#FFFFFF' '#1E3A8A' '#1E3A8A' '#FFFFFF' 18 16 46

Draw-Card $g 760 720 620 350 '<<database>> Nucleo Relacional Transaccional (CP)' @(
    '- Motor Productivo: PostgreSQL 16 Lider-Replica Sincrona (:5432)',
    '- Motor MVP Ejecutable: SQLite 3 en modo WAL (hce_urgencia_caso5.db)',
    '- Tablas: users, patients (vector version), medical_orders, sync_conflicts',
    '- Tabla Series: vital_sign_observations (Indice Unico idempotency_key)',
    '- Cifrado en Reposo: AES-256 gestionado por HSM externo'
) '#FFFFFF' '#1E3A8A' '#1E3A8A' '#FFFFFF' 18 16 46

Draw-Card $g 80 1125 1300 345 '<<isolated security zone>> Segmento de Red Aislado: Servicio de Auditoria Forense y HSM (ADR-03 / ADR-08)' @(
    '- Artefacto: forensic-audit-ledger-service + Tabla Inmutable audit_ledger (Encadenamiento Criptografico SHA-256: prev_hash -> current_hash)',
    '- Aislamiento Normativo: Subred privada sin ruta de salida a Internet y sin credenciales administrativas compartidas con el resto del cluster',
    '- Inmutabilidad Verificable: El usuario de BD del servicio carece de privilegios SQL UPDATE y DELETE (solo INSERT y SELECT para verificacion)',
    '- Hardware Security Module (HSM FIPS 140-3): Custodia de llaves maestras JWT/AES-256 - Puerto Interno Exclusivo mTLS: TCP 8443'
) '#FEF2F2' '#DC2626' '#991B1B' '#FFFFFF' 18 16 46

Draw-Card $g 1465 640 890 865 '<<cloud environment>> Nube Publica Multi-AZ Elegible HIPAA (Componentes Elasticos de Rafaga 10x / 20x)' @() '#FFFBEB' '#B45309' '#92400E' '#FFFFFF' 20 16 52

Draw-Card $g 1500 720 820 350 '<<artifact>> Cluster Pasarela Multimedia WebRTC (SFU) + Subtitulado' @(
    '- Escalabilidad: Autoescalado horizontal por numero de sesiones activas (Referente Zoom 2020)',
    '- Senalizacion: WebSocket Seguro WSS (TCP 443) | Transporte Media: SRTP sobre UDP (10000-20000)',
    '- Resiliencia: Degradacion adaptativa de resolucion de video antes que desconexion de llamada',
    '- Servicio Desacoplado de Subtitulado Clinico en Vivo suscrito al audio del SFU (Circuit Breaker activo)'
) '#FFFFFF' '#B45309' '#B45309' '#FFFFFF' 18 16 46

Draw-Card $g 1500 1125 820 345 '<<database / storage>> Ingesta Telemetria (AP) y Almacenamiento Clinico (AP)' @(
    '- Broker MQTT (TCP 8883 TLS, QoS 1) + Base de Series de Tiempo TimescaleDB (:5432) por lotes',
    '- Almacen Documental MongoDB (:27017) para recursos FHIR R4 variables de sistemas legados',
    '- Object Storage S3-Compatible (:443, AES-256) para estudios de imagen DICOM y grabaciones SRTP',
    '- Infraestructura como Codigo (Terraform) portable entre proveedores para mitigar Vendor Lock-in'
) '#FFFFFF' '#B45309' '#B45309' '#FFFFFF' 18 16 46

Draw-Arrow $g 390 510 390 720 'HTTPS REST FHIR R4 (TLS 1.3 :443)' '#1D4ED8' $false -20
Draw-Arrow $g 1180 510 560 720 'HTTPS REST + JWT (:443)' '#1D4ED8' $false 15
Draw-Arrow $g 1950 510 1910 720 'WSS (:443) + SRTP (UDP 10000-20000)' '#B45309'
Draw-Arrow $g 700 895 760 895 ':5432' '#0F172A'
Draw-Arrow $g 390 1070 390 1125 'mTLS :8443' '#DC2626'
Draw-Arrow $g 1415 575 1465 575 'Enlace Privado HA mTLS' '#059669'

$p3 = Join-Path $OutDir '3_diagrama_despliegue_hibrido_uml.png'
$c3.Bitmap.Save($p3, [System.Drawing.Imaging.ImageFormat]::Png)
$c3.Graphics.Dispose(); $c3.Bitmap.Dispose()

# =============================================================================
# 4. DIAGRAMA DE CLASES Y COMPONENTES DE LOS 4 PATRONES IMPLEMENTADOS
# =============================================================================
$c4 = New-Canvas 2400 1550
$g = $c4.Graphics
Draw-TitleBanner $g 'DIAGRAMA DE CLASES Y COMPONENTES UML - 4 PATRONES DE DISENO APLICADOS EN EL CODIGO FUENTE' 'Evidencia de Implementacion (Criterio 2.2): MVVM (Frontend) + Strategy, Observer y Repository (Backend Python/FastAPI)'

Draw-Card $g 55 160 685 570 'PATRON 1: MVVM + Outbox (Frontend React 18)' @(
    'Archivo View: frontend/src/App.jsx',
    '  + Renderiza Panel Urgencia, Ficha FHIR, Teleconsulta y Auditoria',
    '  + Conmuta Tema Alto Contraste WCAG 2.2 AAA (7:1) y Botones >= 48px',
    '',
    'Archivo ViewModel: frontend/src/viewmodels/useClinicalViewModel.js',
    '  + session, episodeState, outboxQueue, latestVitals, pendingConflicts',
    '  + submitVitalSigns(), drainOutboxQueue(), toggleOfflineTunnel()',
    '  + updateMutableField(), resolveClinicalConflict(), submitMedicalOrder()',
    '',
    'Archivo Model: frontend/src/models/clinicalApi.js',
    '  + enqueueOutboxTransaction(UUID), clearOutboxTransaction(UUID)',
    '  + Clientes HTTP/REST para endpoints FHIR R4'
) '#EFF6FF' '#1D4ED8' '#1E3A8A' '#FFFFFF' 19 16 48

Draw-Card $g 855 160 685 570 'ORQUESTADOR DE DOMINIO (Servicio Cohesivo ADR-03)' @(
    'Archivo Router: backend/app/routers/api_router.py',
    '  + get_current_user(Bearer JWT HS256)',
    '  + require_roles([PARAMEDICO, MEDICO_URGENCIA, ...])',
    '',
    'Archivo Servicio: backend/app/services/clinical_service.py',
    'Clase: ClinicalEHRService',
    '  - db: Session | - repo: PatientEHRRepository',
    '  - triage_strategy: ClinicalTriageStrategy',
    '  + get_patient_ehr(patient_id, actor) -> PatientModel',
    '  + record_vital_signs_triage(patient_id, payload, actor)',
    '  + update_mutable_clinical_field(patient_id, payload, actor)',
    '  + resolve_sync_conflict(conflict_id, payload, actor)',
    '  + create_medical_order(patient_id, payload, actor)'
) '#F8FAFC' '#0F172A' '#16324F' '#FFFFFF' 19 16 48

Draw-Card $g 1655 160 685 570 'PATRON 2: STRATEGY (clinical_strategies.py)' @(
    '<<interface>> ClinicalTriageStrategy (ABC)',
    '  + evaluate(hr, spo2, sys, dia, temp, glasgow) -> TriageEvaluationResult',
    'Clase Concreta: EmergencySeverityIndexStrategy',
    '  + Clasifica ESI-1 Critico (SpO2 < 90%), ESI-2 Alto Riesgo, ESI-3 Estable',
    '',
    '<<interface>> SyncResolutionStrategy (ABC - ADR-05)',
    '  + can_auto_merge(client_version, server_version) -> Tuple[bool, str]',
    'Clases Concretas:',
    '  1. AppendOnlyCRDTGSetStrategy (Fusion conmutativa por UUID)',
    '  2. OptimisticConcurrencyClinicalArbitrationStrategy (Desvia a arbitraje)',
    '',
    'Clase Concreta: DrugSafetyGuardStrategy (ADR-03)',
    '  + check_allergy_contraindication(allergies, drug) -> Bloquea Penicilina'
) '#ECFDF5' '#059669' '#065F46' '#FFFFFF' 19 16 48

Draw-Card $g 140 870 980 600 'PATRON 3: OBSERVER (backend/app/observers/audit_observer.py)' @(
    'Clase Publicadora (Subject): ClinicalDomainEventBus',
    '  - _observers: List[ClinicalEventObserver]',
    '  + subscribe(observer: ClinicalEventObserver) -> None',
    '  + publish(db: Session, event: ClinicalDomainEvent) -> None',
    '',
    '<<interface>> ClinicalEventObserver (ABC)',
    '  + on_clinical_event(db: Session, event: ClinicalDomainEvent) -> None',
    '',
    'Suscriptor Concreto 1: ForensicAuditLedgerObserver (ADR-03 / ADR-08)',
    '  + compute_entry_hash(seq, actor, role, action, resource, details, ts, prev_hash) -> SHA-256',
    '  + Encadena cada lectura y escritura al bloque previo en la tabla audit_ledger',
    '',
    'Suscriptor Concreto 2: CriticalTelemetryAlertObserver',
    '  + Mantiene buffer en tiempo real de alertas ESI-1, conflictos y bloqueos de seguridad'
) '#FEF2F2' '#DC2626' '#991B1B' '#FFFFFF' 19 16 48

Draw-Card $g 1280 870 980 600 'PATRON 4: REPOSITORY (backend/app/repositories/ehr_repository.py)' @(
    'Clase: PatientEHRRepository (Agregado Expediente-Ordenes)',
    '  + get_vital_sign_by_idempotency_key(UUID) -> Previene duplicados Store-and-Forward',
    '  + save_vital_sign_observation(obs) / save_medical_order(order)',
    '  + update_mutable_field(patient, field, val) -> Incrementa atomicamente version + 1',
    '  + create_sync_conflict(...) / resolve_conflict(...) -> Gestiona tabla sync_conflicts',
    '',
    'Clase: AuditLedgerRepository (Inmutabilidad Estructural ADR-03)',
    '  + list_entries(limit=100) -> List[AuditLedgerModel]',
    '  + verify_chain_integrity() -> Recorre desde Genesis recalculando SHA-256 (0 adulteraciones)',
    '  * Carece deliberadamente de metodos update() y delete()',
    '',
    'Clase: UserRepository -> Gestion de los 4 perfiles RBAC institucionales'
) '#FFFBEB' '#B45309' '#92400E' '#FFFFFF' 19 16 48

Draw-Arrow $g 740 445 855 445 'REST FHIR R4' '#1D4ED8'
Draw-Arrow $g 1540 445 1655 445 'Inyecta Strategy' '#059669'
Draw-Arrow $g 1020 730 680 870 'Publica Evento Dominio (Observer)' '#DC2626'
Draw-Arrow $g 1380 730 1680 870 'Persiste via Repository' '#B45309'
Draw-Arrow $g 1120 1170 1280 1170 'Inserta Bloque SHA-256' '#991B1B'

$p4 = Join-Path $OutDir '4_diagrama_patrones_implementados.png'
$c4.Bitmap.Save($p4, [System.Drawing.Imaging.ImageFormat]::Png)
$c4.Graphics.Dispose(); $c4.Bitmap.Dispose()

Write-Output "4 Diagramas PNG perfeccionados en: $OutDir"
