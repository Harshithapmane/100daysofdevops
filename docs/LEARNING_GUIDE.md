# Learning Guide: Python and the Incident Copilot App

A beginner-friendly walkthrough, written for someone who already knows some PowerShell.
Read it in order. Every code example in Part 1 was run and the output shown is real.

**Contents**
0. How to run Python (2 minutes)
1. Python basics (with PowerShell comparisons)
2. How web APIs work
3. Your app, file by file, line by line
4. Running the app on your computer
5. How each DevOps phase touches this app
6. Practice exercises (with answers)
7. Glossary

---

## Part 0: How to run Python

Open a terminal (PowerShell on Windows, Terminal on Mac/Linux) and check Python is installed:

```powershell
python --version        # Windows (or try: py --version)
python3 --version       # Mac / Linux
```

You need 3.10 or newer (3.12 is what the project uses).

There are two ways to run Python code:

1. **Interactive mode.** Type `python` and press Enter. You get a `>>>` prompt where you type one line and see the result immediately. It is like typing commands in PowerShell. Type `exit()` to leave. Best for experimenting.
2. **Script files.** Put code in a file such as `hello.py` and run `python hello.py`. This is how real programs run.

Try it now:

```python
>>> 2 + 3
5
>>> print("hello")
hello
```

---

## Part 1: Python basics

### 1.1 The one big rule: indentation matters

PowerShell uses braces `{ }` to group code. Python uses a **colon** and **indentation** (4 spaces):

```python
if age > 18:
    print("adult")      # indented = inside the if
    print("still inside")
print("outside the if")  # not indented = outside
```

If the indentation is wrong, Python gives an `IndentationError`. Comments start with `#`, the same as PowerShell.

### 1.2 PowerShell vs Python cheat sheet

| Idea | PowerShell | Python |
|---|---|---|
| Variable | `$name = "Sam"` | `name = "Sam"` (no `$`) |
| Print | `Write-Host $x` | `print(x)` |
| List | `@("a","b")` | `["a", "b"]` |
| Dictionary | `@{id=1; title="x"}` | `{"id": 1, "title": "x"}` |
| If | `if ($x -eq 5) { }` | `if x == 5:` |
| Loop | `foreach ($s in $servers) { }` | `for s in servers:` |
| Function | `function Greet($n) { }` | `def greet(n):` |
| Nothing | `$null` | `None` |
| Insert into text | `"Hi $name"` | `f"Hi {name}"` |
| Error handling | `try { } catch { }` | `try:` / `except:` |
| Load a library | `Import-Module X` | `import x` |

### 1.3 Variables and basic types

A variable is a name stuck onto a value. No declaration needed.

```python
name = "Sam"        # str   (text)
age = 30            # int   (whole number)
price = 9.99        # float (decimal number)
is_open = True      # bool  (True or False, capital first letter)
nothing = None      # None  (means "no value")

print(name, age, price, is_open, nothing)
# Sam 30 9.99 True None

print(type(age), type(name))
# <class 'int'> <class 'str'>
```

**f-strings** put variables inside text. Put an `f` before the quote and use `{ }`:

```python
print(f"{name} is {age} years old")
# Sam is 30 years old
```

### 1.4 Lists

An ordered collection. Counting starts at **0**.

```python
servers = ["web1", "web2", "db1"]
servers.append("cache1")             # add to the end

print(servers[0], servers[-1], len(servers))
# web1 cache1 4                      # [-1] means "the last one"
```

### 1.5 Dictionaries (very important, the whole API is built on them)

A dictionary stores **key: value** pairs, like a PowerShell hashtable.

```python
incident = {"id": 1, "title": "Disk full", "severity": "high"}

print(incident["title"])             # Disk full
incident["fix"] = "Deleted logs"     # add a new key
print(incident.get("root_cause"))    # None  (.get is safe if the key is missing)
print(incident)
# {'id': 1, 'title': 'Disk full', 'severity': 'high', 'fix': 'Deleted logs'}
```

