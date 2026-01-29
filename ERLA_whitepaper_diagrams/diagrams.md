# ERLA Whitepaper Diagrams

These diagrams are designed to be rendered with Mermaid and exported as SVG/PNG for the whitepaper.

---

## Diagram 1: ERLA Architecture Overview

```mermaid
flowchart TB
    subgraph BASE["🔒 BASE LAYER (Persistent)"]
        direction LR
        BM["🧠 Base Model<br/>(Frozen)"]
        LA["⚡ LoRA Adapter<br/>(Evolving)"]
        KI["📚 Knowledge<br/>Index"]
    end
    
    subgraph AGENTS["👻 AGENT LAYER (Ephemeral)"]
        direction LR
        A1["Agent 1<br/>Task A"]
        A2["Agent 2<br/>Task B"]
        A3["Agent 3<br/>Task C"]
        AN["Agent N<br/>Task N"]
    end
    
    A1 & A2 & A3 & AN -->|"Distilled Learnings"| LA
    A1 & A2 & A3 & AN -->|"Abstract Patterns"| KI
    
    LIFECYCLE["SPAWN → ANALYZE → LEARN → DISTILL → DESTROY"]
    
    AGENTS --> LIFECYCLE
    
    style BASE fill:#1e3a5f,stroke:#8b5cf6,stroke-width:2px,color:#fff
    style AGENTS fill:#2d1b4e,stroke:#f97316,stroke-width:2px,color:#fff
    style BM fill:#3b82f6,stroke:#fff,color:#fff
    style LA fill:#8b5cf6,stroke:#fff,color:#fff
    style KI fill:#f97316,stroke:#fff,color:#fff
    style A1 fill:#4c1d95,stroke:#a78bfa,color:#fff
    style A2 fill:#4c1d95,stroke:#a78bfa,color:#fff
    style A3 fill:#4c1d95,stroke:#a78bfa,color:#fff
    style AN fill:#4c1d95,stroke:#a78bfa,color:#fff
    style LIFECYCLE fill:#0f172a,stroke:#f97316,color:#fb923c
```

---

## Diagram 2: Two-Speed Response System

```mermaid
flowchart TD
    Q["📥 INCOMING QUERY"]
    
    Q --> KI["🔍 Knowledge Index<br/>(Vector Search)"]
    
    KI --> MATCH{{"Match > 90%?"}}
    
    MATCH -->|"✅ YES"| FAST["⚡ FAST PATH<br/>~10ms<br/>Return cached response"]
    MATCH -->|"❌ NO"| SLOW["🐢 SLOW PATH<br/>~1-5s<br/>Spawn agent + Full LLM"]
    
    SLOW --> LEARN["📝 Extract Learning<br/>Update Index<br/>Destroy Agent"]
    
    FAST --> RESP["📤 RESPONSE"]
    LEARN --> RESP
    
    style Q fill:#1e3a5f,stroke:#8b5cf6,stroke-width:2px,color:#fff
    style KI fill:#8b5cf6,stroke:#fff,color:#fff
    style MATCH fill:#f97316,stroke:#fff,color:#fff
    style FAST fill:#22c55e,stroke:#fff,color:#fff
    style SLOW fill:#ef4444,stroke:#fff,color:#fff
    style LEARN fill:#a78bfa,stroke:#fff,color:#fff
    style RESP fill:#1e3a5f,stroke:#8b5cf6,stroke-width:2px,color:#fff
```

---

## Diagram 3: Ephemeral Agent Lifecycle

```mermaid
flowchart LR
    subgraph LIFECYCLE["Agent Lifecycle"]
        direction LR
        S["1️⃣ SPAWN<br/>Create with<br/>base layer refs"]
        A["2️⃣ ANALYZE<br/>Process task<br/>two-speed system"]
        L["3️⃣ LEARN<br/>Abstract<br/>knowledge"]
        D["4️⃣ DISTILL<br/>Push to<br/>base layer"]
        X["5️⃣ DESTROY<br/>Secure<br/>erasure"]
    end
    
    S --> A --> L --> D --> X
    
    style S fill:#3b82f6,stroke:#fff,color:#fff
    style A fill:#8b5cf6,stroke:#fff,color:#fff
    style L fill:#a78bfa,stroke:#fff,color:#fff
    style D fill:#f97316,stroke:#fff,color:#fff
    style X fill:#ef4444,stroke:#fff,color:#fff
    style LIFECYCLE fill:#0f172a,stroke:#8b5cf6,stroke-width:2px,color:#fff
```

---

## Diagram 4: Knowledge Abstraction Process

