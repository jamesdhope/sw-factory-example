# Software Factory Architecture

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> SPEC_DEVELOPMENT: Start Project
    SPEC_DEVELOPMENT --> PLANNING: Spec Created
    PLANNING --> EXECUTION: Tasks Generated
    
    state EXECUTION {
        [*] --> Task_Iteration
        Task_Iteration --> Branch_Creation
        Branch_Creation --> Goose_Worker
        Goose_Worker --> commit_work
        commit_work --> Task_Iteration: Next Task
    }
    
    EXECUTION --> INTEGRATION: All Tasks Done
    INTEGRATION --> CODE_RELEASE: Merge & Tests Passed
    INTEGRATION --> FAILED: Merge/Test Error
    CODE_RELEASE --> [*]
    FAILED --> [*]

    note right of EXECUTION
        Isolated Git branches for each task
        task/build_[id]_[slug]
    end note

    note left of INTEGRATION
        Resolves conflicts
        Runs final test suite
    end note
```

## 🏗 Workflow Components

### 1. Orchestrator (`factory.py`)
The central state machine that manages transitions and maintains the build context (token usage, project history, etc.).

### 2. Planner Agent
Decomposes high-level requirements into a discrete `tasks.json` file.

### 3. Worker Fleet
Stateless Goose sessions instantiated per task. Each worker is given a fresh git branch to prevent cross-contamination.

### 4. Integration Agent
A specialized session that performs the complex multi-branch merge, resolves file-level conflicts, and executes a final quality gate.

### 5. Web Dashboard (`dashboard.py` + `static/`)
A real-time observability interface with a log-focused view, resource monitoring, and a task-orchestration strip.
