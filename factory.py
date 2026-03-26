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
        os.makedirs(self.context.build_dir, exist_ok=True)
        
        # Initialize isolated git repository in the build folder
        subprocess.run(["git", "init"], cwd=self.context.build_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "factory@goose.os"], cwd=self.context.build_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Software Factory"], cwd=self.context.build_dir, capture_output=True)
        
        # Create initial commit to establish 'master' branch
        with open(os.path.join(self.context.build_dir, ".init"), "w") as f:
            f.write("Initial")
        subprocess.run(["git", "add", ".init"], cwd=self.context.build_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.context.build_dir, capture_output=True)
        
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
        try:
            with open("status.json", "w") as f:
                json.dump(status, f, indent=2)
        except:
            pass
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
            raw_output = result.stdout
            tokens = 0
            text_response = ""
            
            if "{" in raw_output:
                try:
                    json_part = raw_output[raw_output.find("{"):]
                    data = json.loads(json_part)
                    tokens = data.get("metadata", {}).get("total_tokens") or 0
                    
                    # Extract last assistant message text
                    for msg in reversed(data.get("messages", [])):
                        if msg.get("role") == "assistant":
                            for content in msg.get("content", []):
                                if content.get("type") == "text":
                                    text_response += content.get("text", "")
                            if text_response: break
                except:
                    text_response = raw_output # Fallback
            else:
                text_response = raw_output

            self.context.total_tokens += tokens
            return text_response, tokens
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
        if output and not "error" in output.lower():
            # Commit the spec to the isolated repo's master branch
            subprocess.run(["git", "add", "spec.md"], cwd=self.context.build_dir, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Added Technical Specification"], cwd=self.context.build_dir, capture_output=True)
            self.transition(State.PLANNING, "Specification created. Moving to planning...")
        else:
            self.transition(State.FAILED, f"Failed to create specification: {output[:100]}")

    def handle_planning(self):
        prompt = f"Based on the spec in {self.context.spec_path}, create a tasks.json file with a list of discrete coding tasks. Format each task as {{'id': 1, 'title': 'name', 'description': '...'}}. Output ONLY the raw JSON array. No preamble."
        output, _ = self.run_goose_command(prompt)
        try:
            # Robust JSON extraction from the text response
            json_match = re.search(r'\[.*\]', output, re.DOTALL)
            if json_match:
                tasks_str = json_match.group()
                tasks = json.loads(tasks_str)
                # Ensure each task has necessary keys
                for t in tasks:
                    if 'title' not in t: t['title'] = t.get('name', f"Task {t.get('id', '?')}")
                
                self.context.tasks = tasks
                with open(self.context.tasks_path, "w") as f:
                    json.dump(tasks, f, indent=2)
                
                # Commit tasks.json to the isolated repo's master branch
                subprocess.run(["git", "add", "tasks.json"], cwd=self.context.build_dir, capture_output=True)
                subprocess.run(["git", "commit", "-m", "Added Task List"], cwd=self.context.build_dir, capture_output=True)
                
                self.transition(State.EXECUTION, f"Planned {len(tasks)} tasks.")
            else:
                self.transition(State.FAILED, f"Planner did not return JSON. Response: {output[:100]}")
        except Exception as e:
            self.transition(State.FAILED, f"Failed to parse tasks: {e}")

    def handle_execution(self):
        for task in self.context.tasks:
            task_id = task.get('id', 'unknown')
            title = task.get('title', 'untitled').replace(" ", "_")
            branch_name = f"task/build_{self.context.build_dir.split('/')[-1]}_{title}"
            task['branch'] = branch_name
            task['status'] = 'WORKING'
            task['tokens'] = 0
            
            self.update_status(f"Worker Task {task_id}: {task.get('title', 'untitled')}")
            
            try:
                # Target the isolated repo in the build folder
                build_cvd = self.context.build_dir
                subprocess.run(["git", "checkout", "-b", branch_name], cwd=build_cvd, check=False)
                subprocess.run(["git", "checkout", branch_name], cwd=build_cvd, check=True)
                
                prompt = f"Executing task: {task.get('title')}. Description: {task.get('description')}. Spec in {self.context.spec_path}. Implement and commit work."
                output, tokens = self.run_goose_command(prompt)
                task['tokens'] = tokens
                
                if output:
                    # Capture identifying filenames if goose created any
                    exclude = ['.gitignore', 'factory.py', 'dashboard.py', 'status.json', 'README.md', '.DS_Store']
                    new_files = [f for f in os.listdir(build_cvd) if os.path.isfile(os.path.join(build_cvd, f)) and not f.startswith('.') and f not in exclude]
                    
                    if not new_files:
                        # Fallback: Save the entire output as a markdown file for this task
                        filename = f"{title}.md"
                        file_path = os.path.join(build_cvd, filename)
                        with open(file_path, "w") as f:
                            f.write(output)
                        self.update_status(f"Saved fallback output to {filename}")

                    subprocess.run(["git", "add", "."], cwd=build_cvd, check=True)
                    subprocess.run(["git", "commit", "-m", f"Completed Task {task_id}"], cwd=build_cvd, check=False)
                    task['status'] = 'COMPLETED'
                else:
                    task['status'] = 'FAILED'
                
                subprocess.run(["git", "checkout", "master"], cwd=build_cvd, check=False)
            except Exception as e:
                self.update_status(f"Task {task_id} failed: {e}")
                task['status'] = 'ERROR'

        self.transition(State.INTEGRATION, "Execution complete.")

    def handle_integration(self):
        self.update_status("Final integration merging...")
        branch_list = [t['branch'] for t in self.context.tasks if t.get('status') == 'COMPLETED']
        
        prompt = f"Merge these branches: {', '.join(branch_list)}. Resolve conflicts, run final tests to ensure no regressions were introduced, and finalize project in {self.context.build_dir}."
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