`incident["root_cause"]` (square brackets) would crash with a `KeyError` because that key doesn't exist. `.get()` returns `None` instead.

### 1.6 Decisions and loops

```python
severity = "high"
if severity == "critical":
    print("Wake everyone up")
elif severity == "high":
    print("Page the on-call")          # this one runs
else:
    print("Handle tomorrow")
```

```python
for s in servers:
    print("Checking", s)
# Checking web1
# Checking web2
# Checking db1
# Checking cache1
```

A one-line if/else (used in `store.py`):

```python
x = "yes" if age > 18 else "no"       # x is "yes"
```

### 1.7 Functions

```python
def greet(name, punctuation="!"):     # punctuation has a default value
    return "Hello, " + name + punctuation

print(greet("Sam"), greet("Sam", "?"))
# Hello, Sam! Hello, Sam?
```

`return` sends a value back. A function with no `return` gives back `None`.

### 1.8 List comprehensions (a compact way to filter a list)

```python
incidents = [
    {"id": 1, "severity": "high"},
    {"id": 2, "severity": "low"},
    {"id": 3, "severity": "high"},
]
high = [i for i in incidents if i["severity"] == "high"]
print(high)
# [{'id': 1, 'severity': 'high'}, {'id': 3, 'severity': 'high'}]
```

Read it aloud as: "give me `i`, for every `i` in `incidents`, but only if its severity is high."

### 1.9 Classes (a blueprint for objects)

A class describes what something has (data) and can do (actions). Your app uses classes heavily.

```python
class Server:
    def __init__(self, name, cpu):     # runs when you create a Server
        self.name = name               # 'self' means "this particular server"
        self.cpu = cpu

    def describe(self):
        return f"{self.name} has {self.cpu} CPUs"

web = Server("web1", 4)                # create an object from the blueprint
print(web.describe(), web.cpu)
# web1 has 4 CPUs 4
```

- `__init__` is the setup step, called automatically.
- `self` is how an object refers to its own data.
- A name starting with `_` (like `_items`) is a hint meaning "private, internal use only".

**Inheritance:** a class can build on another and keep everything it has.

```python
class BigServer(Server):               # BigServer gets everything Server has
    def __init__(self, name, cpu, ram):
        super().__init__(name, cpu)    # let Server do its setup first
        self.ram = ram

big = BigServer("db1", 16, 64)
print(big.describe(), big.ram)
# db1 has 16 CPUs 64
```

### 1.10 Unpacking with `**` (used in `store.py`)

`**` spreads a dictionary out into separate named values:

```python
a = {"title": "Disk full", "severity": "high"}

b = {**a, "id": 7}                     # copy a, then add id
print(b)
# {'title': 'Disk full', 'severity': 'high', 'id': 7}

def show(title, severity, id):
    return f"#{id} [{severity}] {title}"

print(show(**a, id=7))                 # same as show(title="Disk full", severity="high", id=7)
# #7 [high] Disk full
```

### 1.11 Errors: try/except and raise

```python
try:
    int("abc")                         # this fails
except ValueError:
    print("not a number")              # so this runs instead of crashing

def get_or_fail(x):
    if x is None:
        raise ValueError("nothing here")   # deliberately cause an error
    return x

try:
    get_or_fail(None)
except ValueError as e:
    print("caught:", e)
# caught: nothing here
```

`raise` means "stop here and signal a problem". `HTTPException` in `main.py` is the web version of this.

### 1.12 The `with` statement

`with` grabs something, lets you use it, and **always cleans up afterwards**, even if an error happens.

```python
with open("notes.txt", "w") as f:
    f.write("hi")
print(f.closed)
# True   (the file was closed automatically)
```

`store.py` uses `with self._lock:` the same way: take the lock, do the work, release the lock.

### 1.13 Imports and files

Each `.py` file is a **module**. `import` pulls in code from elsewhere.

