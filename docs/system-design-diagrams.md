# Ball Mill Monitoring System Architecture Diagrams

## 1. High-Level System Architecture
```mermaid
graph TD
    A[Browser Client] --> B[Next.js App]
    B --> C[API Routes]
    B --> D[WebSocket Server]
    B --> E[MQTT Client]
    C --> F[PostgreSQL Database]
    C --> G[External Services]
    D --> H[WebSocket Clients]
    E --> I[MQTT Broker]
    F --> J[Data Tables]
    G --> K[YouTube API]
    G --> L[External APIs]
    
    subgraph Frontend
        B
    end
    
    subgraph Backend
        C
        D
        E
    end
    
    subgraph Database
        F
        J
    end
    
    subgraph External Services
        G
        K
        L
    end
```

## 2. Component Architecture
```mermaid
graph TD
    A[App Layout] --> B[Navbar]
    A --> C[Main Content]
    A --> D[Footer]
    
    B --> E[Navigation Items]
    B --> F[Location Dropdown]
    
    C --> G[Dashboard]
    C --> H[Ball Mill]
    C --> I[Pipeline]
    C --> J[PLC]
    C --> K[Something]
    
    subgraph Monitoring Sections
        G --> L[Overview]
        H --> M[Live Stream]
        H --> N[Data Acquisition]
        I --> O[Valve Control]
        I --> P[Leak Detection]
        J --> Q[Device Status]
    end
    
    subgraph Data Components
        M --> R[YouTube Stream]
        N --> S[Sensor Data]
        O --> T[Valve States]
        P --> U[Heatmaps]
        Q --> V[PLC Status]
    end
```

## 3. Data Flow Diagram
```mermaid
graph TD
    A[User Request] --> B[Next.js App]
    B --> C[Authentication]
    B --> D[Route Handler]
    D --> E[Data Fetching]
    D --> F[WebSocket Connection]
    D --> G[MQTT Connection]
    
    subgraph Data Sources
        E --> H[PostgreSQL]
        E --> I[Cache]
        E --> J[External APIs]
    end
    
    subgraph Real-time Updates
        F --> K[WebSocket Events]
        G --> L[MQTT Events]
        K --> M[UI Updates]
        L --> M
    end
    
    subgraph UI Components
        M --> N[Charts]
        M --> O[Tables]
        M --> P[Maps]
        M --> Q[Controls]
    end
```

## 4. Database Schema
```mermaid
erDiagram
    LOCATIONS ||--o{ SENSORS : has
    SENSORS ||--o{ SENSOR_DATA : records
    LOCATIONS ||--o{ ACQUISITION_SESSIONS : has
    ACQUISITION_SESSIONS ||--o{ SENSOR_DATA : contains
    
    LOCATIONS {
        int id PK
        string name
        string type
        string status
        string youtubeStreamId
    }
    
    SENSORS {
        int id PK
        int location_id FK
        string type
        string name
        string status
    }
    
    ACQUISITION_SESSIONS {
        int id PK
        int location_id FK
        datetime start_time
        datetime end_time
        string notes
    }
    
    SENSOR_DATA {
        int id PK
        int sensor_id FK
        int session_id FK
        float value
        datetime timestamp
    }
```

## 5. Component Hierarchy
```mermaid
classDiagram
    class App {
        +render()
    }
    
    class Layout {
        +Navbar
        +MainContent
        +Footer
    }
    
    class Navbar {
        +NavigationItems
        +LocationDropdown
    }
    
    class MonitoringSection {
        +LiveStream
        +DataAcquisition
        +Controls
    }
    
    class DataComponents {
        +Charts
        +Tables
        +Maps
        +Controls
    }
    
    App --> Layout
    Layout --> Navbar
    Layout --> MonitoringSection
    MonitoringSection --> DataComponents
```

## 6. Real-time Communication Flow
```mermaid
sequenceDiagram
    participant Browser
    participant NextApp
    participant WebSocket
    participant MQTT
    participant Database
    participant UI
    
    Browser->>NextApp: Request Data
    NextApp->>Database: Fetch Initial Data
    Database-->>NextApp: Return Data
    NextApp-->>Browser: Render Initial UI
    
    Browser->>WebSocket: Connect
    WebSocket-->>Browser: Confirm Connection
    
    Browser->>MQTT: Subscribe to Topics
    MQTT-->>Browser: Confirm Subscription
    
    Database->>WebSocket: Data Change
    WebSocket->>UI: Update UI
    
    MQTT->>UI: Real-time Updates
    UI-->>NextApp: User Actions
    NextApp-->>Database: Save Changes
```

## 7. Location-Based Monitoring Flow
```mermaid
graph TD
    A[User Selects Location] --> B[Location Type Check]
    B -->|Ball Mill| C[BallMillPage]
    B -->|Pipeline| D[PipelinePage]
    B -->|PLC| E[PLCPage]
    B -->|Something| F[SomethingPage]
    
    C --> G[Load Live Stream]
    C --> H[Fetch Sensor Data]
    
    D --> I[Initialize Valves]
    D --> J[Setup Leak Detection]
    
    E --> K[Connect to PLC]
    E --> L[Fetch Device Status]
    
    F --> M[Load Placeholder]
    F --> N[Setup Sensors]
```

## 8. Data Acquisition Flow
```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Sensor
    participant Database
    participant Analysis
    
    User->>UI: Select Sensor
    UI->>UI: Configure Parameters
    UI->>Sensor: Start Acquisition
    Sensor->>Database: Stream Data
    Database->>Analysis: Process Data
    Analysis->>UI: Update Charts
    UI->>User: Show Results
```

## Legend
- Solid lines: Direct connections
- Dashed lines: Event-driven connections
- Arrowheads: Data flow direction
- Boxes: Components/Services
- Rounded boxes: Processes
- Diamonds: Decision points
- Clouds: External services
- Cylinders: Databases
