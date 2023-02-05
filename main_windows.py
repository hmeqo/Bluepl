from src.platform_windows import main

if __name__ == "__main__":
    from src.gconfig import App
    App.debug = True
    main()
