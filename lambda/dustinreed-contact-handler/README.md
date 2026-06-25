# dustinreed-contact-handler

AWS Lambda contact form handler for [dustinreed.info](https://dustinreed.info).

- Accepts `POST` JSON: `{ name, email, subject, message }`
- Sends email via SES to `dustin@dustinreed.info`
- Sets `Reply-To` to the submitter's email

Environment variables (set on the Lambda):

| Variable | Default |
| --- | --- |
| `SENDER_EMAIL` | `noreply@dustinreed.info` |
| `RECIPIENT_EMAIL` | `dustin@dustinreed.info` |
| `SITE_NAME` | `Dustin Reed Website` |

See [DEPLOYMENT.md](../../DEPLOYMENT.md) for Function URL setup and redeploy commands.
