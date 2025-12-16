# **📘 Guía de Uso \- Backend Portal** 

Este servicio opera como la autoridad central de gestión y seguridad para el Espacio de Datos, diseñado para formalizar el registro de nuevos participantes exclusivamente mediante un flujo de invitación administrativa. Su arquitectura cumple una doble función crítica de seguridad: primero, autentica a los usuarios en el portal de gestión mediante la emisión de Tokens JWT tras un inicio de sesión validado; y segundo, protege la infraestructura (conector e identity hub) asignando claves API Keys cifradas, garantizando así que solo los propietarios legítimos puedan operar su infraestructura de datos.

## **🚀 1\. Cómo Ejecutar el Proyecto**

Desde la carpeta raíz portal-backend:

1. **Levantar servicios:**  
   docker-compose up \--build

2. **Verificar estado:**  
   * API Documentation (Swagger): [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)  
   * Base de datos (Puerto externo): localhost:5432  
3. Usuario Administrador por Defecto:  
   El sistema crea automáticamente este usuario al iniciar si la DB está vacía:  
   * **Email:** admin@dataspace.com  
   * **Password:** adminpassword

## **🔌 2\. Catálogo de Endpoints Implementados**

### **🔐 Autenticación (Público)**

| Método | Endpoint | Descripción | Body Requerido |
| :---- | :---- | :---- | :---- |
| POST | /token | Iniciar sesión y obtener JWT. | username, password (Form-data) |

### **🛡️ Administración (Requiere Rol ADMIN)**

| Método | Endpoint | Descripción | Body Requerido |
| :---- | :---- | :---- | :---- |
| POST | /admin/invite | Crea usuario en estado PENDING y genera pass temporal. | {"email": "user@example.com"} |
| POST | /admin/accept/{user\_id} | Acepta usuario REGISTERED, genera DID, URLs y API Key. | N/A (Solo UUID en URL) |

### **👤 Participante (Requiere Rol PARTICIPANT)**

| Método | Endpoint | Descripción | Body Requerido |
| :---- | :---- | :---- | :---- |
| POST | /form | Registra datos de empresa y cambia estado a REGISTERED. | JSON con datos de empresa (ver abajo). |
| GET | /me | Devuelve la información del usuario logueado. | N/A |

## **👣 3\. Guía de Prueba.**

Sigue estos pasos para probar el ciclo completo de vida de un participante.

### **Paso 1: Login como Admin**

1. Ve a Swagger UI.  
2. Usa el botón **Authorize**.  
3. Credenciales: admin@dataspace.com / adminpassword.

### **Paso 2: Invitar Participante**

1. Endpoint: POST /admin/invite.  
2. Payload: {"email": "empresa@test.com"}.  
3. **Acción:** Copia la temp\_password que devuelve la respuesta JSON.

### **Paso 3: Registro del Participante**

1. Haz **Logout** (botón Authorize \-\> Logout).  
2. Haz **Login** con el usuario nuevo: empresa@test.com y la contraseña temporal.  
3. Endpoint: POST /form.  
4. Payload (Ejemplo):  
   {  
     "company\_name": "Mi Empresa S.L.",  
     "legal\_id": "B12345678",  
     "address": { "calle": "Gran Via 1", "ciudad": "Madrid" },  
     "contact\_person": "CEO Nombre",  
     "sector": "Energía"  
   }

5. Resultado: El usuario pasa a estado REGISTERED. Guarda el user\_id

### **Paso 4: Despliegue de Infraestructura**

1. Haz **Logout** del participante.  
2. Haz **Login** como Admin nuevamente.  
3. Endpoint: POST /admin/accept/{user\_id} (Necesitas el ID del usuario, búscalo en la respuesta del paso 2 o 3).  
4. **Resultado:**  
   * Se genera el **DID** (did:web:dataspace...).  
   * Se generan URLs del conector.
   * Aqui se tendrá que llamar a los helm para desplegar los helm chart.  
   * **IMPORTANTE:** Mira la consola/terminal de Docker. Ahí verás impresa la **API KEY** descifrada (simulando un envío seguro).
