import subprocess
import os
import json
import dataclasses
from enum import Enum
from typing import List, Optional

class State(Enum):
    IDLE = "IDLE"
    SPEC_DEVELOPMENT = "SPEC_DEVELOPMENT"
    CODE_GENERATION = "CODE_GENERATION"
    CODE_TESTING = "CODE_TESTING"
    CODE_INTEGRATION = "CODE_INTEGRATION"
    CODE_RELEASE = "CODE_RELEASE"
    FAILED = "FAILED"

@dataclasses.dataclass
class FactoryContext:
    objective: str
    project_name: str = "project"
    build_dir: str = ""
    spec_path: str = ""
    code_path: str = ""
    test_path: str = ""
    history: List[str] = dataclasses.field(default_factory=list)

class SoftwareFactory:
    def __init__(self, objective: str, project_name: str = "auto_project"):
        self.state = State.IDLE
        self.context = FactoryContext(objective=objective, project_name=project_name)
        self.setup_build_dir()
        self.transitions = {
            State.IDLE: self.handle_idle,
            State.SPEC_DEVELOPMENT: self.handle_spec,
            State.CODE_GENERATION: self.handle_code,
            State.CODE_TESTING: self.handle_test,
            State.CODE_INTEGRATION: self.handle_integration,
            State.CODE_RELEASE: self.handle_release,
        }
        self.update_status("Initialized")

    def setup_build_dir(self):
        """Creates an incremented build directory."""
        base_dir = "builds"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        
        # Find next increment
        existing = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        indices = [int(d.split('_')[0]) for d in existing if d.split('_')[0].isdigit()]
        next_idx = max(indices, default=0) + 1
        
        dir_name = f"{next_idx:03d}_{self.context.project_name.replace(' ', '_')}"
        self.context.build_dir = os.path.join(base_dir, dir_name)
        os.makedirs(self.context.build_dir)
        
        self.context.spec_path = os.path.join(self.context.build_dir, "spec.md")
        self.context.code_path = os.path.join(self.context.build_dir, "implementation.py")
        self.context.test_path = os.path.join(self.context.build_dir, "tests.py")

    def update_status(self, message: str):
        """Writes current state and message to status.json for the dashboard."""
        status = {
            "state": self.state.value,
            "message": message,
            "objective": self.context.objective,
            "project": self.context.project_name,
            "build_dir": self.context.build_dir,
            "history": self.context.history
        }
        with open("status.json", "w") as f:
            json.dump(status, f, indent=2)
        print(f"[{self.state.value}] {message}")

    def run_goose_command(self, prompt: str):
        """Helper to run goose CLI commands."""
        self.update_status(f"Running Goose: {prompt[:100]}...")
        goose_path = "/Users/jamesdhope/.local/bin/goose"
        try:
            result = subprocess.run(
                [goose_path, "run", "-i", "-"], 
                input=prompt,
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.update_status(f"Goose failed: {e.stderr}")
            return None
        except FileNotFoundError:
            self.update_status("Error: 'goose' command not found.")
            return None

    def transition(self, next_state: State, message: str = ""):
        self.state = next_state
        self.context.history.append(f"State: {next_state.value} - {message}")
        self.update_status(message or f"Transitioned to {next_state.value}")

    def run(self):
        while self.state != State.CODE_RELEASE and self.state != State.FAILED:
            handler = self.transitions.get(self.state)
            if handler:
                handler()
            else:
                self.transition(State.FAILED, f"No handler for state {self.state}")
                break
        
        if self.state == State.CODE_RELEASE:
            self.update_status("Software Factory: Task Completed Successfully!")
        else:
            self.update_status("Software Factory: Task Failed.")

    def handle_idle(self):
        self.transition(State.SPEC_DEVELOPMENT, f"Starting project: {self.context.project_name}")

    def handle_spec(self):
        prompt = f"Create a technical specification for the following objective: {self.context.objective}. Save it to {self.context.spec_path}."
        output = self.run_goose_command(prompt)
        if output:
            self.transition(State.CODE_GENERATION, "Specification created.")
        else:
            self.transition(State.FAILED, "Failed to create specification.")

    def handle_code(self):
        prompt = f"Based on the spec in {self.context.spec_path}, generate the implementation in {self.context.code_path}."
        output = self.run_goose_command(prompt)
        if output:
            self.transition(State.CODE_TESTING, "Implementation generated.")
        else:
            self.transition(State.FAILED, "Failed to generate code.")

    def handle_test(self):
        prompt = f"Write unit tests for the code in {self.context.code_path} and save them to {self.context.test_path}. Then run the tests and report results."
        output = self.run_goose_command(prompt)
        if output and "FAIL" not in output.upper():
            self.transition(State.CODE_INTEGRATION, "Tests passed.")
        else:
            self.update_status("Tests failed. Retrying code generation...")
            self.transition(State.CODE_GENERATION, "Retrying code generation due to test failure.")

    def handle_integration(self):
        # In a real scenario, this might involve git or merging files.
        # For now, we just acknowledge receipt in the build dir.
        prompt = f"Finalize and integrate the generated code in {self.context.code_path}. Ensure it is clean and ready for release."
        output = self.run_goose_command(prompt)
        if output:
            self.transition(State.CODE_RELEASE, "Integration complete.")
        else:
            self.transition(State.FAILED, "Integration failed.")

    def handle_release(self):
        pass

if __name__ == "__main__":
    import sys
    obj = "Create a simple Python utility that prints the first 10 Fibonacci numbers."
    name = "fibonacci_tool"
    
    if len(sys.argv) > 1:
        obj = sys.argv[1]
    if len(sys.argv) > 2:
        name = sys.argv[2]
    
    factory = SoftwareFactory(obj, name)
    factory.run()
