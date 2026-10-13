# Engineering Decisions

Decisions made during Week 01-02 will be documented here.

## Use In-Memory List for Initial MVP Data Store

- **Status:** Accepted
- **Context:** We needed a fast way to bootstrap the core API endpoints and validate Pydantic schemas without getting bogged down configuring a database driver, connection strings, or migrations right out of the gate.
- **Decision:** Store services in a global Python `list` in memory for the initial MVP release.
- **Consequences:**
  - Data will not persist when the FastAPI server restarts (which is fine for early prototyping).
  - The CRUD logic is isolated enough that replacing the list with a real database (like SQLite or PostgreSQL via an ORM) in a future ticket will be straightforward.