```python
from enum import Enum                  # from Python's built-in library
from app.models import Incident        # from YOUR file app/models.py
```

A folder with an `__init__.py` file is a **package**. Yours is `app/` (the `__init__.py` is empty, and it just tells Python "this folder is importable").

### 1.14 Enums (a fixed list of allowed values)

```python
from enum import Enum

class Color(str, Enum):
    red = "red"
    blue = "blue"

print(Color("red"), Color.red.value, Color.red == "red")
# Color.red red True

Color("green")
# ValueError: 'green' is not a valid Color
```

Your app uses this so severity can only be `low`, `medium`, `high` or `critical`.

### 1.15 Type hints

```python
def add(a: int, b: int) -> int:        # "a and b are ints, and the result is an int"
    return a + b
```

Python does **not** enforce hints (`add("x", "y")` just returns `xy`). They are notes for humans and tools. FastAPI and Pydantic read them and use them to check data automatically, which is why they matter in your app.

- `x: str` means text.
- `x: str | None` means text or nothing.
- `list[int]` means a list of ints.
- `dict[int, Incident]` means a dictionary with int keys and Incident values.

### 1.16 Decorators (the `@` lines in `main.py`)

A decorator wraps a function to change or register it.

```python
def shout(func):
    def wrapper():
        return func().upper()
    return wrapper

@shout                                 # same as: hello = shout(hello)
def hello():
    return "hi"

print(hello())
# HI
```

In `main.py`, `@app.get("/health")` does the same kind of thing. It registers the function below it as the answer to `GET /health`. You don't need to write decorators, only to recognize them.

### 1.17 Pydantic (checks data for you)

Pydantic is a library: describe the shape of your data as a class, and it validates it.

```python
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(min_length=3)
    age: int

p = Person(name="Sam", age="30")       # "30" is converted to the number 30
print(p, p.age, type(p.age))
# name='Sam' age=30 30 <class 'int'>

Person(name="Al", age=5)
# ValidationError: String should have at least 3 characters

print(p.model_dump())                  # turn it back into a plain dictionary
# {'name': 'Sam', 'age': 30}
```

### 1.18 Virtual environments and pip

- **pip** installs Python libraries: `pip install fastapi`.
- **requirements.txt** is a shopping list of libraries the project needs: `pip install -r requirements.txt`.
- A **virtual environment** (`.venv` folder) is a private box of libraries for one project, so projects don't interfere with each other. That's why `.venv/` is in `.gitignore`: it's big and anyone can recreate it.

---

## Part 2: How web APIs work

### 2.1 The restaurant picture

A web API is a program that waits for **requests** and sends back **responses**.

- **Client** (you, a browser, `curl`, another program) is the customer.
- **Server** (your app) is the kitchen.
- The request is the order. The response is the meal.

### 2.2 What a request contains

```
POST /incidents?severity=high  HTTP/1.1
Content-Type: application/json

{"title": "AKS node NotReady", "severity": "high", "symptoms": "Pods Pending"}
```

| Part | Example | Meaning |
|---|---|---|
| **Method** | `POST` | What you want to do |
| **Path** | `/incidents` | Which thing you're talking about |
| **Query** | `?severity=high` | Optional extra filter, after the `?` |
| **Body** | `{"title": ...}` | Data you're sending (only some methods) |

Common methods:

| Method | Meaning | Restaurant version |
|---|---|---|
| `GET` | Read something | "What's on the menu?" |
| `POST` | Create something | "I'd like to place an order" |
| `PUT` / `PATCH` | Change something | "Change my order" |
| `DELETE` | Remove something | "Cancel my order" |

### 2.3 JSON

The text format almost every API uses. It looks just like a Python dictionary or list:

```json
{"id": 1, "title": "Disk full", "fix": null}
```

Small differences: JSON writes `null` where Python writes `None`, and `true`/`false` in lowercase.

### 2.4 What a response contains

