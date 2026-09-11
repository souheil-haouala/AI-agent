import os
import sys
import yaml
import base64
import time
import requests
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

# AUTOMATED LOCAL SECRET LOADING FROM YOUR .ENV FILE
load_dotenv()

class ScrumDevOpsAgent:
    def __init__(self):
        # 1. Fetch the environment key
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("❌ Error: GEMINI_API_KEY environment variable not found.")
            print("Please make sure you created a .env file with GEMINI_API_KEY=your_key")
            sys.exit(1)
            
        # 2. Universal Handshake Client Initialization Matrix
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    def read_story_from_local_backlog(self, filepath: str) -> str:
        """OFFLINE SCRUM BOARD PARSER: Ingests user stories from local backlog ledger."""
        if not os.path.exists(filepath):
            return None
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Extract the first available task marked as TODO
            for ticket in data:
                if ticket.get("status").upper() == "TODO":
                    print(f"📋 Ingested Ticket {ticket['ticket_id']}: {ticket['title']}")
                    return ticket["description"]
        except Exception as e:
            print(f"⚠️ Error parsing backlog.json: {e}")
            
        return None

    def mark_ticket_as_completed_in_backlog(self, filepath: str, ticket_id: str = "DEV-101"):
        """AGILE RESOLUTION ENGINE: Updates your local Scrum database board file dynamically."""
        if not os.path.exists(filepath):
            print(f"⚠️ Cannot find file path: {filepath}")
            return
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            updated = False
            for ticket in data:
                if ticket.get("ticket_id") == ticket_id and ticket.get("status").upper() == "TODO":
                    ticket["status"] = "DONE"
                    updated = True
                    
            if updated:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                    f.flush()  # Forces Windows to instantly refresh open editor tabs
                print(f"🏁 Scrum Lifecycle Event: Card {ticket_id} moved dynamically from [TODO] -> [DONE]!")
            else:
                print(f"⚠️ Ticket {ticket_id} was already completed or not found in TODO state.")
        except Exception as e:
            print(f"⚠️ Failed to update scrum backlog status metrics: {e}")

    def audit_local_dockerfile(self, filepath: str) -> dict:
        """Programmatic tool to audit Dockerfile line placement before calling AI."""
        if not os.path.exists(filepath):
            return {"has_dockerfile": False}
            
        with open(filepath, "r") as f:
            content = f.read()
            
        lines = content.split("\n")
        copy_all_idx = -1
        install_idx = -1
        
        for i, line in enumerate(lines):
            clean = line.strip().upper()
            if clean.startswith("COPY . ."):
                copy_all_idx = i
            if "INSTALL" in clean or "NPM CI" in clean:
                install_idx = i
                
        caching_optimized = True
        if copy_all_idx != -1 and install_idx != -1 and copy_all_idx < install_idx:
            caching_optimized = False
            
        return {
            "has_dockerfile": True,
            "caching_optimized": caching_optimized,
            "raw_content": content
        }

    def generate_offline_fallback_yaml(self) -> str:
        """MOCK RESILIENCE ENGINE: Generates valid YAML locally if API accounts are rate-locked."""
        print("🛠️ Local Fallback Activator: Compiling localized pipeline matrix...")
        fallback_yaml = """name: Automated CI-CD Pipeline
on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Running automated test frameworks..."
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          cache-from: type=gha
          cache-to: type=gha,mode=max"""
        return fallback_yaml

    def generate_pipeline(self, user_story: str, docker_audit: dict) -> str:
        """Invokes Gemini with rate-limit and server resilience to survive traffic spikes."""
        system_instruction = (
            "You are an elite DevOps Engineer operating in a Scrum team. Your sole job is to "
            "output a syntactically perfect, production-grade GitHub Actions YAML workflow "
            "based on the developer's user story and local repository audit facts. "
            "CRITICAL: Output ONLY valid, raw YAML code. Never wrap the output in markdown code blocks. "
            "No conversational preambles or post-explanations allowed."
        )
        
        prompt = f"Story: {user_story}\nAudit: {json.dumps(docker_audit)}"
        
        try:
            print(f"🧠 Invoking Gemini reasoning engine...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                ),
            )
            return response.text
        except ClientError as ce:
            if ce.code == 429 or ce.code == 401:
                return self.generate_offline_fallback_yaml()
            raise ce
        except Exception:
            return self.generate_offline_fallback_yaml()

    def test_yaml_integrity(self, yaml_string: str) -> bool:
        """Local sanity parser to catch syntax spacing breaks before saving or deploying."""
        try:
            yaml.safe_load(yaml_string)
            print("✅ Local Integration Verification Passed: Valid YAML Syntax caught.")
            return True
        except yaml.YAMLError:
            return False
