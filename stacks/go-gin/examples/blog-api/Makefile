.PHONY: build run test lint fmt vet quality tidy migrate-up migrate-down

build:
	go build -o bin/server ./cmd/server

run:
	go run ./cmd/server

test:
	go test ./... -v -race -cover

lint:
	golangci-lint run

fmt:
	gofmt -w .
	goimports -w .

vet:
	go vet ./...

tidy:
	go mod tidy

quality: fmt vet lint test
	@echo "All quality checks passed!"

migrate-up:
	migrate -database "$$DATABASE_URL" -path migrations up

migrate-down:
	migrate -database "$$DATABASE_URL" -path migrations down 1
