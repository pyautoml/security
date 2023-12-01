#!/usr/bin/python3.11

"""
Save this file in the path where your .gitignore file is located. 
Run it to check if there are any files containing sensitive data,
such as passwords, that haven't been added to .gitignore.

Example file structure:
    main_directory:
        /conf
            conf.conf
        /other
            ..
        .gitignore
        passwords.txt
        hidden_credentials.txt
        hidden_credentials_validator.py

"""

__created__ = "01.12.2023"
__last_update__ = ""
__author__ = "https://github.com/pyautoml"


import os
import re
import gc


def absolute_path(directory: str = None) -> str:
    return (
        os.path.abspath(os.path.join(os.path.dirname(__file__)))
        if not directory
        else os.path.abspath(os.path.join(os.path.dirname(__file__), directory))
    )


def final_decision(check_data: dict) -> str:
    if check_data:
        print()
        print("---------- ❌  Push is forbidden! ❌ ----------")
        for key, value in check_data.items():
            print(f"{key} {value}")
        print()
    else:
        print()
        print("---------- ✅ OK! No hidden credentials ✅ ----------")
        print()


def check_gitignore():
    ignored_files = []
    checked_ignored_files = []

    if os.path.isfile(".gitignore"):
        with open(".gitignore", "r") as gitignore_file:
            ignored_files = gitignore_file.read().splitlines()
            for file in ignored_files:
                if file.startswith("."):
                    checked_ignored_files.append(file[1:])
                elif file.startswith("./"):
                    checked_ignored_files.append(file[2:])
                else:
                    checked_ignored_files.append(file)
    del ignored_files
    gc.collect()
    return checked_ignored_files


def check_for_forbidden_entries(file_path):
    forbidden_patterns = [
        r"\[.*\]",
        r"\bpass\b",
        r"\bpassword\b",
        r"\bserver\b",
        r"\bproxy\b",
        r"\bmail\b",
        r"\buser\b",
        r"\bemail\b",
    ]

    prevent_to_push = []

    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            for pattern in forbidden_patterns:
                if re.search(pattern, line):
                    if file_path not in prevent_to_push:
                        prevent_to_push.append(file_path)
    return prevent_to_push


def is_file_in_ignored_directory(file_path, ignored_directories):
    file_path = file_path.replace("\\", "/")
    return any(ignored_dir in file_path for ignored_dir in ignored_directories)


def check_possible_config_files(ignored_directories):
    ignored_files = []
    possible_config_files = []
    common_credential_file_extensions = (".conf", ".txt", ".cf")

    for directory in ignored_directories:
        try:
            ignored_files = [file for file in os.listdir(absolute_path(directory))]
            for root, dirs, files in os.walk(".", topdown=True):
                dirs[:] = [d for d in dirs if d not in ignored_files]

                for file in files:
                    file_path = os.path.join(root, file)
                    if (
                        file.lower().endswith(common_credential_file_extensions)
                        or "." not in file
                        and os.path.isfile(file)
                    ):
                        if file not in ignored_files and file not in check_gitignore():
                            possible_config_files.append(file_path)
        except:
            pass

    del ignored_files
    del common_credential_file_extensions
    gc.collect()
    return possible_config_files


def main():
    check_data = {}
    prevent_to_push = []
    ignored_files = check_gitignore()
    _, tail = os.path.split(__file__)
    ignored_directories = [
        d.replace("/", "").replace("./", "")
        for d in ignored_files
        if (d.startswith("/") or d.startswith("./"))
    ]

    for root, dirs, files in os.walk(".", topdown=True):
        files = [file for file in files if file not in ignored_files]
        if tail in files:
            files.remove(tail)
        for file in files:
            file_path = os.path.join(root, file)
            try:
                compare_dir = file_path.split("\\")
                if compare_dir[1] in ignored_directories:
                    pass
                else:
                    prevent_to_push += check_for_forbidden_entries(file_path)
            except:
                prevent_to_push += check_for_forbidden_entries(file_path)

    prevent_to_push = [file.replace(".\\", "") for file in prevent_to_push]
    possible_config_files = [
        file.replace(".\\", "")
        for file in check_possible_config_files(ignored_directories)
    ]

    if prevent_to_push or possible_config_files:
        check_data = {
            "-> Some credentials might still be stored in:": ", ".join(
                [file for file in prevent_to_push]
            ),
            "-> Please add to .gitignore:": ", ".join(
                [file for file in possible_config_files]
            ),
        }

    final_decision(check_data)


if __name__ == "__main__":
    main()
