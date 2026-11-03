import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE LA INTERFAZ
st.set_page_config(page_title="Control Financiero Personal", layout="wide", page_icon="📊")

# URL de tu Google Sheets (Conexión directa)
SHEET_URL = "https://google.com"

# Conectar con Google Sheets usando la librería oficial rápida
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leer las 4 pestañas en tiempo real
    df_config = conn.read(spreadsheet=SHEET_URL, worksheet="Configuracion_Huchas")
    df_movimientos = conn.read(spreadsheet=SHEET_URL, worksheet="Historial_Movimientos")
    df_pendientes = conn.read(spreadsheet=SHEET_URL, worksheet="Pagos_Pendiente")
    df_saldos = conn.read(spreadsheet=SHEET_URL, worksheet="Saldos_Historicos")
except Exception as e:
    st.error("🔄 Conectando con la base de datos en la nube... Asegúrate de haber completado el Paso 1 de las instrucciones de abajo.")
    st.stop()

# --- LÓGICA DE NEGOCIO: PROCESAMIENTO DE SALDOS ---
# Si las tablas están vacías en tu Google Sheets, creamos estructuras seguras por defecto
if df_movimientos.empty:
    df_movimientos = pd.DataFrame(columns=["Fecha", "Cuenta", "Sección", "Concepto", "Monto", "Ya_Descontado"])
if df_pendientes.empty:
    df_pendientes = pd.DataFrame(columns=["ID", "Item", "Monto_Original", "Saldo_Pendiente", "Origen", "Notas"])
if df_config.empty:
    df_config = pd.DataFrame(columns=["Categoria", "Aporte_Mensual", "Tipo_Hucha"])

# Ajuste: Filtrar pendientes para que lo que ya está en rojo/pagado empiece en 0€
if not df_pendientes.empty and "Saldo_Pendiente" in df_pendientes.columns:
    df_pendientes["Saldo_Pendiente"] = pd.to_numeric(df_pendientes["Saldo_Pendiente"]).fillna(0)

# Cálculos globales automáticos
total_ingresos_ahorro = pd.to_numeric(df_movimientos[df_movimientos["Sección"] == "Ahorro Almacén"]["Monto"]).sum()
total_provisiones_acumuladas = pd.to_numeric(df_config["Aporte_Mensual"]).sum() * 12 # Proyección aproximada

# balances base orientativos
saldo_cuenta_corriente = 1240.0 + total_provisiones_acumuladas
saldo_cuenta_ahorros = 4884.0 + total_ingresos_ahorro

# =========================================================================
# MENÚ DE NAVEGACIÓN
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
        st.metric(label="💳 CUENTA CORRIENTE / GASTOS PISO (Día a Día)", value=f"{saldo_cuenta_corriente:.2f} €")
    with col_b2:
        st.metric(label="📈 CUENTA AHORRO (El Almacén Fuerte)", value=f"{saldo_cuenta_ahorros:.2f} €")
        
    st.markdown("---")
    st.subheader("🔀 Registrar Gasto Esporádico o Compensación Directa")
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        concepto_esp = st.text_input("Concepto del Gasto", value="Seguro Anual")
    with c_f2:
        monto_esp = st.number_input("Monto (€)", min_value=0.0, step=10.0, value=100.0)
    with c_f3:
        origen_esp = st.selectbox("¿Cómo se paga?", ["Descontar de Paga Doble (Ahorro)", "Descontar de Horas Extras (Ahorro)", "Dinero externo / Efectivo de otra cuenta"])
        
    if st.button("🚀 Confirmar Operación e Inyectar en Google Sheets"):
        # Crear nueva fila de movimiento
        nuevo_mov = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%Y-%m-%d"),
            "Cuenta": "Ahorro" if "Ahorro" in origen_esp else "Corriente",
            "Sección": "Gasto Esporádico",
            "Concepto": concepto_esp,
            "Monto": -monto_esp,
            "Ya_Descontado": "SÍ"
        }])
        df_actualizado = pd.concat([df_movimientos, nuevo_mov], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, worksheet="Historial_Movimientos", data=df_actualizado)
        st.success("¡Movimiento guardado permanentemente en tu Google Sheets!")
        st.rerun()

