# Análisis de Arquitectura — `alefeans/python-clean-architecture`

## 1. Identificación de Capas

Este proyecto es una plantilla de referencia (starter template) en Python con FastAPI, diseñada para resolver un caso de uso real: gestión de usuarios y autenticación. Sirve como base escalable lista para extenderse hacia nuevos módulos de negocio (por ejemplo, la gestión de roles).

Diseño Arquitectónico:
Implementa Clean Architecture apoyada en patrones tácticos de DDD. En lugar de seguir la división rígida de cuatro capas de los libros de texto, utiliza una variante pragmática inspirada en la Arquitectura Hexagonal (Ports & Adapters), estructurada en dos macro-paquetes:

app/core: Concentra toda la lógica de dominio y de aplicación (Casos de uso).

app/infra: Maneja la infraestructura, los detalles técnicos y los adaptadores externos.

| Capa teórica (Clean/Hexagonal) | ¿Presente? | Ubicación real |
|---|---|---|
| Entidades de dominio | ✅ | `app/core/entities/` |
| Value Objects | ✅ (DDD táctico) | `app/core/value_objects/` |
| Casos de Uso (Application/Interactors) | ✅ | `app/core/usecases/<agregado>/` |
| Puertos (interfaces/Protocols) | ✅ (patrón Hexagonal explícito) | `app/core/ports/` |
| DTOs (fronteras de entrada/salida) | ✅ | `app/core/dtos/` |
| Excepciones de dominio | ✅ | `app/core/exceptions.py` |
| Adaptadores de entrada (Controllers/API) | ✅ | `app/infra/api/routers/` |
| Adaptadores de salida (DB/Repos) | ✅ | `app/infra/db/repositories/`, `app/infra/db/models/` |
| Inyección de Dependencias | ✅ (FastAPI `Depends` + `Annotated`) | `app/infra/api/dependencies/` |
| Unit of Work | ✅ | `app/core/ports/unit_of_work.py` + `app/infra/db/unit_of_work/` |
| Presenters / ViewModels separados | ❌ No existen; el DTO de salida (`UserResponse`) hace ese rol | — |
| Capa de "Frameworks & Drivers" separada explícitamente | ⚠️ Implícita en `infra/`, no nombrada así | `app/infra/` |

**Regla de dependencia:** `core` nunca importa de `infra`. `infra` importa de `core` (ports, dtos, entities). Se cumple la Inversión de Dependencias (DIP): los casos de uso dependen de `Protocol`s definidos en `core/ports`, e `infra` provee las implementaciones concretas.

## 2. Inventario de Componentes

| Componente | Responsabilidad | Ruta |
|---|---|---|
| **Entidad `User`** | Regla de negocio invariante (`dataclass frozen`, valida nombre no vacío) | `app/core/entities/user.py` |
| **Value Objects** `ID`, `Email`, `Password` | Autovalidación e inmutabilidad de primitivas | `app/core/value_objects/*.py` |
| **DTOs** `CreateUserRequest`, `UpdateUser`, `UserResponse` | Contratos de entrada/salida | `app/core/dtos/user.py` |
| **Excepciones de dominio** | `UserNotFoundError`, `UserAlreadyExistsError`, `InvalidUserError`, etc. heredan de `DomainException` | `app/core/exceptions.py` |
| **Puertos (`Protocol`)** `UserRepo`, `UserUnitOfWork`, `Hasher`, `UnitOfWork` | Contratos que la capa de infraestructura debe cumplir | `app/core/ports/*.py` |
| **Casos de Uso** `CreateUserUsecase`, `GetUserUsecase`, `UpdateUserUsecase`, `DeleteUserUsecase`, `AuthenticateUserUsecase` | Orquestan reglas de negocio, VOs y puertos | `app/core/usecases/user/*.py` |
| **Modelo ORM** `User(SQLModel, table=True)` | Mapeo objeto-relacional (tabla `users`) | `app/infra/db/models/user.py` |
| **Repositorio** `UserRepo` | Implementa el puerto `UserRepo` usando `AsyncSession`/SQLModel | `app/infra/db/repositories/user.py` |
| **Unit of Work** `UserUnitOfWork` + `user_uow_factory` | Agrupa repos y controla `commit`/`rollback`/`close` | `app/infra/db/unit_of_work/*.py` |
| **Seguridad** `Hasher` (Passlib), `JWTProvider` | Adaptadores de criptografía/token | `app/infra/security/crypto.py`, `app/infra/auth/jwt.py` |
| **Dependencias FastAPI** | "Wiring" de DI (composition root) | `app/infra/api/dependencies/*.py` |
| **Routers (Controladores)** `user.py`, `auth.py`, `root.py` | Reciben DTO validado, llaman `usecase.execute()`, mapean excepciones de dominio → `HTTPException` | `app/infra/api/routers/v1/*.py` |
| **App factory** `create_app`, `register_routers`, `register_extensions`, `lifespan` | Ensambla FastAPI, ciclo de vida, handlers globales | `app/infra/api/app.py`, `lifespan.py`, `extensions.py` |
| **Migraciones** Alembic | Versionado del esquema | `app/infra/db/migrations/versions/` |

## 3. Flujo de una Petición Típica (`POST /api/v1/users`)

1. **Framework (FastAPI)**: la request HTTP llega al router `app/infra/api/routers/v1/user.py`. FastAPI valida el body contra el DTO `CreateUserRequest` automáticamente.
2. **Inyección de dependencias**: el parámetro `usecase: CreateUserUsecase` se resuelve vía `Annotated[CreateUserUsecase, Depends(get_create_user_usecase)]` (`dependencies/usecases/user.py`), que a su vez depende de `UnitOfWork` y `Hasher`. Cada `Depends` abre su propio `AsyncSession` vía `async_session()`.
3. **Controlador**: el endpoint `create()` llama `await usecase.execute(dto)` dentro de un `try/except` que traduce excepciones de dominio a códigos HTTP (`InvalidUserError`→400, `UserAlreadyExistsError`→409).
4. **Caso de Uso** (`CreateUserUsecase.execute`):
   - Construye Value Objects `Email` y `Password` (auto-validación; si fallan → `InvalidUserError`).
   - Entra al `async with self.uow:` (Unit of Work) → abre transacción.
   - Verifica duplicado con `uow.user_repo.get_by_email(email)` (Puerto).
   - Hashea password con `self.hasher.hash(...)` (Puerto `Hasher`).
   - Construye la **Entidad** `User` (con validación de invariantes en `__post_init__`).
   - Llama `uow.user_repo.save(user)` (Puerto → implementación concreta).
   - Al salir del `async with`, `UnitOfWork.__aexit__` hace `commit()` (o `rollback()` si hubo excepción).
5. **Repositorio**: traduce la Entidad de dominio al **Modelo ORM** (`DBUser`) y lo agrega a la sesión SQLAlchemy async.
6. **Infraestructura de persistencia**: SQLAlchemy async ejecuta el `INSERT` contra Postgres al hacer `commit`.
7. **Retorno**: el caso de uso construye un `UserResponse` (DTO de salida) y lo retorna. El controlador lo devuelve tal cual (FastAPI lo serializa a JSON con `status_code=201`).
8. **Manejo transversal de errores de validación**: si el DTO de entrada no matchea el schema, `RequestValidationError` es capturado globalmente por `extensions.py`, devolviendo 422 con mensajes adaptados.

.....