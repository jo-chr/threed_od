import sys

yes = {'yes','y', 'ye', ''}
no = {'no','n'}

def main(message: str):
    print(message)
    choice = input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")