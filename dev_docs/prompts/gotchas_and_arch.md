# Common Gotchas & Architecture Notes (prompt reference)

- Threading & memory
  - Use `piw.tsd_lock()` for thread safety.
  - C++ objects often use `pic::tracked_t` for ownership tracking.

- Builds
  - Treat compiler warnings as errors — fix immediately.
  - Do not mix ARM/x86_64 plugins on macOS.

- VST/JUCE
  - Project uses external VST3 SDK; JUCE embedded SDK removed.
  - VST utility objects built in `tmp/obj/vst3sdk/`.

- Agent pattern
  - See `pi/agent.py` for structure; follow Agent pattern when adding plugins.

Keep entries short and actionable. Move long explanations to `dev_docs/dev_notes.md` if required.
