# Recovery and handoffs

Keep useful work when a connection drops, a session fails, or a harness reaches its quota. The right action depends on whether you want to resume the same workspace or start a new task from it.

## Reconnect after a restart

Agent sessions run through a relay inside each task container. Closing the browser, restarting caic, or losing SSH does not stop the agent. Reopen the dashboard after the server returns. Live task restoration happens in the background, followed by recent settled history.

Host sleep pauses local containers. Sessions can resume after the machine wakes, as long as the runtime and container remain available.

## Revive a retained task

A **Stopped** task retains its container filesystem. A **Crashed** task may also retain a recoverable runtime. Use **Revive** to reconnect or restart the agent in that workspace. Before revival, caic recreates a mapped host branch that was deleted and configures an existing branch that lost its upstream to track the repository's default remote branch again. Existing branch commits are preserved. If revival fails, read the displayed error and retry after fixing its cause.

Do not purge the task while you are diagnosing a failure. A task whose container has been destroyed cannot recover files from that container.

## Fork with a handoff

Fork when you want a new task with the current workspace as its starting point. You can fork a running, stopped, or crashed task. Review and edit the handoff prompt, choose a harness and model, and add repositories if needed.

The new task has its own branches and container. Use the handoff to describe the goal, completed work, remaining work, and constraints the next agent needs.

## Continue after a quota limit

A quota warning can offer a path to continue with another harness. Review the suggested harness and model, edit the handoff, and start the new task. A suggestion depends on the quota information available to caic; unknown provider capacity is not a promise that a task can run.

You can also wait for the provider's limit to reset and continue the existing task. Check the task state and latest error before resending a message.

## Stop or purge

**Stop** shuts down the task container while preserving its workspace for revival. **Purge** deletes the container and leaves archived task history.

Purging an active or crashed task first stops it and offers a recovery window. The default is 15 seconds; **Settings** permits 10 seconds to 24 hours. Revive during that window to cancel deletion. Purging an already stopped task deletes it immediately.

Save generated files and push the changes you need before purging. Archived history does not replace the deleted container filesystem.

## Recover super administration

If you lose access to the super administrator account, set [`super_admin`](./configuration#server) to another account and restart caic. Sign in with that account, then use `account_set_enabled` to re-enable the old account if needed. caic refuses to start when the newly selected account was already disabled. Select a different account in that case.

## Diagnose a failed task

Read the task's error first. It can distinguish setup failure, missing harness credentials, a failed agent session, out-of-memory termination, or runtime loss. Use the task's [Performance view](./tasks#inspect-usage-and-resources) and the process view when memory or CPU pressure is involved. Check [Configuration](./configuration) for runtime limits, caches, and model refresh controls.

For a recurring problem, include the error and `caic -version` when [reporting an issue](https://github.com/caic-xyz/caic/issues). Remove credentials from any logs you share.
