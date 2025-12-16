# **Documentación del Portal Backend**

Este documento detalla el flujo de trabajo para el alta de participantes en el espacio de datos y las funciones necesarias a implementar en el backend.

## **1\. Flujo de Trabajo**

El proceso de alta y gestión de participantes sigue la siguiente secuencia lógica:

### **Paso 1: Invitación (Administrador)**

El administrador inicia el proceso creando un nuevo participante en el sistema.

* **Acción:** El administrador utiliza sus credenciales para invitar a un usuario.  
* **Lógica:**  
  * Dado un correo electrónico, se asigna una contraseña (temporal o generada).  
  * Se establece el modelo de datos del usuario con **status: PENDING**.  
  * **Notificación:** Se envía un correo al participante con su usuario y contraseña.

### **Paso 2: Autenticación y Registro (Participante)**

El participante recibe las credenciales y accede al portal.

* **Acción:** El participante se autentica utilizando usuario \+ contraseña.  
* **Flujo Condicional:**  
  * **Si es la primera vez:**  
    1. Se obliga al cambio de contraseña (personalizada).  
    2. Se solicita el envío del formulario de registro (Endpoint /form).  
  * **Si es un acceso recurrente:**  
    * Inicio de sesión normal (/login).  
    * El usuario puede visualizar su información y acceder al portal de su conector.

### **Paso 3: Aceptación y Despliegue (Sistema/Admin)**

Una vez el participante ha completado su registro, se procede a la aceptación y generación de infraestructura.

* **Acción:** Aceptar al participante en el espacio de datos.  
* **Secuencia de Despliegue:**  
  1. Despliegue del **Identity Hub**.  
  2. Generación de **DID** (Identidad Digital) \+ Emisión de **Credenciales Verificables**.  
  3. Despliegue del **Conector**.  
  4. **Vinculación final:** Se asocia en base de datos: Usuario \+ Conector \+ DID \+ API Key.

## **2\. Funciones del Backend (Endpoints)**

A continuación, se listan los endpoints requeridos en el portal-backend, agrupados por funcionalidad.

### **Gestión de Usuarios**

| Endpoint | Descripción |
| :---- | :---- |
| /invite | Crea el registro inicial del usuario y envía la notificación/correo. |
| /login | Maneja la autenticación de usuarios (Admin y Participantes). |
| /form | Recibe y guarda los datos del formulario de registro del participante. |
| /status | Consulta el estado actual del participante (ej. PENDING, ACTIVE). |
| /aceptarParticipante | Trigger para iniciar el flujo de aceptación y despliegue. |

### **Gestión de Despliegue**

Estas funciones son invocadas internamente o por el administrador para gestionar la infraestructura.

* Deploy Identity hub: Orquestación para levantar el contenedor o servicio del Identity Hub.  
* Deploy conector: Orquestación para levantar el conector del Dataspace.

### **Seguridad y Criptografía**

| Categoría | Dato Protegido | Algoritmo | Propiedad | Archivo Fuente |
| :---- | :---- | :---- | :---- | :---- |
| **Autenticación** | Password Usuario | **Bcrypt** | Irreversible | security.py |
| **Integridad** | Token Sesión (JWT) | **HS256** | Firma Simétrica | security.py |
| **Confidencialidad** | API Keys Conector | **Fernet (AES-128)** | Reversible | crypto.py |



### **Credenciales e Identidad**

Funciones específicas para la gestión de la identidad soberana.

* Lanzar emision de DID con el Identity Hub: Generación del identificador descentralizado.  
* Lanzar emision de credenciales con el Identity hub: Creación de las Verifiable Credentials (VC) asociadas al participante.