A **status code** (a number saying how it went) plus usually a JSON body.

| Code | Meaning | In your app |
|---|---|---|
| `200` | OK | Normal success for GET |
| `201` | Created | After `POST /incidents` |
| `404` | Not found | `GET /incidents/99` when 99 doesn't exist |
| `422` | Invalid data | Title too short, bad severity |
| `500` | Server crashed | A bug in the code |

Rule of thumb: **2xx = success, 4xx = your request was wrong, 5xx = the server is broken.** You'll read these codes constantly in DevOps.

### 2.5 Your app's four endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | "Are you alive?" |
| POST | `/incidents` | Save a new incident |
| GET | `/incidents` | List incidents (optional `?severity=`) |
| GET | `/incidents/{id}` | Fetch one incident by number |

---

## Part 3: Your app, file by file

The project layout:

```
incident-copilot/
├── app/
│   ├── __init__.py     empty; marks 'app' as an importable package
│   ├── models.py       the SHAPE of an incident and the rules for valid data
│   ├── store.py        the MEMORY: where incidents are kept
│   └── main.py         the ROUTES: which URL runs which function
└── requirements.txt    libraries needed
```

Think of three staff members: **models** is the form template, **store** is the filing cabinet, **main** is the receptionist who takes requests and uses the other two.

### 3.1 `models.py`: the shape of an incident

```python
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
```
Imports: `datetime` for timestamps, `Enum` for fixed choices (see 1.14), and `BaseModel`/`Field` from Pydantic for validation (see 1.17).

```python
class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Status(str, Enum):
    open = "open"
    resolved = "resolved"
```
Two fixed lists of allowed values. Anything else, like `"meh"`, is rejected. The `str` in `(str, Enum)` makes the values behave like text, so they convert cleanly to JSON.

```python
class IncidentCreate(BaseModel):
    """What a client sends to POST /incidents."""

    title: str = Field(min_length=3, max_length=120, examples=["AKS node NotReady"])
    severity: Severity
    symptoms: str = Field(min_length=1, examples=["Pods stuck Pending after node drain"])
    root_cause: str | None = None
    fix: str | None = None
```
This is the **form a client must fill in** to report an incident. Line by line:

- `title: str = Field(min_length=3, max_length=120, ...)`: title must be text, 3 to 120 characters. `examples` only appears in the auto-generated docs.
- `severity: Severity`: must be one of the four allowed values. It has no default, so it is **required**.
- `symptoms: str = Field(min_length=1, ...)`: required, at least 1 character (so not empty).
- `root_cause: str | None = None`: text **or nothing**, and the `= None` default makes it **optional**.
- `fix: str | None = None`: same, optional.

The triple-quoted text is a **docstring**, a description for humans.

```python
class Incident(IncidentCreate):
    """What the API returns: the input plus server-generated fields."""

    id: int
    status: Status
    created_at: datetime
```
`Incident(IncidentCreate)` uses **inheritance** (see 1.9): an `Incident` has everything in `IncidentCreate` (title, severity, symptoms, root_cause, fix) **plus** three fields the server adds: `id`, `status`, `created_at`. The client never sends those. The server fills them in. Splitting "what goes in" from "what comes out" is a very common pattern.

### 3.2 `store.py`: the memory

```python
from datetime import datetime, timezone
from threading import Lock

from app.models import Incident, IncidentCreate, Severity, Status
```
Imports. Note `from app.models import ...` pulls your own file's classes in.

```python
class InMemoryIncidentStore:
    def __init__(self) -> None:
        self._items: dict[int, Incident] = {}
        self._next_id = 1
        self._lock = Lock()
```
This runs once when the store is created (see `__init__` in 1.9).

- `self._items` is a dictionary from id to incident, starting empty `{}`. Example after two saves: `{1: <incident>, 2: <incident>}`.
- `self._next_id = 1` is the ID the next incident will get.
- `self._lock = Lock()` prevents two requests from writing at the same instant and mixing things up. Think of a "one at a time" key for the filing cabinet.

