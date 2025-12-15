# **Definición de Modelos de Datos (Schema Proposal)**

Para mantener una arquitectura limpia y segura, propongo dividir la información en 4 entidades relacionales.

## **1\. Usuario (User)**

*Responsabilidad: Autenticación y Estado del Ciclo de Vida.*

No debe contener datos técnicos del conector ni detalles masivos de la empresa.

| Campo | Tipo | Descripción |
| :---- | :---- | :---- |
| id | UUID | Identificador único interno. |
| email | String | Correo electrónico (único). |
| passwordHash | String | Hash de la contraseña (bcrypt/argon2). |
| role | Enum | ADMIN, PARTICIPANT. |
| status | Enum | INVITED, REGISTERED, DEPLOYING, ACTIVE, SUSPENDED. |
| activationToken | String | Token temporal para el flujo de invitación (opcional si usas tabla aparte). |
| createdAt | Date | Fecha de invitación. |

## **2\. Perfil del Participante (ParticipantProfile)**

*Responsabilidad: Información de Negocio (recogida en el /form).*

Se separa del usuario para que la tabla de usuarios sea ligera y porque estos datos son los que luego se firman en las credenciales.

| Campo | Tipo | Descripción |
| :---- | :---- | :---- |
| id | UUID | PK. |
| userId | UUID | FK \-\> Relación 1:1 con User. |
| companyName | String | Nombre legal de la organización. |
| legalId | String | CIF/NIF/VAT ID. |
| address | JSON | Dirección física completa. |
| contactPerson | String | Nombre de la persona de contacto. |
| sector | String | Sector industrial (ej. Automoción, Energía). |

## **3\. Infraestructura Dataspace (DataspaceDeployment)**

*Responsabilidad: Datos técnicos de conexión (El JSON que seleccionaste).*

Esta tabla contiene los secretos y direcciones IP. Es la más crítica a nivel de seguridad.

| Campo | Tipo | Descripción |
| :---- | :---- | :---- |
| id | UUID | PK. |
| userId | UUID | FK \-\> Relación 1:1 con User. |
| did | String | El DID generado (ej. did:web:dominio:123). |
| connectorUrl | String | URL pública del conector DSP. |
| managementUrl | String | URL interna de gestión (desde donde el backend ataca). |
| identityHubUrl | String | URL del Identity Hub. |
| apiKeyEncrypted | String | **La clave API cifrada** (AES-256). |
| encryptionIv | String | Vector de inicialización para desencriptar. |
| lastRotation | Date | Fecha de la última rotación de claves. |

## **4\. Credenciales Verificables (VerifiableCredential)**

*Responsabilidad: Historial de emisiones.*

Necesario para saber qué credenciales tiene un usuario, cuándo caducan y si han sido revocadas.

| Campo | Tipo | Descripción |
| :---- | :---- | :---- |
| id | UUID | PK. |
| userId | UUID | FK \-\> Relación 1:N con User. |
| type | Enum | Ej. MembershipCredential, LegalPersonCredential. |
| issuanceDate | Date | Fecha de emisión. |
| expirationDate | Date | Fecha de caducidad (si aplica). |
| status | Enum | ACTIVE, REVOKED, EXPIRED. |
| rawVc | Text/JSON | (Opcional) Copia de la VC firmada o referencia al Identity Hub. |

## **(Opcional) 5\. Logs de Despliegue (DeploymentLog)**

*Responsabilidad: Trazabilidad de errores asíncronos.*

Útil si implementas el sistema de colas mencionado en las mejoras.

* jobId: ID del trabajo en la cola.  
* userId: Usuario afectado.  
* step: Paso actual (ej. "Minting DID").  
* status: SUCCESS, FAILED.  
* errorMessage: Detalle técnico del error.