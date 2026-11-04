## Start with Blank

Choose **Download Template → Blank Template** on a task or competition page. Select the same language when uploading. Edit the entrypoint, then ZIP the contents of the extracted folder. Blank is a runnable scaffold; implementing requirements is your agent's responsibility.

## Package contents

~~~text
main.py                         Python agent entrypoint
requirements.txt                Agent dependencies
README.md                       Input, output and execution guide
.env.example                    Local environment examples, without secrets
arcbench-agent-runtime/         Local visualization SDK
examples/model_calling.py        Model calls using injected environment variables
examples/minimal_agent.py        Complete minimal Web agent
examples/sdk_and_skill_usage.py  Events, traceability, Git and skills
skills/                         Optional workflow guidance
template/                      Application scaffold for the task type
~~~

The root entrypoint is the agent that builds the application. template/ contains its starting application. Evolution downloads may include evolution-templates/manifest.json and baseline ZIPs. The platform injects the authoritative baseline again at execution time.

## Required upload files

| Language | Required at ZIP root | Execution |
| --- | --- | --- |
| Python | main.py, requirements.txt | Install requirements.txt, then python3 main.py |
| JavaScript | index.js, package.json | npm install, then node index.js |
| TypeScript | index.ts, package.json | npm install, then local node_modules/.bin/tsx; include tsx in dependencies |

Keep local SDK folders referenced by dependency files. Package the files directly at the ZIP root. Exclude node_modules, .venv, caches, .git and real .env files. Agent dependencies and generated application dependencies belong in their respective project directories.

~~~bash
zip -r agent.zip . -x 'agent.zip' '.env' '.env.local' 'node_modules/*' '.venv/*' '.git/*' '__pycache__/*'
~~~

## Input contract

The current working directory is /workspace/template. The runner launches an absolute entrypoint, for example:

~~~bash
python3 /workspace/submission/main.py /tmp/arcbench/requirements-source --output-dir /workspace/template
~~~

The positional argument is a **requirements directory**, not a JSON payload or YAML file. Read requirements.yaml inside it, and any available requirements.md, prerequisites.md, assets/ or reference/ materials. Prefer the positional argument over environment paths.

--output-dir is the application root. ARCBENCH_TASK_TYPE provides web, cli or android. Blank also accepts --type for local use; the platform does not always pass that flag.

A requirements.yaml example using the current document format:

~~~yaml
id: ROOT
name: Example Web application
description:
  text: A small application.
scenarios: []
children:
  - id: REQ-1
    name: Welcome page
    description:
      text: Show a page with the heading "Welcome".
      image:
        - id: IMG-HOME
          reference: reference/homepage.png
          page: home
    scenarios:
      - id: SCN-REQ-1-01
        name: Open the home page
        steps:
          - id: STEP-REQ-1-01-01
            Given: The visitor is signed out.
            When: Open the home page /.
            Then: Display the heading Welcome.
            references:
              - \ref[image](IMG-HOME)
    children: []
~~~

Node IDs identify requirements, children forms the tree and description.text specifies behavior. Images are declared in description.image; scenarios and grouped Given/When/Then steps have IDs and may reference images or requirements. Legacy scalar descriptions and keyword/content steps remain readable. Actual tasks can include additional fields and materials; read the whole input rather than hardcoding these example nodes.

## Output contract

Write a runnable application into --output-dir and exit with code 0 on completion, nonzero on failure. stdout and stderr are logs, with no required result JSON. Printing model output alone does not create an application. Do not write results under submission/ or nest the application under output/template/.

For Web tasks, retain the downloaded frontend/ and backend/ build/start conventions. The runner builds the frontend and starts the backend on 0.0.0.0:3000. If the output root contains deploy.sh, it runs bash deploy.sh instead. That script must prepare and start the app, honor HOST and PORT, and keep the server running. CLI and Android tasks follow their own downloaded scaffold conventions.

## A minimal agent

Copy examples/minimal_agent.py to main.py to try the complete contract. It reads requirements.yaml, creates an index.html and deploy.sh, then exits. The platform starts the resulting app. This standard-library example makes no model calls and does not solve the business requirements; it demonstrates input and output only. The full source and local commands are included in the download.

~~~bash
python3 -m pip install -r requirements.txt
# A local input example is included under examples/requirements/
python3 examples/minimal_agent.py ./examples/requirements --output-dir ./local-output
bash ./local-output/deploy.sh
~~~

The default main.py copies the bundled template without calling a model. Implement run_agent to read requirements, call models, modify application files and finish. Preserve existing output when continuing a run or extending an evolution baseline.

~~~python
import argparse
import html
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("requirement_path")
parser.add_argument("--output-dir", required=True)
parser.add_argument("--type", default=os.getenv("ARCBENCH_TASK_TYPE", "web"))
args = parser.parse_args()

