# Contributing to QR Network Scanner

Thank you for your interest in contributing! We welcome bug fixes, feature improvements, and documentation updates.

## 🛠 Developer Setup

### Prerequisites

1. **Python 3.10+**
2. **uv** (Fast Python package installer)

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/elephantatech/QR_Network_Scanner.git
    cd QR_Network_Scanner
    ```

2. **Install dependencies (including dev tools):**

    ```bash
    uv sync --all-extras
    ```

3. **Install Git Hooks (Critical):**
    We use `pre-commit` to ensure code quality before every commit.

    ```bash
    uv run pre-commit install
    ```

## 🧪 Quality Assurance

### Local Checks

Before submitting a Pull Request, run our all-in-one check script. This runs formatting, linting, and unit tests.

```bash
./scripts/check.sh
```

### Pre-commit Hooks

The following checks run automatically when you `git commit`:

- **Ruff Formatting:** Auto-formats code.
- **Ruff Linting:** Checks for errors (and fixes some automatically).
- **Markdown Linting:** Ensures documentation consistency.
- **Unit Tests:** Runs `pytest` to ensure no regressions.

If a hook fails, it may have auto-fixed the file. Review the changes, `git add` them, and try committing again.

## 📝 Best Practices

1. **Atomic Commits:** Keep commits focused on a single change.
2. **Tests:** Add unit tests for new features in the `tests/` directory.
3. **Documentation:** Update `README.md` or `HELP.md` if you change user-facing features.
4. **Branching:** Create a feature branch (e.g., `feature/my-cool-feature`) off `main`.

## 🚀 Running the App

**GUI Mode:**

```bash
uv run qr-network gui
```

**CLI Mode:**

```bash
uv run qr-network scan
```

We look forward to your PRs! 🚀