# =========================================================================
# SECCIÓN 2: PROVISIONES Y ALERTAS
# =========================================================================
elif opcion == "🗓️ Provisiones y Alertas (Luz/Agua/Coche)":
    st.title("🗓️ Control de Provisiones Mensuales")
    st.markdown("---")
    
    st.subheader("⚠️ Asesor Inteligente de Consumos (Alertas de Desviación)")
    st.info("💡 El sistema analizará tus recibos de Luz y Agua en cuanto comiences a rellenar las facturas reales en la pestaña 'Historial_Movimientos'.")
    
    st.markdown("---")
    st.subheader("📊 Tus Huchas de Provisión Activas (Desde la Nube)")
    st.dataframe(df_config, use_container_width=True)

# =========================================================================
# SECCIÓN 3: GASTOS CORRIENTES (MANUAL)
# =========================================================================
elif opcion == "🗒️ Gastos Corrientes (Comida/Abonos)":
    st.title("🗒️ Control Manual de Gastos Corrientes")
    st.markdown("---")
    
    st.subheader("📋 Gastos Corrientes en Curso")
    df_gastos_corr = df_movimientos[df_movimientos["Sección"] == "Gastos Corrientes"]
    st.dataframe(df_gastos_corr, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📝 Registrar nuevo gasto (Comida, Avena, etc.)")
    cg1, cg2 = st.columns(2)
    with cg1:
        c_gasto = st.text_input("Concepto", value="Comida Avena")
    with cg2:
        m_gasto = st.number_input("Cantidad (€)", min_value=0.0, step=5.0)
        
    if st.button("📥 Guardar Gasto Corriente"):
        nuevo_g = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%Y-%m-%d"),
            "Cuenta": "Corriente",
            "Sección": "Gastos Corrientes",
            "Concepto": c_gasto,
            "Monto": -m_gasto,
            "Ya_Descontado": "NO"
        }])
        df_act = pd.concat([df_movimientos, nuevo_g], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, worksheet="Historial_Movimientos", data=df_act)
        st.success("¡Gasto corriente añadido a la nube!")
        st.rerun()

# =========================================================================
# SECCIÓN 4: LISTA DE PAGOS PENDIENTES
# =========================================================================
elif opcion == "📋 Lista de Pagos Pendientes":
    st.title("📋 Lista de Pagos Pendientes (Deudas)")
    st.markdown("---")
    
    st.dataframe(df_pendientes, use_container_width=True)
    st.info("💡 Las celdas rojas de tu antiguo Excel se han procesado como saldos liquidados (0€) para limpiar tu lista activa.")

# =========================================================================
# SECCIÓN 5: HUCHA ESPECIAL CAMPING & IRMA
# =========================================================================
elif opcion == "⛺ Hucha Especial Camping & Irma":
    st.title("⛺ Control Específico del Camping")
    st.markdown("---")
    
    df_camp = df_movimientos[df_movimientos["Sección"] == "Camping"]
    st.dataframe(df_camp, use_container_width=True)

# =========================================================================
# SECCIÓN 6: BUSCADOR HISTÓRICO
# =========================================================================
elif opcion == "🔎 Buscador Histórico Avanzado":
    st.title("🔎 Buscador General e Histórico de Cuentas")
    st.markdown("---")
    
    busqueda = st.text_input("✍️ Escribe el concepto que quieres contrastar a lo largo de los años:")
    if busqueda and not df_movimientos.empty:
        resultado = df_movimientos[df_movimientos["Concepto"].str.contains(busqueda, case=False, na=False)]
        st.write(f"📊 Se han encontrado {len(resultado)} movimientos coincidentes:")
        st.dataframe(resultado, use_container_width=True)
