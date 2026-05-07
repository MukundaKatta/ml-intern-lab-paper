# ML Intern Lab Paper Package

Submission-ready research package for the paper:

**ML Intern Lab: A Minimal Agentic Workflow for Reproducible Machine Learning Experiment Reports**

## Contents

- `paper.md`: manuscript source.
- `abstract.txt`: plain-text abstract for submission forms.
- `keywords.txt`: suggested keywords.
- `paper.bib`: compact BibTeX references.
- `submission-metadata.json`: platform metadata.
- `render_preprint_pdf.py`: local PDF renderer.
- `ml-intern-lab-agentic-ml-reporting-preprint.pdf`: generated manuscript PDF.
- `ml-intern-lab-paper-package.zip`: upload bundle.

## Artifact Basis

This paper is grounded in the local `ml-intern-lab` package, including:

- zero-dependency Python runner
- paper-note, experiment-plan, and model-report templates
- majority-class baseline experiment
- generated `metrics.json`
- generated `model-report.md`

Local verification on 2026-05-06:

```bash
PYTHONPATH=src python3 -m pytest -q
```

Result:

```text
1 passed in 0.01s
```

