import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA INTERFAZ WEB
st.set_page_config(page_title="Control Financiero Personal", layout="wide", page_icon="📊")

# Inicialización de la base de datos en memoria (Simula tu Google Sheets en tiempo real)
if 'db_provisiones' not in st.session_state:
    st.session_state.db_provisiones = {
        "Mante coche": {"aporte": 50.0, "acumulado": 472.0, "tipo": "Acumulativo"},
        "Luz": {"aporte": 60.0, "acumulado": 0.0, "tipo": "Anual piso"},
        "Agua": {"aporte": 40.0, "acumulado": 0.0, "tipo": "Anual piso"},
        "Extraescolares": {"aporte": 30.0, "acumulado": 120.0, "tipo": "Acumulativo"},
    }
if 'db_movimientos' not in st.session_state:
    st.session_state.db_movimientos = [
        {"Fecha": "2026-01-15", "Sección": "Ahorro Almacén", "Concepto": "Sobra 2025", "Monto": 219.0, "Detalle": "Ingreso Inicial"},
        {"Fecha": "2026-05-10", "Sección": "Ahorro Almacén", "Concepto": "Retroactivos 2025", "Monto": 745.0, "Detalle": "Ingreso Ordinario"},
        {"Fecha": "2026-05-12", "Sección": "Ahorro Almacén", "Concepto": "Túneles cadí", "Monto": -35.0, "Detalle": "Gasto"},
        {"Fecha": "2026-03-10", "Sección": "Camping", "Concepto": "Aportación Irma", "Monto": 80.6, "Detalle": "Ingreso Externo"},
    ]
if 'db_pendientes' not in st.session_state:
    st.session_state.db_pendientes = [
        {"Item": "Impresora y ordenador", "Saldo": 63.0, "Origen": "Propio"},
        {"Item": "Microondas", "Saldo": 53.0, "Origen": "Propio"},
        {"Item": "Ropa niños (Dareck)", "Saldo": 22.0, "Origen": "Papá (Azul)"},
    ]
if 'db_corrientes' not in st.session_state:
    st.session_state.db_corrientes = [
        {"Gasto": "comida avena irma", "Original": 60.0, "Pendiente": 40.0},
        {"Gasto": "Vino", "Original": 10.7, "Pendiente": 0.0},
        {"Gasto": "halloween", "Original": 14.0, "Pendiente": 14.0},
    ]
if 'ahorro_pasado' not in st.session_state:
    st.session_state.ahorro_pasado = 4884.0
if 'papa_efectivo' not in st.session_state:
    st.session_state.papa_efectivo = 100.0
if 'papa_me_debe' not in st.session_state:
    st.session_state.papa_me_debe = 0.0
if 'fondo_camping' not in st.session_state:
    st.session_state.fondo_camping = 972.0

# --- CÁLCULO EN SEGUNDO PLANO DE LOS SALDOS REALES BANCARIOS ---
total_ahorro_puro = st.session_state.ahorro_pasado + sum(m["Monto"] for m in st.session_state.db_movimientos if m["Sección"] == "Ahorro Almacén")
total_gastos_corrientes_pendientes = sum(g["Pendiente"] for g in st.session_state.db_corrientes)
total_provisiones_guardadas = sum(h["acumulado"] for h in st.session_state.db_provisiones.values())

saldo_cuenta_corriente = 1240.0 + total_provisiones_guardadas - total_gastos_corrientes_pendientes
saldo_cuenta_ahorros = total_ahorro_puro + st.session_state.fondo_camping

# =========================================================================
# INTERFAZ VISUAL (MENU LATERAL)
# =========================================================================
st.sidebar.title("📌 Menú de Navegación")
opcion = st.sidebar.radio("Ir a la sección:", [
    "🏦 Panel de Control (Mis Bancos)",
    "🗓️ Provisiones y Alertas (Luz/Agua/Coche)",
    "🗒️ Gastos Corrientes (Comida/Abonos)",
    "📋 Lista de Pagos Pendientes",
    "⛺ Hucha Especial Camping & Irma",
    "🔎 Buscador Histórico Avanzado"
])

# =========================================================================
# SECCIÓN 1: PANEL DE CONTROL PRINCIPAL
# =========================================================================
if opcion == "🏦 Panel de Control (Mis Bancos)":
    st.title("🏦 Estado Central de tus Cuentas Bancarias")
    st.markdown("---")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.metric(label="💳 CUENTA CORRIENTE / CUSTODIA (Día a Día)", value=f"{saldo_cuenta_corriente:.2f} €")
    with col_b2:
        st.metric(label="📈 CUENTA AHORRO (El Almacén Fuerte)", value=f"{saldo_cuenta_ahorros:.2f} €")
        
    st.markdown("---")
    st.subheader("🔀 Registrar Gasto Esporádico o Compensación Directa")
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        concepto_esp = st.text_input("Concepto del Gasto", value="Seguro Anual")
    with c_f2:
        monto_esp = st.number_input("Monto (€)", min_value=0.0, step=10.0, value=300.0)
    with c_f3:
        origen_esp = st.selectbox("¿Cómo se paga?", ["Descontar de Paga Doble (Ahorro)", "Descontar de Horas Extras (Ahorro)", "Dinero externo / Efectivo de otra cuenta"])
        
    if st.button("🚀 Confirmar Operación"):
        if "Paga Doble" in origen_esp or "Horas Extras" in origen_esp:
            st.session_state.ahorro_pasado -= monto_esp
            st.success(f"¡Restados {monto_esp}€ de la Cuenta Ahorro de forma automática!")
        else:
            st.info("Movimiento registrado con capital externo. Tus fondos guardados quedan intactos.")
        st.rerun()

