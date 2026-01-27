Task Manager API

Simple REST API for managing tasks.

Tech stack:
-Python
-FastAPI
-SQLModel
-SQLite

Features:
-Adding a task
-Removing a task
-Updating a task
-List of tasks
-Separation between database models and API schemas 
-Input validation using separate requests and response schemas
-Optional /tasks filtering by completion status

Design decisions:
-Database models are separate from API schemas to ensure clean API contracts and input validation
-Filtering implemented using query parameters 

How to run:
1.Create virutal environment
2.Install requirements
3.Run uvicorn
4.Open /docs

Notes:
-Database is created on first startup.

