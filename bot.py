import streamlit as st
from groq import Groq
from datetime import datetime

st.set_page_config(page_title="AsesorIA", page_icon="+", layout="centered")

hora_actual = datetime.now().hour

if 6 <= hora_actual < 12:
    saludo = "¡Buenos días!"
elif 12 <= hora_actual < 20:
    saludo = "¡Buenas tardes!"
else:
    saludo = "Buenas noches"
    
st.title(saludo)

nombre = st.text_input("¿Cúal es tu nombre?: ")

if st.button("Saludar"):
    st.write(f"¡Hola {nombre}! Te doy la bienvenida.")
    
modelos = ['llama3-8b-8192', 'llama3-70b-8192', 'gemma2-9b-it']

def configurar_pagina():      #configuramos página
    st.title("AsesorIA")
    st.sidebar.title("Configurar la IA")
    elegirModelo = st.sidebar.selectbox("Elegi un modelo",options=modelos,index=0)
    return elegirModelo

#Funcion que nos ayuda a conectar con Groq
def crear_usuario_groq():
    claveSecreta = st.secrets["claveAPI"]
    return Groq(api_key=claveSecreta)

#Configurar el modelo y el mensaje del usuario. 
def configurar_modelo(cliente, modelo, mensajeDeEntrada):
    return cliente.chat.completions.create(
        model=modelo,
        messages =[{"role":"user", "content": mensajeDeEntrada}],
        stream=True
    )
    
#Permite poder generar o guardar un historial mientras el navegador esté abierto
def incializacion_estado():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

#Clase 8
#Actualizar el estado: cuando yo hago otra pregunta, no se pierde lo anterior
def actualizar_historial(rol, contenido, avatar):
    st.session_state.mensajes.append({"role":rol,"content":contenido, "avatar":avatar}) #crea una lista vacía y la completa con un diccionario, compuesto del rol, contenido y avatar. Rol me muestra quién está hablando. Content para el usuario va a ser la solicitud/pregunta, y para el modelo su respuesta. Avatar es mi cara básicamente

#Mostrar historial
def mostrar_historial(): #Tiene que verificar si hay algo que mostrar (es decir, si la lista no está vacía)
    for mensaje in st.session_state.mensajes:    #revisa cada mensaje
        with st.chat_message(mensaje["role"]):  #de cada mensaje, revisa rol y avatar
            st.markdown(mensaje["content"])      #y revisa contenido
            

#Espacio para que muestre el historial
def area_chat():
    contenedorDelChat = st.container(height=300, border=True)    #el 300 se lo toma en pixeles. Border es True para que se vea
    with contenedorDelChat:  
        mostrar_historial()    #hace que, con contenedorDelChat, se ejecute esta función

#Generar respuesta (voy a capturar la respuesta del modelo)
def generar_respuesta(chat_completo):
    respuesta_completa = ""
    for frase in chat_completo:       #Ciclo que recorre cada palabra del contenido y se pregunta si hay algo que mostrar. La variable chat_completo captura la respuesta. Comprueba si hay alguna respuesta del modelo
        if frase.choices[0].delta.content:    #elige la primera opción que ofrezca el modelo de IA
            respuesta_completa += frase.choices[0].delta.content   #lo asigna a respuesta_completa
            yield frase.choices[0].delta.content
    return respuesta_completa
        
def main():   #esta va a ser la función principal. Todo tiene que quedar dentro de la función con la identación
    modelo = configurar_pagina()
    clienteUsuario = crear_usuario_groq()   #conecta con groq
    incializacion_estado()   
    area_chat()

    mensaje = st.chat_input("¿Con qué puedo asesorIArte?")  
    if mensaje:
        actualizar_historial("user", mensaje, "")
        chat_completo = configurar_modelo(clienteUsuario, modelo, mensaje)
        if chat_completo:
            with st.chat_message("assistant"):
                respuesta_completa = st.write_stream(generar_respuesta(chat_completo)) #write.stream hace que se escriba en tiempo real
                actualizar_historial("assistant", respuesta_completa, "")
                
            
            
            st.rerun()
            
if __name__ == "__main__":
    main()