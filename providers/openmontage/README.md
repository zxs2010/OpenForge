# OpenMontage Provider Candidate

[OpenMontage](https://github.com/calesthio/OpenMontage) supplies agent-driven
video pipelines, production tools, review gates, checkpoints, and cost logs.

The planned adapter will run OpenMontage independently and translate its project
checkpoints into OpenForge job states. It will not copy AGPL-3.0 source into the
Apache-2.0 OpenForge core.

Planned mappings:

| OpenForge | OpenMontage |
| --- | --- |
| `create_job` | Initialize a pinned pipeline project and start a runner agent |
| `get_status` | Read the latest validated checkpoint |
| `get_result` | Return final render, review artifact, and cost log |
| `cancel_job` | Stop the runner and prevent subsequent stages |

This candidate is intentionally pinned to an immutable commit because the
upstream repository does not currently publish versioned releases.
