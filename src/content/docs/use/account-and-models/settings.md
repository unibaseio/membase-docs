---
title: "Settings"
description: "Manage your account, plan, payments, exports and account-data deletion."
---

Manage your account, plan, payments, exports and account-data deletion.

Manage your account, plan, transactions and data.

![Settings](/images/shots/settings-page.png)

## Account

View or edit your display name, check your sign-in identity, and copy your account identifier
when contacting support. **Sign out** ends your current session.

## Plan & usage

Review your storage usage, quota and free chat turns. Select **Change plan** to view available
plans and their terms. Check the confirmation before making a payment or changing your plan.

- An upgrade applies after payment succeeds.
- A scheduled downgrade keeps the current plan until the date shown. **Keep current plan**
  cancels that scheduled change.
- **Cancel subscription** keeps the paid plan through its current period. The page shows the
  period end and any pending change.
- If usage exceeds the new storage quota, additional writes may be blocked. Files are not
  automatically compressed to fit. Export data you want to keep before removing files.

## Transactions

Review payments sent and received, including plan payments and marketplace purchases. Where
available, open the linked block explorer to inspect an on-chain settlement.

## Data & export

Select **Download** beside **Export account data** to download a ZIP archive of available
account data and agent memory files.

Check the result message. If it says **Export downloaded without agent memory files**, the
archive is incomplete: wait briefly and export again to include those files. Check the
archive contains the data you need before using it as a backup.

If export is unavailable or fails, resolve the error before deleting data you want to retain.

## Delete everything

**Delete everything** under **Delete account data** opens a two-step confirmation. It removes
your agent and memory, files including Trash, sources and their credentials, and connected
apps and their access. The dialog also identifies affected marketplace subscribers.
Your sign-in identity is retained.

1. Review the consequences and select **Download** to save an export. An export missing agent
   memory files is not marked as a completed backup in this flow. Export again to include them,
   or explicitly choose **Continue without downloading** if you do not need a backup.
2. Continue to the final confirmation, type `delete everything`, then select **Delete everything**.

> Account-data deletion cannot be undone. Keep and verify any export you need before confirming.
