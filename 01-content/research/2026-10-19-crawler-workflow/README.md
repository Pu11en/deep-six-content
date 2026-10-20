# Crawler workflow check

**Authenticated crawler access works. The repeatable research procedure is documented; the writing runner’s automatic connection is still pending.**

Checked October 19 with client `imac-research`, using its existing MacBook login from `/Users/drewp/ultimate-crawler-agent/config/clients.json`. Token stayed in memory. Connected through SSH to `drewp@100.80.131.62`, forwarding MacBook localhost:8766. No legacy 8600 request.

Only two reads ran: authenticated capabilities and the API schema. No research job, model call, paid request, new content batch or installation.

- [Access record](access-check.json)
- [Current capabilities](capabilities.json): public search/read and evidence tools; browser/cookies/model calls/paid fallback disabled for this client.
- [Planning and agent API contract](api-contract.json)
- [Checks](verification.json): documented endpoints and limits match the live contract; links resolve; approved audio and choices remain preserved.
- [Repeatable stage instructions](../../mp3-system/crawler-flow.md)
- [Top-to-bottom ASCII whiteboard](../../mp3-system/whiteboard.md)

Progress: identified research at source discovery, supporting science and depth retries; separate hook-library maintenance and optional voice troubleshooting. Current search availability remains best effort and was not re-tested here. Social/video capabilities are not established by this endpoint. Existing episode selections and the approved MP3 were preserved.
