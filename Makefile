generate-cert:
	openssl req -nodes -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -subj "/C=US/ST=MA/O=MeltzgSoft"