```python
    def add(self, data: IncidentCreate) -> Incident:
        with self._lock:
            incident = Incident(
                **data.model_dump(),
                id=self._next_id,
                # An incident with a recorded fix counts as resolved.
                status=Status.resolved if data.fix else Status.open,
                created_at=datetime.now(timezone.utc),
            )
            self._items[incident.id] = incident
            self._next_id += 1
            return incident
```
Saves a new incident. Step by step:

1. `with self._lock:` take the "one at a time" key (see 1.12). It's released automatically at the end.
2. `data.model_dump()` turns the form the client sent into a plain dictionary.
3. `Incident(**data.model_dump(), id=..., status=..., created_at=...)` uses `**` unpacking (see 1.10). It builds the full incident from the client's fields **plus** the three server-generated ones.
4. `Status.resolved if data.fix else Status.open` is the one-line if/else (see 1.6). If a `fix` was given it's resolved, otherwise open.
5. `datetime.now(timezone.utc)` is the current time in UTC (a world-standard time zone, best for servers).
6. `self._items[incident.id] = incident` stores it in the dictionary under its id.
7. `self._next_id += 1` gets ready for the next one (`+= 1` means "add 1 to itself").
8. `return incident` hands the saved incident back.

```python
    def list(self, severity: Severity | None = None) -> list[Incident]:
        items = list(self._items.values())
        if severity is not None:
            items = [i for i in items if i.severity == severity]
        return items
```
Returns all incidents, optionally filtered.

- `self._items.values()` gives all the incidents (not the ids). `list(...)` makes it a list.
- `if severity is not None:` means "if the caller asked for a filter".
- The list comprehension (see 1.8) keeps only the incidents matching that severity.

```python
    def get(self, incident_id: int) -> Incident | None:
        return self._items.get(incident_id)
```
Looks up one incident by id. Because it uses `.get()` (see 1.5), a missing id gives back `None` rather than crashing. The `-> Incident | None` hint says exactly that.

### 3.3 `main.py`: the routes

```python
from fastapi import Depends, FastAPI, HTTPException, status

from app.models import Incident, IncidentCreate, Severity
from app.store import InMemoryIncidentStore
```
Imports: the web framework pieces, plus your own models and store.

```python
app = FastAPI(
    title="Incident Copilot",
    version="0.1.0",
    description="Log and search ops incidents. v0: in-memory storage.",
)
```
Creates the application. `app` is the object that listens for requests. Everything below attaches to it. The title, version and description only appear on the auto-generated `/docs` page.

```python
_store = InMemoryIncidentStore()


def get_store() -> InMemoryIncidentStore:
    return _store
```
Creates **one** store (one filing cabinet) when the app starts, and defines a function that hands it out. There must be exactly one, or each request would get its own empty cabinet and data would vanish.

```python
@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check (used later by Docker HEALTHCHECK and K8s probes)."""
    return {"status": "ok"}
```
The `@app.get("/health")` decorator (see 1.16) means: "when a **GET** request arrives at `/health`, run this function." It returns a dictionary, and FastAPI converts it to JSON automatically. `-> dict[str, str]` is a type hint: a dictionary with text keys and text values.

```python
@app.post("/incidents", response_model=Incident, status_code=status.HTTP_201_CREATED)
def create_incident(
    data: IncidentCreate, store: InMemoryIncidentStore = Depends(get_store)
) -> Incident:
    return store.add(data)
```
- `@app.post("/incidents", ...)`: runs for a **POST** to `/incidents`.
- `response_model=Incident`: the reply will look like a full `Incident` (with id, status, created_at).
- `status_code=status.HTTP_201_CREATED`: reply with code 201 ("created") instead of the default 200.
- `data: IncidentCreate`: FastAPI reads the request body and checks it against `IncidentCreate`. If it fails (short title, bad severity) FastAPI replies **422** and **this function never runs**. If it passes, `data` is a ready-to-use object.
- `store: ... = Depends(get_store)`: "call `get_store()` and give me the result." This is called **dependency injection**. You don't fetch the store yourself, the framework passes it in.
- `return store.add(data)`: the store saves it and returns the complete incident, which goes back to the client.

