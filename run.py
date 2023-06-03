import os


def main():
    from bot import start_bot
    start_bot()


if __name__ == '__main__':
    os.system('git reset --hard')
    os.system('git pull origin master')
    main()
