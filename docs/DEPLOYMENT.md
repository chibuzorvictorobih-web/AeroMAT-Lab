# Running, updating and deploying AeroMAT Lab

AeroMAT Lab is an independent educational engineering calculator. The project is
already available as a [public GitHub repository](https://github.com/chibuzorvictorobih-web/AeroMAT-Lab)
and a [live Streamlit app](https://aeromat-lab.streamlit.app/).

## A — Run locally on Windows with VS Code

1. Open your **clean local repository clone** in VS Code. The repository root contains
   `app.py`, `aeromat/`, `tests/` and `requirements.txt`. If cloning afresh, use:

   ```powershell
   git clone https://github.com/chibuzorvictorobih-web/AeroMAT-Lab.git
   cd AeroMAT-Lab
   ```

2. With a Python 3.11 or 3.13 installation available, run commands individually:

   ```powershell
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   .venv\Scripts\python.exe -m pytest -q
   .venv\Scripts\python.exe -m streamlit run app.py
   ```

3. Open the local Streamlit address displayed by your terminal. Adjust the airspeed
   and material; examine the five tabs and export a sample result. Upload
   `data/example_scenarios.csv` in the Batch CSV tab and verify that four rows
   are processed successfully. Stop the app with **Ctrl+C**.

## B — Update the existing GitHub repository safely

**Do not initialize another repository or push an older project folder.** The published
Git history was rebuilt to exclude previous local cache paths. Work from the current
clean clone, rather than another folder that still contains old commits.

1. In GitHub **Settings → Emails**, keep email privacy enabled, and use your own GitHub
   `@users.noreply.github.com` address for local commits.
2. In the clean clone, verify Git configuration before committing:

   ```powershell
   git status
   git remote get-url origin
   git branch --show-current
   if ((git config --local user.email) -match '@users\.noreply\.github\.com$') { 'Email protected' } else { 'STOP: fix email configuration' }
   ```

3. Make only intended changes. Stage reviewed files, not local environment folders.
   Run tests before publishing. After checking `git diff --cached`, use your own
   meaningful commit message and push the `main` branch:

   ```powershell
   git add README.md docs/DEPLOYMENT.md docs/DEVELOPMENT_TASKS.md docs/TEST_REPORT.md .gitignore
   git diff --cached --stat
   git commit -m 'Refresh project verification documents'
   git push origin main
   ```

4. Confirm the GitHub Actions workflow passes. Avoid uploading virtual environments,
   local caches, API credentials, desktop settings, private files or screenshots
   containing private local paths. The `.gitignore` covers common local artefacts,
   but always review staged changes.

## C — Streamlit Community Cloud

The live website is `https://aeromat-lab.streamlit.app/`. The existing deployment
should use `chibuzorvictorobih-web/AeroMAT-Lab`, branch `main` and entrypoint `app.py`.
If a repository recreation breaks the deployment, open your existing Streamlit
Community Cloud app settings, inspect the source repository and branch, and reconnect
or redeploy it from the same clean repository. Avoid creating duplicate apps unless
necessary.

## D — Release checks

- Confirm the README and app links open, and the GitHub branch is `main`.
- Ensure GitHub Actions shows successful Python 3.11 and 3.13 jobs for the new commit.
- On a phone, check the layout, inputs and charts; browser rendering is not covered by AppTest.
- Upload the bundled CSV, confirm four successful example rows, and download results.
- Verify that no laptop paths, API keys, private email addresses, local config files
  or unauthorized affiliation claims appear in tracked files and commit metadata.
- Keep this project clearly labelled as a preliminary educational screening model;
  do not claim aircraft certification, CFD/FEA, physical validation or a verified LCA.

## Troubleshooting

If Python is not on PATH, install a supported version and reopen VS Code. If a package
is missing, repeat the install command within `.venv`. If Git authentication fails,
check that you are signed into the correct GitHub account. If a Streamlit port is busy,
stop the previous process or open the different address printed by the server.
