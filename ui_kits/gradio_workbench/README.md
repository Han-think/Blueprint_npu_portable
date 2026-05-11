# UI Kit — Gradio Workbench

High‑fidelity HTML/JSX recreation of the **Blueprint NPU Batch Runner v5** — the `ai/ui/blueprint_batch_ui.py` Gradio surface. Not a real Gradio binding; it's a visual mock with interactive switches so downstream designs can riff on the workbench without running the Python stack.

Covers:
- Title strip + meta
- Prompts textarea + run‑count slider
- NPU / XPU accordions with model dir, device, dtype, tokens
- Wrapper / blueprint toggles
- Session save options
- Run buttons (NPU only, XPU only, Both) — Gradio's default variants
- Output stream (Markdown rendering of NPU + XPU responses)
- Artifacts tab (Blueprint / Print‑Pack export)

Caveat: Gradio's visual chrome is utilitarian and light‑themed by default. This kit reskins it to the Blueprint NPU dark identity — this is the *recommended* look when we redesign the workbench, not a pixel copy of what ships today.
