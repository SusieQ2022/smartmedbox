# Individual Contributions

> The project is graded **individually**. Every member contributed to all four
> aspects (Hardware, Code, Report, Presentation); the table below records each
> member's **primary** work package. Update names and refine details as the
> project progresses — and let the Git commit history reflect each person's
> contributions (everyone should commit their own work under their own account).

## Work package ownership

| Member | Hardware | Code | Report | Presentation |
|--------|----------|------|--------|--------------|
| **[Name 1]** | Lead: sensor wiring & assembly | `sensors.py` | Hardware section | Demo operation |
| **[Name 2]** | Support | Lead: `llm_engine.py`, prompt engineering | Reasoning / AI section | AI explanation |
| **[Name 3]** | Camera mounting | Lead: `camera.py`, vision confirmation | Innovation section | Live demo lead |
| **[Name 4]** | Speaker / audio | Lead: `voice.py`, `notifier.py` | Act / notification section | Q&A |
| **[Name 5]** | Enclosure | `config.py`, integration & tests | Lead: report & business model | Presentation lead |

## How to read the Git history

Each commit is authored by the member who did the work. To see an individual's
contributions:

```bash
git log --author="Name 1" --oneline
git shortlog -sne          # summary of commits per author
```

## Notes

- Replace every `[Name X]` placeholder with the actual member name.
- Keep this file updated as responsibilities shift.
- The grading explicitly checks "who did what" — accurate authorship in commits
  plus this document together provide that evidence.