```python
@app.get("/incidents", response_model=list[Incident])
def list_incidents(
    severity: Severity | None = None,
    store: InMemoryIncidentStore = Depends(get_store),
) -> list[Incident]:
    """List incidents, optionally filtered: /incidents?severity=high"""
    return store.list(severity)
```
`severity: Severity | None = None` is a function parameter that is **not** in the path, so FastAPI treats it as a **query parameter**: `/incidents?severity=high`. It's optional (default `None`) and must be a valid `Severity`, so `?severity=meh` gives a 422 automatically.

```python
@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(
    incident_id: int, store: InMemoryIncidentStore = Depends(get_store)
) -> Incident:
    incident = store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident
```
- `{incident_id}` in the path is a blank to fill in. Visiting `/incidents/2` makes `incident_id` equal to `2`. Because of `: int`, `/incidents/abc` is rejected automatically.
- `store.get(...)` returns the incident or `None`.
- If `None`, `raise HTTPException(404, ...)` (see 1.11) stops the function and sends the standard "not found" reply with a message. The f-string (see 1.3) puts the id in the message.
- Otherwise it returns the incident.

### 3.4 One full trip: creating an incident

You send:

```
POST /incidents
{"title": "AKS node NotReady", "severity": "high", "symptoms": "Pods Pending"}
```

1. `uvicorn` (the server program, see Part 4) receives the request and hands it to FastAPI.
2. FastAPI matches "POST + `/incidents`" to `create_incident`.
3. It validates the body against `IncidentCreate`. Title length OK, `"high"` is valid, symptoms present. `root_cause` and `fix` are missing, which is fine because they're optional (`None`).
4. It calls `get_store()` and passes the store in.
5. `store.add(data)` builds an `Incident`: `id=1`, `status=open` (no fix), `created_at=now`.
6. The incident is stored in `_items` as `{1: ...}` and `_next_id` becomes 2.
7. FastAPI turns the incident into JSON and replies with **201**.

If the title had been `"x"`, the trip would stop at step 3 with a 422 and never reach the store.

### 3.5 The other files

- **`__init__.py`**: empty. Its presence makes `app/` a package so `from app.models import ...` works.
- **`requirements.txt`**: lists `fastapi` (the framework) and `uvicorn` (the server program that actually listens on a network port and passes requests to FastAPI).
- **`.gitignore`**: files git should never upload (secrets, `.venv`, Terraform state).
- **`README.md`**, **`docs/PROJECT_BRIEF.md`**: documentation.

---

## Part 4: Running the app on your computer

Do this in a terminal, inside the project folder.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
If activation is blocked with an "execution policy" error, run this once in that window, then try again:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

What you should see: a message like `Uvicorn running on http://127.0.0.1:8000`. Leave that terminal open (it *is* your running app; press Ctrl+C to stop).

**Decoding `uvicorn app.main:app --reload`:**
- `app.main` means the file `app/main.py`.
- `:app` means the variable named `app` inside it (the `FastAPI(...)` object).
- `--reload` means restart automatically when you edit code (for development only).

**Try it, the easy way:** open http://127.0.0.1:8000/docs in a browser. FastAPI builds an interactive page where you can click an endpoint, press "Try it out", fill in the form and see the real response. This is the best way to *see* everything from Part 3 working.

**Try it, the terminal way** (open a second terminal):
```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/incidents -H "Content-Type: application/json" -d '{"title":"Disk full","severity":"high","symptoms":"No space on /var"}'
curl http://127.0.0.1:8000/incidents
```
On Windows PowerShell, `curl` is an alias for something different. Use `curl.exe` instead, or just use the `/docs` page.

