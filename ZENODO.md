# Zenodo deposit

## Metadata: `.zenodo.json` is authoritative

For categorization and deposit metadata, **edit `.zenodo.json` only**.

| File | Role |
|------|------|
| **`.zenodo.json`** | **Primary.** Resource type, LOC `subjects`, keywords, creators, license, GitHub link, version. Used by Zenodo upload autofill and GitHub–Zenodo release sync. |
| `CITATION.cff` | **Secondary.** Minimal file so GitHub can show “Cite this repository.” Zenodo **ignores** it when `.zenodo.json` is present. |

Why prefer `.zenodo.json` over `CITATION.cff` for this project:

- **`subjects`** — controlled vocabulary with persistent IDs (LOC URIs), not just free-text tags
- **`publication_type`** — explicit `report` vs generic “software” or “other”
- **`related_identifiers`** — structured link back to GitHub
- **`access_right`**, **`language`**, **`communities`** — Zenodo-native fields CFF does not model well

When both files exist in the repo root, [Zenodo’s GitHub integration uses only `.zenodo.json`](https://help.zenodo.org/docs/github/describe-software/zenodo-json/).

## GitHub vs Zenodo

**GitHub** — canonical source (`arxiv.md`, figures, build scripts). Repository licensed **Apache-2.0**.

**Zenodo** — citable **DOI** for `zenodo.pdf`. Publication licensed **CC-BY-4.0**. No full-repo upload required.

## Build outputs

| File | Purpose |
|------|---------|
| `zenodo.tex` / `zenodo.pdf` | Deposit PDF (no arXiv categories) |
| `.zenodo.json` | **Edit this for categorization** |
| `arxiv.tex` / `arxiv.pdf` | Optional arXiv path |

```bash
./scripts/rebuild_zenodo.sh      # zenodo.pdf + dist/zenodo_submit.zip
./scripts/rebuild_arxiv.sh       # separate arXiv build
```

## Current `.zenodo.json` categorization

| Field | Value |
|-------|--------|
| Resource type | Publication → **Report** |
| Access | Open |
| Language | English |
| License | **CC-BY-4.0** (publication); GitHub repo remains Apache-2.0 |
| Keywords | tokamak, fusion safety, component failure, runaway electrons, … |
| Subjects (LOC) | Nuclear fusion · Tokamaks · Fusion reactors · Plasma (Ionized gases) · Nuclear engineering |
| Related ID | GitHub repo (`isSupplementedBy`) |
| Version | 1.0.0 |

PDF title page mirrors this: **Resource type: Technical report** (no arXiv subject classes).

## Upload

1. `./scripts/package_zenodo.sh`
2. [zenodo.org/deposit/new](https://zenodo.org/deposit/new)
3. Upload `dist/zenodo_submit.zip` (`zenodo.pdf` + `.zenodo.json`)
4. Confirm metadata, publish, add DOI to `preferred-citation` in `CITATION.cff` if you want GitHub to show it

## Citation (after upload)

```text
Ericson, L. W. (2026). Fusion Reactor Component Failures: A Review of Historical
Non-Thermonuclear Energetic Excursions (Version 1.0.0) [Report]. Zenodo.
https://doi.org/10.5281/zenodo.XXXXXXX
```

Source: https://github.com/catskillsresearch/fusion_reactor_component_failures
