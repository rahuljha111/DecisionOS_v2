# Identity module

The Identity module owns account identity and access-control concerns: the user
record, credentials, authentication tokens, and authorization rules. It does
not own profile information or any decision data.

Dependencies flow inward from the HTTP boundary:

```text
router -> dependencies / service -> repository -> database
                         |
                         +-> schemas / security
```

- `models.py` defines persistence mappings only.
- `repository.py` will contain user-specific database queries only.
- `service.py` will own registration and authentication workflows.
- `security.py` will own password hashing and JWT primitives.
- `schemas.py` will define request and response contracts.

The initial `User` model deliberately stores `role` and `auth_provider` as
strings. The module enums introduced later in the sprint will define the
allowed application values, while retaining database compatibility and keeping
the model independent of HTTP/API concerns.
