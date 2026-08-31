# CLI

The initial command-line client exposes the community provider catalog:

```bash
openforge providers list
openforge providers inspect moneyprinter-turbo
openforge jobs create --provider moneyprinter-turbo --brief "A product video"
openforge jobs status --provider moneyprinter-turbo --job-id TASK_ID
openforge jobs result --provider moneyprinter-turbo --job-id TASK_ID
```

MoneyPrinterTurbo is the first runnable job integration. Its service remains a
separate installation, and its optional API key is read from the
`MONEYPRINTER_TURBO_API_KEY` environment variable rather than a command-line
argument.
