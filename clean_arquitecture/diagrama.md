```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#e3f2fd', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#f3e5f5'}}}%%
graph TD
    subgraph "Capa Externa: Infraestructura (Frameworks & Drivers)"
        API["api/ (FastAPI)"]
        DB["db/ (SQLAlchemy, Repositories)"]
        AUTH["auth/ (JWT, Security)"]
    end

    subgraph "Capa Intermedia: Adaptadores"
        DTOs["dtos/ (Pydantic Schemas)"]
    end

    subgraph "Capa Interna: Nucleo (Core / Dominio)"
        USE_CASES["usecases/ (Application Logic)"]
        PORTS["ports/ (Interfaces de Repositorios)"]
        ENTITIES["entities/ (Business Rules)"]
        VO["value_objects/ (Email, ID)"]
        EXC["exceptions.py"]
    end

    Cliente(("Usuario / Frontend")) -->|"1. Peticion HTTP"| API
    
    API -->|"2. Valida Entrada"| DTOs
    API -->|"3. Inyecta Dependencias y llama al Caso de Uso"| USE_CASES
    
    USE_CASES -->|"4. Aplica logica y reglas"| ENTITIES
    ENTITIES -->|"5. Usa primitivas inmutables"| VO
    USE_CASES -->|"Manejo de errores"| EXC
    
    USE_CASES -->|"6. Llama a la interfaz (Puerto)"| PORTS
    DB -.->|"7. Implementa la interfaz"| PORTS
    
    USE_CASES -->|"8. Devuelve datos limpios"| DTOs
    DTOs -->|"9. Formatea respuesta"| API
    API -->|"10. Respuesta HTTP"| Cliente

    classDef core fill:#e8f5e9,stroke:#4caf50,stroke-width:2px;
    classDef infra fill:#ffebee,stroke:#f44336,stroke-width:2px;
    
    class USE_CASES,PORTS,ENTITIES,VO,EXC core;
    class API,DB,AUTH infra;