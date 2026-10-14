# Engineering Notes

## 10/13/2026

Project Setup & Package Management

- "uv init --bare": Initialized a minimal Python project using 'uv', a Rust-backed package manager. The --bare flag creates only a pyproject.toml file, omitting sample code and boilerplate.

Data Validation & Flow (Pydantic Models)

- Inbound Validation (Client data coming into server): Enforces data contracts (models) on client payloads (e.g. endpoint param type: new_service: ServiceClientCreate). This catches validation errors. E.g. client sends { "random_property": "random" } while the model doesn't have that property. Client will get a validation error.

- Outbound Validation (Server data going to client): Formats data leaving the server (e.g. return type: -> Service). It handles data masking (stripping out sensitive internal database fields) and automated serialized. Serialization is the process of flattening live, complex memory structures (like datetime objects) into transportable plain text strings (like JSON payloads).

Dictionary Unpack Operator

Calling model_dump() extracts a model's data into a raw Python dictionary. The `**` operator acts as a formatting bridge to pour that dictionary into its next destination. In almost every case, you will need to use the `**` when using model_dump(). E.g. we need to dump the client's data into a Service object. Service object holds key=value pairs and model_dump() returns a dict so we have a format mismatch. We grab the client's data using model_dump() and format it into key=value pairs using `**`. It can also format into a dict inside another dict. E.g. We need to update an exisiting entry with properties the client sent (e.g. PATCH request). We use model_copy() to copy the exisiting entry and use model_dump(exclude_unset=True) inside model_copy(update=) to overwrite only the the properties the client sent and `**` to format it into the exisiting entry.

Data Mutation

- enumerate(): Used over basic for-in loops when traversing in-memory lists to gain access to the item's index, making it possible to safely target and replace entries inline.

## 10/08/2026

- Initialized the repository and established the Git branching/PR workflow.
- Learned how GitHub PR diffs are reviewed before merging.
