PORT ?= 8000

.PHONY: build serve clean

# Reconstrói o site estático em _site/
build:
	jekyll build

# Reconstrói e serve em http://localhost:$(PORT) para testar no navegador.
# Ctrl+C para parar.
serve: build
	@echo "Servindo em http://localhost:$(PORT)  (Ctrl+C para parar)"
	cd _site && python3 -m http.server $(PORT)

# Apaga o build local (o Jekyll o recria no próximo build)
clean:
	rm -rf _site .jekyll-cache
