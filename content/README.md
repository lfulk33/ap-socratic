Content lives here as one JSON file per subject: `content/<subject_id>/units.json`.

## Sourcing content legally

College Board does not offer scraping-friendly access, and their site terms
restrict automated collection. Populate these files by hand from material
they publish publicly as downloadable documents, e.g.:

- The Course and Exam Description (CED) for each AP subject — includes the
  full curriculum framework, skills categories, and sample questions.
- Released free-response questions (FRQs) from past exams.
- Scoring guidelines / rubrics for released FRQs.

Do not paste large verbatim excerpts of copyrighted exam content (full FRQ
prompts, passages, scoring notes) into these files or into prompts sent to
the API beyond what's reasonable for study/commentary use. Prefer
summarizing the skill/topic being tested and writing your own practice
questions modeled on the released format.

## Schema

```json
{
  "subject": "AP English Literature and Composition",
  "units": [
    {
      "id": "poetry-diction-imagery",
      "title": "Poetry: Diction, Imagery, and Tone",
      "essential_questions": [
        "How does word choice shape a reader's emotional response to a poem?",
        "How do image patterns build toward a poem's larger meaning?"
      ],
      "focus_skills": [
        "Identify and explain the function of diction and imagery",
        "Connect figurative language to tone and theme"
      ],
      "texts": [
        "Student-selected or teacher-assigned poems for this unit"
      ]
    }
  ]
}
```

Add a `units.json` per subject directory (e.g. `content/ap_lit/units.json`,
later `content/ap_bio/units.json`) following this shape.