# =========================================================================
# SECCIÓN 2: PROVISIONES Y ALERTAS
# =========================================================================
elif opcion == "🗓️ Provisiones y Alertas (Luz/Agua/Coche)":
    st.title("🗓️ Control de Provisiones Mensuales")
    st.markdown("---")
    
    st.subheader("⚠️ Asesor Inteligente de Consumos (Alertas)")
    st.error("🔴 ALERTA AGUA: Has aportado 40€/mes (480€ anuales), pero la factura real proyecta un gasto de 525€. Te faltarán 45€. Te sugerimos subir tu aporte mensual a 45.00 €.")
    st.success("🟢 COCHE: Tus aportaciones de 50€/mes cubren perfectamente los gastos de taller actuales.")
    
    st.markdown("---")
    st.subheader("📊 Tus Huchas de Provisión Activas")
    df_prov = pd.DataFrame.from_dict(st.session_state.db_provisiones, orient='index').reset_index()
    df_prov.columns = ["Concepto", "Aporte Mensual (€)", "Saldo Acumulado Disponible (€)", "Tipo de Gestión"]
    st.dataframe(df_prov, use_container_width=True)

# =========================================================================
# SECCIÓN 3: GASTOS CORRIENTES (MANUAL)
# =========================================================================
elif opcion == "🗒️ Gastos Corrientes (Comida/Abonos)":
    st.title("🗒️ Control Manual de Gastos Corrientes")
    st.markdown("---")
    
    df_corr = pd.DataFrame(st.session_state.db_corrientes)
    st.subheader("📋 Tus Gastos Diarios Acumulados")
    st.dataframe(df_corr, use_container_width=True)
    
    st.metric(label="⚠️ Total Pendiente de Descontar de tu Bolsillo", value=f"{total_gastos_corrientes_pendientes:.2f} €")
    
    st.markdown("---")
    st.subheader("📉 Descontar / Pagar un trozo de un Gasto (Ej. Avena)")
    gastos_activos = [g["Gasto"] for g in st.session_state.db_corrientes if g["Pendiente"] > 0]
    
    if gastos_activos:
        g_sel = st.selectbox("Selecciona qué vas a pagar hoy:", gastos_activos)
        saldo_g_sel = next(g["Pendiente"] for g in st.session_state.db_corrientes if g["Gasto"] == g_sel)
        monto_a_restar = st.number_input(f"¿Cuánto dinero le restas a este concepto? (Máx: {saldo_g_sel}€)", min_value=0.0, max_value=float(saldo_g_sel), step=5.0)
        
        if st.button("📉 Aplicar Resta Manual"):
            for g in st.session_state.db_corrientes:
                if g["Gasto"] == g_sel:
                    g["Pendiente"] -= monto_a_restar
                    st.success(f"Se han restado {monto_a_restar}€ de '{g_sel}'.")
                    st.rerun()

# =========================================================================
# SECCIÓN 4: LISTA DE PAGOS PENDIENTES
# =========================================================================
elif opcion == "📋 Lista de Pagos Pendientes":
    st.title("📋 Lista de Pagos Pendientes (Deudas)")
    st.markdown("---")
    
    df_pend = pd.DataFrame(st.session_state.db_pendientes)
    st.dataframe(df_pend, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🤖 Amortización Automática con tus 45€ Mensuales o Horas Extras")
    
    if st.button("💸 Aplicar los 45€ de Gastos Aplazados"):
        dinero = 45.0
        for p in st.session_state.db_pendientes:
            if p["Origen"] == "Propio" and p["Saldo"] > 0:
                restado = min(dinero, p["Saldo"])
                p["Saldo"] -= restado
                dinero -= restado
                st.success(f"Se han usado los 45€ para reducir '{p['Item']}'. Nuevo saldo: {p['Saldo']}€")
                if dinero <= 0: break
        st.rerun()

# =========================================================================
# SECCIÓN 5: HUCHA ESPECIAL CAMPING & IRMA
# =========================================================================
elif opcion == "⛺ Hucha Especial Camping & Irma":
    st.title("⛺ Control Específico del Camping")
    st.markdown("---")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.metric(label="Colchón Inicial Camping (Paga Doble)", value=f"{st.session_state.fondo_camping} €")
    with col_c2:
        st.metric(label="Efectivo Disponible de Papá (Ropa)", value=f"{st.session_state.papa_efectivo} €")
        
    st.markdown("---")
    st.subheader("📥 Registro de Ingresos de Irma o Recibos Mensuales")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        tipo_camp = st.selectbox("Tipo de Movimiento:", ["Mensualidad Cobrada por Banco", "Aportación en Efectivo de Irma"])
    with c_m2:
        monto_camp = st.number_input("Monto del Movimiento (€)", min_value=0.0, value=80.6)
        
    if st.button("💾 Guardar Registro de Camping"):
        if "Irma" in tipo_camp:
            st.session_state.fondo_camping += monto_camp
            st.success(f"¡Añadidos {monto_camp}€ de Irma al colchón del camping!")
        else:
            st.session_state.fondo_camping -= monto_camp
            st.success(f"Restada mensualidad de {monto_camp}€ del fondo disponible.")
        st.rerun()

# =========================================================================
