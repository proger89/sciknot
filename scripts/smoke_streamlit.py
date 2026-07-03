from __future__ import annotations

from pathlib import Path


def main() -> int:
    app = Path("app.py")
    if not app.exists():
        print("smoke_streamlit: app.py missing")
        return 1
    text = app.read_text(encoding="utf-8")
    needed = ["st.set_page_config", "SciKnot Navigator", "prepared_questions"]
    missing = [item for item in needed if item not in text]
    if missing:
        print("smoke_streamlit: missing markers " + ", ".join(missing))
        return 1
    screenshots = Path("demo/screenshots")
    screenshots.mkdir(parents=True, exist_ok=True)
    placeholder = screenshots / "streamlit_smoke.txt"
    placeholder.write_text("Streamlit smoke passed; launch http://localhost:8501 for browser screenshot.\n", encoding="utf-8")
    print(f"smoke_streamlit: static smoke passed; screenshot placeholder {placeholder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
