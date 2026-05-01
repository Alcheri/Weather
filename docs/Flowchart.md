```mermaid
flowchart TD

    subgraph CMD [Command Layer]
        C1[weather command with options and location text]
        C2{user option provided}
        C3[Resolve hostmask from nick]
        C4[Use message prefix as hostmask]
        C5{location argument provided}
        C6[Use location argument]
        C7[Load saved location from db by hostmask]
        C8{location found}
        C9[Reply error no saved location]
        C10[Run async pipeline on event loop]
    end

    subgraph GEO [Geocoding Layer]
        G1{Google Maps API key configured}
        G2[Raise handled error missing Google Maps key]
        G3[Fetch geocode data]
        G4{Geocode status is OK}
        G5[Raise handled error geocode failed]
        G6[Extract lat lon postcode place id formatted address]
    end

    subgraph WX [Weather Layer]
        W1{OpenWeather API key configured}
        W2[Raise handled error missing OpenWeather key]
        W3[Fetch onecall weather data]
        W4{Weather fetch succeeded}
        W5[Raise handled error weather fetch failed]
        W6[Return weather data]
    end

    subgraph FMT [Formatting Layer]
        F1{Forecast option enabled}
        F2[Format current weather result]
        F3[Format current condition details]
        F4[Apply colour temperature UV and wind direction helpers]
        F5[Format location using DMS]
        F6[Build current weather reply text]
        F7[Format forecast result]
        F8[Iterate daily forecast entries]
        F9[Build forecast reply text]
    end

    subgraph OUT [Output Layer]
        O1[Send irc reply]
        O2[Handled exception path]
        O3[Done]
    end

    C1 --> C2
    C2 -->|yes| C3
    C2 -->|no| C4
    C3 --> C5
    C4 --> C5
    C5 -->|yes| C6
    C5 -->|no| C7
    C7 --> C8
    C8 -->|no| C9
    C8 -->|yes| C10
    C6 --> C10
    C9 --> O3

    C10 --> G1
    G1 -->|no| G2
    G1 -->|yes| G3
    G3 --> G4
    G4 -->|no| G5
    G4 -->|yes| G6

    G6 --> W1
    W1 -->|no| W2
    W1 -->|yes| W3
    W3 --> W4
    W4 -->|no| W5
    W4 -->|yes| W6

    W6 --> F1
    F1 -->|no| F2
    F2 --> F3
    F3 --> F4
    F4 --> F5
    F5 --> F6
    F6 --> O1

    F1 -->|yes| F7
    F7 --> F8
    F8 --> F9
    F9 --> O1

    G2 --> O2
    G5 --> O2
    W2 --> O2
    W5 --> O2
    O2 --> O3
    O1 --> O3

    %% Force dark node and panel colors (no cream boxes)
    classDef process fill:#1f2937,stroke:#93c5fd,color:#e5e7eb,stroke-width:1px;
    classDef decision fill:#111827,stroke:#fbbf24,color:#f9fafb,stroke-width:1px;
    classDef error fill:#7f1d1d,stroke:#f87171,color:#fee2e2,stroke-width:1px;
    classDef done fill:#0f172a,stroke:#94a3b8,color:#e2e8f0,stroke-width:1px;

    class C1,C3,C4,C6,C7,C10,G3,G6,W3,W6,F2,F3,F4,F5,F6,F7,F8,F9,O1 process;
    class C2,C5,C8,G1,G4,W1,W4,F1 decision;
    class C9,G2,G5,W2,W5,O2 error;
    class O3 done;

    style CMD fill:#0b1220,stroke:#334155,color:#e2e8f0
    style GEO fill:#0b1220,stroke:#334155,color:#e2e8f0
    style WX fill:#0b1220,stroke:#334155,color:#e2e8f0
    style FMT fill:#0b1220,stroke:#334155,color:#e2e8f0
    style OUT fill:#0b1220,stroke:#334155,color:#e2e8f0
```
