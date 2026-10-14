# Run and publish AeroMAT Lab (Windows / VS Code)

This is an independent aerospace engineering calculator. Upload the extracted **project files**, not the ZIP, to your GitHub repository.

## A — Run the local application

1. Extract `aeromat-lab-independent.zip`. Open the newly extracted `aeromat-lab` folder in **VS Code → File → Open Folder**. Make sure `app.py` is visible at the top level.
2. Open **Terminal → New Terminal** and enter `python --version`. Python 3.10+ is required.
3. If this is a new folder, run the following commands **one at a time**, waiting for each to finish:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m streamlit run app.py
```

4. Open the local address printed by Streamlit, commonly `http://localhost:8501`. Change **Airspeed** or **Spar height** and check that outputs update. Explore all five tabs. Upload `data/example_scenarios.csv` in the **Batch CSV** tab.
5. Stop Streamlit with **Ctrl + C** in the terminal when finished.

**Tip:** Your computer may have Python installed but not the `py` launcher; that is normal. The commands above use `python`. You do not need to activate `.venv` in PowerShell.

## B — Create a GitHub repository

1. Log in at [github.com](https://github.com/) and select **New repository**.
2. Name the repository `aeromat-lab` and select Public or Private. Do not pre-create a README, license or `.gitignore`, because these exist in the folder.
3. In VS Code's terminal, with `aeromat-lab` open, run these commands one at a time:

```powershell
git init
git add .
git commit -m "Publish standalone AeroMAT Lab calculator"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/aeromat-lab.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If an `origin` remote already exists, check it with `git remote -v` instead of adding it again. Git may ask you to set your name/email or sign in using the system browser. Never paste passwords or access tokens into the code or chat.

4. Refresh the repository page. Ensure `app.py`, `aeromat/`, `tests/`, `docs/`, `.github/`, `.streamlit/` and `requirements.txt` are visible. `.venv` should **not** be uploaded. Review the **Actions** tab to see test results.

## C — Deploy a public website with Streamlit

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
2. Choose to deploy a new app from your GitHub repository.
3. Repository: `YOUR-USERNAME/aeromat-lab`. Branch: `main`. Main file: `app.py`.
4. Deploy. Streamlit will install packages from `requirements.txt` and create a URL for your website.
5. Test input recalculation, materials comparison, spar exploration, JSON/CSV downloads and batch upload on the deployed site.

## D — Public presentation checklist

- Put the actual app link in the repository's About section and `README.md`.
- Check that screenshots do not reveal local file paths or private information.
- Keep engineering assumptions and limitations visible; calculations are educational screening estimates, not certified designs.
- Rerun tests after changes to equations or input handling.
- Before publishing, search all project files for unwanted affiliations or outdated text.

## Troubleshooting

- If the command `python` is missing, reinstall a supported Python version with command-line access configured, then restart VS Code.
- If a package is missing, rerun the pip command using the explicit `.venv\Scripts\python.exe` path.
- If `git` is not found, install Git for Windows, then reopen the terminal.
- If port 8501 is busy, stop the previous Streamlit server with **Ctrl + C**, or use the new URL shown in the terminal.
