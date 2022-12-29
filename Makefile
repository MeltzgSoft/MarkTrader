generate-cert:
	openssl req -nodes -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -subj "/C=US/ST=MA/O=MeltzgSoft"

build-client:
	cd client && \
	npm run build

run:
	uvicorn app:app \
		--host 0.0.0.0 \
		--port 8089 \
		--reload \
		--ssl-keyfile key.pem \
		--ssl-certfile cert.pem
