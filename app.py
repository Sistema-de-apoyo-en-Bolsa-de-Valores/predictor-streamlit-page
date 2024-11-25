import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuración inicial de la página
st.set_page_config(
    page_title="Sistema de Apoyo para la Compra de Acciones",
    page_icon="📈",
    layout="wide"
)

# Estilo general
st.markdown("""
    <style>
        .stButton>button {
            color: white;
            background-color: #1f77b4;
            border-radius: 8px;
            font-size: 16px;
            padding: 10px 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Función de login
def login(username, password):
    url = "http://arq-api-gateway-1:8080/auth/login"
    payload = {"username": username, "password": password}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al iniciar sesión. Verifica tus credenciales.")
        return None

# Función de registro
def signup(username, password, email, name, lastname):
    url = "http://arq-api-gateway-1:8080/auth/signup"
    payload = {
        "username": username,
        "password": password,
        "email": email,
        "name": name,
        "lastname": lastname
    }
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        st.success("Usuario registrado de forma exitosa.")
    else:
        st.error("Error al registrarse. Verifica los datos ingresados.")

# Función de logout
def logout():
    st.session_state.pop("jwt", None)
    st.session_state.pop("username", None)
    st.success("Cierre de sesión exitoso.")

# Función de predicción y análisis de sentimiento
def call_stock_prediction_api(ticker, training_period_days, future_days):
    url = "http://arq-api-gateway-1:8080/stock/predict"
    headers = {"Authorization": f"Bearer {st.session_state['jwt']}"}
    payload = {"ticker": ticker, "training_period_days": training_period_days, "future_days": future_days}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al predecir los precios.")
        return None

def call_sentiment_news_analysis_api(ticker, max_results):
    url = "http://arq-api-gateway-1:8080/news/analyze"
    headers = {"Authorization": f"Bearer {st.session_state['jwt']}"}
    params = {"ticker": ticker, "max_results": max_results}
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error al realizar el análisis de sentimiento.")
        return None

# Gráficos
def plot_training_and_test_predictions(training_predictions, test_predictions, actual_prices):
    look_back = 60
    training_predictions_plot = np.empty_like(actual_prices)
    training_predictions_plot[:] = np.nan
    training_predictions_plot[look_back:len(training_predictions) + look_back] = np.array(training_predictions)

    test_predictions_plot = np.empty_like(actual_prices)
    test_predictions_plot[:] = np.nan
    test_start = len(actual_prices) - len(test_predictions)
    test_predictions_plot[test_start:] = np.array(test_predictions)

    plt.figure(figsize=(15, 6))
    plt.plot(actual_prices, color='black', label="Precio Real")
    plt.plot(training_predictions_plot, color='red', label="Predicción en Conjunto de Entrenamiento")
    plt.plot(test_predictions_plot, color='blue', label="Predicción en Conjunto de Prueba")
    plt.title("Predicción del Precio del Activo en Entrenamiento y Prueba")
    plt.xlabel("Tiempo")
    plt.ylabel("Precio del Activo")
    plt.legend()
    st.pyplot(plt)
    plt.clf()

def plot_future_predictions(future_days, future_predictions):
    plt.figure(figsize=(15, 6))
    plt.plot(future_predictions, marker='*', color='green')
    plt.title(f'Predicción del Precio para los Próximos {future_days} Días')
    plt.xlabel('Días')
    plt.ylabel('Precio')
    plt.xticks(range(0, future_days), [f'Día {i+1}' for i in range(future_days)])
    plt.grid(True)
    st.pyplot(plt)
    plt.clf()

def plot_sentiment_analysis(data_sentiment_news_analysis_api):
    st.write("📰 Noticias Relacionadas:")
    st.dataframe(data_sentiment_news_analysis_api["news"])
    sentiment_result = data_sentiment_news_analysis_api["result"]
    st.subheader("🔍 **Resultado del Análisis de Sentimiento**")
    if sentiment_result == "POSITIVE":
        st.success("📈 El análisis de sentimiento es positivo.")
    elif sentiment_result == "NEGATIVE":
        st.warning("📉 El análisis de sentimiento es negativo.")
    else:
        st.info("⚖️ El análisis de sentimiento es neutral o indeterminado.")

# Función para realizar compra de acciones
def buy_order(symbol, sec_type, exchange, quantity, order_type, price):
    url = "http://arq-api-gateway-1:8080/order/buy"
    headers = {"Authorization": f"Bearer {st.session_state['jwt']}"}
    payload = {
        "symbol": symbol,
        "sec_type": sec_type,
        "exchange": exchange,
        "quantity": quantity,
        "order_type": order_type,
        "price": price
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        st.success("Orden de compra ejecutada exitosamente!")
        return response.json()
    else:
        st.error("Error al ejecutar la orden de compra.")
        return None

# Función para simular el ingreso de datos de la tarjeta de crédito
def enter_payment_info():
    st.subheader("💳 Información de Pago")
    card_number = st.text_input("Número de Tarjeta", type="password")
    card_expiry = st.text_input("Fecha de Expiración (MM/AA)")
    card_cvc = st.text_input("CVC", type="password")
    if card_number and card_expiry and card_cvc:
        st.success("Datos de la tarjeta ingresados correctamente.")
    else:
        st.warning("Por favor ingrese los datos completos de la tarjeta para proceder con la compra.")

# Navegación entre páginas
if "jwt" not in st.session_state:
    page = st.sidebar.selectbox("Selecciona una opción", ["Iniciar Sesión", "Registro"])

    if page == "Iniciar Sesión":
        st.title("Iniciar Sesión")
        login_username = st.text_input("Usuario", key="login_username")
        login_password = st.text_input("Contraseña", type="password", key="login_password")
        if st.button("Iniciar Sesión"):
            login_data = login(login_username, login_password)
            if login_data:
                st.session_state["jwt"] = login_data["jwt"]
                st.session_state["username"] = login_data["username"]
                st.success(f"¡Bienvenido, {login_data['username']}!")

    elif page == "Registro":
        st.title("Registro")
        signup_username = st.text_input("Usuario", key="signup_username")
        signup_password = st.text_input("Contraseña", type="password", key="signup_password")
        signup_email = st.text_input("Email")
        signup_name = st.text_input("Nombre")
        signup_lastname = st.text_input("Apellido")
        if st.button("Registrar"):
            signup(signup_username, signup_password, signup_email, signup_name, signup_lastname)

# Página principal después de iniciar sesión
if "jwt" in st.session_state:
    st.sidebar.header("Bienvenido, " + st.session_state["username"])
    if st.sidebar.button("Cerrar Sesión"):
        logout()

    # Título y descripción de la aplicación
    st.title("📈 Sistema de Apoyo para la Compra de Acciones en la Bolsa de Valores")
    st.markdown("""
        Bienvenido al sistema de predicción de precios de acciones. 
        Ingresa el símbolo del activo (ticker) y configura los parámetros de entrenamiento y predicción para visualizar las tendencias y precios futuros.
    """)

    # Entradas del usuario
    st.sidebar.header("⚙️ Configuración de Predicción")
    ticker = st.sidebar.text_input("Ticker del Activo", "BTC-USD")
    training_period_days = st.sidebar.number_input("Período de Entrenamiento (días)", min_value=1, value=1825)
    future_days = st.sidebar.number_input("Días a Predecir", min_value=1, value=365)
    max_results = st.sidebar.number_input("Máximo de Noticias para Análisis de Sentimiento", min_value=1, value=50)

    # Botón para obtener predicciones
    if st.button("Obtener Predicciones"):
        with st.spinner("Cargando predicciones... Por favor, espera."):
            data_stock_prediction_api = call_stock_prediction_api(ticker, training_period_days, future_days)

        if data_stock_prediction_api:
            dates = data_stock_prediction_api["dates"]
            actual_prices = data_stock_prediction_api["actual_prices"]
            training_predictions = data_stock_prediction_api["training_predictions"]
            test_predictions = data_stock_prediction_api["test_predictions"]
            future_predictions = data_stock_prediction_api["future_predictions"]

            # Mostrar gráficos de predicciones
            st.subheader(f"📉 Predicción de Precio para {ticker}")
            plot_training_and_test_predictions(training_predictions, test_predictions, actual_prices)
            plot_future_predictions(future_days, future_predictions)

        # Análisis de sentimiento
        data_sentiment_news_analysis_api = call_sentiment_news_analysis_api(ticker, max_results)
        if data_sentiment_news_analysis_api:
            plot_sentiment_analysis(data_sentiment_news_analysis_api)

    # Formulario de compra
    st.subheader("🛒 Realizar Compra de Acciones")
    with st.form("purchase_form"):
        symbol = st.text_input("Símbolo del Activo", value="AAPL")
        sec_type = st.selectbox("Tipo de Seguridad", ["STK", "OPT", "FUT"])
        exchange = st.selectbox("Exchange", ["NASDAQ", "NYSE", "AMEX"])
        quantity = st.number_input("Cantidad", min_value=1, value=1)
        order_type = st.selectbox("Tipo de Orden", ["MKT", "LMT", "STP"])
        price = st.number_input("Precio por Unidad", min_value=0.01, step=0.01, value=100.00)

        # Simulación del pago
        enter_payment_info()

        submit_button = st.form_submit_button("Realizar Compra")
        if submit_button:
            buy_order(symbol, sec_type, exchange, quantity, order_type, price)