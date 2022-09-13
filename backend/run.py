from app import create_app

if __name__ == "__main__":
    a = create_app()
    a.run(debug=True)
