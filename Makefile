export APP_NAME=test-flask-server
run:
	python main.py
install-dependencies:
	pip install -r requirements.txt
build-docker:
	docker build -t ${APP_NAME} .
run-docker:
	docker run -d -p 5000:5000 ${APP_NAME}