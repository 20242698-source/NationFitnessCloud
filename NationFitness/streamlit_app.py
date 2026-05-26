import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
from datetime import datetime, timedelta
import database_manager as db

# Configuración de la página
st.set_page_config(page_title="Nation Fitness", layout="wide", initial_sidebar_state="expanded")

# Inicializar estado de sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "rol" not in st.session_state:
    st.session_state.rol = ""

# ==================== FUNCIONES DE AUTENTICACIÓN ====================
def login(usuario, clave):
    rol = db.validar_usuario(usuario, clave)
    if rol:
        st.session_state.logged_in = True
        st.session_state.username = usuario
        st.session_state.rol = rol
        return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.rol = ""

# ==================== FUNCIÓN DE VALIDACIÓN DE TELÉFONO ====================
def validar_telefono(telefono):
    """Verifica que el teléfono tenga exactamente 10 dígitos numéricos."""
    if not telefono:
        return True  # Permitir vacío? Depende. Lo dejamos opcional, pero si se ingresa debe tener 10 dígitos.
    return bool(re.fullmatch(r"\d{10}", telefono))

# ==================== PANTALLA DE LOGIN ====================
if not st.session_state.logged_in:
    st.title("🏋️ Nation Fitness - Sistema de Gestión")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo.jpg", width=250) if os.path.exists("logo.jpg") else None
        with st.form("login_form"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar")
            if submit:
                if login(usuario, clave):
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
    st.stop()

# ==================== MENÚ PRINCIPAL ====================
def main_app():
    # Sidebar con info del usuario
    st.sidebar.image("logo.jpg", width=200) if os.path.exists("logo.jpg") else None
    st.sidebar.title(f"Bienvenido, {st.session_state.username}")
    st.sidebar.markdown(f"**Rol:** {st.session_state.rol}")
    if st.sidebar.button("Cerrar sesión"):
        logout()
        st.rerun()
    
    # Menú según rol
    st.sidebar.markdown("---")
    if st.session_state.rol == "administrador":
        opciones = [
            "🏠 Dashboard",
            "👥 Socios",
            "📅 Membresías",
            "💰 Catálogo de planes",
            "💸 Egresos",
            "👤 Usuarios",
            "📊 Reportes",
            "📈 Contabilidad"
        ]
    else:  # recepcionista
        opciones = [
            "🏠 Dashboard",
            "👥 Socios",
            "📅 Membresías",
            "💰 Catálogo de planes",
            "📊 Reportes",
            "📈 Contabilidad"
        ]
    
    seleccion = st.sidebar.radio("Navegación", opciones)
    
    # ==================== DASHBOARD ====================
    if seleccion == "🏠 Dashboard":
        st.title("Panel de control")
        col1, col2, col3, col4 = st.columns(4)
        total_socios = db.obtener_total_socios()
        ingresos_mes = db.obtener_ingresos_mes_actual()
        egresos_mes = db.obtener_egresos_mes_actual()
        utilidad = ingresos_mes - egresos_mes
        col1.metric("Total Socios", total_socios)
        col2.metric("Ingresos del mes", f"${ingresos_mes:,.2f}")
        col3.metric("Egresos del mes", f"${egresos_mes:,.2f}")
        col4.metric("Utilidad", f"${utilidad:,.2f}", delta_color="normal" if utilidad>=0 else "inverse")
        
        st.subheader("Membresías por vencer (próximos 7 días)")
        por_vencer = db.obtener_membresias_por_vencer(7)
        if por_vencer:
            df_venc = pd.DataFrame(por_vencer, columns=["Socio", "Plan", "Vencimiento"])
            st.dataframe(df_venc, width='stretch')
        else:
            st.info("No hay membresías próximas a vencer")
        
        st.subheader("Últimos pagos")
        ultimos = db.obtener_ultimos_pagos(5)
        if ultimos:
            df_pagos = pd.DataFrame(ultimos, columns=["Socio", "Plan", "Monto", "Fecha"])
            st.dataframe(df_pagos, width='stretch')
    
    # ==================== SOCIOS ====================
    elif seleccion == "👥 Socios":
        st.title("Gestión de Socios")
        tab1, tab2, tab3 = st.tabs(["Lista de socios", "Registrar socio", "Editar / Eliminar"])
        
        with tab1:
            socios = db.obtener_socios_con_estado()
            if socios:
                df_socios = pd.DataFrame(socios, columns=["ID", "Clave", "Nombre", "Paterno", "Materno", "Teléfono", "Email", "Observaciones", "Fecha creación", "Estado", "Vencimiento"])
                st.dataframe(df_socios, width='stretch')
                # Búsqueda
                busqueda = st.text_input("Buscar socio (nombre, apellido o clave)")
                if busqueda:
                    resultados = db.buscar_socios_filtro(busqueda)
                    if resultados:
                        st.dataframe(pd.DataFrame(resultados), width='stretch')
            else:
                st.info("No hay socios registrados")
        
        with tab2:
            with st.form("registro_socio"):
                col1, col2 = st.columns(2)
                with col1:
                    clave = st.text_input("Clave (ID único)")
                    nombre = st.text_input("Nombre")
                    paterno = st.text_input("Apellido paterno")
                    materno = st.text_input("Apellido materno")
                with col2:
                    telefono = st.text_input("Teléfono (10 dígitos, solo números)")
                    email = st.text_input("Email")
                    observaciones = st.text_area("Observaciones")
                submit = st.form_submit_button("Registrar socio")
                if submit:
                    # Validaciones
                    errores = []
                    if not clave or not nombre:
                        errores.append("Clave y nombre son obligatorios.")
                    if telefono and not validar_telefono(telefono):
                        errores.append("El teléfono debe tener exactamente 10 dígitos numéricos.")
                    if errores:
                        for err in errores:
                            st.error(err)
                    else:
                        # Verificar duplicado
                        if db.existe_socio_duplicado(clave, nombre, paterno, materno):
                            st.error("Ya existe un socio con esa clave/nombre completo")
                        else:
                            db.insertar_socio((clave, nombre, paterno, materno, telefono, email, observaciones))
                            st.success("Socio registrado correctamente")
                            st.rerun()
        
        with tab3:
            socios_edit = db.obtener_socios()
            if socios_edit:
                socio_seleccionado = st.selectbox("Seleccionar socio", socios_edit, format_func=lambda x: f"{x[0]} - {x[2]} {x[3]}")
                if socio_seleccionado:
                    id_socio = socio_seleccionado[0]
                    with st.form("editar_socio"):
                        clave = st.text_input("Clave", socio_seleccionado[1])
                        nombre = st.text_input("Nombre", socio_seleccionado[2])
                        paterno = st.text_input("Apellido paterno", socio_seleccionado[3])
                        materno = st.text_input("Apellido materno", socio_seleccionado[4])
                        telefono = st.text_input("Teléfono (10 dígitos)", socio_seleccionado[5])
                        email = st.text_input("Email", socio_seleccionado[6])
                        observaciones = st.text_area("Observaciones", socio_seleccionado[7])
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Actualizar"):
                                # Validar teléfono
                                if telefono and not validar_telefono(telefono):
                                    st.error("El teléfono debe tener exactamente 10 dígitos numéricos.")
                                else:
                                    if db.actualizar_socio(id_socio, (clave, nombre, paterno, materno, telefono, email, observaciones)):
                                        st.success("Socio actualizado")
                                        st.rerun()
                                    else:
                                        st.error("Error al actualizar")
                        with col2:
                            if st.form_submit_button("Eliminar socio"):
                                if st.checkbox("Confirmar eliminación permanente"):
                                    if db.eliminar_socio(id_socio):
                                        st.success("Socio eliminado")
                                        st.rerun()
                                    else:
                                        st.error("Error al eliminar")
            else:
                st.info("No hay socios para editar")
    
    # ==================== MEMBRESÍAS ====================
    elif seleccion == "📅 Membresías":
        st.title("Asignación de membresías")
        socios = db.obtener_socios()
        if not socios:
            st.warning("Primero registra un socio")
        else:
            socio_opciones = {f"{s[0]} - {s[2]} {s[3]}": s[0] for s in socios}
            seleccionado = st.selectbox("Seleccionar socio", list(socio_opciones.keys()))
            id_socio = socio_opciones[seleccionado]
            
            # Historial
            historial = db.obtener_historial_membresias(id_socio)
            if historial:
                st.subheader("Historial de membresías")
                df_hist = pd.DataFrame(historial, columns=["ID", "Inicio", "Vencimiento", "Tipo", "Precio", "Estado"])
                st.dataframe(df_hist, width='stretch')
            
            # Formulario nueva membresía
            with st.form("nueva_membresia"):
                planes = db.obtener_planes_membresia()
                if not planes:
                    st.error("No hay planes en el catálogo. Ve a 'Catálogo de planes' y agrega uno.")
                else:
                    plan_seleccionado = st.selectbox("Plan", planes, format_func=lambda x: f"{x[1]} - ${x[2]}")
                    fecha_inicio = st.date_input("Fecha de inicio", datetime.now())
                    duracion = st.selectbox("Duración", [30, 60, 90, 180, 365], format_func=lambda x: f"{x} días")
                    vencimiento = fecha_inicio + timedelta(days=duracion)
                    st.write(f"Vencimiento: {vencimiento.strftime('%Y-%m-%d')}")
                    observaciones = st.text_area("Observaciones")
                    if st.form_submit_button("Asignar membresía"):
                        tipo = plan_seleccionado[1]
                        precio = plan_seleccionado[2]
                        estado = "Activo"
                        datos = (id_socio, tipo, fecha_inicio.strftime("%Y-%m-%d"), vencimiento.strftime("%Y-%m-%d"), precio, "", estado, observaciones)
                        if db.asignar_membresia(datos):
                            st.success("Membresía asignada correctamente")
                            st.rerun()
                        else:
                            st.error("Error al asignar")
    
    # ==================== CATÁLOGO DE PLANES ====================
    elif seleccion == "💰 Catálogo de planes":
        st.title("Catálogo de membresías")
        if st.session_state.rol == "administrador":
            with st.expander("Agregar nuevo plan"):
                with st.form("nuevo_plan"):
                    nombre = st.text_input("Nombre del plan")
                    costo = st.number_input("Costo", min_value=0.0, step=50.0)
                    if st.form_submit_button("Guardar"):
                        if db.agregar_plan_membresia(nombre, costo):
                            st.success("Plan agregado")
                            st.rerun()
                        else:
                            st.error("Ya existe un plan con ese nombre")
        
        planes = db.obtener_planes_membresia()
        if planes:
            df_planes = pd.DataFrame(planes, columns=["ID", "Plan", "Costo"])
            st.dataframe(df_planes, width='stretch')
            
            if st.session_state.rol == "administrador":
                st.subheader("Editar / Eliminar planes")
                plan_editar = st.selectbox("Seleccionar plan", planes, format_func=lambda x: f"{x[1]} - ${x[2]}")
                if plan_editar:
                    id_plan, nombre_old, costo_old = plan_editar
                    with st.form("editar_plan"):
                        nuevo_nombre = st.text_input("Nombre", nombre_old)
                        nuevo_costo = st.number_input("Costo", value=float(costo_old), step=50.0)
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Actualizar"):
                                if db.actualizar_plan_membresia(id_plan, nuevo_nombre, nuevo_costo):
                                    st.success("Plan actualizado")
                                    st.rerun()
                        with col2:
                            if st.form_submit_button("Eliminar"):
                                if db.eliminar_plan_membresia(id_plan):
                                    st.success("Plan eliminado")
                                    st.rerun()
        else:
            st.info("No hay planes registrados")
    
    # ==================== EGRESOS ====================
    elif seleccion == "💸 Egresos" and st.session_state.rol == "administrador":
        st.title("Registro de egresos")
        with st.form("nuevo_egreso"):
            concepto = st.text_input("Concepto")
            monto = st.number_input("Monto", min_value=0.0, step=10.0)
            if st.form_submit_button("Registrar egreso"):
                if db.registrar_egreso(concepto, monto):
                    st.success("Egreso registrado")
                    st.rerun()
                else:
                    st.error("Error")
        
        egresos = db.obtener_egresos()
        if egresos:
            df_egresos = pd.DataFrame(egresos, columns=["ID", "Concepto", "Monto", "Fecha"])
            st.dataframe(df_egresos, width='stretch')
            
            # Editar/eliminar egresos
            st.subheader("Editar/Eliminar")
            egreso_seleccionado = st.selectbox("Seleccionar egreso", egresos, format_func=lambda x: f"{x[1]} - ${x[2]}")
            if egreso_seleccionado:
                id_eg, concepto_old, monto_old, fecha = egreso_seleccionado
                with st.form("editar_egreso"):
                    nuevo_concepto = st.text_input("Concepto", concepto_old)
                    nuevo_monto = st.number_input("Monto", value=float(monto_old), step=10.0)
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("Actualizar"):
                        if db.actualizar_egreso(id_eg, nuevo_concepto, nuevo_monto):
                            st.success("Actualizado")
                            st.rerun()
                    if col2.form_submit_button("Eliminar"):
                        if db.eliminar_egreso(id_eg):
                            st.success("Eliminado")
                            st.rerun()
        else:
            st.info("No hay egresos registrados")
    
    # ==================== USUARIOS (solo admin) ====================
    elif seleccion == "👤 Usuarios" and st.session_state.rol == "administrador":
        st.title("Gestión de usuarios")
        with st.form("nuevo_usuario"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            rol = st.selectbox("Rol", ["recepcionista", "administrador"])
            if st.form_submit_button("Crear usuario"):
                if db.agregar_usuario(usuario, clave, rol):
                    st.success("Usuario creado")
                    st.rerun()
                else:
                    st.error("El usuario ya existe o error en BD")
        
        usuarios = db.obtener_usuarios()
        if usuarios:
            df_usuarios = pd.DataFrame(usuarios, columns=["ID", "Usuario", "Rol"])
            st.dataframe(df_usuarios, width='stretch')
            
            # Eliminar usuarios (excepto admin actual)
            usuarios_no_admin = [u for u in usuarios if u[2] != "administrador"]
            if usuarios_no_admin:
                usuario_eliminar = st.selectbox("Eliminar usuario", usuarios_no_admin, format_func=lambda x: x[1])
                if st.button("Eliminar usuario seleccionado"):
                    db.eliminar_usuario(usuario_eliminar[0])
                    st.success("Usuario eliminado")
                    st.rerun()
            else:
                st.info("No hay usuarios no-admin para eliminar")
    
    # ==================== REPORTES ====================
    elif seleccion == "📊 Reportes":
        st.title("Reportes")
        tipo_reporte = st.selectbox("Tipo", ["Ingresos", "Egresos"])
        desde = st.date_input("Desde", datetime.now().replace(day=1))
        hasta = st.date_input("Hasta", datetime.now())
        if st.button("Generar"):
            if tipo_reporte == "Ingresos":
                datos = db.obtener_ingresos_filtrados(desde.strftime("%Y-%m-%d"), hasta.strftime("%Y-%m-%d"))
                if datos:
                    df = pd.DataFrame(datos, columns=["ID", "Clave", "Socio", "Plan", "Monto", "Fecha"])
                    st.dataframe(df, width='stretch')
                    total = df["Monto"].sum()
                    st.metric("Total ingresos", f"${total:,.2f}")
                else:
                    st.info("Sin ingresos en ese período")
            else:
                datos = db.obtener_egresos_filtrados(desde.strftime("%Y-%m-%d"), hasta.strftime("%Y-%m-%d"))
                if datos:
                    df = pd.DataFrame(datos, columns=["ID", "Concepto", "Monto", "Fecha"])
                    st.dataframe(df, width='stretch')
                    total = df["Monto"].sum()
                    st.metric("Total egresos", f"${total:,.2f}")
                else:
                    st.info("Sin egresos en ese período")
    
    # ==================== CONTABILIDAD ====================
    elif seleccion == "📈 Contabilidad":
        st.title("📊 Balance General - Contabilidad")
        st.markdown("Visualiza ingresos, egresos y utilidad con gráficos interactivos.")
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_desde = st.date_input("Desde", datetime.now().replace(day=1))
        with col2:
            fecha_hasta = st.date_input("Hasta", datetime.now())
        
        if st.button("Actualizar balance"):
            desde_str = fecha_desde.strftime("%Y-%m-%d")
            hasta_str = fecha_hasta.strftime("%Y-%m-%d")
            
            ingresos_raw = db.obtener_ingresos_filtrados(desde_str, hasta_str)
            egresos_raw = db.obtener_egresos_filtrados(desde_str, hasta_str)
            
            total_ingresos = sum(row[4] for row in ingresos_raw) if ingresos_raw else 0
            total_egresos = sum(row[2] for row in egresos_raw) if egresos_raw else 0
            utilidad = total_ingresos - total_egresos
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("💰 Ingresos totales", f"${total_ingresos:,.2f}")
            col_b.metric("💸 Egresos totales", f"${total_egresos:,.2f}")
            col_c.metric("📈 Utilidad neta", f"${utilidad:,.2f}", delta_color="normal" if utilidad >= 0 else "inverse")
            
            st.subheader("📅 Evolución mensual")
            if ingresos_raw or egresos_raw:
                df_ing = pd.DataFrame(ingresos_raw, columns=["ID", "Clave", "Socio", "Plan", "Monto", "Fecha"]) if ingresos_raw else pd.DataFrame(columns=["Fecha", "Monto"])
                df_egr = pd.DataFrame(egresos_raw, columns=["ID", "Concepto", "Monto", "Fecha"]) if egresos_raw else pd.DataFrame(columns=["Fecha", "Monto"])
                
                if not df_ing.empty:
                    df_ing["Fecha"] = pd.to_datetime(df_ing["Fecha"])
                    df_ing["Mes"] = df_ing["Fecha"].dt.to_period("M").astype(str)
                    ingresos_mensuales = df_ing.groupby("Mes")["Monto"].sum().reset_index()
                else:
                    ingresos_mensuales = pd.DataFrame(columns=["Mes", "Monto"])
                
                if not df_egr.empty:
                    df_egr["Fecha"] = pd.to_datetime(df_egr["Fecha"])
                    df_egr["Mes"] = df_egr["Fecha"].dt.to_period("M").astype(str)
                    egresos_mensuales = df_egr.groupby("Mes")["Monto"].sum().reset_index()
                else:
                    egresos_mensuales = pd.DataFrame(columns=["Mes", "Monto"])
                
                meses = set(ingresos_mensuales["Mes"]).union(set(egresos_mensuales["Mes"]))
                balance_mensual = pd.DataFrame({"Mes": sorted(meses)})
                balance_mensual = balance_mensual.merge(ingresos_mensuales, on="Mes", how="left").rename(columns={"Monto": "Ingresos"})
                balance_mensual = balance_mensual.merge(egresos_mensuales, on="Mes", how="left").rename(columns={"Monto": "Egresos"})
                balance_mensual.fillna(0, inplace=True)
                balance_mensual["Utilidad"] = balance_mensual["Ingresos"] - balance_mensual["Egresos"]
                
                fig_bar = px.bar(balance_mensual, x="Mes", y=["Ingresos", "Egresos"], barmode="group", title="Ingresos vs Egresos por mes", labels={"value": "Monto ($)", "variable": "Tipo"})
                st.plotly_chart(fig_bar, use_container_width=True)
                
                fig_line = px.line(balance_mensual, x="Mes", y="Utilidad", markers=True, title="Utilidad mensual", labels={"Utilidad": "Utilidad ($)"})
                fig_line.add_hline(y=0, line_dash="dash", line_color="red")
                st.plotly_chart(fig_line, use_container_width=True)
            
            if ingresos_raw:
                st.subheader("🥧 Ingresos por tipo de membresía")
                df_ing_tipo = pd.DataFrame(ingresos_raw, columns=["ID", "Clave", "Socio", "Plan", "Monto", "Fecha"])
                ingresos_por_plan = df_ing_tipo.groupby("Plan")["Monto"].sum().reset_index()
                fig_pie = px.pie(ingresos_por_plan, values="Monto", names="Plan", title="Composición de ingresos por plan", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            if egresos_raw:
                st.subheader("📉 Principales egresos")
                df_egr_top = pd.DataFrame(egresos_raw, columns=["ID", "Concepto", "Monto", "Fecha"])
                top_egresos = df_egr_top.groupby("Concepto")["Monto"].sum().reset_index().sort_values("Monto", ascending=False).head(5)
                fig_horiz = px.bar(top_egresos, x="Monto", y="Concepto", orientation="h", title="Top 5 conceptos de gasto", labels={"Monto": "Monto ($)", "Concepto": "Concepto"})
                st.plotly_chart(fig_horiz, use_container_width=True)
        else:
            st.info("Selecciona un rango de fechas y presiona 'Actualizar balance' para ver los gráficos.")

if __name__ == "__main__":
    main_app()
