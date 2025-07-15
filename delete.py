import os

if os.path.exists("tasks.db"):
    os.remove("tasks.db")
    print("Tasks.db database successfully deleted")
else:
    print("The file tasks.db was not found")
