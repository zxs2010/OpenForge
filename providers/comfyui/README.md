# ComfyUI Provider Candidate

[ComfyUI](https://github.com/Comfy-Org/ComfyUI) is a candidate local and hosted
workflow execution provider. Its graph API can validate OpenForge's ability to
route production work to local GPUs without coupling the core protocol to a
specific model.

The first adapter will submit a pinned workflow, map queue and execution events
to OpenForge job states, and return generated artifacts with workflow
provenance.
