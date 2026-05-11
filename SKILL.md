---
name: blueprint-npu-design
description: Use this skill to generate well-branded interfaces and assets for Blueprint NPU, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the README.md file within this skill, and explore the other available files (`colors_and_type.css`, `assets/`, `preview/`, `ui_kits/blueprint_artifact/`, `ui_kits/gradio_workbench/`).

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view — always include `colors_and_type.css` on every surface.

If working on production code, copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts *or* production code, depending on the need.

Core rule of thumb: **line art on navy, white + one pastel accent per element, monospace numbers with units, no emoji, no gradients, no shadows.** When in doubt, pull components from `ui_kits/blueprint_artifact/Components.jsx` (Frame, Stage, Tank, EngineRow, Legend, DimLadder, PartTreeBlock, LaneChip, Button) rather than hand-rolling new ones.
