from config import LOCAL_GITHUB_DIR
import argparse
import os
import shutil
import zipfile

def unzip_files(name: str, dir_name: str):
    os.makedirs(dir_name, exist_ok=True)
    with zipfile.ZipFile(name,"r") as zip_ref:
        zip_ref.extractall(dir_name) 
    os.remove(name)
    for root, dirs, files in os.walk(dir_name):
        for file in files:
            if file.endswith(".zip"):
                nested_zip = os.path.join(root, file)
                nested_dir = os.path.splitext(nested_zip)[0]
                unzip_files(nested_zip, nested_dir)

def content_check(name: str):
    print("-----CONTENTS-----")
    for root, dirs, files in os.walk(name):
        for file in files:
            file_path = os.path.join(root, file)
            if not zipfile.is_zipfile(file_path) and not file_path.lower().endswith('.csv'):
                print(file)
    print("------------------")

def github_move(dirname: str, reponame: str, f_name: str):
    local_github_dir = os.path.join(LOCAL_GITHUB_DIR, reponame)
    if not os.path.isdir(local_github_dir):
        print("Github folder doesn't exist")
        return False
    else:
        f_dir = os.path.join(local_github_dir, f_name)
        # if os.path.isdir(f_dir):
        #     resp = input("Folder already exists. Wish to overwrite? (Y/n): ")
        #     if resp == "Y":
        #         shutil.rmtree(f_dir)
        #     else:
        #         print("Please choose a different folder name")
        #         return False
        os.makedirs(f_dir, exist_ok=True)
        print("-------------------")
        files_to_move = []
        for root, dirs, files in os.walk(dirname):
            for file in files:
                file_path = os.path.join(root, file)
                if not zipfile.is_zipfile(file_path) and not file_path.lower().endswith('.csv'):
                    files_to_move.append(file_path)
        for file_path in files_to_move:
            filename = os.path.basename(file_path)
            destination_path = os.path.join(f_dir, filename)
            if os.path.exists(destination_path):
                resp = input(f"{filename} already exists. Wish to overwrite? (Y/n): ")
                if resp == "Y":
                    os.remove(destination_path)
                else:
                    print(f"Skipping: {filename}")
                    continue  
            print("Moving file:", filename)
            shutil.move(file_path, f_dir)
        shutil.rmtree(dirname)
    return True


def reformat_titles(dir_name: str):
    for root, dirs, files in os.walk(dir_name):
        for file in files:
            old_path = os.path.join(root, file)
            if file.endswith('.md'):
                name, ext = os.path.splitext(file)
                new_name = name.rsplit(" ", 1)[0] + ext
                new_name = new_name.replace(" ", "_")
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)
                print(f"{file} -> {new_name} is formatted")



def github_remote(repo_name: str):
    repo_dir = os.path.join(LOCAL_GITHUB_DIR, repo_name)
    os.chdir(repo_dir)
    os.system("git add .")
    os.system('git commit -m "Update commit"')
    os.system("git push -u origin main")
    print("Successfully pushed to github")

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('foldername')
    args = parser.parse_args()
    folder_name = args.foldername
    dir_name = os.path.splitext(folder_name)[0]
    return folder_name, dir_name

def main():
    folder_name, dir_name = parser()

    if not folder_name.endswith('zip'):
        print("Not a zip file")
        return
    
    unzip_files(folder_name, dir_name)

    if dir_name in os.listdir('.'):
        content_check(dir_name)
    else:
        print("Problem with unzipping: Retry.")
    
    reformat_titles(dir_name)

    resp = input("Do you wish to move it to local github repo?(Y/n): ")
    if resp == "n":
        return 
    if resp == "Y":
        repo_name = input("Repo name (should already exist): ")
        f_name = input("Folder name: ")
        move_successful = github_move(dir_name, repo_name, f_name)
        if not move_successful:
            return
    else:
        print("Invalid option.")
        return

    resp2 = input("Do you wish to push to remote github repo?(Y/n): ")
    if resp2 == "Y":
        github_remote(repo_name)
    elif resp2 == "n":
        return
    else:
        print("Invalid option.")
        


if __name__=="__main__":
    main()  

    