Then **stop the app (Ctrl+C), restart it, and list incidents again.** They're gone. That's the "in-memory" limitation, and it's exactly what Day 4 (persistence) fixes.

---

## Part 5: How each DevOps phase touches this app

Here is the key point about your 100 days: **after the app exists, you mostly don't change its code**. You change how it is packaged, run and shipped. This table shows what you actually need to know about the app at each step.

| Phase | What you'll do | What you need to know about the app |
|---|---|---|
| **P1** (now) | Persistence, tests, git practice | Read/edit a little Python; the store is the part that changes |
| **P2** Docker | Package the app into a container image | How to start it (`uvicorn app.main:app --host 0.0.0.0`), the port (8000), the file list (`requirements.txt`), and that `/health` exists |
| **P2** Compose | Run the app with a real Postgres database | The app will read the database address from an **environment variable** instead of being hardcoded |
| **P3** Kubernetes | Run many copies, restart them, expose them | `/health` becomes the **liveness/readiness probe** target; config and DB password become ConfigMap/Secret |
| **P4** Terraform + Azure | Create the cloud servers/cluster as code | Nothing new about the app; you're building where it runs |
| **P5** CI/CD | GitHub Actions builds, tests, ships automatically | The test command (`pytest`) and the build command |
| **P6** Monitoring | Logs and dashboards | The app will print structured logs and expose request counts |
| **P7** AI | Call an AI service to summarize incidents | The most Python you'll write, in small pieces |
| **P8** MLOps | Train a small model and deploy it | Basic scikit-learn, most of the code is examples you adapt |

So a comfortable working knowledge of Parts 1 to 3 of this guide is enough to get through most of the program. I (or the docs) can supply the code; your job is to understand what it does and why.

---

## Part 6: Practice exercises

Do these in order. Type the code yourself instead of pasting, since typing is where learning happens. Answers are at the end of this part, so try first.

### Level 1: Python basics (use `python` interactive mode)

1. Make a list of three server names of your own. Print the **second** one.
2. Make a dictionary for an incident with keys `title` and `severity`. Print just the severity.
3. Write a function `is_urgent(severity)` that returns `True` if severity is `"high"` or `"critical"`, otherwise `False`.
4. Given `inc = [{"title": "a", "fix": None}, {"title": "b", "fix": "restarted"}]`, use a list comprehension to get only the **titles of incidents that have a fix**.
5. Write a function `count_by_severity(items)` that takes a list of dictionaries like `{"severity": "high"}` and returns counts such as `{"high": 2, "low": 1}`. (Hint: loop, and use `counts.get(key, 0) + 1`.)

### Level 2: Read the app (no coding)

Answer these by looking at the code in Part 3:

1. You POST an incident with the title `"x"`. Does `store.add` ever run? Why?
2. What does `GET /incidents/abc` return, and which piece of the code causes that?
3. After saving three incidents, what does `_next_id` equal?
4. You POST an incident that includes a `fix`. What will its `status` be?
5. Why is `_store` created once at the top of `main.py` rather than inside each function?

### Level 3: Change the app (start it with `--reload` so edits apply instantly)

Use the `/docs` page to confirm each change works.

**A. Add a home page.** Add an endpoint `GET /` that returns `{"message": "Incident Copilot is running"}`. (Copy the shape of `health`.)

**B. Add a field.** Add an optional `reporter` field (the person who reported it) to `IncidentCreate` in `models.py`. Create an incident with a reporter and check it comes back.

**C. Tighten a rule.** Change the maximum title length from 120 to 60. Confirm a 61-character title is rejected with 422 and a 60-character one is accepted.

**D. Stretch: delete an incident.** Add `DELETE /incidents/{id}`. You'll need a new `delete` method in `store.py` and a new route in `main.py`. It should return status **204** (success, nothing to send back) and **404** for a missing id.

### Answers

