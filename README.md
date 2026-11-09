# BioMat CodeLab — Three Missions + Unified Student Progress

This Streamlit project combines:
1. Biotechnology Quest
2. Materials Science Mission
3. Bio-Materials Mission

It now includes a shared XP system and a student progress dashboard.

## Run locally

Use Python 3.10 or newer. Open a terminal in this project folder and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run Home.py
```

## Student profiles and saved progress

1. Open the Home page (shown in the sidebar instead of “app”).
2. In the sidebar, enter a student username/ID and display name.
3. Click **Save / load profile**.
4. Complete challenges in any of the three missions.
5. Visit **Student Progress Dashboard** to see combined XP, mission breakdown, completed task IDs, and the leaderboard.
6. Use exactly the same username/ID on later visits to retrieve that profile's progress.

Progress is stored in `student_progress.db` using SQLite. The database is created automatically beside `Home.py`. It is intentionally excluded from Git by `.gitignore`, so do not expect a fresh deployment to inherit a database from your computer.

### Important hosting note

SQLite storage is persistent on your own computer as long as `student_progress.db` is retained. Streamlit Community Cloud uses an ephemeral application filesystem; its local SQLite file may be lost when the app restarts or is redeployed. For durable progress across online users and restarts, connect a hosted database such as Supabase/PostgreSQL and store credentials in Streamlit Secrets. The current SQLite implementation is suitable for local testing and demonstrations, not secure identity verification or a production multi-user service.

Student usernames are classroom identifiers, not authentication credentials. Do not collect passwords or sensitive personal information in this prototype.

## Repository structure

```text
Home.py
progress_store.py
requirements.txt
README.md
.gitignore
pages/
  1_Biotechnology_Quest.py
  2_Materials_Science_Mission.py
  3_BioMaterials_Mission.py
  4_Student_Progress.py
images/
  ... biological image assets ...
```

Upload the contents of this folder (not the ZIP itself) to the root of your GitHub repository. In Streamlit Community Cloud, set the main file path to `Home.py`.

## Scientific limitations

The scaffold dataset and several simulator examples are educational illustrations. They are not validated clinical or engineering recommendations.
