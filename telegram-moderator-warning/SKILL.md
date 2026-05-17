<!-- ui:visible=true -->
<!-- ui:label=Telegram Moderator Warning -->
<!-- ui:icon=alert-triangle -->

# Telegram Member Warning Skill

This skill manages a warning system for members in Telegram groups to discourage rude or uncooperative behavior.

## When to use
Use this skill when a member's behavior is identified as rude, resistant, or uncooperative. It should be triggered during message processing in a group.

## Execution Logic
The agent should follow these steps:

1. **Identify Infraction**:
   - Analyze the message from the user. If the tone is rude, resistant, or uncooperative, proceed to warn.
2. **Load Warning State**:
   - Read the current warning count for the specific `user_id` and `chat_id` from `memory/member-warnings.json`.
   - Format: `{ "chat_id": { "user_id": warning_count } }`
3. **Increment Warning**:
   - Increase the warning count by 1.
   - Update `memory/member-warnings.json`.
4. **Determine Action**:
   - **If count < 3**:
     - Send a stern warning message in the group, explicitly mentioning the warning number (e.g., "Warning 1/3").
     - Use the "Anh Cốt" persona: tough, direct, and intimidating.
   - **If count >= 3**:
     - Execute `restrictChatMember` via Telegram API to mute the user for 5 minutes.
     - Send an announcement in the group that the user has been muted due to reaching the warning limit.
     - Reset the warning count for this user to 0 in `memory/member-warnings.json`.


