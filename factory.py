import subprocess
import os
import json
import dataclasses
import re
from enum import Enum
from typing import List, Optional, Dict

class State(Enum):
    IDLE = "IDLE"
    SPEC_DEVELOPMENT = "SPEC_DEVELOPMENT"
    PLANNING = "PLANNING"
    EXECUTION = "EXECUTION"
    INTEGRATION = "INTEGRATION"
    CODE_RELEASE = "CODE_RELEASE"
    FAILED = "FAILED"

@dataclasses.dataclass
class FactoryContext:
    objective: str
    project_name: str = "project"
    build_dir: str = ""
    spec_path: str = ""
    tasks_path: str = ""
    history: List[str] = dataclasses.field(default_factory=list)
    tasks: List[Dict] = dataclasses.field(default_factory=list)
    total_tokens: int = 0

class SoftwareFactory:
    def __init__(self, objective: str, project_name: str = "auto_project"):
        self.state = State.IDLE
        self.context = FactoryContext(objective=objective, project_name=project_name)
        self.setup_build_dir()
        self.transitions = {
            State.IDLE: self.handle_idle,
            State.SPEC_DEVELOPMENT: self.handle_spec,
            State.PLANNING: self.handle_planning,
            State.EXECUTION: self.handle_execution,
            State.INTEGRATION: self.handle_integration,
            State.CODE_RELEASE: self.handle_release,
        }
        self.update_status("Initialized")

    def setup_build_dir(self):
        base_dir = "builds"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        
        existing = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        indices = [int(d.split('_')[0]) for d in existing if d.split('_')[0].isdigit()]
        next_idx = max(indices, default=0) + 1
        
        dir_name = f"{next_idx:03d}_{self.context.project_name.replace(' ', '_')}"
        self.context.build_dir = os.path.join(base_dir, dir_name)
        os.makedirs(self.context.build_dir)
        
        self.context.spec_path = os.path.join(self.context.build_dir, "spec.md")
        self.context.tasks_path = os.path.join(self.context.build_dir, "tasks.json")

    def update_status(self, message: str):
        status = {
            "state": self.state.value,
            "message": message,
            "objective": self.context.objective,
            "project": self.context.project_name,
            "build_dir": self.context.build_dir,
            "history": self.context.history,
            "tasks": self.context.tasks,
            "total_tokens": self.context.total_tokens
        }
        with open("status.json", "w") as f:
            json.dump(status, f, indent=2)
        print(f"[{self.state.value}] {message}")

    def run_goose_command(self, prompt: str):
        self.update_status(f"Running Goose: {prompt[:100]}...")
        goose_path = "/Users/jamesdhope/.local/bin/goose"
        try:
            result = subprocess.run(
                [goose_path, "run", "-i", "-", "--output-format", "json"], 
                input=prompt,
                capture_output=True, 
                text=True, 
                check=True
            )
            output = result.stdout
            tokens = 0
            if "{" in output:
                try:
                    # JSON from Goose might have conversational text outside it
                    json_parts = re.findall(r'\{.*\}', output, re.DOTALL)
                    if json_parts:
                        # Find the largest JSON block (the session summary)
                        data = json.loads(json_parts[-1])
                        tokens = data.get("metadata", {}).get("total_tokens") or 0
                except:
                    pass
            self.context.total_tokens += tokens
            return output, tokens
        except Exception as e:
            self.update_status(f"Goose failed: {e}")
            return None, 0

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
        prompt = f"Create a technical specification for: {self.context.objective}. Save to {self.context.spec_path}."
        output, _ = self.run_goose_command(prompt)
        if output:
            self.transition(State.PLANNING, "Specification created. Moving to planning...")
        else:
            self.transition(State.FAILED, "Failed to create specification.")

    def handle_planning(self):
        prompt = f"Based on the spec in {self.context.spec_path}, create a tasks.json file with a list of discrete coding tasks. Format each task as {{'id': 1, 'title': 'name', 'description': '...'}}. Output ONLY the raw JSON array. No preamble, no markdown code blocks."
        output, _ = self.run_goose_command(prompt)
        try:
            # Robust JSON extraction
            json_match = re.search(r'\[.*\]', output, re.DOTALL)
            if json_match:
                tasks_str = json_match.group()
                tasks = json.loads(tasks_str)
                self.context.tasks = tasks
                with open(self.context.tasks_path, "w") as f:
                    json.dump(tasks, f, indent=2)
                self.transition(State.EXECUTION, f"Planned {len(tasks)} tasks.")
            else:
                self.transition(State.FAILED, f"Goose output did not contain valid JSON array for tasks. Output start: {output[:50]}...")
        except Exception as e:
            self.transition(State.FAILED, f"Failed to parse tasks.json: {e}")

    def handle_execution(self):
        for task in self.context.tasks:
            task_id = task['id']
            title = task['title'].replace(" ", "_")
            branch_name = f"task/build_{self.context.build_dir.split('/')[-1]}_{title}"
            task['branch'] = branch_name
            task['status'] = 'WORKING'
            task['tokens'] = 0
            
            self.update_status(f"Starting Worker Task {task_id}: {task['title']}")
            
            try:
                subprocess.run(["git", "checkout", "-b", branch_name], check=True)
                
                prompt = f"Executing task: {task['title']}. Description: {task['description']}. The spec is in {self.context.spec_path}. Implement the code and tests within the project structure. Commit your work."
                output, tokens = self.run_goose_command(prompt)
                task['tokens'] = tokens
                
                if output:
                    subprocess.run(["git", "add", "."], check=True)
                    subprocess.run(["git", "commit", "-m", f"Completed Task {task_id}: {task['title']}"], check=False)
                    task['status'] = 'COMPLETED'
                else:
                    task['status'] = 'FAILED'
                
                subprocess.run(["git", "checkout", "master"], check=True)
            except Exception as e:
                self.update_status(f"Git or Worker failed for task {task_id}: {e}")
                task['status'] = 'ERROR'
                subprocess.run(["git", "checkout", "master"], check=False)

        self.transition(State.INTEGRATION, "Execution complete. Moving to integration...")

    def handle_integration(self):
        self.update_status("Release Agent merging branches...")
        branch_list = [f"task/build_{self.context.build_dir.split('/')[-1]}_{t['title'].replace(' ', '_')}" 
                       for t in self.context.tasks if t.get('status') == 'COMPLETED']
        
        prompt = f"Merge the following branches into master: {', '.join(branch_list)}. Resolve any conflicts and finalize the build. Spec is in {self.context.spec_path}. Resolve logic in the project directory."
        output, _ = self.run_goose_command(prompt)
        if output:
            self.transition(State.CODE_RELEASE, "Multi-agent integration successful.")
        else:
            self.transition(State.FAILED, "Integration failed.")

    def handle_release(self):
        pass

if __name__ == "__main__":
    import sys
    obj = "Build a Turing Test Machine."
    name = "turing_factory"
    if len(sys.argv) > 1: obj = sys.argv[1]
    if len(sys.argv) > 2: name = sys.argv[2]
    
    factory = SoftwareFactory(obj, name)
    factory.run()
