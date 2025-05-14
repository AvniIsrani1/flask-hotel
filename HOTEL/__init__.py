from .factory import Factory

factory = Factory()
app = factory.create_app()

if __name__ == "__main__":
    app.run(debug=True)