```mermaid
flowchart LR
    subgraph SPECIFIC["❌ Specific Data (Dies)"]
        S1["john.doe@company.com"]
        S2["192.168.1.50"]
        S3["mimikatz.exe"]
        S4["Full incident report"]
    end
    
    ABSTRACT["🔄 ABSTRACTION<br/>PROCESS"]
    
    subgraph ABSTRACT_OUT["✅ Abstract Knowledge (Lives)"]
        A1["internal_user"]
        A2["internal_ip"]
        A3["credential_dump_tool"]
        A4["Pattern: insider_threat"]
    end
    
    S1 --> ABSTRACT --> A1
    S2 --> ABSTRACT --> A2
    S3 --> ABSTRACT --> A3
    S4 --> ABSTRACT --> A4
    
    style SPECIFIC fill:#ef4444,stroke:#fff,color:#fff
    style ABSTRACT fill:#f97316,stroke:#fff,color:#fff
    style ABSTRACT_OUT fill:#22c55e,stroke:#fff,color:#fff
```

---

## Diagram 5: Recursive Improvement Over Time

```mermaid
flowchart LR
    subgraph TIME["TIME →"]
        direction LR
        V1["v1.0<br/>54 patterns"]
        V2["v1.1<br/>154 patterns"]
        V3["v1.2<br/>254 patterns"]
        V4["v1.3<br/>354 patterns"]
        VN["v1.N<br/>∞ patterns"]
    end
    
    V1 -->|"+100"| V2 -->|"+100"| V3 -->|"+100"| V4 -->|"..."| VN
    
    subgraph AGENTS["Agents Contributing"]
        AG1["Agents<br/>1-100"]
        AG2["Agents<br/>101-200"]
        AG3["Agents<br/>201-300"]
    end
    
    AG1 -->|"learnings"| V2
    AG2 -->|"learnings"| V3
    AG3 -->|"learnings"| V4
    
    style V1 fill:#1e3a5f,stroke:#8b5cf6,color:#fff
    style V2 fill:#3b5998,stroke:#8b5cf6,color:#fff
    style V3 fill:#5b7bb8,stroke:#8b5cf6,color:#fff
    style V4 fill:#7b9bd8,stroke:#8b5cf6,color:#fff
    style VN fill:#8b5cf6,stroke:#fff,color:#fff
    style AG1 fill:#f97316,stroke:#fff,color:#fff
    style AG2 fill:#f97316,stroke:#fff,color:#fff
    style AG3 fill:#f97316,stroke:#fff,color:#fff
```

---

## Diagram 6: Privacy Properties

```mermaid
flowchart TD
    subgraph AGENT["👻 Ephemeral Agent"]
        CTX["agent.context<br/>(sensitive data)"]
        MEM["agent.memory<br/>(task state)"]
    end
    
    DESTROY["🔥 destroy()"]
    
    CTX --> DESTROY
    MEM --> DESTROY
    
    DESTROY -->|"Secure Zero"| GONE["❌ Data Gone Forever"]
    
    subgraph BASE["🔒 Base Layer"]
        ABSTRACT["✅ Abstract Learnings<br/>(no PII)"]
    end
    
    AGENT -->|"Distill"| ABSTRACT
    
    style AGENT fill:#ef4444,stroke:#fff,color:#fff
    style CTX fill:#dc2626,stroke:#fff,color:#fff
    style MEM fill:#dc2626,stroke:#fff,color:#fff
    style DESTROY fill:#f97316,stroke:#fff,color:#fff
    style GONE fill:#6b7280,stroke:#fff,color:#fff
    style BASE fill:#22c55e,stroke:#fff,color:#fff
    style ABSTRACT fill:#16a34a,stroke:#fff,color:#fff
```

---

## How to Export

1. **Mermaid Live Editor**: https://mermaid.live
   - Paste each diagram code
   - Export as SVG or PNG

2. **VS Code Extension**: "Markdown Preview Mermaid Support"
   - Preview and export directly

3. **CLI Tool**: `mmdc` (mermaid-cli)
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   mmdc -i diagrams.md -o diagram.svg
   ```

---

## Color Palette Used

| Color | Hex | Usage |
|-------|-----|-------|
| Purple | `#8b5cf6` | Primary accent, headers |
| Purple Light | `#a78bfa` | Secondary elements |
| Dark Blue | `#1e3a5f` | Backgrounds, base layer |
| Orange | `#f97316` | Tertiary accent, highlights |
| Green | `#22c55e` | Success, safe data |
| Red | `#ef4444` | Danger, ephemeral data |