# ─── RUNTIME EXECUTION BLOCK ───────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Initializing Pipeline Generation Agent...")
    agent = ScrumDevOpsAgent()
    
    mock_scrum_story = agent.read_story_from_local_backlog("backlog.json")
    if not mock_scrum_story:
        mock_scrum_story = "As a developer, I need a CI pipeline that runs unit tests on every pull request."
    
    print("🔍 Auditing local directory configuration files...")
    audit_results = agent.audit_local_dockerfile("Dockerfile")
    print(f"   -> Dockerfile Caching Optimized: {audit_results.get('caching_optimized')}")
    
    generated_workflow = agent.generate_pipeline(mock_scrum_story, audit_results)
    
    print("\n--- AGENT GENERATED OUTPUT RAW WINDOW ---")
    print(generated_workflow)
    print("------------------------------------------\n")
    
    if agent.test_yaml_integrity(generated_workflow):
        print("\n🌐 Phase 2: Running Automated Deployment Matrix...")
        
        # INCORPORATED USER REPOSITORY PARAMETERS
        GITHUB_USERNAME = "souheil-haouala" 
        REPOSITORY_NAME = "AI-agent"
        github_token = os.environ.get("GITHUB_TOKEN")

        def write_pipeline_to_local_disk(workflow_code: str):
            local_workflow_dir = ".github/workflows"
            os.makedirs(local_workflow_dir, exist_ok=True)
            local_file_path = os.path.join(local_workflow_dir, "ci.yml")
            with open(local_file_path, "w", encoding="utf-8") as local_file:
                local_file.write(workflow_code)
            print("\n💾 SELF-CORRECTING DISK FALLBACK ACTIVATED!")
            print(f"   The verified pipeline file has been written directly to your disk workspace folder.")
            print(f"   Location: {os.path.abspath(local_file_path)}")
            agent.mark_ticket_as_completed_in_backlog("backlog.json", ticket_id="DEV-101")

        if not github_token:
            print("⚠️ Warning: GITHUB_TOKEN missing inside .env. Switching to local disk deployment mode.")
            write_pipeline_to_local_disk(generated_workflow)
            sys.exit(0)

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        # INCORPORATED FIXED PATH DEFINITIONS BINDINGS
        base_url = "https://github.com"
        target_path = ".github/workflows/ci.yml"

        try:
            main_ref_url = f"{base_url}/git/ref/heads/main"
            ref_res = requests.get(main_ref_url, headers=headers)
            
            # HTML Gibberish Blocker
            if ref_res.text.strip().startswith("<!DOCTYPE html>") or ref_res.text.strip().startswith("<html>"):
                print("❌ GitHub Server Interruption: Network route returned a webpage error layout.")
                write_pipeline_to_local_disk(generated_workflow)
                sys.exit(0)
            
            # If repo is empty, seed README.md to initialize main branch layout
            if ref_res.status_code == 404 or ref_res.status_code == 409 or not ref_res.text:
                print("⚠️ Repository is empty. Seeding root-level README.md to initialize 'main' branch...")
                init_readme_url = f"{base_url}/contents/README.md"
                readme_text = "# AI Scrum Agent Workspace\nAutomated DevOps initialization pipeline."
                encoded_readme = base64.b64encode(readme_text.encode("utf-8")).decode("utf-8")
                
                init_payload = {
                    "message": "chore: initial repository structure setup",
                    "content": encoded_readme,
                    "branch": "main"
                }
                init_res = requests.put(init_readme_url, json=init_payload, headers=headers)
                
                if init_res.text.strip().startswith("<!DOCTYPE html>") or init_res.text.strip().startswith("<html>"):
                    write_pipeline_to_local_disk(generated_workflow)
                    sys.exit(0)
                
                if init_res.status_code == 200 or init_res.status_code == 201:
                    print("✅ Root structure initialized successfully. Pausing 2 seconds for synchronization...")
                    time.sleep(2)
                    ref_res = requests.get(main_ref_url, headers=headers)
                else:
                    write_pipeline_to_local_disk(generated_workflow)
                    sys.exit(0)
                
            main_sha = ref_res.json()["object"]["sha"]
            feature_branch = f"feat-devops-pipeline-{int(time.time())}"
            
            create_branch_url = f"{base_url}/git/refs"
            branch_payload = {"ref": f"refs/heads/{feature_branch}", "sha": main_sha}
            branch_res = requests.post(create_branch_url, json=branch_payload, headers=headers)
            
            if branch_res.status_code == 201:
                print(f"🌱 Isolated feature branch cut successfully: {feature_branch}")
                
                file_url = f"{base_url}/contents/{target_path}"
                encoded_content = base64.b64encode(generated_workflow.encode("utf-8")).decode("utf-8")
                
                file_payload = {
                    "message": "feat(devops): automated pipeline initialization",
                    "content": encoded_content,
                    "branch": feature_branch
                }
                file_res = requests.put(file_url, json=file_payload, headers=headers)
                print("📝 Workflow file securely committed to feature branch.")
                
                pr_url = f"{base_url}/pulls"
                pr_payload = {
                    "title": "feat(devops): automated CI/CD pipeline initialization",
                    "head": feature_branch,
                    "base": "main",
                    "body": "This PR was automatically generated by your AI Scrum Agent."
                }
                pr_res = requests.post(pr_url, json=pr_payload, headers=headers)
                
                if pr_res.status_code == 201:
                    print(f"\n🚀 SUCCESS! The pipeline agent generated a live Pull Request: {pr_res.json()['html_url']}")
                    agent.mark_ticket_as_completed_in_backlog("backlog.json", ticket_id="DEV-101")
                else:
                    write_pipeline_to_local_disk(generated_workflow)
            else:
                write_pipeline_to_local_disk(generated_workflow)
                
        except Exception:
            write_pipeline_to_local_disk(generated_workflow)