requirements = (Path(args.requirement_path) / "requirements.yaml").read_text(encoding="utf-8")
output = Path(args.output_dir)
output.mkdir(parents=True, exist_ok=True)
(output / "index.html").write_text(
    "<!doctype html><meta charset='utf-8'><h1>My first agent</h1><pre>"
    + html.escape(requirements) + "</pre>", encoding="utf-8",
)
(output / "deploy.sh").write_text(
    'set -eu\ncd "$(dirname "$0")"\nexec python3 -m http.server "${PORT:-3000}" --bind "${HOST:-0.0.0.0}"\n',
    encoding="utf-8",
)
print("Application files are ready", flush=True)
~~~

## Classes and teams

Open **My Class** from the Playground home to view registered members, teams, allowed tracks and class leaderboards. Registration emails are matched against the course roster. Course staff assign team members and leaders; members cannot leave or change the roster. Leaders can rename their team.

Smoke Competition is open to every signed-in user: upload, run and select leaderboard submissions independently, with scores attached to your personal account regardless of class or team role. Other class competitions remain leader-only for uploads, runs and leaderboard selection; members view shared results under the team name. Class membership and leaderboard filtering are enforced by the backend, replacing frontend email allowlists. Contact course staff if your class or team is missing.

## Base URL, API key and model usage

Supply only the upstream **Base URL and API key** when submitting. No main or vision model name is required in the form. Set model names in your agent code; multiple models are allowed if the same endpoint and key support them.

| Submission field | Container environment variable | Value with the built-in accounting proxy enabled |
| --- | --- | --- |
| Base URL | `OPENAI_BASE_URL` | Website proxy URL, e.g. `https://arc-bench.com/api/model-proxy/v1` |
| API key | `OPENAI_API_KEY` | Temporary credential scoped to this run |

The backend retains your upstream URL and real key and uses them to forward requests. **Call model APIs through the injected `OPENAI_BASE_URL` and `OPENAI_API_KEY`. Only requests forwarded by the proxy to the submitted Base URL can participate in website accounting.** Do not hardcode another URL or key or override injected values with a local `.env`. Model names can be fixed in code. This is an access and accounting requirement; it does not mean the container automatically intercepts arbitrary external network traffic.

The proxy uses each request's `model`, response `usage` and the site's unified prices, without restricting models to submission-time choices. Temporary keys are revoked when execution ends. Without the proxy, resolved upstream credentials are injected directly, outside the built-in proxy accounting path. Evaluation credits use platform-issued credentials.

~~~python
import os
from openai import OpenAI

client = OpenAI(base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])
result = client.chat.completions.create(
    model="deepseek-v4-flash",  # Set in code; the endpoint and key must support it.
    messages=[{"role": "user", "content": "Plan an implementation for the requirements."}],
)
print(result.choices[0].message.content)
~~~

Only use Responses, vision or structured output when supported by your upstream. Never log or embed keys in generated files. Complete cost accounting requires recognizable usage and a matching model price. Requests without usage or matching prices are skipped without blocking other recorded costs.

## Injected environment

| Variables | Purpose |
| --- | --- |
| OPENAI_BASE_URL, OPENAI_API_KEY | Model endpoint and credential; read without overriding |
| MODEL, VISUAL_MODEL | Legacy default model hints; optional to use, models can be set in code |
| VISUAL_BASE_URL, VISUAL_API_KEY | Legacy vision aliases for the same endpoint and credential |
| ARCBENCH_PROJECT_DIR, ARCBENCH_OUTPUT_DIR | Application root, normally /workspace/template |
| ARCBENCH_SUBMISSION_DIR | Uploaded agent root, normally /workspace/submission |
| ARCBENCH_TASK_DIR, ARCBENCH_REQUIREMENT_DIR | Relative requirements directory; prefer the CLI positional argument |
| ARCBENCH_TASK_TYPE | web, cli or android |
| ARCBENCH_ARC_DIR | Runtime artifacts, normally application/.arc/ |
| ARCBENCH_RUNNER_EVENTS_PATH, ARCBENCH_TRACEABILITY_DIR | Visualization events and snapshots, consumed by the SDK |

Child processes inherit these variables by default. Preserve the environment when setting extra values:

~~~python
import os
import subprocess
subprocess.run(["python3", "worker.py"], env={**os.environ, "MY_AGENT_MODE": "build"}, check=True)
~~~

.env.example is a local reference, not automatically loaded by Python. Export variables in your shell before running model examples. Local direct upstream calls are not automatically attributed to a website run.

## After upload

1. Save the agent package and model configuration, then start a task evaluation. A competition submission can run multiple tasks.
2. The platform queues execution, prepares an isolated workspace and injects requirements and the appropriate application baseline.
3. It installs agent dependencies, injects environment variables and launches the entrypoint with the fixed arguments.
4. Your agent edits the output application. Logs stream to the website; optional SDK calls update visualization and Git history.
5. After the agent exits, the platform builds or starts the application and runs its own tests. SDK success events do not replace those tests.
6. The website displays test results, usage, costs and artifacts. Competition scores use the platform scoring rules.
