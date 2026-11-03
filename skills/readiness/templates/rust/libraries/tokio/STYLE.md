### tokio and tokio-util

1. **Use tokio when the program waits on many sockets, files, timers or child processes at once.** A CLI that does one thing at a time needs no runtime: std's blocking I/O is simpler. Each crate enables only the features it uses (`rt-multi-thread`, `macros`, `net`, `fs`, `io-util`, `time`, `sync`, `signal`, `process`).
2. **Shut down with tokio-util:** a `CancellationToken` that every long task listens to, and a `TaskTracker` to wait for them all. `TaskTracker` only waits until every task has exited; when the caller needs each task's result as it finishes, or must stop the rest on the first error or panic, use `tokio::task::JoinSet`, whose `join_next` returns tasks in finishing order and whose drop aborts the tasks still running.

   ```rust
   let token = CancellationToken::new();
   let tracker = TaskTracker::new();
   let worker = tracker.spawn(run_worker(queue, token.child_token()));
   tokio::signal::ctrl_c().await?;
   token.cancel();
   tracker.close();
   tracker.wait().await;
   worker.await??;
   ```

3. **Connect stages that run at different rates with a bounded channel,** so a slow consumer slows the producer instead of growing memory. Each stage owns its state and listens for cancellation. Make each `select!` branch a cancel-safe future (`recv` is); the arm body runs to completion, so the work goes there, not in a branch. `send().await` waits when the channel is full; `try_send` lets the producer drop and count. Await each stage's handle and handle its `Result`: a dropped handle drops the error.

   ```rust
   async fn write_batches(mut batches: mpsc::Receiver<Batch>, store: Store, token: CancellationToken) -> Result<(), WriteError> {
       loop {
           tokio::select! {
               () = token.cancelled() => return Ok(()),
               received = batches.recv() => {
                   let Some(batch) = received else { return Ok(()) };
                   store.write(&batch).await?;
               }
           }
       }
   }
   ```
