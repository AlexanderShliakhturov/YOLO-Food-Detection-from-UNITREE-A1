import os

for root, dirs, files in os.walk("./media"):  
    for filename in files:
        print(f'{root}/{filename}')