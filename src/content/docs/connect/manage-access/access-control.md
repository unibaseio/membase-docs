---
title: "Access control"
description: "What a connected client may do, decided by its credential and by the switches on Connect: reach, level, the profile tick, confirmation, and revocation."
---

What a connected client may do, decided by its credential and by the switches on Connect: reach, level, the profile tick, confirmation, and revocation.

A connected AI can do exactly what its credential allows, and the credential is the
person's: they minted it or approved it, and they change it on the **Connect** page without
touching the client. Every rule below is enforced on the server, on the credential's next
call; nothing here depends on the client behaving.

## Two credentials, two ceilings

| | Consent (an app connected over MCP) | Developer key (the skill, a header, code) |
|---|---|---|
| Ceiling | read-only, always | the key's level: Read, Read & write, Full access |
| Reach | the Memories ticked on consent, switchable later | the Memories ticked on the key, or all including later ones |
| Profile | when **Profile access** was ticked on the consent screen | when **Your profile** was ticked |
| Confirmation | is not offered a delete or forget at all | can, with `confirm=true` at Full access |
| Ends | **Disconnect…** on the app's page, or per credential under **Approvals** | **Revoke…**, or expiry |

An app that needs to write does not get a wider consent; the person mints a key for it
instead, and the key says how wide.

## Reach

Reach is the list of Memories a credential may use. It has one state and three views of it:
the **Uses** card on the client's page in Connect, the **Use in** card on the Memory's page,
and the **Memory access** switches on a key's page. Off takes effect on the very next call.

![One grant seen from three places, Uses, Use in and Memory access; on means in reach, off means 403 and not listed on the next call](/images/figures/reach-one-switch.svg)

A Memory outside the reach is refused the same way as one that does not exist: `403`,
*may not use that container*. `list_containers` does not list it. A client cannot tell
withheld from absent, and cannot ask for more; only the person can switch it on.

## The tool list is the grant

`tools/list` is filtered per caller. A consent-minted client is offered `list_containers`,
`search_memories` and, when ticked, `get_profile`, and nothing that writes; a key is offered
the tools of its level. A model cannot call what it was not offered, and a call that
bypasses the list is refused with `403` anyway. The full table per level is on
[Authentication & Scopes](/build/reference/authentication/#access-levels).

## Destructive verbs

`delete_document` and `forget_memory` exist only at Full access, and even there they do not
execute on a bare call: without `confirm=true` the answer is `status: confirmation_required`
with a `how` sentence for the model to relay. A consent-minted client is never offered
these verbs, and a call is refused with `403` (*not in this agent's capability profile*)
rather than answered with the sentence. From a Full access key, `confirm=true` counts as
the owner's confirmation, which is why the skill tells the AI to pass it only after the
person agreed.

Deleting a Memory, a source's material or the account has no agent-protocol verb at all;
those belong to the owner's session, in the app.

## The profile

The profile is about the person, not a topic, so it is granted separately from reach. A
client offered `get_profile` reads the standing facts and what changed recently; one that
was not ticked is not offered the tool. On a key the tick is **Your profile**, changeable
later on the key's page. On a consent connection it is **Profile access**, set only on the
consent screen: to change it, **Disconnect…** the app and authorize it again.

## Revocation

* **Disconnect…** on a client's page revokes every credential that client holds, at once.
* **Revoke** under **Approvals** ends one credential when a client holds several.
* **Revoke…** on a key ends it at once; it stays listed for thirty days.
* Removing the connector inside the client does not tell Membase. Revoke on Connect to be sure.

Revocation and permission changes apply to subsequent requests. They do not remove content
an external client has already received. A revoked key must be replaced with a new key;
reconnecting an app requires a new authorization.

## Seeing what a client did

A client's page on Connect shows its last activity. A key's page shows **Usage** (calls,
refusals, the tool it calls most) and **Recent activity** (each call: tool, Memory, what came
back, when; a refused call in red with the reason; a refused `ask_agent` is the one call
not recorded). A refusal is the sign that a client asked
for a Memory or a verb it does not have, which is usually the person's cue to widen it or to
leave it.

## Rules the skill teaches the model

Because the server enforces the ceiling, the skill's rules are about behaving well beneath
it: read the profile first when it is granted; search before answering about the person's
past work; cite the container a result came from; save only what the person supplied; never
pass `confirm` on the model's own initiative; treat `403` as withdrawn access and ask the
person rather than retry.