**Level 1**
```python
servers = ["alpha", "beta", "gamma"]
print(servers[1])                                   # beta

incident = {"title": "Disk full", "severity": "high"}
print(incident["severity"])                         # high

def is_urgent(severity):
    return severity == "high" or severity == "critical"
# is_urgent("high") -> True, is_urgent("low") -> False

inc = [{"title": "a", "fix": None}, {"title": "b", "fix": "restarted"}]
print([i["title"] for i in inc if i["fix"] is not None])    # ['b']

def count_by_severity(items):
    counts = {}
    for i in items:
        s = i["severity"]
        counts[s] = counts.get(s, 0) + 1
    return counts
# count_by_severity([{"severity":"high"},{"severity":"low"},{"severity":"high"}])
# -> {'high': 2, 'low': 1}
```

**Level 2**
1. No. FastAPI validates the body against `IncidentCreate` first. A 1-character title breaks `min_length=3`, so it replies 422 and the function never runs.
2. **422.** The route declares `incident_id: int`, and `"abc"` isn't a whole number, so FastAPI rejects it before your code runs.
3. **4.** It starts at 1 and goes up by one after each save (1, 2, 3 used, so the next is 4).
4. `resolved`, from `Status.resolved if data.fix else Status.open`.
5. If each request made its own store, every request would see an empty filing cabinet, so saved incidents would vanish immediately. Creating one shared store keeps the data between requests.

**Level 3** (all four were tested on a copy of the app)

A. In `main.py`, above the `/health` route:
```python
@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Incident Copilot is running"}
```

B. In `models.py`, inside `IncidentCreate`, after the `fix` line:
```python
    reporter: str | None = None
```
`Incident` inherits it automatically, so it appears in responses too.

C. In `models.py`, change `max_length=120` to `max_length=60`.

D. In `store.py`, add inside the class:
```python
    def delete(self, incident_id: int) -> bool:
        with self._lock:
            return self._items.pop(incident_id, None) is not None
```
In `main.py`, at the bottom:
```python
@app.delete("/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: int, store: InMemoryIncidentStore = Depends(get_store)
) -> None:
    if not store.delete(incident_id):
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
```
`.pop(key, None)` removes the key and returns its value, or `None` if it wasn't there. So `is not None` tells us whether something was actually deleted.

---

## Part 7: Glossary

| Term | Plain meaning |
|---|---|
| **API** | A program other programs talk to, using requests and responses |
| **REST** | A common style of API built around URLs and the methods GET/POST/PUT/DELETE |
| **Endpoint / route** | One URL + method combination, like `GET /health` |
| **JSON** | Text format for data; looks like a Python dictionary |
| **Status code** | A number saying how a request went (200 OK, 404 not found, 422 bad data) |
| **Framework** | A library that does the common work for you (FastAPI does the web plumbing) |
| **FastAPI** | The Python web framework used here |
| **Uvicorn** | The server program that listens on a port and runs your FastAPI app |
| **Pydantic** | The library that validates data against a class definition |
| **Validation** | Checking data is acceptable before using it |
| **Module / package** | A `.py` file / a folder of them with `__init__.py` |
| **Virtual environment** | A private set of installed libraries for one project (`.venv`) |
| **pip** | Python's tool for installing libraries |
| **In-memory** | Stored in the running program's RAM, so lost when the program stops |
| **Persistence** | Data that survives restarts (a file or database) |
| **Decorator** | An `@something` line that registers or modifies the function below it |
| **Dependency injection** | The framework passes needed objects into your function (`Depends`) |
| **Docstring** | The triple-quoted description at the top of a function or class |
| **Commit / push** | Saving a snapshot in git / uploading your snapshots to GitHub |

---

*Suggested pace: Parts 0 to 2 in one sitting, Part 3 in a second, then run the app (Part 4) and do Level 1 and 2 exercises. Level 3 can wait until you've run it. If any section doesn't click, note the section number and ask about that specific part.*
