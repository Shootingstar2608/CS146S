# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Phuc, Quan, Huy, Tan** \
Citations: **None**

This assignment took me about **1** hours to do. 


## Brief findings overview 
> The Semgrep `auto` config scan initially identified 5 security vulnerabilities within the backend code. These issues spanned a variety of categories including Cross-Origin Resource Sharing (CORS) misconfigurations (`wildcard-cors`), SQL Injection (`avoid-sqlalchemy-text`), Code Injection (`eval-detected`), Command Injection (`subprocess-shell-true`), and Server-Side Request Forgery / arbitrary file read (`dynamic-urllib-use-detected`). All identified issues were true positives highlighting typical vulnerabilities found in Python web applications. No findings were ignored as false positives, although we chose 3 critical ones to remediate.

## Fix #1
a. File and line(s)
> `backend/app/main.py`, line 24

b. Rule/category Semgrep flagged
> `python.fastapi.security.wildcard-cors.wildcard-cors`

c. Brief risk description
> The CORS middleware was configured to allow any origin (`allow_origins=["*"]`). This is insecure as it permits malicious or unauthorized domains to interact with the API on behalf of users, potentially leading to unauthorized data access.

d. Your change (short code diff or explanation, AI coding tool usage)
> Modified the `allow_origins` array to only include trusted localhost domains instead of the wildcard `*`.
> ```diff
> -    allow_origins=["*"],
> +    allow_origins=[
> +        "http://localhost:3000",
> +        "http://localhost:8000",
> +        "http://127.0.0.1:8000",
> +        "http://127.0.0.1:3000",
> +    ],
> ```

e. Why this mitigates the issue
> By explicitly specifying the allowed origins, the browser will enforce the Same-Origin Policy and block cross-origin requests from untrusted websites, thereby preventing Cross-Origin attacks.

## Fix #2
a. File and line(s)
> `backend/app/routers/notes.py`, lines 71-79

b. Rule/category Semgrep flagged
> `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text`

c. Brief risk description
> An f-string was used to construct an SQL query (`WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'`), which allows a malicious user to inject arbitrary SQL statements by crafting a specific `q` payload.

d. Your change (short code diff or explanation, AI coding tool usage)
> Replaced the f-string interpolation with parameterized variables `:q` in the query, and passed the values as a dictionary to `db.execute()`.
> ```diff
> -        WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
> +        WHERE title LIKE :q OR content LIKE :q
> ...
> -    rows = db.execute(sql).all()
> +    rows = db.execute(sql, {"q": f"%{q}%"}).all()
> ```

e. Why this mitigates the issue
> Parameterized queries ensure that the database engine treats the input as literal values (data) rather than executable code, entirely preventing SQL Injection vulnerabilities regardless of what the user inputs.

## Fix #3
a. File and line(s)
> `backend/app/routers/notes.py`, lines 108-113

b. Rule/category Semgrep flagged
> `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true`

c. Brief risk description
> Calling `subprocess.run(cmd, shell=True)` with a user-controlled string allows an attacker to execute arbitrary shell commands by appending shell metacharacters like `;` or `&&` to their input.

d. Your change (short code diff or explanation, AI coding tool usage)
> Set `shell=False` and safely tokenized the string command into an array of arguments using Python's built-in `shlex` library.
> ```diff
> -    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
> +    import shlex
> +    args = shlex.split(cmd)
> +    completed = subprocess.run(args, shell=False, capture_output=True, text=True)
> ```

e. Why this mitigates the issue
> Setting `shell=False` bypasses the system's shell interpreter, meaning special shell characters like `&&` or `|` lose their special meaning. `shlex.split` safely breaks down the user input into command arguments that are passed directly to the `exec()` system call.